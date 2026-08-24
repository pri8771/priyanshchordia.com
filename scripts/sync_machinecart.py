#!/usr/bin/env python3
"""Mount the autonomous MachineCart site into the production portfolio build.

The source repository remains the durable business/operator source of truth.
This script copies only the public ``docs/`` tree, rewrites canonical URLs for
the production path, adds consent-gated analytics, and validates the mounted
site before GitHub Pages deployment.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

PRODUCTION_BASE = "https://priyanshchordia.com/machinecart/"
LEGACY_BASES = (
    "https://pri8771.github.io/autonomous_apps/",
    "https://raw.githack.com/pri8771/autonomous_apps/main/docs/",
)
REQUIRED_FILES = (
    "index.html",
    "scanner.html",
    "privacy.html",
    "status.html",
    "status.json",
    "sample-audit.html",
    "founding-audit.html",
    "agency.html",
    "assets/site.css",
    "guides/index.html",
    "sitemap.xml",
)
ANALYTICS_FILENAME = "analytics.js"
HUBSPOT_PORTAL_ID = "246481057"


class PublicPageParser(HTMLParser):
    """Collect the small set of invariants needed for the mounted product."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h1_count = 0
        self.main_count = 0
        self.title_parts: list[str] = []
        self.in_title = False
        self.canonicals: list[str] = []
        self.anchors: list[str] = []
        self.assets: list[str] = []
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()

    @property
    def title(self) -> str:
        return "".join(self.title_parts).strip()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "h1":
            self.h1_count += 1
        elif tag == "main":
            self.main_count += 1
        elif tag == "title":
            self.in_title = True
        elif tag == "a" and values.get("href"):
            self.anchors.append(values["href"])
        elif tag == "script" and values.get("src"):
            self.assets.append(values["src"])
        elif tag == "link" and values.get("href"):
            rel = set(values.get("rel", "").lower().split())
            if "canonical" in rel:
                self.canonicals.append(values["href"])
            elif "stylesheet" in rel or "icon" in rel:
                self.assets.append(values["href"])
        node_id = values.get("id")
        if node_id:
            if node_id in self.ids:
                self.duplicate_ids.add(node_id)
            self.ids.add(node_id)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)


def canonical_for(relative_path: Path) -> str:
    posix = relative_path.as_posix()
    if posix == "index.html":
        return PRODUCTION_BASE
    if relative_path.name == "index.html":
        return PRODUCTION_BASE + relative_path.parent.as_posix().strip("/") + "/"
    return PRODUCTION_BASE + posix


def relative_asset_prefix(relative_path: Path) -> str:
    return "../" * len(relative_path.parent.parts)


def extract_meta(content: str, attribute: str, value: str) -> str:
    pattern = re.compile(
        rf'<meta\b[^>]*\b{re.escape(attribute)}=["\']{re.escape(value)}["\'][^>]*\bcontent=["\']([^"\']*)["\'][^>]*>',
        re.IGNORECASE,
    )
    match = pattern.search(content)
    if match:
        return html.unescape(match.group(1)).strip()
    reverse = re.compile(
        rf'<meta\b[^>]*\bcontent=["\']([^"\']*)["\'][^>]*\b{re.escape(attribute)}=["\']{re.escape(value)}["\'][^>]*>',
        re.IGNORECASE,
    )
    match = reverse.search(content)
    return html.unescape(match.group(1)).strip() if match else ""


def extract_title(content: str) -> str:
    match = re.search(r"<title>(.*?)</title>", content, flags=re.IGNORECASE | re.DOTALL)
    return re.sub(r"\s+", " ", html.unescape(match.group(1))).strip() if match else "MachineCart"


def replace_or_insert_canonical(content: str, canonical: str) -> str:
    tag = f'<link rel="canonical" href="{html.escape(canonical, quote=True)}">'
    pattern = re.compile(r'<link\b[^>]*\brel=["\'][^"\']*\bcanonical\b[^"\']*["\'][^>]*>', re.IGNORECASE)
    if pattern.search(content):
        return pattern.sub(tag, content, count=1)
    return content.replace("</head>", f"  {tag}\n</head>", 1)


