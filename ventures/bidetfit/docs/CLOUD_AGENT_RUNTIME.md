# BidetFit Autonomous Cloud Runtime

**Work item:** BF-034  
**Jira:** PCH-127  
**Notion:** https://app.notion.com/p/3c8ab1f2276581a1bef8fbbecbcff5c6?pvs=204  
**Status:** Open — architecture selected; owner cloud and credential actions pending  
**Last updated:** 2026-08-26

## Goal

Provide a durable execution environment that can wake on schedules and trusted events while Priyansh's laptop and this ChatGPT conversation are closed. It must collect analytics, inspect the approved Jira queue, conduct bounded research, propose code and content changes, run tests, open pull requests, verify deployments, record evidence, and escalate owner-only actions.

“24×7” means continuously available and event-driven, not an expensive stateful process that consumes compute while idle.

## Current state

- GitHub Pages hosts the public site.
- GitHub Actions runs the deterministic BidetFit operator every six hours.
- The operator validates state, governance, schemas, and public health.
- No external model runtime is connected.
- Jira does not yet trigger executions.
- Search Console and behavioral analytics are not connected.
- The current operator does not write substantive code or content.

## Two deployment paths

### Path A — strict zero-budget pilot

Use the existing public GitHub repository and free cloud surfaces:

- GitHub Actions as disposable compute.
- Scheduled Jira polling plus manual or validated repository-dispatch events.
- Google Search Console and GA4 APIs for metrics.
- A free-tier model API only for public or redacted information whose provider terms permit the use.
- GitHub branches, pull requests, checks, preview deployment, and production verification.
- Google Apps Script later for low-volume Gmail intake and draft creation.
- GitHub secrets for non-customer OAuth/API credentials; no raw customer data in the repository or logs.

Advantages: no card or billable Google Cloud project.  
Limitations: schedules may be delayed; polling is not instant; state is awkward for private customer data; free model quotas and data-use terms may be unsuitable for sensitive support; no continuously available authenticated webhook endpoint.

### Path B — robust event-driven runtime

Use a dedicated Google Cloud project:

- Cloud Run service for authenticated Jira, GitHub, Gmail, and internal webhooks.
- Cloud Run Jobs for bounded analytics, research, browser testing, and code-update runs.
- Firestore for private task, lease, checkpoint, approval, policy-version, and execution-receipt state.
- Pub/Sub and/or Cloud Tasks for durable queueing, retries, deduplication, and dead-letter handling.
- Cloud Scheduler for health, analytics, editorial queue, and decay runs.
- Secret Manager for OAuth and API credentials.
- Cloud Logging, Error Reporting, monitoring, and alerts.
- A private GitHub App installed only on the required repository.
- Jira as owner command plane.
- A separately authorized model API for open-ended reasoning.

Advantages: real webhooks, private durable state, stronger identity and access control, reliable event handling, better observability, and a direct path to customer operations.  
Constraint: Google Cloud requires a linked billing account even when services remain in their free tiers. This is an owner-approved exception to the original no-card rule and does not authorize actual spending.

## Selected rollout

1. Build Path A immediately for analytics and Jira-to-PR automation where no sensitive data is involved.
2. Prepare Path B infrastructure as code and a no-op vertical slice.
3. Ask the owner once for Google Cloud project, billing linkage, OAuth, GitHub App installation, and model credentials.
4. Deploy Path B only after explicit approval and cost controls.
5. Keep Path A as fallback and independent health monitor.

## Event-driven architecture

```text
Jira / GitHub / Scheduler / Analytics / Gmail
                  |
                  v
        authenticated event intake
                  |
                  v
       event validation + idempotency
                  |
                  v
       durable queue and task record
                  |
                  v
        lease-based bounded worker
          |               |
          |               +--> deterministic tools
          +--> approved model API
                  |
                  v
       policy and authorization gate
                  |
       +----------+-----------+
       |                      |
       v                      v
branch / PR / report     owner approval or block
       |
       v
 tests -> preview -> merge policy -> deploy -> verify
       |
       v
 Jira + Notion + GitHub + diary execution receipt
```

