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

    if "import os\n" not in text:
        text = replace_once(text, "import json\n", "import json\nimport os\n", "os import")

    if '    "assets/analytics.js",\n' not in text:
        text = replace_once(
            text,
            '    "assets/site.css",\n',
            '    "assets/site.css",\n    "assets/analytics.js",\n',
            "required analytics asset",
        )

    replacement = r'''def rewrite_public_tree(target: Path) -> None:
    analytics_target = target / "assets" / ANALYTICS_FILENAME
    loader_pattern = re.compile(
        r'\s*<script\b[^>]*\bsrc=["\'][^"\']*assets/analytics\.js["\'][^>]*>\s*</script>',
        re.IGNORECASE,
    )
    for path in sorted(target.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlinks are not allowed in public assets: {path}")
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for old in OLD_BASES:
            text = text.replace(old, PRODUCTION_BASE)
        text = text.replace("MachineCart", "CommerceLint").replace("machinecart", "commercelint")
        if path.suffix.lower() == ".html":
            text = replace_or_insert_canonical(text, canonical_for(path.relative_to(target)))
            text = loader_pattern.sub("", text)
            relative = os.path.relpath(analytics_target, path.parent).replace(os.sep, "/")
            if "</head>" not in text:
                raise ValueError(f"{path.relative_to(target)} has no closing head tag")
            text = text.replace("</head>", f'  <script defer src="{relative}"></script>\n</head>', 1)
        path.write_text(text, encoding="utf-8")


def og_card_svg'''
    text, count = re.subn(
        r"def rewrite_public_tree\(target: Path\) -> None:.*?\n\n\ndef og_card_svg",
        replacement,
        text,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise RuntimeError("Could not replace the production tree rewriter and no-op analytics generator")

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

    old_validation = '''    privacy = (target / "privacy.html").read_text(encoding="utf-8") if (target / "privacy.html").exists() else ""
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
    new_validation = f'''    privacy = (target / "privacy.html").read_text(encoding="utf-8") if (target / "privacy.html").exists() else ""
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
        'readConsent() !== "granted"',
    ):
        if marker not in analytics:
            errors.append(f"analytics.js: missing consent marker {{marker!r}}")
    for forbidden in ("storeUrl", "pageTitle", "246481057", "js.hs-scripts.com"):
        if forbidden in analytics:
            errors.append(f"analytics.js: prohibited marker {{forbidden!r}}")

    loader_pattern = re.compile(r'<script\\b[^>]*src=["\\\'][^"\\\']*assets/analytics\\.js["\\\']', re.I)
    for page in sorted(target.rglob("*.html")):
        page_text = page.read_text(encoding="utf-8")
        loader_count = len(loader_pattern.findall(page_text))
        if loader_count != 1:
            errors.append(f"{{page.relative_to(target)}}: expected one local analytics loader, found {{loader_count}}")
        if "googletagmanager.com/gtag/js" in page_text:
            errors.append(f"{{page.relative_to(target)}}: Google tag is loaded directly before consent")'''
    text = replace_once(text, old_validation, new_validation, "production analytics validation")

    SYNC.write_text(text, encoding="utf-8")


def patch_pages_workflow() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    old = '''      - name: Check CommerceLint privacy and JavaScript invariants
        shell: bash
        run: |
          node --check site/commercelint/assets/analytics.js
          test -z "$(grep -RIlE '246481057|js\\.hs-scripts\\.com' site/commercelint || true)"
          grep -q 'CommerceLint' site/commercelint/index.html
          grep -q 'priyanshchordia.com/commercelint/' site/commercelint/index.html
          grep -q 'priyanshchordia.com/commercelint/' site/machinecart/index.html'''
    new = f'''      - name: Check CommerceLint privacy and analytics invariants
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
    text = replace_once(text, old, new, "build analytics invariant step")

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
        "os.path.relpath",
    )
    required_workflow = (
        MEASUREMENT_ID,
        "commercelint:analyticsConsent:v1",
        "public HTML did not load the Google tag before consent",
    )
    missing = [f"sync:{marker}" for marker in required_sync if marker not in sync]
    missing += [f"workflow:{marker}" for marker in required_workflow if marker not in workflow]
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
