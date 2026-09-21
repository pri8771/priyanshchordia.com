# Writing roadmap

## Public batch 1 — Own Your AI Stack

The through-line is simple: move durable project state out of any one model or vendor, make workers interchangeable, then redesign work so more of it can happen safely in parallel.

| Order | Article | Core question |
| --- | --- | --- |
| 1 | The Repo Is the Agent | What happens when the project, not the chat session, owns context? |
| 2 | I Turned My AI Tools Into Remote Workers | How can Mac, Windows, cloud tools, and servers behave like interchangeable workers? |
| 3 | Artifact-First Development | Can implementation dependencies be replaced with explicit artifact contracts? |

Only these three articles belong to the current public batch and should render under `/blogs/`.

## Article contract

Every technical article should include:

- a concrete problem that actually happened;
- at least one architecture diagram rendered as text;
- code, configuration, or a real repository example;
- a section on what failed or what is not solved yet;
- enough implementation detail that a technical reader can reproduce the core idea;
- an explicit line between current reality and future work;
- a lightweight open-source call-to-action when a reusable component exists.

The website at `/blogs/` is the canonical copy. Substack can syndicate polished versions and point back to the site/project pages. The legacy `/journal/` routes exist only as compatibility redirects.

Future article ideas are intentionally kept outside this public repository until they are approved for publication.
