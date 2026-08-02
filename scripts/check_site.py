#!/usr/bin/env python3
"""Dependency-free structural checks for the generated public site."""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter, deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PUBLIC_HOSTS = {"priyanshchordia.com", "www.priyanshchordia.com"}
BASE_URL = "https://priyanshchordia.com"
VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}
REQUIRED_APP_SLUGS = {"mala", "anjali", "svara", "roam"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[str] = []
        self.asset_refs: list[str] = []
        self.canonicals: list[str] = []
        self.ids: list[str] = []
        self.h1_count = 0
        self.main_count = 0
        self.title_count = 0
        self.meta_names: set[str] = set()
        self.meta_name_values: dict[str, str] = {}
        self.meta_properties: set[str] = set()
        self.json_ld: list[str] = []
        self.stack: list[str] = []
        self.structure_errors: list[str] = []
        self._json_parts: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag not in VOID_ELEMENTS:
            self.stack.append(tag)
        if tag == "a" and values.get("href"):
            self.anchors.append(values["href"])
        if tag == "script" and values.get("src"):
            self.asset_refs.append(values["src"])
        if tag == "link" and values.get("href"):
            rel = set(values.get("rel", "").lower().split())
            if "canonical" in rel:
                self.canonicals.append(values["href"])
            elif "stylesheet" in rel or "icon" in rel:
                self.asset_refs.append(values["href"])
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "h1":
            self.h1_count += 1
        if tag == "main":
            self.main_count += 1
        if tag == "title":
            self.title_count += 1
        if tag == "meta":
            if values.get("name"):
                name = values["name"].lower()
                self.meta_names.add(name)
                self.meta_name_values[name] = values.get("content", "")
            if values.get("property"):
                self.meta_properties.add(values["property"].lower())
        if tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self._json_parts = []

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_ELEMENTS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_ELEMENTS:
            return
        if not self.stack:
            self.structure_errors.append(f"unexpected closing </{tag}>")
        elif self.stack[-1] != tag:
            self.structure_errors.append(
                f"closing </{tag}> encountered while <{self.stack[-1]}> was open"
            )
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.stack.pop()
                if self.stack:
                    self.stack.pop()
        else:
            self.stack.pop()
        if tag == "script" and self._json_parts is not None:
            self.json_ld.append("".join(self._json_parts))
            self._json_parts = None

    def handle_data(self, data: str) -> None:
        if self._json_parts is not None:
            self._json_parts.append(data)


def local_target(current: Path, raw_url: str) -> Path | None:
    parsed = urlsplit(raw_url)
    if parsed.scheme:
        if parsed.scheme not in {"http", "https"} or parsed.hostname not in PUBLIC_HOSTS:
            return None
    elif parsed.netloc:
        return None
    path = unquote(parsed.path)
    if not path:
        target = current
    elif path.startswith("/"):
        target = SITE / path.lstrip("/")
    else:
        target = current.parent / path
    if path.endswith("/") or target.is_dir():
        target /= "index.html"
    elif not target.suffix:
        target /= "index.html"
    try:
        resolved = target.resolve()
        resolved.relative_to(SITE.resolve())
        return resolved
    except ValueError:
        return Path("__outside_site__")


def parse_pages() -> tuple[dict[Path, PageParser], list[str]]:
    errors: list[str] = []
    parsed: dict[Path, PageParser] = {}
    for path in sorted(SITE.rglob("*.html")):
        raw = path.read_text(encoding="utf-8")
        rel = path.relative_to(SITE)
        if not raw.lstrip().lower().startswith("<!doctype html>"):
            errors.append(f"{rel}: missing HTML5 doctype")
        parser = PageParser()
        parser.feed(raw)
        parser.close()
        parsed[path.resolve()] = parser
        if parser.stack:
            errors.append(f"{rel}: unclosed elements: {', '.join(parser.stack)}")
        errors.extend(f"{rel}: {message}" for message in parser.structure_errors)
        if parser.h1_count != 1:
            errors.append(f"{rel}: expected one h1, found {parser.h1_count}")
        if parser.main_count != 1:
            errors.append(f"{rel}: expected one main, found {parser.main_count}")
        if parser.title_count != 1:
            errors.append(f"{rel}: expected one title, found {parser.title_count}")
        for required in (
            "description", "robots", "viewport", "twitter:card",
            "twitter:image", "twitter:image:alt",
        ):
            if required not in parser.meta_names:
                errors.append(f"{rel}: missing meta name={required}")
        for required in (
            "og:type", "og:title", "og:description", "og:url", "og:image",
            "og:image:width", "og:image:height", "og:image:alt",
        ):
            if required not in parser.meta_properties:
                errors.append(f"{rel}: missing meta property={required}")
        if len(parser.canonicals) != 1:
            errors.append(f"{rel}: expected one canonical URL, found {len(parser.canonicals)}")
        else:
            expected_path = "/" if rel == Path("index.html") else "/" + rel.as_posix()
            if rel.name == "index.html" and rel.parent != Path("."):
                expected_path = "/" + rel.parent.as_posix() + "/"
            expected_canonical = BASE_URL + expected_path
            if parser.canonicals[0] != expected_canonical:
                errors.append(
                    f"{rel}: canonical is {parser.canonicals[0]!r}, expected {expected_canonical!r}"
                )
        duplicates = [value for value, count in Counter(parser.ids).items() if count > 1]
        if duplicates:
            errors.append(f"{rel}: duplicate ids: {', '.join(sorted(duplicates))}")
        for payload in parser.json_ld:
            try:
                json.loads(payload)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}: invalid JSON-LD: {exc}")
    return parsed, errors