def social_meta(title: str, description: str, canonical: str, prefix: str) -> str:
    image = PRODUCTION_BASE + "assets/og-card.svg"
    safe_title = html.escape(title, quote=True)
    safe_description = html.escape(description or "Evidence-first AI-shopping readiness for ecommerce stores.", quote=True)
    safe_canonical = html.escape(canonical, quote=True)
    return f"""
  <meta name="robots" content="index,follow">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{safe_title}">
  <meta property="og:description" content="{safe_description}">
  <meta property="og:url" content="{safe_canonical}">
  <meta property="og:image" content="{image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{safe_title}">
  <meta name="twitter:description" content="{safe_description}">
  <meta name="twitter:image" content="{image}">
  <script defer src="{prefix}assets/{ANALYTICS_FILENAME}"></script>"""


def rewrite_html(path: Path, root: Path) -> None:
    relative = path.relative_to(root)
    content = path.read_text(encoding="utf-8")
    for old in LEGACY_BASES:
        content = content.replace(old, PRODUCTION_BASE)
    canonical = canonical_for(relative)
    content = replace_or_insert_canonical(content, canonical)

    for pattern in (
        r'\s*<meta\b[^>]*\bname=["\']robots["\'][^>]*>',
        r'\s*<meta\b[^>]*\bproperty=["\']og:[^"\']+["\'][^>]*>',
        r'\s*<meta\b[^>]*\bname=["\']twitter:[^"\']+["\'][^>]*>',
        rf'\s*<script\b[^>]*\bsrc=["\'][^"\']*{re.escape(ANALYTICS_FILENAME)}["\'][^>]*>\s*</script>',
    ):
        content = re.sub(pattern, "", content, flags=re.IGNORECASE)

    title = extract_title(content)
    description = extract_meta(content, "name", "description")
    prefix = relative_asset_prefix(relative)
    content = content.replace("</head>", social_meta(title, description, canonical, prefix) + "\n</head>", 1)
    path.write_text(content, encoding="utf-8")


