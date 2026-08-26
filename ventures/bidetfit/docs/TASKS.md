# BidetFit Work-Item Ledger

**Scope version:** `BF-1.1-governed-autonomy`  
**Operating standard:** App Factory Operating Standard 1.1  
**Canonical detailed data:** `WORK_ITEMS.csv`  
**Lifecycle mirror:** Jira  
**Command-center mirror:** Notion  
**Last updated:** 2026-08-25 local / 2026-08-26 UTC

This ledger backfills every substantive task, bug, decision, story, and release gate completed or identified in the BidetFit experiment. Mechanical clicks and tiny implementation steps are not split into artificial work items. Historical exact hours remain blank when durable evidence is insufficient.

## Status rules

Canonical statuses are Open, In Progress, Blocked, Deferred, and Done. Review state and deferred disposition remain separate. A work item is not Done until acceptance evidence, applicable testing, canonical documentation, Jira synchronization, and Notion synchronization are complete.

## Work items

| ID | Type | Title | Status | Priority | Estimate | Accountable | Execution | Approval |
|---|---|---|---|---|---:|---|---|---|
| BF-001 | Task | Activate the 90-day affiliate experiment and record owner constraints | Done | P0 | 1h | Priyansh | ChatGPT | Yes |
| BF-002 | Task | Audit available assets, hosting, repositories, accounts, and autonomy capabilities | Done | P0 | 2h | Priyansh | ChatGPT | No |
| BF-003 | Task | Research and score commercially viable affiliate niches | Done | P0 | 4h | Priyansh | ChatGPT | No |
| BF-004 | Decision | Select BidetFit brand, niche, positioning, and initial business thesis | Done | P0 | 1.5h | Priyansh | ChatGPT | Yes |
| BF-005 | Story | Define the MVP product, user journey, content architecture, and safety boundaries | Done | P0 | 3h | Priyansh | ChatGPT | No |
| BF-006 | Story | Build the 11-page BidetFit public beta and browser-based fit checker | Done | P0 | 8h | Priyansh | ChatGPT | No |
| BF-007 | Release Gate | Deploy BidetFit to GitHub Pages and verify critical public routes | Done | P0 | 4h | Priyansh | Automated CI | No |
| BF-008 | Story | Build the unattended six-hour operator, durable state, incident handling, and kill switch | Done | P0 | 7h | Priyansh | ChatGPT | No |
| BF-009 | Bug | Fix Python standard-library shadowing in the unattended operator | Done | P0 | 2h | Priyansh | ChatGPT | No |
| BF-010 | Bug | Fix false-negative deployment incident cleanup | Done | P1 | 1.5h | Priyansh | ChatGPT | No |
| BF-011 | Task | Research post-launch competitors and narrow BidetFit differentiation | Done | P1 | 3h | Priyansh | ChatGPT | No |
| BF-012 | Task | Adopt App Factory Operating Standard 1.1 and backfill canonical governance records | Done | P0 | 8h | Priyansh | ChatGPT | Yes |
| BF-013 | Task | Configure Search Console, analytics ownership, and indexing baseline | Open | P0 | 4h | Priyansh | ChatGPT | Yes |
| BF-014 | Task | Reverify affiliate program terms and prepare owner-ready application package | Open | P0 | 6h | Priyansh | ChatGPT | Yes |
| BF-015 | Story | Define and implement the exact toilet-model × bidet-model compatibility data schema | Open | P0 | 8h | Priyansh | ChatGPT | No |
| BF-016 | Story | Publish toilet-model identification and printable measurement/photo tools | Open | P1 | 7h | Priyansh | ChatGPT | No |
| BF-017 | Story | Design and implement Jira as the owner command and work-control plane | Open | P0 | 8h | Priyansh | ChatGPT | Yes |
| BF-018 | Task | Provision BidetFit support mailbox, aliases, authentication, and routing | Blocked | P0 | 4h | Priyansh | Human | Yes |
| BF-019 | Story | Build private support-ticket datastore, message model, and retention controls | Open | P0 | 8h | Priyansh | ChatGPT | Yes |
| BF-020 | Story | Implement cloud email intake, deduplication, threading, and queueing | Open | P0 | 8h | Priyansh | ChatGPT | Yes |
| BF-021 | Story | Connect an external model runtime for support classification and draft generation | Blocked | P0 | 8h | Priyansh | ChatGPT | Yes |
| BF-022 | Task | Define support taxonomy, approved knowledge base, response templates, and escalation matrix | Open | P0 | 8h | Priyansh | ChatGPT | Yes |
| BF-023 | Story | Implement action-risk classification, authorization, approvals, receipts, and emergency controls | Open | P0 | 8h | Priyansh | ChatGPT | Yes |
| BF-024 | Task | Run a draft-only customer-support pilot and independent quality evaluation | Blocked | P0 | 8h | Priyansh | ChatGPT | Yes |
| BF-025 | Release Gate | Enable narrowly scoped low-risk support auto-send categories | Blocked | P1 | 6h | Priyansh | ChatGPT | Yes |
| BF-026 | Story | Implement authenticated customer, account, and order lookup | Deferred | P2 | 8h | Priyansh | ChatGPT | Yes |
| BF-027 | Story | Integrate seller or merchant order, cancellation, return, and refund APIs | Deferred | P2 | 8h | Priyansh | ChatGPT | Yes |
| BF-028 | Story | Implement RMA, return-label, replacement, cancellation, and bounded refund workflows | Deferred | P2 | 8h | Priyansh | ChatGPT | Yes |
| BF-029 | Story | Build the autonomous metrics, diagnosis, experiment, and learning loop | Open | P0 | 8h | Priyansh | ChatGPT | Yes |
| BF-030 | Story | Add browser-level checker tests, accessibility checks, and synthetic production monitoring | Open | P0 | 8h | Priyansh | ChatGPT | No |
| BF-031 | Task | Implement owner notifications, escalation channels, and service health summaries | Open | P1 | 6h | Priyansh | ChatGPT | Yes |
| BF-032 | Release Gate | Complete privacy, security, legal, and commercial-policy review for autonomous customer operations | Open | P0 | 8h | Priyansh | ChatGPT | Yes |
| BF-033 | Release Gate | Launch autonomous customer operations v1 | Blocked | P1 | 8h | Priyansh | ChatGPT | Yes |

