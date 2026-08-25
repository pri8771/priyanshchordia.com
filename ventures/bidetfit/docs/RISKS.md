# BidetFit Risk Register

| ID | Risk | Likelihood | Impact | Current control | Next mitigation | Owner |
|---|---|---|---|---|---|---|
| R-001 | Checker produces overconfident fit advice | Medium | High | Conservative result bands and no-guarantee language | Exact-model evidence, browser tests, complaint loop | ChatGPT |
| R-002 | Site is live but not indexed or measured | High | High | Sitemap exists | Search Console and isolated analytics | ChatGPT / Priyansh |
| R-003 | Affiliate approval is delayed or denied | Medium | High | Useful non-affiliate site first | Multiple programs and exact-term ledger | ChatGPT / Priyansh |
| R-004 | Competitors make broad fit content undifferentiated | High | High | Strategy narrowed after research | Exact model pairs and difficult retrofit cases | ChatGPT |
| R-005 | GitHub schedule is delayed, disabled, or fails | Low–Medium | Medium | Run logs and incidents | Independent watchdog and owner notifications | ChatGPT |
| R-006 | External model hallucinates a customer answer | Medium | Critical | No external support model active | Approved KB, structured output, draft-only pilot, QA gates | Priyansh |
| R-007 | Prompt injection in customer email causes unauthorized action | High | Critical | No email action runtime active | Treat email as untrusted data; deterministic allowlist and policy service | ChatGPT / Security Review |
| R-008 | Raw PII leaks into public GitHub, Jira, or logs | Medium | Critical | No support ingestion active | Private ticket store, redaction, secret scanning, retention policy | Priyansh |
| R-009 | Duplicate event causes duplicate email, RMA, or refund | Medium | Critical | No commerce actions active | Idempotency keys, action receipts, compensation tests | ChatGPT |
| R-010 | BidetFit attempts a return it does not legally control | Medium | Critical | Affiliate-only business model documented | Route to merchant unless explicit seller/API authority exists | Priyansh |
| R-011 | API or model runtime violates zero-budget rule | Medium | High | No runtime connected | Verify free limits or seek approval; enforce budget kill switch | Priyansh |
| R-012 | Support reply creates legal, safety, or contractual commitment | Medium | Critical | No auto-send | Category denylist, approved templates, owner escalation | Priyansh |
| R-013 | Customer identity is insufficient for account or order action | High | Critical | No accounts or orders | Authenticated lookup and failed-verification privacy controls | Priyansh |
| R-014 | Jira task text is treated as executable code | Medium | Critical | No bridge exists | Trusted project/user checks, task schema, no shell interpolation | ChatGPT |
| R-015 | Notion, Jira, and repository drift | Medium | High | Repo-first doctrine | Sync receipts, conflict issue, checkpoint validation | ChatGPT |
| R-016 | Historical effort is misrepresented | Medium | Medium | Exact hours left blank | Backfill only from reliable evidence; mark confidence | ChatGPT |
