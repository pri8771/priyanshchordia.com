from __future__ import annotations

import ast
import importlib.util
import json
import re
import unittest
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("generate_site", ROOT / "scripts" / "generate_site.py")
assert SPEC and SPEC.loader
GEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GEN)


class GeneratorTests(unittest.TestCase):
    def test_quote_becomes_blockquote(self) -> None:
        rendered = GEN.markdown("> a\n> b")
        self.assertIn("<blockquote", rendered)
        self.assertIn("a b", rendered)

    def test_numbered_list_becomes_ol(self) -> None:
        rendered = GEN.markdown("1. x\n2. y")
        self.assertIn("<ol><li>x</li><li>y</li></ol>", rendered)

    def test_local_picture_becomes_img(self) -> None:
        rendered = GEN.markdown("![alt text](/blog-media/s/a.gif)")
        self.assertIn('src="/blog-media/s/a.gif"', rendered)
        self.assertIn('alt="alt text"', rendered)

    def test_remote_picture_stays_text(self) -> None:
        rendered = GEN.markdown("![x](http://example.com/a.gif)")
        self.assertNotIn("<img", rendered)
