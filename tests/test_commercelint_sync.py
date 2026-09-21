import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_commercelint.py"
SPEC = importlib.util.spec_from_file_location("sync_commercelint", SCRIPT)
sync = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(sync)


class CommerceLintSyncTests(unittest.TestCase):
    def test_rewriter_preserves_source_analytics_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "assets").mkdir()
            analytics = 'const MEASUREMENT_ID = "G-MC3PB0Q7EX";\n'
            (target / "assets" / "analytics.js").write_text(analytics, encoding="utf-8")
            (target / "index.html").write_text(
                '<!doctype html><html><head><title>CommerceLint</title>'
                '<script defer src="assets/analytics.js"></script></head>'
                '<body><main><h1>CommerceLint</h1></main></body></html>',
                encoding="utf-8",
            )
            sync.rewrite_public_tree(target)
            self.assertEqual(
                (target / "assets" / "analytics.js").read_text(encoding="utf-8"),
                analytics,
            )
            self.assertIn(
                'rel="canonical" href="https://priyanshchordia.com/commercelint/"',
                (target / "index.html").read_text(encoding="utf-8"),
            )

    def test_portfolio_promotion_uses_blogs_markers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = (
                '<!doctype html><html><head><title>Portfolio</title></head>'
                '<body><nav><a href="blogs/">Blogs</a></nav><main>'
                '<section id="blogs"><span class="label">02 / Blogs</span>'
                '<h1>Notes</h1></section></main></body></html>'
            )
            (root / "index.html").write_text(page, encoding="utf-8")

            sync.inject_portfolio_promotion(root)

            rendered = (root / "index.html").read_text(encoding="utf-8")
            self.assertIn('id="commercelint-live"', rendered)
            self.assertIn('<span class="label">03 / Blogs</span>', rendered)
            self.assertIn('>CommerceLint</a><a href="blogs/">Blogs</a>', rendered)

    def test_no_noop_analytics_generator_remains(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("def analytics_javascript", source)
        self.assertNotIn("window.commerceLintTrack = noOp", source)


if __name__ == "__main__":
    unittest.main()
