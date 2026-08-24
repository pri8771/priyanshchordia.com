#!/usr/bin/env python3
"""Teach the production CommerceLint mount to preserve and verify opt-in GA4."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNC = ROOT / "scripts" / "sync_commercelint.py"
WORKFLOW = ROOT / ".github" / "workflows" / "pages.yml"
MEASUREMENT_ID = "G-3TY7EMFMWM"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Could not locate {label}")
    return text.replace(old, new, 1)


def patch_sync() -> None:
    text = SYNC.read_text(encoding="utf-8")

    if '    "assets/analytics.js",\n' not in text:
        text = replace_once(
            text,
            '    "assets/site.css",\n',
            '    "assets/site.css",\n    "assets/analytics.js",\n',
            "required analytics asset",
        )

    text, count = re.subn(
        r"\n\ndef analytics_javascript\(\) -> str:\n.*?\n\n\ndef og_card_svg",
        "\n\ndef og_card_svg",
        text,
        count=1,
        flags=re.DOTALL,
    )
    if count == 0 and "def analytics_javascript()" in text:
        raise RuntimeError("Could not remove the obsolete no-op analytics generator")

    text = text.replace(
        '    (assets / ANALYTICS_FILENAME).write_text(analytics_javascript(), encoding="utf-8")\n',
        "",
        1,
    )

    old_metadata = '''        "analytics": {
            "provider": "None",
            "mode": "disabled",
            "consent_required": False,
            "network_requests": False,
        },'''
    new_metadata = f'''        "analytics": {{
            "provider": "Google Analytics 4",
            "measurement_id": "{MEASUREMENT_ID}",
            "mode": "explicit_opt_in",
            "consent_required": True,
            "network_requests_before_consent": False,
            "network_requests_after_consent": True,
            "event_namespace": "cl_",
            "data_minimization": [
                "query strings removed from page location",
                "no pasted HTML, scanned URLs, scanned titles, evidence, emails, or form contents",
                "advertising storage, Google signals, ad personalization, and ad user data disabled",
            ],
        }},'''
    text = replace_once(text, old_metadata, new_metadata, "deployment analytics metadata")

    old_privacy = '''    privacy = (target / "privacy.html").read_text(encoding="utf-8") if (target / "privacy.html").exists() else ""
    privacy_lower = privacy.lower()
    has_tracker_disclosure = (
        "third-party analytics" in privacy_lower
        and ("advertising tracker" in privacy_lower or "advertising trackers" in privacy_lower)
    )
    has_no_network_disclosure = any(
        marker in privacy_lower
        for marker in ("no network events", "sends no page or scanner data", "no-network")
    )
    if not (has_tracker_disclosure and has_no_network_disclosure):
        errors.append("privacy.html: no-network analytics disclosure is missing")'''
    new_privacy = f'''    privacy = (target / "privacy.html").read_text(encoding="utf-8") if (target / "privacy.html").exists() else ""
    privacy_lower = privacy.lower()
    for marker in (
        "google analytics 4",
        "only after you select",
        "does <strong>not</strong> send pasted html",
        "global privacy control",
    ):
        if marker not in privacy_lower:
            errors.append(f"privacy.html: missing consent disclosure marker {{marker!r}}")

    analytics_path = target / "assets" / ANALYTICS_FILENAME
    analytics = analytics_path.read_text(encoding="utf-8") if analytics_path.exists() else ""
    for marker in (
        "{MEASUREMENT_ID}",
        "commercelint:analyticsConsent:v1",
        "window.commerceLintTrack = track",
        "send_page_view: false",
        "readConsent() !== \\\"granted\\\"",
    ):
        if marker not in analytics:
            errors.append(f"analytics.js: missing consent marker {{marker!r}}")
    for forbidden in ("storeUrl", "pageTitle", "246481057", "js.hs-scripts.com"):
        if forbidden in analytics:
            errors.append(f"analytics.js: prohibited marker {{forbidden!r}}")

    analytics_loader = re.compile(r'<script\\b[^>]*src=["\\\'][^"\\\']*assets/analytics\\.js["\\\']', re.I)
    for page in sorted(target.rglob("*.html")):
        page_text = page.read_text(encoding="utf-8")
        count = len(analytics_loader.findall(page_text))
        if count != 1:
            errors.append(f"{{page.relative_to(target)}}: expected one local analytics loader, found {{count}}")
        if "googletagmanager.com/gtag/js" in page_text:
            errors.append(f"{{page.relative_to(target)}}: Google tag is loaded directly before consent")'''
    text = replace_once(text, old_privacy, new_privacy, "production analytics validation")

    SYNC.write_text(text, encoding="utf-8")


def patch_pages_workflow() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    old_invariants = '''      - name: Check CommerceLint privacy and JavaScript invariants
        shell: bash
        run: |
          node --check site/commercelint/assets/analytics.js
          test -z "$(grep -RIlE '246481057|js\\.hs-scripts\\.com' site/commercelint || true)"
          grep -q 'CommerceLint' site/commercelint/index.html
          grep -q 'priyanshchordia.com/commercelint/' site/commercelint/index.html
          grep -q 'priyanshchordia.com/commercelint/' site/machinecart/index.html'''
    new_invariants = f'''      - name: Check CommerceLint privacy and analytics invariants
        shell: bash
        run: |
          node --check site/commercelint/assets/analytics.js
          test -z "$(grep -RIlE '246481057|js\\.hs-scripts\\.com' site/commercelint || true)"
          test -z "$(grep -RIl 'googletagmanager.com/gtag/js' site/commercelint --include='*.html' || true)"
          grep -q '{MEASUREMENT_ID}' site/commercelint/assets/analytics.js
          grep -q 'commercelint:analyticsConsent:v1' site/commercelint/assets/analytics.js
          grep -q 'window.commerceLintTrack = track' site/commercelint/assets/analytics.js
          grep -q 'send_page_view: false' site/commercelint/assets/analytics.js
          grep -q 'only after you select' site/commercelint/privacy.html
          grep -q 'assets/analytics.js' site/commercelint/index.html
          grep -q 'CommerceLint' site/commercelint/index.html
          grep -q 'priyanshchordia.com/commercelint/' site/commercelint/index.html
          grep -q 'priyanshchordia.com/commercelint/' site/machinecart/index.html'''
    text = replace_once(text, old_invariants, new_invariants, "build analytics invariant step")

    text = replace_once(
        text,
        '          status="$(mktemp)"\n          legacy="$(mktemp)"',
        '          status="$(mktemp)"\n          analytics="$(mktemp)"\n          privacy="$(mktemp)"\n          legacy="$(mktemp)"',
        "production temporary files",
    )

    text = replace_once(
        text,
        '              && curl -fsSL --max-time 20 "https://priyanshchordia.com/commercelint/status.json" -o "$status" \\\n              && curl -fsSL --max-time 20 "https://priyanshchordia.com/machinecart/" -o "$legacy" \\\',
        '              && curl -fsSL --max-time 20 "https://priyanshchordia.com/commercelint/status.json" -o "$status" \\\n              && curl -fsSL --max-time 20 "https://priyanshchordia.com/commercelint/assets/analytics.js" -o "$analytics" \\\n              && curl -fsSL --max-time 20 "https://priyanshchordia.com/commercelint/privacy.html" -o "$privacy" \\\n              && curl -fsSL --max-time 20 "https://priyanshchordia.com/machinecart/" -o "$legacy" \\\',
        "production analytics fetches",
    )

    text = replace_once(
        text,
        '              && grep -q "analyzeMarkup" "$scanner" \\\n              && grep -q "priyanshchordia.com/commercelint/" "$legacy" \\\',
        f'''              && grep -q "analyzeMarkup" "$scanner" \\
              && grep -q "assets/analytics.js" "$home" \\
              && ! grep -q "googletagmanager.com/gtag/js" "$home" \\
              && grep -q "{MEASUREMENT_ID}" "$analytics" \\
              && grep -q "commercelint:analyticsConsent:v1" "$analytics" \\
              && grep -q "window.commerceLintTrack = track" "$analytics" \\
              && grep -q "send_page_view: false" "$analytics" \\
              && grep -q "only after you select" "$privacy" \\
              && grep -q "does <strong>not</strong> send pasted HTML" "$privacy" \\
              && grep -q "priyanshchordia.com/commercelint/" "$legacy" \\''',
        "production consent assertions",
    )

    text = replace_once(
        text,
        '                  "excluded Primandir analytics references were absent",\n                  "IndexNow ownership key was publicly reachable",',
        '                  "excluded Primandir analytics references were absent",\n                  "GA4 runtime was local, explicit-opt-in, and data-minimized",\n                  "public HTML did not load the Google tag before consent",\n                  "IndexNow ownership key was publicly reachable",',
        "deployment receipt analytics checks",
    )

    WORKFLOW.write_text(text, encoding="utf-8")


def validate() -> None:
    sync = SYNC.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    required_sync = (
        '"assets/analytics.js"',
        '"provider": "Google Analytics 4"',
        MEASUREMENT_ID,
        "network_requests_before_consent",
        "expected one local analytics loader",
    )
    required_workflow = (
        MEASUREMENT_ID,
        "commercelint:analyticsConsent:v1",
        "public HTML did not load the Google tag before consent",
        'privacy="$(mktemp)"',
    )
    missing = [f"sync:{m}" for m in required_sync if m not in sync]
    missing += [f"workflow:{m}" for m in required_workflow if m not in workflow]
    if "analytics_javascript()" in sync:
        missing.append("sync:obsolete no-op generator remains")
    if missing:
        raise RuntimeError("Production analytics migration incomplete: " + ", ".join(missing))


def main() -> int:
    patch_sync()
    patch_pages_workflow()
    validate()
    print("Production CommerceLint mount now preserves and verifies consent-gated GA4.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
