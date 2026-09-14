"""Inactive affiliate integration guards for BidetFit."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "ventures" / "bidetfit" / "public"
MISSION = ROOT / "ventures" / "bidetfit"


class AffiliateGuardTests(unittest.TestCase):
    def test_no_active_affiliate_markers_in_public_html(self) -> None:
        for page in PUBLIC.rglob("*.html"):
            text = page.read_text(encoding="utf-8")
            self.assertNotIn('data-affiliate="active"', text, page.name)

    def test_disclosure_lists_inactive_manybidets_and_premium_bidet_exception(self) -> None:
        text = (PUBLIC / "disclosure.html").read_text(encoding="utf-8")
        self.assertIn('data-affiliate="inactive"', text)
        self.assertIn("ManyBidets", text)
        self.assertIn("HTTP 404", text)
        self.assertIn("No affiliate links are active", text)

    def test_affiliate_integrations_config_is_inactive(self) -> None:
        config = json.loads((MISSION / "config" / "affiliate_integrations.json").read_text(encoding="utf-8"))
        self.assertEqual(config["active_links"], 0)
        for integration in config["integrations"]:
            self.assertEqual(integration["status"], "inactive")
            self.assertIsNone(integration["tracking_url"])

    def test_affiliate_links_csv_has_no_tracking_urls(self) -> None:
        rows = (MISSION / "AFFILIATE_LINKS.csv").read_text(encoding="utf-8").splitlines()
        self.assertGreater(len(rows), 1)
        for line in rows[1:]:
            if not line.strip():
                continue
            self.assertIn("inactive", line)
            self.assertTrue(line.endswith(",,") or ",," in line or line.count(",") >= 4)


if __name__ == "__main__":
    unittest.main()
