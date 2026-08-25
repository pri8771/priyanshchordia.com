#!/usr/bin/env python3
"""Mount and validate the isolated BidetFit public beta."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

PRODUCTION_BASE = "https://priyanshchordia.com/bidetfit/"
REQUIRED_FILES = (
    "index.html", "fit-checker.html", "how-to-measure.html",
    "french-curve-toilets.html", "skirted-toilets.html",
    "round-vs-elongated.html", "electric-vs-non-electric.html",
    "no-outlet-bidet-options.html", "about.html", "disclosure.html",
    "privacy.html", "status.json", "robots.txt", "sitemap.xml",
    "assets/site.css", "assets/fit-checker.js", "assets/og.svg",
)


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h1 = 0
        self.main = 0
        self.title = 0
        self.canonical: list[str] = []
        self.links: list[str] = []
        self.assets: list[str] = []
        self.ids: list[str] = []
        self.json_ld: list[str] = []
        self._json: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "h1": self.h1 += 1
        if tag == "main": self.main += 1
        if tag == "title": self.title += 1
        if values.get("id"): self.ids.append(values["id"])
        if tag == "a" and values.get("href"): self.links.append(values["href"])
        if tag == "script" and values.get("src"): self.assets.append(values["src"])
        if tag == "link" and values.get("href"):
            rel = set(values.get("rel", "").lower().split())
            if "canonical" in rel: self.canonical.append(values["href"])
            elif "stylesheet" in rel or "icon" in rel: self.assets.append(values["href"])
        if tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self._json = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._json is not None:
            self.json_ld.append("".join(self._json))
            self._json = None

    def handle_data(self, data: str) -> None:
        if self._json is not None: self._json.append(data)


def canonical(relative: Path) -> str:
    if relative.as_posix() == "index.html": return PRODUCTION_BASE
    return PRODUCTION_BASE + relative.as_posix()


def local_target(current: Path, raw: str, root: Path) -> Path | None:
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc or raw.startswith(("mailto:", "tel:", "data:", "#")):
        return None
    path = unquote(parsed.path)
    if path.startswith("/bidetfit/"):
        target = root / path[len("/bidetfit/"):]
    elif path.startswith("/"):
        return None
    elif not path:
        target = current
    else:
        target = current.parent / path
    if path.endswith("/") or target.is_dir(): target /= "index.html"
    resolved = target.resolve()
    try: resolved.relative_to(root.resolve())
    except ValueError as exc: raise ValueError(f"link escapes BidetFit root: {raw}") from exc
    return resolved


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_FILES:
        if not (root / name).is_file(): errors.append(f"missing required file: {name}")
    pages: dict[Path, Parser] = {}
    for page in sorted(root.rglob("*.html")):
        rel = page.relative_to(root)
        text = page.read_text(encoding="utf-8")
        parser = Parser(); parser.feed(text); pages[page.resolve()] = parser
        if not text.lstrip().lower().startswith("<!doctype html>"): errors.append(f"{rel}: missing doctype")
        if parser.h1 != 1: errors.append(f"{rel}: expected one h1, found {parser.h1}")
        if parser.main != 1: errors.append(f"{rel}: expected one main, found {parser.main}")
        if parser.title != 1: errors.append(f"{rel}: expected one title, found {parser.title}")
        expected = canonical(rel)
        if parser.canonical != [expected]: errors.append(f"{rel}: canonical {parser.canonical!r}, expected {[expected]!r}")
        duplicates = [value for value, count in Counter(parser.ids).items() if count > 1]
        if duplicates: errors.append(f"{rel}: duplicate ids {duplicates}")
        for payload in parser.json_ld:
            try: json.loads(payload)
            except json.JSONDecodeError as exc: errors.append(f"{rel}: invalid JSON-LD: {exc}")
        if "246481057" in text or "js.hs-scripts.com" in text: errors.append(f"{rel}: contains excluded Primandir reference")
        if "data-affiliate=\"active\"" in text: errors.append(f"{rel}: active affiliate marker before approval")
        for raw in parser.links + parser.assets:
            try: target = local_target(page.resolve(), raw, root)
            except ValueError as exc: errors.append(f"{rel}: {exc}"); continue
            if target is not None and not target.exists(): errors.append(f"{rel}: broken local reference {raw}")
    status_path = root / "status.json"
    if status_path.exists():
        try: status = json.loads(status_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc: errors.append(f"status.json invalid: {exc}")
        else:
            if status.get("brand") != "BidetFit": errors.append("status.json brand mismatch")
            if status.get("active_affiliate_links") != 0: errors.append("launch status unexpectedly reports active affiliate links")
    sitemap_path = root / "sitemap.xml"
    if sitemap_path.exists():
        try: xml_root = ET.parse(sitemap_path).getroot()
        except ET.ParseError as exc: errors.append(f"sitemap.xml invalid: {exc}")
        else:
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            urls = {node.text for node in xml_root.findall("sm:url/sm:loc", ns) if node.text}
            expected_urls = {canonical(path.relative_to(root)) for path in pages}
            if urls != expected_urls:
                errors.append(f"sitemap mismatch; missing={sorted(expected_urls-urls)}, extra={sorted(urls-expected_urls)}")
    return errors


def merge_discovery(site_root: Path, bidetfit_root: Path) -> None:
    robots = site_root / "robots.txt"
    text = robots.read_text(encoding="utf-8") if robots.exists() else "User-agent: *\nAllow: /\n"
    lines = [line for line in text.splitlines() if "/bidetfit/sitemap.xml" not in line]
    lines.append(f"Sitemap: {PRODUCTION_BASE}sitemap.xml")
    robots.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    sitemap = site_root / "sitemap.xml"
    if not sitemap.is_file(): raise ValueError("portfolio sitemap is missing")
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    tree = ET.parse(sitemap); root = tree.getroot()
    for node in list(root.findall(f"{{{namespace}}}url")):
        loc = node.find(f"{{{namespace}}}loc")
        if loc is not None and loc.text and "/bidetfit/" in loc.text: root.remove(node)
    existing = {node.text for node in root.findall(f"{{{namespace}}}url/{{{namespace}}}loc") if node.text}
    source = ET.parse(bidetfit_root / "sitemap.xml").getroot()
    for source_node in source.findall(f"{{{namespace}}}url"):
        loc = source_node.find(f"{{{namespace}}}loc")
        if loc is None or not loc.text or loc.text in existing: continue
        clone = ET.SubElement(root, f"{{{namespace}}}url")
        ET.SubElement(clone, f"{{{namespace}}}loc").text = loc.text
        lastmod = source_node.find(f"{{{namespace}}}lastmod")
        if lastmod is not None and lastmod.text: ET.SubElement(clone, f"{{{namespace}}}lastmod").text = lastmod.text
        existing.add(loc.text)
    tree.write(sitemap, encoding="utf-8", xml_declaration=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    source = args.source.resolve(); target = args.target.resolve()
    if not source.is_dir(): print(f"source missing: {source}", file=sys.stderr); return 1
    if target.exists(): shutil.rmtree(target)
    shutil.copytree(source, target)
    errors = validate(target)
    if errors:
        print("BidetFit validation failed:", file=sys.stderr)
        for error in errors: print(f"  - {error}", file=sys.stderr)
        return 1
    merge_discovery(target.parent, target)
    print(f"BidetFit mounted and validated: {len(list(target.rglob('*.html')))} HTML pages")
    return 0


if __name__ == "__main__": raise SystemExit(main())
