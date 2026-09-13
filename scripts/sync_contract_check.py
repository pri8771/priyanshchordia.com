#!/usr/bin/env python3
"""Mount the reviewed, offline OPO component through existing Pages builds."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

FILES = {
    "web/index.html": "index.html",
    "web/app.mjs": "web/app.mjs",
    "web/styles.css": "web/styles.css",
    "src/validator.mjs": "src/validator.mjs",
    "src/cli.mjs": "src/cli.mjs",
    "contract/validation-receipt.schema.json": "contract/validation-receipt.schema.json",
}
BASE = "https://priyanshchordia.com/one-person-ops/contract-check/"
README = """One Person Ops — Contract Check

This free tool validates JSON locally in your browser or Node.js. It implements
a documented bounded subset, not the complete JSON Schema specification.
It does not send your input to a server, use an LLM, collect telemetry or charge.

Module: src/validator.mjs — import validateContract({request_id, schema, data}).
CLI: download BOTH src/cli.mjs and src/validator.mjs into the same folder.
Run with Node.js 20+: node cli.mjs < request.json
Exit codes: 0 valid, 1 invalid data, 2 invalid request.
Receipt schema: contract/validation-receipt.schema.json
Exact public artifact hashes and source revision: release.json

Limits: canonical request at most 65,536 UTF-8 bytes; CLI and browser also cap
raw input. Maximum nesting is 16 and at most 100 errors are returned.
String length counts Unicode code points. Supported schema keywords are type,
required, properties, additionalProperties (boolean), items, enum, minLength,
maxLength, minimum, maximum, minItems and maxItems. Unsupported keywords are
rejected; no external references, regex, files or remote schemas are resolved.

The broader One Person Ops agent-facing business service is not provided by
this component. There is no messaging API, persistent inbox, payment service
or promise of revenue in this release. Do not put secrets in public messages.
"""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def mount(source: Path, target: Path) -> dict:
    provenance = json.loads((source / "SOURCE.json").read_text(encoding="utf-8"))
    if set(provenance["files"]) != set(FILES):
        raise ValueError("Source manifest must contain exactly the six public files")
    prepared = {}
    for rel, destination in FILES.items():
        path = source / rel
        if path.is_symlink() or any(p.is_symlink() for p in path.parents):
            raise ValueError("Symlink source is not publishable")
        data = path.read_bytes()
        if digest(data) != provenance["files"][rel]:
            raise ValueError(f"Reviewed source hash mismatch: {rel}")
        prepared[destination] = data

    # Source preview is rooted at /; the public component has a nested mount.
    page = prepared["index.html"].decode("utf-8")
    for old, new in [('href="/web/styles.css"', 'href="./web/styles.css"'),
                     ('src="/web/app.mjs"', 'src="./web/app.mjs"')]:
        if page.count(old) != 1:
            raise ValueError(f"Unexpected preview asset reference: {old}")
        page = page.replace(old, new)
    if "../src/validator.mjs" not in prepared["web/app.mjs"].decode("utf-8"):
        raise ValueError("Browser module must use the reviewed relative validator import")
    if page.count("</head>") != 1 or page.count("</footer>") != 1:
        raise ValueError("Unexpected public page structure")
    page = page.replace("</head>", '<meta name="description" content="Validate a bounded JSON contract locally and download its receipt.">\n'
                        f'<link rel="canonical" href="{BASE}">\n</head>')
    page = page.replace("</footer>", '<nav aria-label="Developer downloads"><a href="./src/validator.mjs" download>Validator module</a> · '
                        '<a href="./src/cli.mjs" download>CLI</a> · '
                        '<a href="./contract/validation-receipt.schema.json">Receipt schema</a> · '
                        '<a href="./README.txt">Usage and limits</a> · '
                        '<a href="./release.json">Release hashes</a></nav>\n</footer>')
    prepared["index.html"] = page.encode("utf-8")
    prepared["README.txt"] = README.encode("utf-8")
    receipt = {
        "schema_version": 1, "component": "One Person Ops Contract Check",
        "source_commit": provenance["source_commit"],
        "source_files_sha256": provenance["files"],
        "public_files_sha256": {name: digest(data) for name, data in prepared.items()},
        "transforms": ["Preview HTML asset paths made relative", "Public canonical and download links added"],
        "business_outcomes": "unmeasured", "messaging_api": False,
    }
    prepared["release.json"] = (json.dumps(receipt, indent=2) + "\n").encode("utf-8")
    if target.name != "contract-check" or target.parent.name != "one-person-ops":
        raise ValueError("Refusing to replace an unrelated target directory")
    if target.is_symlink() or any(p.is_symlink() for p in target.parents):
        raise ValueError("Symlink target is not publishable")
    if target.exists():
        shutil.rmtree(target)
    for name, data in prepared.items():
        output = target / name
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
    return receipt


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: sync_contract_check.py SOURCE site/one-person-ops/contract-check")
    result = mount(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"Mounted reviewed Contract Check: {len(result['public_files_sha256'])} hashed files")