def analytics_javascript() -> str:
    return f"""(() => {{
  "use strict";
  const CONSENT_KEY = "machinecart_analytics_consent";
  const EVENT_KEY = "machinecart_local_events";
  const PORTAL_ID = "{HUBSPOT_PORTAL_ID}";
  const EVENT_BASE = "/machinecart/events/";

  function consent() {{
    try {{ return localStorage.getItem(CONSENT_KEY); }} catch (_) {{ return null; }}
  }}

  function remember(name) {{
    try {{
      const events = JSON.parse(localStorage.getItem(EVENT_KEY) || "{{}}");
      events[name] = (events[name] || 0) + 1;
      localStorage.setItem(EVENT_KEY, JSON.stringify(events));
    }} catch (_) {{}}
  }}

  function loadHubSpot() {{
    if (document.getElementById("hs-script-loader")) return;
    window._hsq = window._hsq || [];
    const script = document.createElement("script");
    script.id = "hs-script-loader";
    script.async = true;
    script.defer = true;
    script.src = `https://js.hs-scripts.com/${{PORTAL_ID}}.js`;
    document.head.appendChild(script);
  }}

  function track(name) {{
    remember(name);
    if (consent() !== "granted") return;
    loadHubSpot();
    window._hsq = window._hsq || [];
    const originalPath = location.pathname + location.search;
    window._hsq.push(["setPath", EVENT_BASE + encodeURIComponent(name)]);
    window._hsq.push(["trackPageView"]);
    window._hsq.push(["setPath", originalPath]);
  }}

  function setConsent(value) {{
    try {{ localStorage.setItem(CONSENT_KEY, value); }} catch (_) {{}}
    document.getElementById("machinecart-consent")?.remove();
    if (value === "granted") {{
      loadHubSpot();
      track("analytics-consent-granted");
    }}
  }}

  function showConsent() {{
    if (consent()) return;
    const banner = document.createElement("aside");
    banner.id = "machinecart-consent";
    banner.setAttribute("aria-label", "Analytics choice");
    banner.innerHTML = `
      <div><strong>Help improve MachineCart</strong><span>Allow privacy-conscious analytics for page views and scanner funnel events. The scanner itself still runs in your browser.</span></div>
      <div class="mc-consent-actions">
        <button type="button" data-mc-consent="denied">Decline</button>
        <button type="button" data-mc-consent="granted">Allow analytics</button>
        <a href="${{location.pathname.includes("/guides/") ? "../" : ""}}privacy.html">Privacy</a>
      </div>`;
    const style = document.createElement("style");
    style.textContent = `
      #machinecart-consent{{position:fixed;z-index:9999;left:1rem;right:1rem;bottom:1rem;display:flex;gap:1rem;align-items:center;justify-content:space-between;padding:1rem 1.15rem;border:1px solid rgba(255,255,255,.16);border-radius:16px;background:#111827;color:#f8fafc;box-shadow:0 18px 60px rgba(0,0,0,.35);font:14px/1.45 system-ui,sans-serif}}
      #machinecart-consent div:first-child{{display:grid;gap:.2rem;max-width:720px}}
      #machinecart-consent span{{color:#cbd5e1}}
      .mc-consent-actions{{display:flex;gap:.55rem;align-items:center;flex-wrap:wrap}}
      .mc-consent-actions button,.mc-consent-actions a{{border:1px solid rgba(255,255,255,.2);border-radius:999px;padding:.55rem .8rem;background:#1f2937;color:#fff;text-decoration:none;cursor:pointer;font:inherit}}
      .mc-consent-actions button[data-mc-consent="granted"]{{background:#fff;color:#111827}}
      @media(max-width:720px){{#machinecart-consent{{align-items:flex-start;flex-direction:column}}}}
    `;
    document.head.appendChild(style);
    document.body.appendChild(banner);
    banner.addEventListener("click", event => {{
      const target = event.target.closest("[data-mc-consent]");
      if (target) setConsent(target.dataset.mcConsent);
    }});
  }}

  function bindFunnel() {{
    document.getElementById("scanButton")?.addEventListener("click", () => track("scanner-start"));
    document.getElementById("loadExample")?.addEventListener("click", () => track("example-loaded"));
    document.getElementById("downloadButton")?.addEventListener("click", () => track("evidence-download"));

    document.addEventListener("click", event => {{
      const link = event.target.closest("a[href]");
      if (!link) return;
      const href = link.getAttribute("href") || "";
      if (href.includes("founding-audit") || href.includes("MachineCart%20founding%20audit") || href.includes("MachineCart%20deep%20audit")) {{
        track("paid-offer-click");
      }} else if (href.includes("agency") || href.includes("agency%20pilot")) {{
        track("agency-intent");
      }} else if (href.startsWith("mailto:")) {{
        track("contact-intent");
      }}
    }});

    const results = document.getElementById("results");
    if (results) {{
      let completed = !results.classList.contains("hidden");
      const observer = new MutationObserver(() => {{
        if (!completed && !results.classList.contains("hidden")) {{
          completed = true;
          track("scanner-completed");
        }}
      }});
      observer.observe(results, {{ attributes: true, attributeFilter: ["class"] }});
    }}
  }}

  if (consent() === "granted") loadHubSpot();
  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", () => {{ showConsent(); bindFunnel(); }}, {{ once: true }});
  }} else {{
    showConsent();
    bindFunnel();
  }}
  window.machineCartTrack = track;
}})();
"""


