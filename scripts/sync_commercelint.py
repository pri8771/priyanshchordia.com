#!/usr/bin/env python3
"""Mount CommerceLint into the public portfolio build and validate the release.

The autonomous_apps repository remains the durable source of truth. This script
copies its public ``docs`` tree into ``site/commercelint``, rewrites canonical
URLs, creates legacy redirects, merges discovery files, and fails closed when a
public invariant is broken.
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

PRODUCTION_BASE = "https://priyanshchordia.com/commercelint/"
LEGACY_PRODUCTION_BASE = "https://priyanshchordia.com/machinecart/"
SOURCE_BASES = (
    "https://pri8771.github.io/autonomous_apps/",
    "https://raw.githack.com/pri8771/autonomous_apps/main/docs/",
)
OLD_BASES = (LEGACY_PRODUCTION_BASE, *SOURCE_BASES)
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
    "assets/analytics.js",
    "guides/index.html",
    "sitemap.xml",
)
TEXT_SUFFIXES = {".html", ".xml", ".json", ".md", ".txt", ".csv", ".js", ".css"}
ANALYTICS_FILENAME = "analytics.js"
INDEXNOW_KEY = "1d88808c1ec138f77fe50484f83e6de7"


class PublicPageParser(HTMLParser):
    """Collect public-page invariants and local references."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h1_count = 0
        self.main_count = 0
        self.in_title = False
        self.title_parts: list[str] = []
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


def replace_or_insert_canonical(content: str, canonical: str) -> str:
    tag = f'<link rel="canonical" href="{html.escape(canonical, quote=True)}">'
    pattern = re.compile(
        r'<link\b[^>]*\brel=["\'][^"\']*\bcanonical\b[^"\']*["\'][^>]*>',
        re.IGNORECASE,
    )
    if pattern.search(content):
        return pattern.sub(tag, content, count=1)
    if "</head>" not in content:
        raise ValueError("HTML document has no closing head tag")
    return content.replace("</head>", f"  {tag}\n</head>", 1)


def rewrite_public_tree(target: Path) -> None:
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
        path.write_text(text, encoding="utf-8")


def og_card_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-labelledby="title desc">
<title id="title">CommerceLint</title><desc id="desc">Product-page linting for ecommerce teams</desc>
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#07111f"/><stop offset="1" stop-color="#172554"/></linearGradient></defs>
<rect width="1200" height="630" rx="36" fill="url(#g)"/>
<circle cx="1030" cy="100" r="210" fill="#38bdf8" opacity=".16"/>
<circle cx="1040" cy="560" r="280" fill="#8b5cf6" opacity=".16"/>
<text x="92" y="215" font-family="system-ui, sans-serif" font-size="42" font-weight="700" fill="#7dd3fc">COMMERCELINT</text>
<text x="92" y="330" font-family="system-ui, sans-serif" font-size="70" font-weight="760" fill="#f8fafc">Turn product-page defects</text>
<text x="92" y="415" font-family="system-ui, sans-serif" font-size="70" font-weight="760" fill="#f8fafc">into repair tickets.</text>
<text x="92" y="515" font-family="system-ui, sans-serif" font-size="32" fill="#cbd5e1">Evidence, repair guidance, acceptance checks, and JSON output.</text>
</svg>
"""


def redirect_document(destination: str) -> str:
    safe = html.escape(destination, quote=True)
    script_value = json.dumps(destination)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CommerceLint moved</title><link rel="canonical" href="{safe}"><meta http-equiv="refresh" content="0;url={safe}">
<script>location.replace({script_value});</script></head><body><main><h1>CommerceLint moved</h1><p><a href="{safe}">Continue to CommerceLint</a>.</p></main></body></html>
"""


def create_legacy_redirects(site_root: Path, target: Path) -> None:
    legacy = site_root / "machinecart"
    if legacy.exists():
        shutil.rmtree(legacy)
    for page in sorted(target.rglob("*.html")):
        relative = page.relative_to(target)
        output = legacy / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(redirect_document(canonical_for(relative)), encoding="utf-8")


