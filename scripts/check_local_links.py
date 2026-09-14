#!/usr/bin/env python3
"""
stdlib-only checker for local href/src links inside generated HTML.

Usage:
    python3 scripts/check_local_links.py [site-root]

Exits 0 when all local links and fragments resolve, non-zero otherwise.

Importable API (for tests):
    check_links(site_root: Path) -> list[str]   # list of error strings
"""

from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

# ---------------------------------------------------------------------------
# HTML parser – extracts refs and ids from a single file
# ---------------------------------------------------------------------------

# Tags whose href/src attributes carry local resource references.
_REF_TAGS: dict[str, str] = {
    # tag -> attribute
    "a": "href",
    "area": "href",
    "img": "src",
    "script": "src",
    "audio": "src",
    "video": "src",
    "source": "src",
    "track": "src",
    "embed": "src",
    "iframe": "src",
}

# <link> elements whose rel values carry local resource references.
_LINK_RELS_WITH_REFS = {"stylesheet", "icon", "shortcut icon", "apple-touch-icon", "manifest"}

# Schemes that must never be fetched / checked for file existence.
_SKIP_SCHEMES = {"http", "https", "mailto", "tel", "data", "ftp", "javascript", "blob"}


class _LinkParser(HTMLParser):
    """Collect (raw_url, has_fragment) refs and element ids from one HTML file."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        # list of raw URL strings found in href/src attributes
        self.refs: list[str] = []
        # set of id attribute values found anywhere in the document
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {k: (v or "") for k, v in attrs}

        # Collect id attributes from any element
        if "id" in values and values["id"]:
            self.ids.add(values["id"])

        # Collect resource refs
        if tag in _REF_TAGS:
            attr = _REF_TAGS[tag]
            if attr in values and values[attr]:
                self.refs.append(values[attr])
        elif tag == "link":
            rel_parts = set(values.get("rel", "").lower().split())
            if rel_parts & _LINK_RELS_WITH_REFS and values.get("href"):
                self.refs.append(values["href"])

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        # Self-closing variant (XHTML / void elements) — same handling
        self.handle_starttag(tag, attrs)


# ---------------------------------------------------------------------------
# URL resolution helpers
# ---------------------------------------------------------------------------

def _resolve_target(current_file: Path, raw_url: str, site_root: Path) -> tuple[Path | None, str | None]:
    """
    Resolve a raw URL string against the current file and site root.

    Returns:
        (resolved_path, fragment)
          resolved_path is None  → skip this URL (external or skip-scheme)
          resolved_path is a Path → check this file for existence
        fragment is the # fragment value, or None if absent.
    """
    parsed = urlsplit(raw_url)

    # Always skip if scheme is a non-file scheme we must ignore
    if parsed.scheme and parsed.scheme in _SKIP_SCHEMES:
        return None, None

    # Any other explicit scheme (e.g. ftp, custom) that is not empty → skip
    if parsed.scheme and parsed.scheme not in ("", "file"):
        return None, None

    # netloc present without a recognised file scheme → external, skip
    if parsed.netloc:
        return None, None

    fragment = parsed.fragment if parsed.fragment else None
    path_part = unquote(parsed.path)  # decode %20 etc.

    if not path_part:
        # Same-page fragment-only link (e.g. href="#section")
        resolved = current_file
    elif path_part.startswith("/"):
        # Root-absolute path: resolve against site_root
        resolved = site_root / path_part.lstrip("/")
    else:
        # Relative path: resolve against the directory of the current file
        resolved = current_file.parent / path_part

    # Resolve directory indexes: a trailing slash or a directory → index.html
    if path_part.endswith("/"):
        resolved = resolved / "index.html"
    elif resolved.is_dir():
        resolved = resolved / "index.html"
    elif not resolved.suffix:
        # Extensionless paths also get index.html treatment
        resolved = resolved / "index.html"

    # Normalise without following symlinks that escape the root
    try:
        resolved = resolved.resolve()
    except OSError:
        pass

    # Guard: make sure we haven't escaped outside the site root
    try:
        resolved.relative_to(site_root.resolve())
    except ValueError:
        # Path escapes the site root – treat as an error-worthy outside link
        return Path("__outside_site__"), fragment

    return resolved, fragment


# ---------------------------------------------------------------------------
# Page database
# ---------------------------------------------------------------------------

def _parse_file(path: Path) -> _LinkParser:
    """Parse a single HTML file and return its LinkParser."""
    parser = _LinkParser()
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return parser
    parser.feed(text)
    parser.close()
    return parser


def _build_page_db(site_root: Path) -> dict[Path, _LinkParser]:
    """Walk all HTML files under site_root and return a map of resolved path → parser."""
    db: dict[Path, _LinkParser] = {}
    for html_file in sorted(site_root.rglob("*.html")):
        resolved = html_file.resolve()
        db[resolved] = _parse_file(html_file)
    return db


# ---------------------------------------------------------------------------
# Core checker
# ---------------------------------------------------------------------------

def check_links(site_root: Path) -> list[str]:
    """
    Check all local href/src links and fragments under site_root.

    Returns a list of human-readable error strings.
    An empty list means everything is fine.
    """
    site_root = site_root.resolve()
    if not site_root.is_dir():
        return [f"site root does not exist or is not a directory: {site_root}"]

    errors: list[str] = []
    page_db = _build_page_db(site_root)

    for source_abs, parser in page_db.items():
        try:
            source_rel = source_abs.relative_to(site_root)
        except ValueError:
            source_rel = source_abs  # fallback

        for raw_url in parser.refs:
            target_path, fragment = _resolve_target(source_abs, raw_url, site_root)

            if target_path is None:
                # External / skip-scheme – intentionally ignored
                continue

            if target_path == Path("__outside_site__"):
                errors.append(
                    f"{source_rel}: link escapes site root: {raw_url!r}"
                )
                continue

            # Check that the target file exists
            if not target_path.exists():
                errors.append(
                    f"{source_rel}: broken link → {raw_url!r} "
                    f"(resolved: {target_path.relative_to(site_root) if target_path.is_relative_to(site_root) else target_path})"
                )
                continue

            # Fragment check (only for HTML targets)
            if fragment and target_path.suffix.lower() == ".html":
                # Look up ids in the target page
                if target_path in page_db:
                    target_ids = page_db[target_path].ids
                else:
                    # Parse on demand (e.g. target is outside the initial walk somehow)
                    target_ids = _parse_file(target_path).ids

                if fragment not in target_ids:
                    errors.append(
                        f"{source_rel}: broken fragment #{fragment} "
                        f"in {raw_url!r} (target: {target_path.relative_to(site_root)})"
                    )

    return errors


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _default_site_root() -> Path:
    """Return the conventional 'site' directory relative to this script."""
    return Path(__file__).resolve().parents[1] / "site"


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    site_root = Path(args[0]) if args else _default_site_root()

    errors = check_links(site_root)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        print(f"\n{len(errors)} broken link(s) found.", file=sys.stderr)
        return 1

    print(f"All local links OK ({site_root})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