## Autonomy loop

Every execution must:

1. Read `MISSION.md`, `STATE.json`, task, decisions, risks, and current kill switches.
2. Validate the event source, actor, project, status, signature, timestamp, and replay key.
3. Create or load one durable task.
4. Acquire a lease so only one worker performs it.
5. Check dependencies, owner approvals, budget, model quota, and data classification.
6. Run deterministic collection and validation before model reasoning.
7. Give the model a bounded structured packet and allowed-action list.
8. Validate structured output and citations.
9. Create a branch and pull request, never an unrestricted direct push to production.
10. Run tests, security checks, browser tests, and preview verification.
11. Apply the approved merge/deploy policy.
12. Verify production and roll back or open an incident on failure.
13. Write an immutable execution receipt and update Jira, Notion, metrics, decisions, and diary.
14. Release the lease and schedule the next eligible action.

## Code authority

The GitHub App receives minimum repository permissions only:

- Read metadata and canonical source.
- Create branches and commits.
- Open and update pull requests.
- Read/write selected issues or checks for receipts.
- No organization administration.
- No repository deletion or transfer.
- No secret reading.
- No branch-protection bypass.

The first release cannot merge its own pull request. Later, low-risk changes may auto-merge only after tests, a canary, and an explicitly approved policy.

## Analytics and learning

Scheduled collectors retrieve:

- Search Console queries, pages, impressions, clicks, CTR, position, country, and device.
- GA4 sessions and approved behavioral events.
- Affiliate clicks, transactions, approval, reversals, and cash received where APIs or exports exist.
- Site health, browser tests, broken links, content age, and merchant changes.
- Jira throughput, failed work, owner-review latency, and automation cost.

The runtime first applies deterministic diagnosis rules, then asks the model to propose a hypothesis and bounded work item. Every experiment has a baseline, metric, guardrails, evidence threshold, evaluation period, stop rule, and rollback. Insufficient evidence stays insufficient.

## Cost and resource controls

Pilot defaults:

- Cloud Run minimum instances: 0.
- Cloud Run maximum instances: 1.
- Worker concurrency: 1 until code is proven reentrant.
- Short request timeouts; long work uses Cloud Run Jobs.
- Daily task, model-token, web-search, and deployment quotas.
- Provider-side project spend cap where supported.
- Cloud Billing budget notifications and a programmatic kill switch.
- Global, model, code-write, deployment, email, merchant-write, and financial kill switches.
- No paid model fallback unless separately approved.
- No use of collected revenue beyond the authorized rolling 24-hour cap.

## Data boundaries

- Public code and public research may use an approved free model tier.
- Customer email, identity, orders, and private analytics remain in private storage.
- A free model tier that permits provider training is not used for raw customer or confidential data.
- Jira and Notion receive sanitized summaries and receipts, not raw PII.
- Secrets are stored in managed secrets and never printed.
- External content is untrusted data and never interpolated into commands.

## First vertical-slice acceptance test

1. Priyansh moves a trusted Jira test task to `Ready for Agent`.
2. The event is authenticated and deduplicated.
3. Exactly one task is stored and leased.
4. The worker reads canonical BidetFit state from GitHub.
5. It fetches the public `status.json` and performs no other side effect.
6. It writes an execution receipt to private state and a sanitized Jira comment.
7. Replaying the same event does not repeat the action.
8. Disabling the global kill switch blocks a second test.
9. Logs contain no credentials or PII.
10. The laptop remains off throughout the test.

## Owner actions

The owner must:

- Create or approve the dedicated Google Cloud project.
- Explicitly authorize linking a billing account if Path B is used.
- Configure account recovery and 2FA.
- Approve project-level cost controls and the no-spend policy.
- Register and install the private GitHub App.
- Authorize Jira webhook/API access.
- Approve Search Console and GA4 access.
- Select and authorize a model provider and credentials.
- Later authorize the BidetFit support mailbox and Gmail scopes.

All other implementation, testing, documentation, and bounded operational decisions can be executed under the existing autonomy mandate.