def inject_portfolio_promotion(site_root: Path) -> None:
    homepage = site_root / "index.html"
    content = homepage.read_text(encoding="utf-8")
    if 'id="commercelint-live"' in content:
        return
    journal_marker = '<section id="journal">'
    if content.count(journal_marker) != 1:
        raise ValueError("Portfolio journal insertion point is missing or ambiguous")
    promotion = """<section id="commercelint-live" data-commercelint-promotion="2026-08-24">
<div class="section-head"><span class="label">02 / Live experiment</span><h2>Machine-readable commerce.</h2></div>
<div class="products"><a class="product" href="commercelint/?utm_source=portfolio&amp;utm_medium=internal&amp;utm_campaign=commercelint_launch">
<span class="num">LIVE</span><h3>CommerceLint</h3>
<p>Turn ecommerce product-page data defects into evidence-backed repair tickets.</p>
<span class="meta">web commerce / free linter</span></a></div>
</section>
"""
    content = content.replace(journal_marker, promotion + journal_marker, 1)
    content = content.replace('<span class="label">02 / Journal</span>', '<span class="label">03 / Journal</span>', 1)
    nav_marker = '<a href="journal/">Journal</a>'
    nav_link = '<a href="commercelint/?utm_source=portfolio_nav&amp;utm_medium=internal&amp;utm_campaign=commercelint_launch">CommerceLint</a>'
    if content.count(nav_marker) != 1:
        raise ValueError("Portfolio journal navigation insertion point is missing or ambiguous")
    content = content.replace(nav_marker, nav_link + nav_marker, 1)
    homepage.write_text(content, encoding="utf-8")


def merge_discovery(site_root: Path, target: Path) -> None:
    robots = site_root / "robots.txt"
    robots_text = robots.read_text(encoding="utf-8") if robots.exists() else "User-agent: *\nAllow: /\n"
    lines = [line for line in robots_text.splitlines() if "/machinecart/sitemap.xml" not in line and "/commercelint/sitemap.xml" not in line]
    lines.append(f"Sitemap: {PRODUCTION_BASE}sitemap.xml")
    robots.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    sitemap = site_root / "sitemap.xml"
    if not sitemap.exists():
        raise ValueError("Generated portfolio sitemap is missing")
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    tree = ET.parse(sitemap)
    root = tree.getroot()
    for url_node in list(root.findall(f"{{{namespace}}}url")):
        loc = url_node.find(f"{{{namespace}}}loc")
        if loc is not None and loc.text and ("/machinecart/" in loc.text or "/commercelint/" in loc.text):
            root.remove(url_node)
    existing = {
        node.text
        for node in root.findall(f"{{{namespace}}}url/{{{namespace}}}loc")
        if node.text
    }
    source_root = ET.parse(target / "sitemap.xml").getroot()
    for source_url in source_root.findall(f"{{{namespace}}}url"):
        loc = source_url.find(f"{{{namespace}}}loc")
        if loc is None or not loc.text or loc.text in existing:
            continue
        clone = ET.SubElement(root, f"{{{namespace}}}url")
        ET.SubElement(clone, f"{{{namespace}}}loc").text = loc.text
        existing.add(loc.text)
    tree.write(sitemap, encoding="utf-8", xml_declaration=True)


def resolve_local(current: Path, raw_url: str, root: Path) -> Path | None:
    parsed = urlsplit(raw_url)
    if parsed.scheme or parsed.netloc or raw_url.startswith(("mailto:", "tel:", "data:", "#")):
        return None
    path = unquote(parsed.path)
    if not path:
        target = current
    elif path.startswith("/commercelint/"):
        target = root / path[len("/commercelint/"):]
    elif path.startswith("/"):
        return None
    else:
        target = current.parent / path
    if path.endswith("/") or target.is_dir():
        target /= "index.html"
    try:
        target.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"local link escapes CommerceLint root: {raw_url}") from exc
    return target.resolve()


