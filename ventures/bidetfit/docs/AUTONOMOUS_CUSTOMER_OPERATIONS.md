# BidetFit Autonomous Customer Operations Architecture

**Work items:** BF-017 through BF-033  
**Status:** Target architecture; no live customer-response or return automation exists  
**Scope version:** `BF-1.1-governed-autonomy`  
**Last updated:** 2026-08-25

## Goal

Reach a state where Priyansh’s laptop and this chat can be closed while:

- A customer emails BidetFit.
- A cloud system receives and threads the message.
- The request is classified against approved policy and knowledge.
- A safe response is drafted or sent.
- High-risk work is escalated to Priyansh with an exact approval packet.
- Every decision, message, and action is auditable.
- If BidetFit later owns or is delegated order authority, an eligible return can be processed idempotently within approved limits.

## Current truth

Today, BidetFit is an anonymous static affiliate-information site. It has no customers, accounts, orders, support inbox, private datastore, external model runtime, or return/refund authority. The existing GitHub Actions operator verifies site and repository health only.

A buyer referred to a merchant purchases from that merchant. BidetFit cannot cancel, return, replace, or refund that merchant’s order merely because an affiliate link was involved. Until explicit seller or delegated merchant authority exists, support can explain general guidance and route post-purchase requests to the merchant.

## Target components

### 1. Project support identity

Create a legitimate `support` or `help` alias under an authorized non-Primandir domain. Enable 2FA, owner recovery, and minimum required OAuth scopes. Store credentials in managed secret storage, never in chat, GitHub, Jira, or Notion.

### 2. Cloud mailbox intake

Zero-budget first pilot:

- A Google Apps Script cloud time trigger polls the mailbox every few minutes.
- It reads new messages or an intake label.
- It emits an idempotent event keyed by Gmail message and thread ID.
- It ignores loops, bounces, spam, and already-processed messages.
- It writes only to private storage and a private queue.

Later, if latency or scale requires it, use Gmail API mailbox watch and an approved event-delivery service. The watch must be renewed and monitored.

### 3. Private ticket and event store

Store:

- Ticket ID and status.
- Gmail thread and message references.
- Customer identity state.
- Sanitized category and summary.
- Raw message content in a private encrypted store.
- Approved knowledge and policy versions used.
- Model, provider, prompt, and execution receipt.
- Proposed and executed actions.
- Owner approvals and expiry.
- Response and send receipt.
- Retention, export, and deletion state.

Jira receives only redacted work summaries and references. Raw customer content and order data remain private.

### 4. Deterministic pre-classifier

Before any model call:

- Detect obvious spam, bounces, duplicate messages, and system notifications.
- Identify possible privacy, legal, safety, security, complaint, chargeback, and financial categories.
- Mark untrusted instructions and links.
- Apply a default-deny or owner-review tier for sensitive categories.
- Limit the data sent to the model.

### 5. External model runtime

An API-accessible model or authorized agent runtime is required because this ChatGPT conversation cannot wake itself. The worker receives a narrow structured packet and returns:

- Category.
- Confidence.
- Required identity level.
- Relevant approved knowledge citations.
- Missing information.
- Draft response.
- Proposed external action.
- Risk class.
- Escalation reason.

The model never receives direct unrestricted Gmail, payment, merchant, shell, or Jira authority. A deterministic executor decides what is allowed.

### 6. Approved knowledge base

Version and approve:

- What BidetFit is and is not.
- Fit-checker methodology and limitations.
- Measurement and exact-model guidance.
- Affiliate and sponsorship disclosure.
- Privacy and data-handling policy.
- Complaint and correction process.
- Merchant-return routing.
- Support tone and uncertainty language.
- Identity and escalation requirements.
- Incident notices and known issues.

A model must answer from these sources or say that it cannot verify the answer.

### 7. Action-risk policy

| Tier | Examples | Default behavior |
|---|---|---|
| 0 | Spam, bounce, duplicate | Close or suppress deterministically |
| 1 | Public FAQ, link to measurement guide, acknowledgment | Draft; later eligible for approved auto-send |
| 2 | Fit interpretation with missing information, content correction | Draft with evidence; human review during pilot |
| 3 | Account/order lookup, cancellation request, RMA preparation | Identity verification and policy engine; normally owner approval |
| 4 | Refund, payout, legal/privacy determination, chargeback, deletion, destructive change | Block and require exact scoped owner approval |
| 5 | Unsupported, ambiguous, security incident, suspected abuse | Stop, preserve evidence, escalate |

