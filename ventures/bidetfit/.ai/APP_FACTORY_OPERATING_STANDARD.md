# BidetFit App Factory Operating Standard Adapter

**Pinned standard:** App Factory Operating Standard 1.1  
**Owner:** Priyansh Chordia  
**Project:** BidetFit  
**Scope version:** `BF-1.1-governed-autonomy`

This version-pinned adapter makes the central App Factory rules operational inside BidetFit. It does not replace the central standard.

## Authority

- Repository documentation and evidence are canonical.
- Notion is the project and portfolio command center and planning mirror.
- Jira is the executable work queue, status, dependency, worklog, approval, and discussion record.
- GitHub owns source, branches, commits, pull requests, CI, deployment, and technical evidence.
- Chat is non-canonical until captured.

## Lifecycle

Canonical statuses are Open, In Progress, Blocked, Deferred, and Done. Review state and deferred disposition are separate.

## Required work items

Every actionable or unresolved Epic, Story, Task, Subtask, Bug, Decision, Discussion, Risk, Change Request, or Release Gate receives one stable work-item record. Required fields and body are implemented in `docs/WORK_ITEM_TEMPLATE.md`.

## Ready and Done

Use `docs/DEFINITION_OF_READY.md` and `docs/DEFINITION_OF_DONE.md`. No evidence, no Done.

## Task sizing

Every active item has an estimate. Work expected to exceed eight active hours must be split where the split creates independently verifiable deliverables, distinct dependencies, separate reviewers, or safer execution. Do not create artificial subtasks for tiny mechanical steps.

## Prompt and model provenance

Substantive prompts receive stable `PRM-BF-` IDs and are stored under `docs/prompts/`, indexed in `docs/PROMPT_LOG.md`, and linked to the authorizing work item, source versions, provider/model where available, tools, artifacts, and evidence. Never overwrite a sent prompt; append a revision.

## Maintenance

Checkpoint documentation after two or three meaningful instructions, after implementation or bug repair, after architecture or strategy decisions, before commits and pull requests, before Done, and at session end. Preserve history and state uncertainty honestly.