def validate(target: Path) -> list[str]:
    errors: list[str] = []
    missing = [name for name in REQUIRED_FILES if not (target / name).is_file()]
    if missing:
        errors.append("Missing required files: " + ", ".join(missing))
    for path in sorted(target.rglob("*.html")):
        relative = path.relative_to(target)
        content = path.read_text(encoding="utf-8")
        parser = PublicPageParser()
        parser.feed(content)
        if not content.lstrip().lower().startswith("<!doctype html>"):
            errors.append(f"{relative}: missing HTML5 doctype")
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
            errors.append(f"{relative}: duplicate ids {sorted(parser.duplicate_ids)}")
        if "MachineCart" in content or LEGACY_PRODUCTION_BASE in content:
            errors.append(f"{relative}: contains the retired brand or production path")
        if "246481057" in content or "js.hs-scripts.com" in content:
            errors.append(f"{relative}: contains an excluded Primandir analytics reference")
        for raw_url in parser.anchors + parser.assets:
            try:
                local = resolve_local(path.resolve(), raw_url, target)
            except ValueError as exc:
                errors.append(f"{relative}: {exc}")
                continue
            if local is not None and not local.exists():
                errors.append(f"{relative}: broken local reference {raw_url}")

    scanner = (target / "scanner.html").read_text(encoding="utf-8") if (target / "scanner.html").exists() else ""
    for marker in ("analyzeMarkup", "Product", "Offer"):
        if marker not in scanner:
            errors.append(f"scanner.html: missing functional marker {marker}")
    privacy = (target / "privacy.html").read_text(encoding="utf-8") if (target / "privacy.html").exists() else ""
    privacy_lower = privacy.lower()
    for marker in (
        "google analytics 4",
        "only after you select",
        "does <strong>not</strong> send pasted html",
        "global privacy control",
    ):
        if marker not in privacy_lower:
            errors.append(f"privacy.html: missing consent disclosure marker {marker!r}")

    analytics_path = target / "assets" / ANALYTICS_FILENAME
    analytics = analytics_path.read_text(encoding="utf-8") if analytics_path.exists() else ""
    for marker in (
        "G-MC3PB0Q7EX",
        "commercelint:analyticsConsent:v1",
        "window.commerceLintTrack = track",
        "send_page_view: false",
        'readConsent() !== "granted"',
    ):
        if marker not in analytics:
            errors.append(f"analytics.js: missing consent marker {marker!r}")
    for forbidden in ("storeUrl", "pageTitle", "246481057", "js.hs-scripts.com"):
        if forbidden in analytics:
            errors.append(f"analytics.js: prohibited marker {forbidden!r}")

    loader_pattern = re.compile(r'<script\b[^>]*src=["\'][^"\']*assets/analytics\.js["\']', re.I)
    for page in sorted(target.rglob("*.html")):
        page_text = page.read_text(encoding="utf-8")
        loader_count = len(loader_pattern.findall(page_text))
        if loader_count != 1:
            errors.append(
                f"{page.relative_to(target)}: expected one local analytics loader, found {loader_count}"
            )
        if "googletagmanager.com/gtag/js" in page_text:
            errors.append(f"{page.relative_to(target)}: Google tag is loaded directly before consent")
    return errors


def source_sha(source: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(source.parent), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="Checked-out autonomous_apps/docs directory")
    parser.add_argument("target", type=Path, help="Production site/commercelint directory")
    args = parser.parse_args()

    source = args.source.resolve()
    target = args.target.resolve()
    site_root = target.parent
    source_missing = [name for name in REQUIRED_FILES if not (source / name).is_file()]
    if source_missing:
        raise SystemExit("CommerceLint source is incomplete: " + ", ".join(source_missing))
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    (target / ".nojekyll").write_text("", encoding="utf-8")

    rewrite_public_tree(target)
    assets = target / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "og-card.svg").write_text(og_card_svg(), encoding="utf-8")
    deployment = {
        "schema_version": 1,
        "brand": "CommerceLint",
        "production_base": PRODUCTION_BASE,
        "source_repository": "pri8771/autonomous_apps",
        "source_commit": source_sha(source),
        "analytics": {
            "provider": "Google Analytics 4",
            "measurement_id": "G-MC3PB0Q7EX",
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
        },
    }
    (target / "deployment.json").write_text(json.dumps(deployment, indent=2) + "\n", encoding="utf-8")

    create_legacy_redirects(site_root, target)
    merge_discovery(site_root, target)
    inject_portfolio_promotion(site_root)

    errors = validate(target)
    if errors:
        print("CommerceLint production mount failed validation:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"mounted CommerceLint: {len(list(target.rglob('*.html')))} HTML pages "
        f"from source {deployment['source_commit'][:12]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
