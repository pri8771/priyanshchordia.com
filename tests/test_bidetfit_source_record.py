"""Manufacturer source-record interface and checker rule export."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MISSION = ROOT / "ventures" / "bidetfit"
SPEC = importlib.util.spec_from_file_location(
    "source_record", MISSION / "tools" / "source_record.py"
)
assert SPEC and SPEC.loader
SOURCE_RECORD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SOURCE_RECORD)


class SourceRecordTests(unittest.TestCase):
    def test_detect_reports_bio_bidet_change(self) -> None:
        changes = SOURCE_RECORD.detect_changes(SOURCE_RECORD.load_sources())
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["source_id"], "biobidet-compatibility-2026")
        self.assertEqual(changes[0]["change_status"], "changed")

    def test_export_rules_match_manufacturer_thresholds(self) -> None:
        rules = SOURCE_RECORD.export_rules(SOURCE_RECORD.load_sources())
        self.assertEqual(rules["bolt_spacing"]["incompatible_below_in"], 5.5)
        self.assertEqual(rules["bolt_spacing"]["incompatible_above_in"], 7.5)
        self.assertEqual(rules["rear_clearance"]["manufacturer_minimum_in"], 1.5)
        self.assertIn("French-curve", rules["french_curve"]["guidance"])

    def test_cli_exports_public_rules_file(self) -> None:
        rules_path = MISSION / "public" / "assets" / "fit-checker-rules.json"
        before = rules_path.read_text(encoding="utf-8") if rules_path.is_file() else ""
        result = subprocess.run(
            [sys.executable, str(MISSION / "tools" / "source_record.py"), "--export-rules"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        exported = json.loads(rules_path.read_text(encoding="utf-8"))
        self.assertEqual(exported["source_freshness"], "2026-09-14")
        if before:
            rules_path.write_text(before, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
