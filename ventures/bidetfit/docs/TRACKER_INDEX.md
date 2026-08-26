# BidetFit Tracker Index

**Scope version:** `BF-1.1-governed-autonomy`  
**Last verified:** 2026-08-25  
**Canonical system:** GitHub repository documentation and evidence

## Project links

- **Website:** https://priyanshchordia.com/bidetfit/
- **GitHub project path:** https://github.com/pri8771/priyanshchordia.com/tree/main/ventures/bidetfit
- **Governance PR:** https://github.com/pri8771/priyanshchordia.com/pull/6
- **Governance merge:** `6f4ff67886167fa5defd7f7fc1dc162e6d5137af`
- **Jira epic:** https://priyanshchordia-1779372280524.atlassian.net/browse/PCH-90
- **Notion project:** https://app.notion.com/p/3c8ab1f2276581f2a8feea94435bc7a2?pvs=204

## Synchronization inventory

- 33 canonical work items: `BF-001` through `BF-033`.
- 33 Jira child issues: `PCH-92` through `PCH-124` under epic `PCH-90`.
- 33 Notion task records with matching IDs, statuses, estimates, acceptance criteria, and Jira links.
- 12 canonical project-document records in the App Factory Notion Docs Library.
- Nine new governance/customer-operations decision mirrors: `D-009` through `D-017`.
- Complete per-item cross-links: `TRACKER_LINKS.csv`.

## Status mapping

Canonical status remains authoritative. Jira has no native Deferred state in the current workflow, so `BF-026` through `BF-028` remain To Do in Jira with explicit `deferred` labels and descriptions while the repository and Notion record `Deferred`.

Historical `BF-001` through `BF-011` were moved to Done only after canonical evidence was attached. Exact historical active hours were not measured contemporaneously and remain `Unknown / Needs Backfill`.

## Sample verification

The following samples were checked across all three systems:

- `BF-001`: historical owner authorization — Done.
- `BF-006`: public beta implementation — Done.
- `BF-009`: operator import bug and repair — Done.
- `BF-012`: governance synchronization — In Progress at link-back creation.
- `BF-018`: support mailbox — Blocked on owner mailbox/OAuth/2FA actions.
- `BF-021`: external model runtime — Blocked on provider, data, credentials, and budget approval.
- `BF-026`: authenticated customer/order lookup — Deferred.
- `BF-033`: autonomous customer operations v1 — Blocked on release gates.

## Operator evidence

After the App Factory governance merge, the external BidetFit operator completed successfully, validated the expanded mission/governance/work-item file set, verified the public status endpoint, and persisted healthy state. The current state file records `last_run_result: success` and the public site remains live.

## Conflict procedure

1. Correct the canonical repository record first.
2. Open or update a visible BF synchronization work item.
3. Update Jira lifecycle/worklog/evidence.
4. Update Notion project/task/doc/decision mirrors.
5. Update `TRACKER_LINKS.csv` and record the verification date.
6. Never silently overwrite history or infer missing actuals.
