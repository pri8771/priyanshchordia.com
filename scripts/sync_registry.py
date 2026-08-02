#!/usr/bin/env python3
"""Export a deliberately small public view of Mission Control registry truth."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT.parent / "mission-control" / "registry.json"
OUTPUT = ROOT / "data" / "registry.public.json"
PUBLIC_PRODUCT_IDS = {"github-japa", "github-anjali", "github-roam", "github-svara"}
PUBLIC_OVERRIDES = {
    "github-japa": {
        "slug": "mala",
        "name": "Mala",
        "summary": "A quiet, local-first digital mala for steady repetition practice.",
    },
    "github-anjali": {
        "summary": "An offline Hindu micro-prayer companion centered on one short sacred pause.",
    },
    "github-roam": {
        "summary": "A private, local-first travel map that colors in the places you have explored.",
    },
    "github-svara": {
        "summary": "A local-first daily spiritual companion rooted in Hindu culture.",
    },
}
PUBLIC_FIELDS = (
    "id",
    "slug",
    "name",
    "summary",
    "stage",
    "portfolio_lane",
    "public_tier",
)


def sanitize(source: Path) -> dict[str, object]:
    data = json.loads(source.read_text(encoding="utf-8"))
    products = []
    for product in data.get("products", []):
        product_id = str(product.get("id", ""))
        if product_id not in PUBLIC_PRODUCT_IDS:
            continue
        public_product = {field: product.get(field) for field in PUBLIC_FIELDS}
        public_product.update(PUBLIC_OVERRIDES.get(product_id, {}))
        public_product["stage"] = "testflight"
        public_product["public_tier"] = "featured"
        if not all(public_product.get(field) for field in ("id", "slug", "name", "summary")):
            raise ValueError(f"Public product is missing identity fields: {product.get('id', '?')}")
        products.append(public_product)
    products.sort(key=lambda item: (item["public_tier"] != "featured", item["name"].casefold()))
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_updated_at": data.get("updated_at"),
        "products": products,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", nargs="?", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()
    public_data = sanitize(args.source.expanduser().resolve())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(public_data, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT} ({len(public_data['products'])} public products)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