## Historical evidence and timing

BF-001 through BF-011 are retrospective work-item records grounded in the mission, diary, decision log, public source, GitHub workflows, and workflow-run evidence. Known dates are recorded. Exact active hours were not measured contemporaneously and remain `Unknown / Needs Backfill`; no exact duration is inferred from elapsed wall-clock time.

BF-012 is complete. App Factory governance was merged in PR #6, all Jira/Notion mirrors were created, permanent link-back was merged in PR #7, sample reconciliation passed, Jira and Notion were closed, and unattended operator run `32916545607` validated the merged tracker system and public site. Its exact active hours remain `Unknown / Needs Backfill` because no reliable contemporaneous duration receipt was recorded.

## Current sequencing

1. Run BF-013, BF-014, BF-015, and BF-030 in parallel where dependencies allow.
2. Implement the trusted Jira command bridge under BF-017.
3. Begin customer operations with BF-018, BF-019, BF-020, BF-022, BF-023, and BF-032.
4. Connect the external model only in BF-021 after provider, data, budget, and policy approval.
5. Run BF-024 draft-only.
6. Enable BF-025 only after measured QA and owner approval.
7. Keep BF-026 through BF-028 Deferred until BidetFit has customer accounts/orders and seller or delegated merchant authority.
8. Launch BF-033 only after every release gate passes.

## Required body

Every Jira and Notion work-item page uses:

- Objective
- Source of truth
- Current state
- Requirements
- Out of scope
- Dependencies
- Deliverable
- Acceptance criteria
- Verification evidence
- Estimates and actuals confidence
- Approval requirement
- Jira, Notion, GitHub, test, and deployment links

`WORK_ITEMS.csv` carries the canonical field-level details for all 33 records. `TRACKER_LINKS.csv` carries the permanent cross-system mappings. `WORK_ITEM_TEMPLATE.md`, `DEFINITION_OF_READY.md`, and `DEFINITION_OF_DONE.md` define future maintenance.