Unclassified actions default to deny or owner approval.

### 8. Authorization and approval

Every external action is evaluated using:

- Actor and service identity.
- Project and environment.
- Ticket and customer identity state.
- Action type and target.
- Data class.
- Reversibility.
- Financial amount.
- Policy version.
- Idempotency key.
- Approval token bound to exact payload hash, scope, amount, expiration, and approver.

The AI cannot grant its own approval or weaken the evaluator.

### 9. Outbound response path

Phase 1 is draft-only. The system saves a Gmail draft and alerts Priyansh.

Phase 2 auto-sends a named list of low-risk categories only after a measured pilot, exact template and prompt approval, confidence threshold, and canary.

Phase 3 adds account-specific actions after authenticated lookup and additional policy gates.

Any complaint, low confidence, unsupported fact, repeated contact, or guardrail breach disables auto-send for that ticket and routes it to the owner.

### 10. Return and refund path

Only after seller or delegated authority exists:

1. Verify customer identity.
2. Resolve the exact order.
3. Load the policy version in force for the purchase and request.
4. Evaluate window, item, condition, geography, merchant, fees, and exceptions.
5. Produce a structured eligibility decision with evidence.
6. Require owner approval where policy or amount requires it.
7. Use an idempotency key to create one cancellation, RMA, label, replacement, or refund.
8. Update order and ticket state only after the external system confirms success.
9. Handle partial failure with compensation or escalation.
10. Send the customer an accurate receipt and next steps.
11. Reconcile the transaction and any affiliate commission reversal.

Until this exists, BidetFit routes the customer to the seller and does not imply that it processed the return.

## Jira and Notion control

Jira holds owner directives and executable work, dependencies, approval gates, comments, worklogs, incidents, and evidence. A secure bridge reads only trusted BidetFit issues in an authorized state. Issue text is data, never interpolated into shell commands. Each execution receipt binds Jira key, source SHA, prompt and template versions, actual model, tools, tests, and outcome.

Notion is the project command center and planning or knowledge mirror. The repository remains canonical if facts conflict.

## Observability and learning

Collect:

- New messages, queue latency, first response, resolution, reopen, escalation, and owner-review time.
- Category, confidence, missing-information rate, citation coverage, human edit distance, and critical-error rate.
- Auto-send canary size, complaints, corrections, and disable events.
- Return eligibility, action success, duplicate suppression, partial failures, refunds, reversals, and cash impact.
- Cost and quota by provider and action.

Pre-register experiments. Do not promote a prompt, template, routing rule, or auto-send category until a fixed evaluation and guardrail threshold passes. Preserve negative evidence and roll back harmful changes.

## Failure and recovery

- Global, mailbox, model, auto-send, merchant-write, and financial kill switches.
- Retries with backoff for transient failures.
- Dead-letter queue for permanent failures.
- Idempotency for every external write.
- Owner alert after bounded retries.
- Immutable execution receipts.
- Daily reconciliation of sent messages and external actions.
- Tested recovery and rollback runbook.

## Phased rollout

### Phase 0 — Governance

Complete BF-012 and BF-017. No customer automation.

### Phase 1 — Draft-only support

Complete BF-018 through BF-024. Mail arrives while the laptop is off; the system classifies and creates a draft, but Priyansh approves every send.

### Phase 2 — Low-risk auto-send

Complete BF-025 after human approval and measured pilot thresholds.

### Phase 3 — Account-aware support

Complete BF-026 only after BidetFit has real accounts or orders or delegated access.

### Phase 4 — Returns and bounded financial actions

Complete BF-027 and BF-028 only with legal or merchant authority, exact policy approval, identity verification, idempotency, audit, and financial limits.

### Phase 5 — Autonomous learning

BF-029 proposes and executes bounded experiments through Jira and pull-request gates; no self-modifying success criteria or authority.

## Owner actions required

- Create and authorize the support alias and mailbox.
- Complete OAuth, 2FA, and recovery.
- Approve the external model provider/runtime and any separate API budget.
- Approve exact support policy, external commitments, auto-send categories, and canary limits.
- Complete merchant or store agreements and API access.
- Define return and refund limits if direct commerce is introduced.
- Approve privacy, security, legal artifacts and the exact production release.

## Launch criteria

Customer operations v1 does not launch until BF-018 through BF-025 and BF-029 through BF-032 are complete, the laptop-off end-to-end test passes, high-risk escalation is proven, no raw PII appears in public systems, the kill switch is tested, and the owner approves the exact release.
