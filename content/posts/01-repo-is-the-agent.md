---
title: "The Repo Is the Agent: Why I Stopped Letting One LLM Own My Project"
slug: "repo-is-the-agent"
date: "2026-09-20"
summary: "If the rules, decisions, tasks, and state live in Git, changing AI models becomes a worker swap instead of a project migration."
series: "Own Your AI Stack"
status: "published"
internal_status: "working-draft"
---

I use ChatGPT, Claude, Cursor, and Gemini. Some of that capacity is paid, some is bundled, and some is promotional. Jio, for example, currently advertises an [18-month Google AI Pro offer for eligible 5G users](https://www.jio.com/google-gemini-offer/), which makes Gemini another useful pool of capacity for me.

And I still run out of inference.

That sounds ridiculous until the AI tools stop being occasional chatbots and start acting like development workers. One session is planning. Another is implementing. Another is reviewing. A long-running conversation accumulates too much context. A coding tool hits a usage limit. A provider throttles. A "free" source is available, but only in a different product.

The obvious response is to buy more AI.

My response has increasingly been: **stop letting any one AI own the project.**

If the project survives the model, then changing models is not a migration. It is a worker swap.

## The failure mode: the chat becomes the database

A lot of AI coding workflows quietly make the conversation the source of truth.

The requirements are in the chat. The reason for a design decision is in the chat. The next task is somewhere 180 messages back. The model has a private mental picture of the architecture that nobody else can inspect.

That works until the session ends or I switch providers.

Then the handoff looks like this:

- summarize the project;
- paste a pile of files;
- explain the current branch;
- repeat the rules;
- explain which bugs are real and which were already fixed;
- hope the new model does not reinterpret the whole thing.

That is exactly the wrong place for durable project state.

The better shape, for me, is a repository that carries not just code but the minimum operating context required to continue the work.

```text
repository/
├── AGENTS.md
├── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── PROJECT_MEMORY.md
│   ├── DECISIONS.md
│   └── coordination/
│       ├── STATE.json
│       ├── WORK_QUEUE.md
│       └── AGENT_MESSAGES.md
├── src/
└── tests/
```

The exact filenames are not important. The separation is.

- `AGENTS.md` says how a worker is allowed to operate.
- architecture docs explain durable structure.
- memory explains decisions that are easy to lose.
- `STATE.json` says what is true now.
- the queue says what is next.
- messages preserve handoffs that have not yet been folded into canonical state.
- tests encode as much "done" as can be made deterministic.

Now ChatGPT is not the project. Claude is not the project. Cursor is not the project.

They are workers that can read the project.

## A new session should need a small bootstrap prompt

A useful test is this:

**How much do I have to explain when I open a brand-new session?**

If the answer is "twenty minutes of project history," the repo is missing context.

A healthy bootstrap can be closer to:

```text
Pull the latest repository.

Read, in order:
1. AGENTS.md
2. docs/ARCHITECTURE.md
3. docs/PROJECT_MEMORY.md
4. docs/coordination/STATE.json
5. docs/coordination/WORK_QUEUE.md
6. unread coordination messages

Do not infer current project state from this chat.
Use repository evidence as the source of truth.

Take only work you are authorized to perform.
Run the required checks.
Record evidence.
Leave a handoff before you stop.
```

That is intentionally boring.

The prompt is not trying to re-create the entire project in natural language. It tells the worker **where truth lives**.

The same bootstrap pattern can work in ChatGPT, Claude, Cursor, Gemini, a local model, or something I have not started using yet.

The model changes. The project contract does not.

## Make current state machine-readable

Markdown is great for people and LLMs. Some project state should still be explicit enough that nobody has to interpret prose.

A small state file can do a lot:

```json
{
  "version": "0.4",
  "status": "implementation_complete_acceptance_pending",
  "current_goal": "complete one real end-to-end example",
  "blocked_by": [],
  "next_tasks": [
    "run live example",
    "capture evidence",
    "review failure modes"
  ]
}
```

That is better than a sentence like:

> I think we are basically done with 0.4, except maybe the live test.

The state file forces me to choose what I actually mean.

It also makes automation easier. A worker can parse the state. A heartbeat can report it. A scheduler can decide whether there is unblocked work. A reviewer can compare a claimed milestone with the artifacts that are supposed to prove it.

## Handoffs become repository events, not memories

Suppose Claude is halfway through a parser and hits a limit.

The old handoff is another summary.

The repo-centric handoff is:

```bash
git add .
git commit -m "Checkpoint parser work and record remaining failures"
git push
```

Then the worker leaves a short structured note:

```yaml
task: parser-042
state: review-needed
changed:
  - src/parser.py
  - tests/test_parser.py
evidence:
  - "41 parser tests passed"
remaining:
  - "one multi-line fixture still fails"
do_not_assume:
  - "customer matcher behavior was not reviewed"
```

The next worker pulls the same branch, reads the same contract, sees the same failing fixture, and continues.

The important unit is no longer the chat session.

It is the **repository state**.

## This makes inference more fungible

I do not mean that all models are equivalent. They are not.

Some work deserves the strongest reasoning model I have. Some work is mechanical. Some review is more useful when it comes from a different provider than the one that wrote the code.

Once context is portable, I can route work by capability and available capacity instead of by provider loyalty.

Conceptually:

```python
def choose_worker(task, capacity):
    if task.risk == "high":
        return capacity.best_reasoning_model()

    if task.kind == "implementation":
        return capacity.available_coding_worker()

    if task.kind == "review":
        return capacity.different_provider_than(task.author)

    return capacity.cheapest_qualified_worker()
```

The key word there is `qualified`.

A free model is not useful just because it is free. It has to be good enough for the bounded task and the output still needs verification.

## The repo does not solve context by itself

There is an easy way to ruin this idea: dump everything into Git and tell every model to read all of it.

That is just a context window problem with folders.

The repository needs hierarchy.

I think of the information in roughly four layers:

```text
durable rules
    ↓
architecture + decisions
    ↓
current machine-readable state
    ↓
task-specific evidence and handoffs
```

Old handoff messages should become less important as canonical state gets updated. Historical notes should not outrank current contracts. A worker should not need to read six months of logs to understand what it can do today.

The goal is not "store infinite context."

The goal is **make the minimum required context recoverable**.

## The bigger idea: the repo becomes the operating environment

This started as a way to switch between AI tools without losing my place.

It is becoming something bigger.

Once the repository contains enough durable context, I can have multiple workers on multiple machines using multiple providers without requiring them to share a single conversation.

My Mac can host one worker. A Windows machine can host another. A server can run local inference or background workers. They can all pull the same project contracts and leave evidence in the same place.

That is the next article in this series: [how I am turning AI sessions and computers into remote workers](/blogs/ai-remote-workers/).

## What I may open-source

If this pattern is useful to other people, the first thing I would open-source is not a giant agent framework.

It would be a tiny repo starter:

```text
AGENTS.md
docs/
  PROJECT_MEMORY.md
  ARCHITECTURE.md
  coordination/
    STATE.schema.json
    STATE.json
    WORK_QUEUE.md
    HANDOFF.template.md
scripts/
  validate_state.py
```

That is enough to make the experiment reproducible without forcing anyone to adopt my entire stack.

If there is interest, I will turn the conventions I am using into a clean starter repository and link it here.

The model should be replaceable.

The project should not be.
