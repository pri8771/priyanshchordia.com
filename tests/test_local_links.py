#!/usr/bin/env python3
"""
Tests for scripts/check_local_links.py

Run with:
    python3 -m unittest tests/test_local_links.py -v

All tests use tempfile-based fixtures; no network access; no external deps.
"""

import sys
import tempfile
import unittest
from pathlib import Path

# Allow import from scripts/ whether running from repo root or tests/ dir.
_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from check_local_links import check_links  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(directory: Path, rel_path: str, content: str) -> Path:
    """Write content to directory/rel_path, creating parent dirs as needed."""
    target = directory / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def _html(body: str = "", extra_head: str = "") -> str:
    """Minimal valid HTML scaffold."""
    return (
        "<!doctype html><html><head>"
        f"{extra_head}"
        "</head><body>"
        f"{body}"
        "</body></html>"
    )


# ---------------------------------------------------------------------------
# 1. Valid local links and fragments pass
# ---------------------------------------------------------------------------

class TestValidLinks(unittest.TestCase):

    def test_valid_internal_page_link(self) -> None:
        """An <a href> pointing to an existing HTML file produces no errors."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html('<a href="/about/index.html">About</a>'))
            _write(root, "about/index.html", _html("About page"))
            errors = check_links(root)
            self.assertEqual(errors, [], errors)

    def test_valid_relative_link(self) -> None:
        """Relative hrefs like '../index.html' resolve correctly."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html("Home"))
            _write(root, "about/index.html", _html('<a href="../index.html">Home</a>'))
            errors = check_links(root)
            self.assertEqual(errors, [], errors)

    def test_valid_fragment_same_page(self) -> None:
        """A same-page fragment (#id) that exists in the page passes."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html(
                '<a href="#section1">Go</a><section id="section1">Content</section>'
            ))
            errors = check_links(root)
            self.assertEqual(errors, [], errors)

    def test_valid_cross_page_fragment(self) -> None:
        """A cross-page fragment href="/about/#intro" passes when id exists."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html('<a href="/about/index.html#intro">About</a>'))
            _write(root, "about/index.html", _html('<h2 id="intro">Intro</h2>'))
            errors = check_links(root)
            self.assertEqual(errors, [], errors)

    def test_valid_img_src(self) -> None:
        """An <img src> pointing to an existing file passes."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "logo.png").write_bytes(b"\x89PNG")
            _write(root, "index.html", _html('<img src="/logo.png" alt="logo">'))
            errors = check_links(root)
            self.assertEqual(errors, [], errors)

    def test_valid_stylesheet_link(self) -> None:
        """A <link rel=stylesheet href=...> pointing to an existing CSS passes."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "styles.css", "body{}")
            _write(root, "index.html", _html(
                extra_head='<link rel="stylesheet" href="/styles.css">'
            ))
            errors = check_links(root)
            self.assertEqual(errors, [], errors)

    def test_valid_script_src(self) -> None:
        """A <script src=...> pointing to an existing JS file passes."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "app.js", "console.log(1)")
            _write(root, "index.html", _html(
                '<script src="/app.js"></script>'
            ))
            errors = check_links(root)
            self.assertEqual(errors, [], errors)

    def test_no_html_files(self) -> None:
        """An empty site root with no HTML files produces no errors."""
        with tempfile.TemporaryDirectory() as tmp:
            errors = check_links(Path(tmp))
            self.assertEqual(errors, [], errors)


# ---------------------------------------------------------------------------
# 2. Missing local files fail with source + target reported
# ---------------------------------------------------------------------------

class TestMissingFiles(unittest.TestCase):

    def test_missing_href_file(self) -> None:
        """A broken <a href> reports the source file and missing target."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html('<a href="/missing.html">Gone</a>'))
            errors = check_links(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("index.html", errors[0])
            self.assertIn("missing.html", errors[0])

    def test_missing_img_src(self) -> None:
        """A broken <img src> reports source file and missing asset."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html('<img src="/ghost.png" alt="x">'))
            errors = check_links(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("index.html", errors[0])
            self.assertIn("ghost.png", errors[0])

    def test_missing_script_src(self) -> None:
        """A broken <script src> reports source file and missing asset."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html('<script src="/nope.js"></script>'))
            errors = check_links(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("index.html", errors[0])
            self.assertIn("nope.js", errors[0])

    def test_missing_stylesheet(self) -> None:
        """A broken <link rel=stylesheet> reports source + missing CSS."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html(
                extra_head='<link rel="stylesheet" href="/missing.css">'
            ))
            errors = check_links(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("index.html", errors[0])
            self.assertIn("missing.css", errors[0])

    def test_error_includes_source_path(self) -> None:
        """Error message must include the source HTML file path."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "sub/page.html", _html('<a href="/nope.html">X</a>'))
            errors = check_links(root)
            self.assertTrue(
                any("sub/page.html" in e or "page.html" in e for e in errors),
                f"Source file not in errors: {errors}",
            )

    def test_multiple_broken_links_all_reported(self) -> None:
        """All broken links are reported, not just the first one."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html(
                '<a href="/a.html">A</a><a href="/b.html">B</a>'
            ))
            errors = check_links(root)
            self.assertEqual(len(errors), 2, errors)


# ---------------------------------------------------------------------------
# 3. Broken fragments fail with source + target reported
# ---------------------------------------------------------------------------

class TestBrokenFragments(unittest.TestCase):

    def test_same_page_broken_fragment(self) -> None:
        """A #fragment with no matching id on the same page is an error."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html('<a href="#ghost">X</a>'))
            errors = check_links(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("ghost", errors[0])
            self.assertIn("index.html", errors[0])

    def test_cross_page_broken_fragment(self) -> None:
        """A cross-page fragment that doesn't exist in the target is an error."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html('<a href="/about/index.html#nosuchid">X</a>'))
            _write(root, "about/index.html", _html("<p>No ids here</p>"))
            errors = check_links(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("nosuchid", errors[0])

    def test_broken_fragment_reports_source(self) -> None:
        """Fragment errors include the source file path."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "news/article.html", _html('<a href="#phantom">X</a>'))
            errors = check_links(root)
            self.assertTrue(
                any("article.html" in e for e in errors),
                f"Source file not in fragment errors: {errors}",
            )

    def test_valid_fragment_does_not_error(self) -> None:
        """A fragment that resolves correctly produces zero errors."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html(
                '<a href="#real">X</a><div id="real">Content</div>'
            ))
            errors = check_links(root)
            self.assertEqual(errors, [], errors)


# ---------------------------------------------------------------------------
# 4. External, mailto, tel, data URLs are skipped (never error)
# ---------------------------------------------------------------------------

class TestSkippedSchemes(unittest.TestCase):

    def _assert_no_errors_for(self, href: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html(f'<a href="{href}">X</a>'))
            errors = check_links(root)
            self.assertEqual(errors, [], f"Expected no errors for {href!r}, got: {errors}")

    def test_http_external_skipped(self) -> None:
        self._assert_no_errors_for("http://example.com/page")

    def test_https_external_skipped(self) -> None:
        self._assert_no_errors_for("https://example.com/page")

    def test_mailto_skipped(self) -> None:
        self._assert_no_errors_for("mailto:user@example.com")

    def test_tel_skipped(self) -> None:
        self._assert_no_errors_for("tel:+15550001234")

    def test_data_uri_skipped(self) -> None:
        self._assert_no_errors_for("data:text/plain;base64,SGVsbG8=")

    def test_javascript_skipped(self) -> None:
        self._assert_no_errors_for("javascript:void(0)")

    def test_external_img_src_skipped(self) -> None:
        """External <img src> should also be silently skipped."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html('<img src="https://cdn.example.com/photo.jpg" alt="x">'))
            errors = check_links(root)
            self.assertEqual(errors, [], errors)


# ---------------------------------------------------------------------------
# 5. Relative paths, root-absolute paths, directory indexes, encoding, query
# ---------------------------------------------------------------------------

class TestResolutionEdgeCases(unittest.TestCase):

    def test_root_absolute_path(self) -> None:
        """A root-absolute href /about/index.html resolves against site root."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html('<a href="/about/index.html">About</a>'))
            _write(root, "about/index.html", _html("About"))
            errors = check_links(root)
            self.assertEqual(errors, [], errors)

    def test_relative_path_deep(self) -> None:
        """Deeply nested relative path resolves correctly."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "a/b/page.html", _html('<a href="../../index.html">Home</a>'))
            _write(root, "index.html", _html("Home"))
            errors = check_links(root)
            self.assertEqual(errors, [], errors)

    def test_directory_index_trailing_slash(self) -> None:
        """href='/about/' (trailing slash) resolves to /about/index.html."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html('<a href="/about/">About</a>'))
            _write(root, "about/index.html", _html("About"))
            errors = check_links(root)
            self.assertEqual(errors, [], errors)

    def test_directory_index_no_extension(self) -> None:
        """href='/about' (no extension) resolves to /about/index.html."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html('<a href="/about">About</a>'))
            _write(root, "about/index.html", _html("About"))
            errors = check_links(root)
            self.assertEqual(errors, [], errors)

    def test_url_encoded_path(self) -> None:
        """Percent-encoded characters in paths are decoded before lookup."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # create file with a space in the name
            _write(root, "my page/index.html", _html("Hi"))
            _write(root, "index.html", _html('<a href="/my%20page/">Go</a>'))
            errors = check_links(root)
            self.assertEqual(errors, [], errors)

    def test_query_string_stripped_for_file_check(self) -> None:
        """Query strings (?v=1) are ignored when checking file existence."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "styles.css", "body{}")
            _write(root, "index.html", _html(
                extra_head='<link rel="stylesheet" href="/styles.css?v=42">'
            ))
            errors = check_links(root)
            self.assertEqual(errors, [], errors)

    def test_query_string_broken_file_still_errors(self) -> None:
        """A query-string URL pointing to a missing file still errors."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html(
                extra_head='<link rel="stylesheet" href="/nope.css?v=1">'
            ))
            errors = check_links(root)
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("nope.css", errors[0])

    def test_fragment_with_query_string(self) -> None:
        """Fragment checks still work when URL also has a query string."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html(
                '<a href="/page.html?v=1#section">X</a>'
            ))
            _write(root, "page.html", _html('<div id="section">Section</div>'))
            errors = check_links(root)
            self.assertEqual(errors, [], errors)

    def test_missing_directory_index(self) -> None:
        """A href='/about/' without a corresponding index.html is an error."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html('<a href="/about/">About</a>'))
            # Note: about/index.html NOT created
            errors = check_links(root)
            self.assertEqual(len(errors), 1, errors)

    def test_site_root_nonexistent(self) -> None:
        """Passing a non-existent site root returns a single error string."""
        errors = check_links(Path("/tmp/__nonexistent_site_root_pch147__"))
        self.assertEqual(len(errors), 1)
        self.assertIn("does not exist", errors[0])


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------

class TestCLI(unittest.TestCase):

    def test_cli_exit_zero_on_clean_site(self) -> None:
        """CLI exits 0 when no broken links found."""
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html('<a href="https://example.com">Ext</a>'))
            result = subprocess.run(
                [sys.executable, str(_REPO_ROOT / "scripts" / "check_local_links.py"), str(root)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_cli_exit_nonzero_on_broken_link(self) -> None:
        """CLI exits non-zero when broken links exist."""
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "index.html", _html('<a href="/missing.html">Gone</a>'))
            result = subprocess.run(
                [sys.executable, str(_REPO_ROOT / "scripts" / "check_local_links.py"), str(root)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing.html", result.stderr)


if __name__ == "__main__":
    unittest.main()
