# Writing roadmap

## Season 1 — Own Your AI Stack

The through-line is simple: move durable state out of any one model or vendor, then progressively own more of the stack.

| Order | Draft | Core question |
| --- | --- | --- |
| 1 | The Repo Is the Agent | What happens when the project, not the chat session, owns context? |
| 2 | I Turned My AI Tools Into Remote Workers | How can Mac, Windows, cloud tools, and servers behave like interchangeable workers? |
| 3 | Artifact-First Development | Can implementation dependencies be replaced with explicit artifact contracts? |
| 4 | Building SwarmAI | How do you coordinate many temporary workers without turning the system into chaos? |
| 5 | Building My Own Inference Server | What changes when some inference becomes local and effectively zero-marginal-cost? |
| 6 | Building My Own ChatGPT | What does a personal model router + UI + tools + local inference look like? |
| 7 | AI Agents Don't Need to Be Brilliant | Can tests, retries, contracts, and escalation make cheaper models useful? |

All seven are public, indexable essays under `/blogs/`. Internally they remain `internal_status: working-draft` so we can keep improving screenshots, measurements, and examples without presenting a public draft badge. Public claims must still distinguish measured reality from planned work; internal draft status is not permission to invent evidence.

## Article contract

Every technical article should include:

- a concrete problem that actually happened;
- at least one architecture diagram rendered as text;
- code, configuration, or a real repository example;
- a section on what failed or what is not solved yet;
- enough implementation detail that a technical reader can reproduce the core idea;
- an explicit line between current reality and future work;
- a lightweight open-source call-to-action when a reusable component exists.

The website at `/blogs/` is the canonical copy. Substack can syndicate each essay and point back to the site/project pages. The legacy `/journal/` routes exist only as redirects.

## Parked for later

### AI + IT Mesh at Thar

A case study on combining practical AI workers with an IT-mesh style environment and existing infrastructure. Before publication, explicitly review what company details, diagrams, vendors, and operational examples are safe to share. This is not part of the first seven-post publishing batch.
