import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "sync_contract_check", Path(__file__).parents[1] / "scripts/sync_contract_check.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class PublicMountTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "source"
        self.target = self.root / "site/one-person-ops/contract-check"
        inputs = {path: b"fixture" for path in module.FILES}
        inputs["web/index.html"] = b'<html><head><link href="/web/styles.css"></head><body><footer></footer><script src="/web/app.mjs"></script></body></html>'
        inputs["web/app.mjs"] = b"import {validateContract} from '../src/validator.mjs';"
        for path, data in inputs.items():
            target = self.source / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        (self.source / "SOURCE.json").write_text(json.dumps({
            "source_commit": "reviewed-fixture", "files": {
                name: hashlib.sha256(data).hexdigest() for name, data in inputs.items()}}))

    def test_nested_mount_excludes_unlisted_private_files_and_binds_downloads(self):
        (self.source / "private-operations.txt").write_text("must not publish")
        self.target.mkdir(parents=True)
        (self.target / "stale-secret.txt").write_text("must not survive rebuild")
        receipt = module.mount(self.source, self.target)
        self.assertEqual(set(p.relative_to(self.target).as_posix()
                             for p in self.target.rglob("*") if p.is_file()),
                         set(module.FILES.values()) | {"README.txt", "release.json"})
        index = (self.target / "index.html").read_text()
        self.assertIn('src="./web/app.mjs"', index)
        self.assertIn('href="./src/cli.mjs"', index)
        for name, expected in receipt["public_files_sha256"].items():
            self.assertEqual(hashlib.sha256((self.target / name).read_bytes()).hexdigest(), expected)

    def test_modified_source_fails_before_replacing_existing_artifact(self):
        self.target.mkdir(parents=True)
        sentinel = self.target / "old.txt"
        sentinel.write_text("keep")
        (self.source / "src/validator.mjs").write_text("unreviewed")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            module.mount(self.source, self.target)
        self.assertEqual(sentinel.read_text(), "keep")

    def test_symlink_source_is_not_followed(self):
        secret = self.root / "secret"
        secret.write_text("fixture")
        source = self.source / "src/cli.mjs"
        source.unlink()
        source.symlink_to(secret)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            module.mount(self.source, self.target)
        self.assertFalse(self.target.exists())

    def test_unrelated_target_is_not_replaced(self):
        unrelated = self.root / "site/commercelint"
        unrelated.mkdir(parents=True)
        marker = unrelated / "index.html"
        marker.write_text("keep")
        with self.assertRaisesRegex(ValueError, "unrelated"):
            module.mount(self.source, unrelated)
        self.assertEqual(marker.read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
