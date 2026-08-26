#!/usr/bin/env python3
"""Deterministic, zero-cost BidetFit operator.

This runner validates persistent state, governance records, tracker links, and
public health. It deliberately does not generate prose, invent metrics, apply
to affiliate programs, answer customer email, process returns, or call a paid
model. Substantive editorial and customer-operations work remains separately
authorized and is tracked through BF work items.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "STATE.json"
RUNS_PATH = ROOT / "RUNS.csv"
LOG_PATH = ROOT / "logs" / "runs.jsonl"
DIARY_PATH = ROOT / "DIARY.md"
KILL_SWITCH = ROOT / "KILL_SWITCH"

REQUIRED_FILES = (
    "MISSION.md",
    "STATE.json",
    "CONTENT_MAP.csv",
    "EDITORIAL_QUEUE.csv",
    "AFFILIATE_PROGRAMS.csv",
    "EXPERIMENTS.csv",
    "METRICS.csv",
    "DECISIONS.md",
    "ACCOUNTS.md",
    "RUNBOOK.md",
    "CHANGELOG.md",
    "DIARY.md",
    "NICHE_SCORECARD.csv",
    "RUNS.csv",
    "AGENTS.md",
    "CLAUDE.md",
    ".ai/standards-version.json",
    ".ai/APP_FACTORY_OPERATING_STANDARD.md",
    "docs/DOCUMENTATION_INDEX.md",
    "docs/PROJECT_DOCUMENTATION.md",
    "docs/STATUS.md",
    "docs/TASKS.md",
    "docs/WORK_ITEMS.csv",
    "docs/TIME_LOG.csv",
    "docs/TRACKER_LINKS.csv",
    "docs/TRACKER_INDEX.md",
    "docs/WORK_ITEM_TEMPLATE.md",
    "docs/BUGS.md",
    "docs/DECISIONS.md",
    "docs/RISKS.md",
    "docs/ASSUMPTIONS.md",
    "docs/DEFINITION_OF_READY.md",
    "docs/DEFINITION_OF_DONE.md",
    "docs/PROMPT_LOG.md",
    "docs/JIRA_SYNC_PENDING.md",
    "docs/HANDOFF.md",
    "docs/AUTONOMOUS_CUSTOMER_OPERATIONS.md",
)

CSV_HEADERS = {
    "CONTENT_MAP.csv": {"page_id", "url", "target_audience", "status", "next_review_date"},
    "EDITORIAL_QUEUE.csv": {"priority", "item_id", "type", "title", "status"},
    "AFFILIATE_PROGRAMS.csv": {"merchant", "commission_structure", "application_status", "approval_status", "source"},
    "EXPERIMENTS.csv": {"experiment_id", "hypothesis", "primary_metric", "status"},
    "METRICS.csv": {"date", "site_status", "affiliate_clicks", "cash_received_usd"},
    "RUNS.csv": {"run_id", "started_at", "finished_at", "trigger", "result"},
    "docs/WORK_ITEMS.csv": {
        "work_item_id", "title", "work_item_type", "status", "priority",
        "estimated_hours", "actuals_confidence", "verification_evidence",
    },
    "docs/TIME_LOG.csv": {
        "work_item_id", "date", "contributor", "duration_minutes",
        "evidence", "actuals_confidence",
    },
    "docs/TRACKER_LINKS.csv": {
        "work_item_id", "jira_key", "jira_url", "notion_url",
        "canonical_status", "last_verified_at",
    },
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def load_state() -> dict[str, Any]:
    payload = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if payload.get("project") != "BidetFit":
        raise ValueError("STATE.json does not identify BidetFit")
    if payload.get("experiment", {}).get("status") not in {"active", "paused", "stopped"}:
        raise ValueError("STATE.json has an invalid experiment status")
    if payload.get("governance", {}).get("scope_version") != "BF-1.1-governed-autonomy":
        raise ValueError("STATE.json does not identify the governed BidetFit scope")
    return payload


def validate_files() -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")
    for relative, required in CSV_HEADERS.items():
        path = ROOT / relative
        if not path.is_file():
            continue
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            try:
                header = set(next(reader))
            except StopIteration:
                errors.append(f"empty CSV: {relative}")
                continue
        missing = required - header
        if missing:
            errors.append(f"{relative} missing columns: {', '.join(sorted(missing))}")
    public = ROOT / "public"
    for relative in ("index.html", "fit-checker.html", "sitemap.xml", "status.json"):
        if not (public / relative).is_file():
            errors.append(f"missing public source: {relative}")
    return errors


def fetch_json(url: str) -> tuple[int | None, dict[str, Any] | None, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "BidetFit-Operator/1.1"})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            status = int(response.status)
            payload = json.loads(response.read().decode("utf-8"))
            return status, payload, "ok"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return None, None, f"{type(exc).__name__}: {exc}"


def append_run(row: dict[str, str], detail: dict[str, Any]) -> None:
    RUNS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RUNS_PATH.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "run_id", "started_at", "finished_at", "trigger", "result",
            "experiment_status", "site_status", "local_checks", "public_http", "notes",
        ])
        writer.writerow(row)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(detail, sort_keys=True) + "\n")


def append_daily_diary(now: datetime, result: str, site_status: str, notes: str) -> None:
    marker = f"<!-- operator:{now.date().isoformat()} -->"
    current = DIARY_PATH.read_text(encoding="utf-8")
    if marker in current:
        return
    entry = (
        f"\n---\n\n## Automated evidence — {now.date().isoformat()}\n\n"
        f"{marker}\n"
        f"- First scheduled operator evidence for this UTC day: **{result}**.\n"
        f"- Public site state observed: **{site_status}**.\n"
        f"- Evidence detail: {notes}\n"
        f"- Additional same-day runs are retained in `RUNS.csv` and `logs/runs.jsonl`.\n"
    )
    DIARY_PATH.write_text(current.rstrip() + entry + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-only", action="store_true")
    args = parser.parse_args()

    started = utc_now()
    run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}-{os.environ.get('GITHUB_RUN_ID', 'local')}"
    trigger = os.environ.get("GITHUB_EVENT_NAME", "manual-local")
    result = "success"
    notes: list[str] = []
    public_http = "skipped"

    try:
        state = load_state()
        experiment_status = str(state["experiment"]["status"])
        site_status = str(state.get("site", {}).get("status", "unknown"))

        if KILL_SWITCH.exists() or experiment_status in {"paused", "stopped"}:
            result = "paused"
            notes.append("kill switch or non-active experiment status honored")
        else:
            errors = validate_files()
            if errors:
                result = "failure"
                notes.extend(errors)
            else:
                notes.append("required mission, governance, tracker, work-item, CSV, and public-source files passed")

            if not args.local_only and result != "failure":
                status_url = str(state["site"]["canonical_url"]).rstrip("/") + "/status.json"
                status, payload, message = fetch_json(status_url)
                public_http = str(status) if status is not None else "unreachable"
                if status == 200 and payload and payload.get("brand") == "BidetFit":
                    site_status = "live"
                    state["site"]["status"] = "live"
                    state["site"]["last_verified_at"] = iso(started)
                    notes.append("public status endpoint verified")
                elif site_status == "launching":
                    notes.append(f"public endpoint still launching: {message}")
                else:
                    result = "failure"
                    notes.append(f"public endpoint failed after launch: {message}")

        finished = utc_now()
        state["automation"]["status"] = "healthy" if result in {"success", "paused"} else "degraded"
        state["automation"]["last_run_at"] = iso(finished)
        state["automation"]["last_run_result"] = result
        state["updated_at"] = iso(finished)
        STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

        note_text = "; ".join(notes) or "no notes"
        row = {
            "run_id": run_id,
            "started_at": iso(started),
            "finished_at": iso(finished),
            "trigger": trigger,
            "result": result,
            "experiment_status": experiment_status,
            "site_status": site_status,
            "local_checks": "pass" if result != "failure" else "fail",
            "public_http": public_http,
            "notes": note_text,
        }
        detail = {**row, "schema_version": 1}
        append_run(row, detail)
        append_daily_diary(finished, result, site_status, note_text)
        print(json.dumps(detail, indent=2))
        return 1 if result == "failure" else 0
    except Exception as exc:
        finished = utc_now()
        detail = {
            "schema_version": 1,
            "run_id": run_id,
            "started_at": iso(started),
            "finished_at": iso(finished),
            "trigger": trigger,
            "result": "failure",
            "error": f"{type(exc).__name__}: {exc}",
        }
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(detail, sort_keys=True) + "\n")
        print(json.dumps(detail, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
