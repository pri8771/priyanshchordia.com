"""BidetFit fit checker static assets and printable packet contract."""

from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "ventures" / "bidetfit" / "public"


class FitCheckerAssetTests(unittest.TestCase):
    def test_checker_js_syntax_and_manufacturer_correction(self) -> None:
        js_path = PUBLIC / "assets" / "fit-checker.js"
        subprocess.run(["node", "--check", str(js_path)], check=True)
        text = js_path.read_text(encoding="utf-8")
        self.assertIn("Bio Bidet", text)
        self.assertIn("incompatible_below_in: 5.5", text)
        self.assertIn("fit_checker.started", text)
        self.assertIn("fit_checker.unresolved", text)
        self.assertIn("print-packet", text)
        self.assertNotIn("rear_clearance", re.findall(r"forbidden_payload_fields|aggregate", text))

    def test_rules_json_matches_source_export(self) -> None:
        rules = json.loads((PUBLIC / "assets" / "fit-checker-rules.json").read_text(encoding="utf-8"))
        self.assertEqual(rules["bolt_spacing"]["incompatible_below_in"], 5.5)
        self.assertEqual(rules["french_curve"]["manufacturer"], "Bio Bidet")

    def test_fit_checker_page_has_packet_section(self) -> None:
        html = (PUBLIC / "fit-checker.html").read_text(encoding="utf-8")
        self.assertIn('id="fit-packet"', html)
        self.assertIn("Printable measurement packet", html)

    def test_event_contract_forbids_raw_measurements(self) -> None:
        config = json.loads(
            (ROOT / "ventures" / "bidetfit" / "config" / "fit_checker_events.json").read_text(encoding="utf-8")
        )
        forbidden = set(config["forbidden_payload_fields"])
        self.assertIn("rear_clearance", forbidden)
        self.assertIn("bolt_spacing", forbidden)
        self.assertIn("fit_checker.completed", config["allowed_event_types"])

    def test_print_styles_present(self) -> None:
        css = (PUBLIC / "assets" / "site.css").read_text(encoding="utf-8")
        self.assertIn("@media print", css)
        self.assertIn(".fit-packet", css)


if __name__ == "__main__":
    unittest.main()
