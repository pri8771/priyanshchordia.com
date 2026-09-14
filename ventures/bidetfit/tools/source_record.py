#!/usr/bin/env python3
"""Manufacturer source-record interface for BidetFit checker corrections."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES_PATH = ROOT / "config" / "manufacturer_sources.json"
RULES_PATH = ROOT / "public" / "assets" / "fit-checker-rules.json"


def load_sources() -> dict:
    return json.loads(SOURCES_PATH.read_text(encoding="utf-8"))


def detect_changes(sources: dict) -> list[dict]:
    results = []
    for record in sources.get("records", []):
        status = record.get("change_status")
        if status not in {"changed", "unchanged"}:
            status = "unchanged" if record.get("content_hash") == record.get("previous_hash") else "changed"
        results.append({
            "source_id": record["source_id"],
            "manufacturer": record["manufacturer"],
            "url": record["url"],
            "change_status": status,
            "retrieved_at": record.get("retrieved_at"),
            "checker_impacts": record.get("checker_impacts", []),
        })
    return results


def export_rules(sources: dict) -> dict:
    """Derive public checker thresholds from manufacturer source records."""
    bolt_low = 5.5
    bolt_high = 7.5
    rear_min = 1.5
    french_curve_citation = None
    source_freshness = None

    for record in sources.get("records", []):
        specs = record.get("specifications", {})
        if "bolt_spacing_incompatible_below_in" in specs:
            bolt_low = float(specs["bolt_spacing_incompatible_below_in"])
        if "bolt_spacing_incompatible_above_in" in specs:
            bolt_high = float(specs["bolt_spacing_incompatible_above_in"])
        if "rear_clearance_minimum_in" in specs:
            rear_min = float(specs["rear_clearance_minimum_in"])
        if record.get("topic", "").find("french_curve") >= 0:
            french_curve_citation = {
                "manufacturer": record["manufacturer"],
                "url": record["url"],
                "retrieved_at": record.get("retrieved_at"),
                "guidance": specs.get("french_curve_deep_one_piece"),
            }
            source_freshness = record.get("retrieved_at")

    return {
        "schema_version": 1,
        "source_freshness": source_freshness,
        "bolt_spacing": {
            "incompatible_below_in": bolt_low,
            "incompatible_above_in": bolt_high,
            "manufacturer_source": "Bio Bidet compatibility guide",
        },
        "rear_clearance": {
            "manufacturer_minimum_in": rear_min,
            "common_screen_in": 1.75,
            "manufacturer_source": "Bio Bidet compatibility guide",
        },
        "french_curve": french_curve_citation,
        "limits_note": "Screening ranges from cited manufacturer guidance. Exact product drawings control.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="BidetFit manufacturer source-record tools")
    parser.add_argument("--detect", action="store_true", help="Print changed/unchanged detection")
    parser.add_argument("--export-rules", action="store_true", help="Write fit-checker-rules.json")
    args = parser.parse_args()

    if not SOURCES_PATH.is_file():
        print(f"missing source register: {SOURCES_PATH}", file=sys.stderr)
        return 1

    sources = load_sources()
    if args.detect:
        print(json.dumps(detect_changes(sources), indent=2))
    if args.export_rules:
        RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
        RULES_PATH.write_text(json.dumps(export_rules(sources), indent=2) + "\n", encoding="utf-8")
        print(f"exported rules: {RULES_PATH}")
    if not args.detect and not args.export_rules:
        parser.print_help()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