def validate_links(pages: dict[Path, PageParser]) -> list[str]:
    errors: list[str] = []
    graph: dict[Path, set[Path]] = {path: set() for path in pages}
    for path, parser in pages.items():
        for raw_url in parser.anchors + parser.asset_refs + parser.canonicals:
            target = local_target(path, raw_url)
            if target is None:
                continue
            rel = path.relative_to(SITE.resolve())
            if target.name == "__outside_site__":
                errors.append(f"{rel}: link escapes site root: {raw_url}")
                continue
            if not target.exists():
                errors.append(f"{rel}: broken local reference {raw_url} -> {target.relative_to(SITE)}")
                continue
            fragment = unquote(urlsplit(raw_url).fragment)
            if fragment and target in pages and fragment not in pages[target].ids:
                errors.append(f"{rel}: missing fragment target {raw_url}")
            if raw_url in parser.anchors and target in pages:
                graph[path].add(target)

    start = (SITE / "index.html").resolve()
    reachable: set[Path] = set()
    queue: deque[Path] = deque([start])
    while queue:
        page = queue.popleft()
        if page in reachable:
            continue
        reachable.add(page)
        queue.extend(graph.get(page, set()) - reachable)
    ignored = {(SITE / "404.html").resolve()}
    for path in sorted(set(pages) - reachable - ignored):
        errors.append(f"{path.relative_to(SITE.resolve())}: HTML page is orphaned")
    return errors


def validate_routes_and_discovery(pages: dict[Path, PageParser]) -> list[str]:
    errors: list[str] = []
    for slug in sorted(REQUIRED_APP_SLUGS):
        for kind in ("privacy", "support"):
            path = (SITE / "apps" / slug / kind / "index.html").resolve()
            if path not in pages:
                errors.append(f"missing required route: /apps/{slug}/{kind}/")

    robots = SITE / "robots.txt"
    sitemap = SITE / "sitemap.xml"
    not_found = SITE / "404.html"
    for path in (robots, sitemap, not_found):
        if not path.exists():
            errors.append(f"missing discovery file: {path.name}")
    if errors:
        return errors
    if "Sitemap: https://priyanshchordia.com/sitemap.xml" not in robots.read_text(encoding="utf-8"):
        errors.append("robots.txt does not advertise the production sitemap")

    try:
        root = ET.parse(sitemap).getroot()
        sitemap_urls = {
            node.text for node in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/"
                                               "{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            if node.text
        }
    except ET.ParseError as exc:
        return errors + [f"sitemap.xml is invalid XML: {exc}"]
    canonical_urls = {
        parser.canonicals[0]
        for path, parser in pages.items()
        if path != not_found.resolve()
        and len(parser.canonicals) == 1
        and "noindex" not in parser.meta_name_values.get("robots", "").lower()
    }
    missing = canonical_urls - sitemap_urls
    extra = sitemap_urls - canonical_urls
    if missing:
        errors.append("sitemap missing canonical URLs: " + ", ".join(sorted(missing)))
    if extra:
        errors.append("sitemap contains unknown URLs: " + ", ".join(sorted(extra)))
    return errors


def main() -> int:
    if not SITE.exists():
        print("site/ does not exist; run scripts/generate_site.py first", file=sys.stderr)
        return 1
    pages, errors = parse_pages()
    errors.extend(validate_links(pages))
    errors.extend(validate_routes_and_discovery(pages))
    if errors:
        print("site validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"site validation passed: {len(pages)} HTML pages, all local routes reachable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