def og_card_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-labelledby="title desc">
<title id="title">MachineCart</title><desc id="desc">AI-shopping readiness for ecommerce stores</desc>
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#07111f"/><stop offset="1" stop-color="#172554"/></linearGradient></defs>
<rect width="1200" height="630" rx="36" fill="url(#g)"/>
<circle cx="1030" cy="100" r="210" fill="#38bdf8" opacity=".16"/>
<circle cx="1040" cy="560" r="280" fill="#8b5cf6" opacity=".16"/>
<text x="92" y="215" font-family="system-ui, sans-serif" font-size="42" font-weight="700" fill="#7dd3fc">MACHINECART</text>
<text x="92" y="330" font-family="system-ui, sans-serif" font-size="70" font-weight="760" fill="#f8fafc">Make your store easier</text>
<text x="92" y="415" font-family="system-ui, sans-serif" font-size="70" font-weight="760" fill="#f8fafc">for machines to buy from.</text>
<text x="92" y="515" font-family="system-ui, sans-serif" font-size="32" fill="#cbd5e1">Evidence-first product, offer, variant and policy diagnostics.</text>
</svg>
"""


def privacy_rewrite(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    old = (
        "<section><h2>Analytics</h2><p>The first release does not embed advertising trackers. "
        "Aggregate first-party analytics may be added later to understand scanner starts, completions, "
        "conversions, and product usefulness. This page will be updated before materially different "
        "collection begins.</p></section>"
    )
    new = (
        "<section><h2>Optional analytics</h2><p>The production site offers a clear analytics choice. "
        "If you select Allow analytics, it loads HubSpot analytics for page views and virtual funnel "
        "events such as scanner start, scanner completion, evidence download, and audit-interest clicks. "
        "If you decline or make no choice, that third-party analytics script is not loaded. Your choice "
        "is stored in this browser and can be reset by clearing site data.</p></section>"
    )
    if old in content:
        content = content.replace(old, new)
    else:
        content = re.sub(
            r"<section><h2>Analytics</h2>.*?</section>",
            new,
            content,
            count=1,
            flags=re.IGNORECASE | re.DOTALL,
        )
    content = content.replace("Last updated August 23, 2026.", "Last updated August 24, 2026.")
    path.write_text(content, encoding="utf-8")


def resolve_local(current: Path, raw_url: str, root: Path) -> Path | None:
    parsed = urlsplit(raw_url)
    if parsed.scheme or parsed.netloc or raw_url.startswith(("mailto:", "tel:", "data:", "#")):
        return None
    path = unquote(parsed.path)
    if not path:
        target = current
    elif path.startswith("/machinecart/"):
        target = root / path[len("/machinecart/"):]
    elif path.startswith("/"):
        return None
    else:
        target = current.parent / path
    if path.endswith("/") or target.is_dir():
        target /= "index.html"
    try:
        target.resolve().relative_to(root.resolve())
    except ValueError:
        raise ValueError(f"{current.relative_to(root)}: local link escapes MachineCart root: {raw_url}")
    return target.resolve()


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    pages: dict[Path, PublicPageParser] = {}
    for path in sorted(root.rglob("*.html")):
        relative = path.relative_to(root)
        content = path.read_text(encoding="utf-8")
        if not content.lstrip().lower().startswith("<!doctype html>"):
            errors.append(f"{relative}: missing HTML5 doctype")
        if any(old in content for old in LEGACY_BASES):
            errors.append(f"{relative}: contains a legacy public base URL")
        parser = PublicPageParser()
        parser.feed(content)
        pages[path.resolve()] = parser
        if parser.h1_count != 1:
            errors.append(f"{relative}: expected one h1, found {parser.h1_count}")
        if parser.main_count != 1:
            errors.append(f"{relative}: expected one main, found {parser.main_count}")
        if not parser.title:
            errors.append(f"{relative}: missing title")
        expected = canonical_for(relative)
        if parser.canonicals != [expected]:
            errors.append(f"{relative}: canonical {parser.canonicals!r}, expected {[expected]!r}")
        if parser.duplicate_ids:
            errors.append(f"{relative}: duplicate ids: {sorted(parser.duplicate_ids)}")
        for raw_url in parser.anchors + parser.assets:
            try:
                target = resolve_local(path.resolve(), raw_url, root)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            if target is not None and not target.exists():
                errors.append(f"{relative}: broken local reference {raw_url} -> {target.relative_to(root.resolve())}")

    scanner = (root / "scanner.html").read_text(encoding="utf-8")
    for marker in ("analyzeMarkup", "Product", "Offer", "localStorage"):
        if marker not in scanner:
            errors.append(f"scanner.html: missing functional marker {marker}")

    if not pages:
        errors.append("No HTML pages were mounted")
    return errors


def merge_discovery(site_root: Path, machinecart_root: Path) -> None:
    robots = site_root / "robots.txt"
    sitemap = site_root / "sitemap.xml"
    machinecart_sitemap = machinecart_root / "sitemap.xml"
    sitemap_line = f"Sitemap: {PRODUCTION_BASE}sitemap.xml"
    robots_text = robots.read_text(encoding="utf-8")
    if sitemap_line not in robots_text:
        robots.write_text(robots_text.rstrip() + "\n" + sitemap_line + "\n", encoding="utf-8")

    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    root = ET.parse(sitemap).getroot()
    existing = {
        node.text
        for node in root.findall(f"{{{namespace}}}url/{{{namespace}}}loc")
        if node.text
    }
    source_root = ET.parse(machinecart_sitemap).getroot()
    for source_url in source_root.findall(f"{{{namespace}}}url"):
        loc = source_url.find(f"{{{namespace}}}loc")
        if loc is None or not loc.text:
            continue
        value = loc.text
        for old in LEGACY_BASES:
            value = value.replace(old, PRODUCTION_BASE)
        if value in existing:
            continue
        node = ET.SubElement(root, f"{{{namespace}}}url")
        ET.SubElement(node, f"{{{namespace}}}loc").text = value
        existing.add(value)
    ET.ElementTree(root).write(sitemap, encoding="utf-8", xml_declaration=True)


def source_sha(source: Path) -> str:
    repo = source.parent
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="Checked-out autonomous_apps/docs directory")
    parser.add_argument("target", type=Path, help="Production site/machinecart directory")
    args = parser.parse_args()

    source = args.source.resolve()
    target = args.target.resolve()
    site_root = target.parent
    missing = [name for name in REQUIRED_FILES if not (source / name).is_file()]
    if missing:
        raise SystemExit("MachineCart source is incomplete: " + ", ".join(missing))

    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    (target / ".nojekyll").write_text("", encoding="utf-8")

    for path in sorted(target.rglob("*")):
        if path.is_symlink():
            raise SystemExit(f"Symlinks are not allowed in MachineCart public assets: {path}")
        if path.is_file() and path.suffix.lower() in {".html", ".xml", ".json"}:
            text = path.read_text(encoding="utf-8")
            for old in LEGACY_BASES:
                text = text.replace(old, PRODUCTION_BASE)
            path.write_text(text, encoding="utf-8")

    privacy_rewrite(target / "privacy.html")
    (target / "assets" / ANALYTICS_FILENAME).write_text(analytics_javascript(), encoding="utf-8")
    (target / "assets" / "og-card.svg").write_text(og_card_svg(), encoding="utf-8")
    for path in sorted(target.rglob("*.html")):
        rewrite_html(path, target)

    deployment = {
        "schema_version": 1,
        "production_base": PRODUCTION_BASE,
        "source_repository": "pri8771/autonomous_apps",
        "source_commit": source_sha(source),
        "analytics": {
            "provider": "HubSpot",
            "portal_id": HUBSPOT_PORTAL_ID,
            "consent_required": True,
        },
    }
    (target / "deployment.json").write_text(json.dumps(deployment, indent=2) + "\n", encoding="utf-8")
    merge_discovery(site_root, target)

    errors = validate(target)
    if errors:
        print("MachineCart production mount failed validation:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"mounted MachineCart: {len(list(target.rglob('*.html')))} HTML pages "
        f"from source {deployment['source_commit'][:12]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
