# BidetFit Documentation Index

**Operating standard:** App Factory Operating Standard 1.1  
**Scope version:** `BF-1.1-governed-autonomy`  
**Repository path:** `ventures/bidetfit`  
**Last updated:** 2026-08-25

## Source-of-truth order

1. Versioned repository documentation and implementation evidence.
2. Notion project page and database mirrors.
3. Jira executable work queue, worklogs, dependencies, approvals, and discussions.
4. Chat history only after it is captured in one of the systems above.

A conflict is recorded and resolved in the repository first, then synchronized to Notion and Jira. History is never silently overwritten.

## Canonical project files

- `MISSION.md` — experiment mission, constraints, authority, and success metrics.
- `STATE.json` — machine-readable current state.
- `DIARY.md` — detailed chronological operating diary.
- `DECISIONS.md` — authoritative architectural and business decisions.
- `RUNBOOK.md` — operating loop, kill switch, recovery, publishing, affiliate, and financial gates.
- `CONTENT_MAP.csv` — page-level audience, intent, value, traffic, and review schedule.
- `EDITORIAL_QUEUE.csv` — prioritized publishing queue.
- `AFFILIATE_PROGRAMS.csv` and `AFFILIATE_LINKS.csv` — program and link evidence.
- `EXPERIMENTS.csv` and `METRICS.csv` — learning loop and measured outcomes.
- `RUNS.csv` and `logs/runs.jsonl` — unattended execution evidence.

## App Factory governance adapters

- `AGENTS.md`
- `CLAUDE.md`
- `.cursor/rules/00-app-factory-governance.mdc`
- `.ai/standards-version.json`
- `.ai/APP_FACTORY_OPERATING_STANDARD.md`

## Detailed governance and handoff docs

- `docs/PROJECT_DOCUMENTATION.md`
- `docs/STATUS.md`
- `docs/TASKS.md`
- `docs/WORK_ITEMS.csv`
- `docs/TIME_LOG.csv`
- `docs/WORK_ITEM_TEMPLATE.md`
- `docs/BUGS.md`
- `docs/DECISIONS.md`
- `docs/RISKS.md`
- `docs/ASSUMPTIONS.md`
- `docs/DEFINITION_OF_READY.md`
- `docs/DEFINITION_OF_DONE.md`
- `docs/PROMPT_LOG.md`
- `docs/prompts/`
- `docs/JIRA_SYNC_PENDING.md`
- `docs/HANDOFF.md`
- `docs/AUTONOMOUS_CUSTOMER_OPERATIONS.md`

## Maintenance rule

Run a documentation checkpoint after every two or three meaningful instructions, after implementation or bug repair, after an architecture or strategy decision, before a commit or pull request, before any Done claim, and before ending a major work session. Update only facts that changed and preserve stable IDs.
