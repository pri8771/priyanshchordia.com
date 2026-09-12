"""PCH-104/PCH-120: health receipts cannot manufacture commercial observations."""

import contextlib
import copy
import io
import json
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import sync_bidetfit
from ventures.bidetfit.scripts import operator


MISSION = Path(__file__).resolve().parents[1] / "ventures/bidetfit"


class StatusFreshnessTests(unittest.TestCase):
    def test_stale_launch_rows_stay_unmeasured_after_new_health_receipt(self):
        state = json.loads((MISSION / "STATE.json").read_text(encoding="utf-8"))
        before_metrics = copy.deepcopy(state["metrics"])
        before_money = copy.deepcopy(state["monetization"])
        before_observation = copy.deepcopy(state["metrics_observation"])
        csv_before = (MISSION / "METRICS.csv").read_bytes()
        now = datetime(2026, 9, 13, 12, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = root / "STATE.json"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            diary = root / "DIARY.md"
            diary.write_text("# Fixture diary\n", encoding="utf-8")
            with patch.multiple(operator, STATE_PATH=state_path,
                                RUNS_PATH=root / "RUNS.csv", LOG_PATH=root / "runs.jsonl",
                                DIARY_PATH=diary, KILL_SWITCH=root / "KILL_SWITCH"), \
                    patch.object(operator, "utc_now", return_value=now), \
                    patch.object(operator, "validate_files", return_value=[]), \
                    patch.object(operator, "fetch_json", return_value=(200, {"brand": "BidetFit"}, "ok")), \
                    patch("sys.argv", ["operator"]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(operator.main(), 0)
            after = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(after["site"]["last_verified_at"], "2026-09-13T12:00:00Z")
        self.assertEqual(after["updated_at_scope"], "operator_health_only")
        self.assertEqual(after["metrics"], before_metrics)
        self.assertEqual(after["monetization"], before_money)
        self.assertEqual(after["metrics_observation"], before_observation)
        snapshot = sync_bidetfit.status_snapshot({"verified_commission_usd": 0}, after, MISSION / "METRICS.csv")
        self.assertEqual(snapshot["metrics_observation"]["last_recorded_date"], "2026-08-25")
        self.assertIsNone(snapshot["metrics_observation"]["last_observed_at"])
        self.assertIsNone(snapshot["verified_commission_usd"])
        self.assertTrue(all(value is None for value in snapshot["traffic"].values()))
        self.assertEqual((MISSION / "METRICS.csv").read_bytes(), csv_before)

    def test_unavailable_or_invalid_metric_dates_are_not_observations(self):
        with tempfile.TemporaryDirectory() as directory:
            metrics = Path(directory) / "METRICS.csv"
            for contents in (None, "date,affiliate_clicks\n", "date,affiliate_clicks\nunknown,0\n"):
                if contents is not None:
                    metrics.write_text(contents, encoding="utf-8")
                result = sync_bidetfit.status_snapshot({}, {}, metrics)
                self.assertEqual(result["metrics_observation"]["status"], "unmeasured")
                self.assertIsNone(result["metrics_observation"]["last_recorded_date"])
                self.assertIsNone(result["metrics_observation"]["last_observed_at"])
                self.assertIsNone(result["health"]["last_public_verified_at"])

    def test_public_build_uses_recorded_health_without_advancing_observation_date(self):
        source_before = (MISSION / "public/status.json").read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / "sitemap.xml").write_text(
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>', encoding="utf-8")
            target = site / "bidetfit"
            with patch("sys.argv", ["sync_bidetfit", str(MISSION / "public"), str(target)]), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(sync_bidetfit.main(), 0)
            status = json.loads((target / "status.json").read_text(encoding="utf-8"))
            state = json.loads((MISSION / "STATE.json").read_text(encoding="utf-8"))
            self.assertEqual(status["health"]["last_public_verified_at"], state["site"]["last_verified_at"])
            self.assertEqual(status["metrics_observation"]["status"], "unmeasured")
            self.assertIsNone(status["verified_commission_usd"])
            self.assertEqual(status["active_affiliate_links"], 0)
        self.assertEqual((MISSION / "public/status.json").read_bytes(), source_before)


if __name__ == "__main__":
    unittest.main()
