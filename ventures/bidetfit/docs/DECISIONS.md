# BidetFit Decision Index

The authoritative full decision text is `../DECISIONS.md`. This index explains governance and records decisions introduced by the App Factory backfill.

## Decision policy

A decision record includes date, status, owner, context, alternatives, rationale, consequences, affected work items and docs, approval requirements, and revisit trigger. Decisions are append-only; a later decision supersedes rather than silently rewriting history.

## Existing decisions

- D-001 — Use existing GitHub Pages infrastructure.
- D-002 — Keep CommerceLint separate.
- D-003 — Select bidet/toilet compatibility.
- D-004 — Use BidetFit as the provisional brand.
- D-005 — Launch utility before affiliate applications.
- D-006 — No active merchant links before approval.
- D-007 — Split deterministic automation from model judgment.
- D-008 — Narrow the moat after competitor discovery.

## Governance and customer-operations decisions

- D-009 — Adopt App Factory Operating Standard 1.1 for every BidetFit work item.
- D-010 — Repository docs are canonical; Jira is lifecycle and control; Notion is command-center mirror.
- D-011 — Use the existing `PCH` Jira project as the BidetFit execution container and a dedicated BidetFit epic.
- D-012 — Never put raw customer email or personal data in the public repository or Jira.
- D-013 — Launch support as draft-only; auto-send only named low-risk categories after measured QA and owner approval.
- D-014 — BidetFit cannot process affiliate-merchant returns unless it becomes seller of record or receives explicit delegated API authority.
- D-015 — Use cloud mailbox polling for the zero-budget first support pilot; move to event push only when justified and authorized.
- D-016 — Open-ended unattended language work requires a separate external model runtime; a ChatGPT subscription is not treated as an API runtime.
- D-017 — A deterministic policy engine, scoped approvals, idempotency, audit receipts, and kill switches gate all external actions.
