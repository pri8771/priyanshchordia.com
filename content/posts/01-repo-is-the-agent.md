---
title: "The Repo Is the Agent: Why I Stopped Letting One LLM Own My Project"
slug: "repo-is-the-agent"
date: "2026-09-20"
summary: "If the rules, decisions, tasks, and state live in Git, changing AI models becomes a worker swap instead of a project migration."
series: "Own Your AI Stack"
status: "draft"
---

I use ChatGPT, Claude, Cursor, and Gemini. That sounds like an absurd amount of AI capacity until you actually start using them as development workers instead of occasional chatbots.

Then the limits show up everywhere.

A provider gets rate-limited. A coding tool runs out of fast requests. A long conversation accumulates too much context. A free tier is available on one service but not another. In my case, Jio currently offers eligible users an extended Google AI Pro subscription, which makes Gemini another useful pool of capacity rather than a model I need to treat as my permanent home. [Jio describes the current offer here](https://www.jio.com/google-gemini-offer/).

The obvious response is to keep buying more inference.

I think the more important response is to stop letting any one AI own the project.

## The project should survive the model

Most AI coding workflows accidentally make the conversation the source of truth.

The chat contains the requirements. The model remembers why a decision was made. The next task is buried 200 messages deep. The coding agent has a private mental model of the architecture that nobody else can see.

That works until you change models.

My preferred shape now looks more like this:

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

The code is only part of the repository. The repository also carries the operating context needed to continue the work.

That changes the relationship with the model.

ChatGPT is not the project. Claude is not the project. Cursor is not the project.

They are workers that can read the project.

## A bootstrap prompt becomes very small

If the repository carries enough state, a new session should not need a giant hand-written prompt.

A useful bootstrap can be closer to this:

```text
Pull the latest repository.

Read, in order:
1. AGENTS.md
2. docs/ARCHITECTURE.md
3. docs/PROJECT_MEMORY.md
4. docs/coordination/STATE.json
5. docs/coordination/WORK_QUEUE.md
6. unread docs/coordination/AGENT_MESSAGES.md entries

Do not infer current status from chat history.
Use repository evidence as the source of truth.
Take the highest-priority unblocked task you are authorized to perform.
Run the required tests, document what changed, and leave a handoff.
```

That prompt works whether the worker is ChatGPT, Claude, Cursor, Gemini, or something local later.

The model changes. The contract does not.

## State should be machine-readable too

Markdown is great for humans and LLMs, but some project state should be unambiguous.

For example:

```json
{
  "version": "0.4",
  "status": "verified",
  "current_goal": "complete one real end-to-end example",
  "blocked_by": [],
  "next_tasks": [
    "run live example",
    "capture evidence",
    "review failure modes"
  ]
}
```

Now a worker does not have to interpret a paragraph like "I think we are basically around v0.4."

It can read a state file.

## Handoffs become commits, not memories

Imagine Claude reaches a limit halfway through a task.

The old workflow is painful:

- summarize the conversation;
- open another tool;
- explain the project again;
- paste code;
- hope nothing important was lost.

The repo-centric workflow is closer to:

```bash
git add .
git commit -m "Checkpoint parser work and record remaining failures"
git push
```

The next worker pulls, reads the state and handoff, then continues.

The important unit is no longer the chat session.

It is the repository state.

## This makes free and paid inference more fungible

I do not mean all models are equivalent. They clearly are not.

A difficult architecture decision may deserve a stronger model. A repetitive test-writing task may not. A code review may benefit from a different model than the one that wrote the code.

Repo-centric context lets me route work by capability and available inference instead of by loyalty.

Conceptually:

```python
def choose_worker(task, capacity):
    if task.risk == "high":
        return capacity.best_reasoning_model()

    if task.kind == "implementation":
        return capacity.available_coding_worker()

    if task.kind == "review":
        return capacity.different_provider_than(task.author)

    return capacity.cheapest_available_worker()
```

That is much harder when each provider has a different private copy of the project's history.

## The repo does not magically solve memory

There is an obvious failure mode here: dumping everything into Git and assuming every model will read all of it.

That just creates a different context problem.

The repository needs structure.

Some files are durable policy. Some are current state. Some are historical decisions. Some are task-specific evidence. Old messages should become less important as canonical state is updated.

The design goal is not "store infinite context."

It is "make the minimum required context easy to recover."

## Why I think this matters beyond coding

Once the repository is the durable workspace, something interesting happens.

You can have multiple workers on multiple machines using multiple providers without needing all of them to share one chat session.

That is the next part of this series.

I am currently treating my Mac, an always-on Windows machine, and eventually local server capacity as worker hosts attached to the same projects.

If enough people want the starter structure, I will turn the repo conventions, state schema, handoff format, and bootstrap prompts into a small open-source template instead of leaving them embedded in my own projects.
