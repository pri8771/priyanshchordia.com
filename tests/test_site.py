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
    def test_markdown_keeps_heading_and_following_paragraph_separate(self) -> None:
        rendered = GEN.markdown("## Collection\nNothing is collected.\n\n- Local data\n- No account")
        self.assertEqual(
            rendered,
            "<h2>Collection</h2><p>Nothing is collected.</p>"
            "<ul><li>Local data</li><li>No account</li></ul>",
        )

    def test_inline_script_json_cannot_close_script_element(self) -> None:
        rendered = GEN.safe_script_json({"summary": "</script><script>alert(1)</script>"})
        self.assertNotIn("</script", rendered.lower())
        self.assertIn("\\u003c/script\\u003e", rendered)
        self.assertEqual(json.loads(rendered)["summary"], "</script><script>alert(1)</script>")

    def test_enabled_app_routes_have_explicit_public_metadata(self) -> None:
        products = GEN.load_products()
        apps = GEN.load_apps(products)
        enabled = [app for app in apps if app.get("route_enabled") is True]
        self.assertEqual({app["slug"] for app in enabled}, {"mala", "anjali", "svara", "roam"})
        for app in enabled:
            with self.subTest(app=app["slug"]):
                self.assertRegex(str(app["support_contact"]), r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
                self.assertGreaterEqual(len(str(app["privacy_body"]).strip()), 200)
                if app.get("app_store_id") is not None:
                    self.assertRegex(str(app["app_store_id"]), r"^\d{9,12}$")
        self.assertEqual(
            {product["slug"] for product in products},
            {"mala", "anjali", "svara", "roam"},
        )

    def test_unapproved_legal_copy_is_dated_as_draft_and_noindex(self) -> None:
        apps = GEN.load_apps(GEN.load_products())
        app = next(app for app in apps if app.get("route_enabled") is True)
        rendered = GEN.app_legal_page(app, "privacy")
        self.assertIn("Draft updated July 29, 2026", rendered)
        self.assertIn('name="robots" content="noindex,follow"', rendered)

    def test_overworld_projects_and_signals_are_reachable(self) -> None:
        source = (ROOT / "scripts" / "experiences" / "overworld.js").read_text(encoding="utf-8")

        def coordinate_array(pattern: str) -> list[list[int]]:
            match = re.search(pattern, source, re.S)
            self.assertIsNotNone(match)
            return ast.literal_eval(match.group(1))

        dimensions = re.search(r"var W = (\d+), H = (\d+), TUNNEL_ROW = (\d+);", source)
        self.assertIsNotNone(dimensions)
        width, height, tunnel_row = (int(value) for value in dimensions.groups())
        walls = coordinate_array(
            r"(\[\[[\d,\]\[\s]+\]\])\s*\.forEach\(function \(c\) \{ grid\[c\[1\]\]\[c\[0\]\] = \"#\";"
        )
        trees = coordinate_array(
            r"(\[\[[\d,\]\[\s]+\]\])\s*\.forEach\(function \(c\) \{ grid\[c\[1\]\]\[c\[0\]\] = \"T\";"
        )
        maze_blocks = coordinate_array(r"var MAZE_BLOCKS = (\[[\d,\]\[\s]+\]);")
        shards = coordinate_array(r"var SHARDS = (\[\[[\d,\]\[\s]+\]\]);")
        preferred_targets = coordinate_array(r"var PREFERRED_TARGETS = (\[[\d,\]\[\s]+\]);")
        bonus_match = re.search(r"var bonusKey = keyFor\((\d+),\s*(\d+)\)", source)
        self.assertIsNotNone(bonus_match)
        bonus = (int(bonus_match.group(1)), int(bonus_match.group(2)))

        blocked = {(x, 0) for x in range(width)} | {(x, height - 1) for x in range(width)}
        blocked |= {(0, y) for y in range(height)} | {(width - 1, y) for y in range(height)}
        blocked |= {(x, y) for y in range(2, 6) for x in range(2, 8)}
        blocked |= {tuple(pair) for pair in walls + trees}
        for x, y, block_width, block_height in maze_blocks:
            blocked |= {
                (block_x, block_y)
                for block_y in range(y, y + block_height)
                for block_x in range(x, x + block_width)
            }
        blocked -= {(x, tunnel_row) for x in range(width)}
        special_signals = [tuple(pair) for pair in shards] + [bonus]
        blocked -= set(special_signals)

        start = (16, tunnel_row)
        reached = {start}
        queue: deque[tuple[int, int]] = deque([start])
        ordered_reached: list[tuple[int, int]] = []
        while queue:
            x, y = queue.popleft()
            ordered_reached.append((x, y))
            neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
            if y == tunnel_row:
                neighbors[0] = ((x - 1) % width, y)
                neighbors[1] = ((x + 1) % width, y)
            for nxt in neighbors:
                if nxt not in blocked and nxt not in reached:
                    reached.add(nxt)
                    queue.append(nxt)

        used: set[tuple[int, int]] = set()
        project_targets: list[tuple[int, int]] = []
        product_count = len(GEN.load_products())
        for preferred in map(tuple, preferred_targets[:product_count]):
            target = preferred if preferred in reached and preferred not in used else next(
                (
                    cell for cell in ordered_reached
                    if cell not in used
                    and cell != start
                    and abs(cell[0] - start[0]) + abs(cell[1] - start[1]) > 3
                ),
                None,
            )
            self.assertIsNotNone(target, "every product must receive a target")
            used.add(target)
            project_targets.append(target)

        self.assertEqual(len(project_targets), product_count)
        self.assertEqual(len(set(project_targets)), product_count)
        for target in project_targets + special_signals:
            with self.subTest(target=target):
                self.assertIn(target, reached)

        self.assertIn("window.location.assign(target.p.href)", source)
        self.assertNotIn("function openPortal", source)
        self.assertIn('if (e.persisted) window.location.reload();', source)
        self.assertIn('window.addEventListener("pageshow", onPageShow);', source)
        self.assertIn('window.removeEventListener("pageshow", onPageShow);', source)


if __name__ == "__main__":
    unittest.main()
