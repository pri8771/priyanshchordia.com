---
title: "Building SwarmAI: What Happens When 50 AI Workers Share One Project?"
slug: "building-swarmai"
date: "2026-09-20"
summary: "SwarmAI is my attempt to coordinate large numbers of temporary AI workers around shared state, contracts, tests, and evidence."
series: "Own Your AI Stack"
status: "draft"
---

Most agent frameworks start by defining a small team.

Give one agent a researcher role. Another is the developer. Another is the reviewer. Connect them in a workflow.

I am interested in a different question:

What if the number of workers is not five, but fifty?

That is the experiment behind SwarmAI.

It is under active development, not a claim that I already have a production-ready hundred-agent system.

## The unit should be work, not personality

I do not want to begin by inventing fifty permanent personas.

I want a task to describe the capability it needs:

```yaml
task:
  id: parser-042
  goal: "Handle multi-line purchase-order items"
  risk: medium

requires:
  capabilities:
    - python
    - parsing
    - tests

inputs:
  - artifact: ocr-order-v2
  - file: docs/PARSER_CONTRACT.md

outputs:
  - code
  - tests
  - evidence

review:
  independent_provider: true
  max_retries: 2
```

The runtime can decide what worker is available.

Claude today. Cursor tomorrow. A local model later. Multiple temporary workers if the task benefits from exploration.

## A swarm needs constraints more than it needs enthusiasm

Spawning agents is easy.

Preventing fifty agents from creating fifty incompatible realities is the actual problem.

The coordination layer needs things like:

- explicit task ownership;
- immutable or versioned contracts;
- shared repository state;
- conflict detection;
- test gates;
- review gates;
- retry budgets;
- cost limits;
- authority boundaries.

Conceptually:

```python
def run_task(task):
    worker = scheduler.assign(task)

    candidate = worker.execute(task)

    if not tests.pass_for(candidate):
        return retry_or_escalate(task, candidate)

    reviewer = scheduler.assign_reviewer(
        task,
        exclude_provider=worker.provider,
    )

    verdict = reviewer.review(candidate)

    if verdict.accepted:
        return merge(candidate)

    return retry_or_escalate(task, verdict)
```

The intelligence is only one component.

## Why not just use a giant permanent crew?

Permanent teams are useful when roles themselves carry durable context.

I want SwarmAI to also handle disposable capacity.

A project may need ten implementation workers for an hour, two research workers for five minutes, and one expensive reasoning model only when the cheap workers disagree.

That suggests a scheduler instead of a fixed org chart.

```text
goal
 ↓
decomposition
 ↓
artifact graph
 ↓
task queue
 ↓
worker pool
 ↓
tests + reviewers
 ↓
accepted artifacts
```

## The repository remains the common ground

SwarmAI is not supposed to replace the repo-centric workflow from the first article.

It depends on it.

If a SwarmAI controller dies, I want another controller to reconstruct project state from durable evidence.

The swarm should be able to stop and restart without losing the project.

That means the control plane can be smart, but the state cannot live only inside the control plane.

## Eventually, SwarmAI should help build SwarmAI

This is one of the milestones I care about most.

At some bootstrap point, the runtime should be capable of accepting bounded work on its own repository:

```text
SwarmAI issue
   ↓
SwarmAI decomposes work
   ↓
workers implement isolated artifacts
   ↓
tests + external review
   ↓
human-controlled acceptance gate
```

That is not permission for uncontrolled self-modification.

It is a test of whether the system is useful enough to consume its own abstractions.

## Product or personal experiment?

I want both layers to remain separate.

My own deployment can be opinionated and messy. It can know about my computers and providers.

SwarmAI the product should be reusable.

Built-in capabilities should be clearly separated from optional integrations and from my personal infrastructure.

If I open-source the bootstrap version, that boundary matters more than the number of agents in the demo.

The interesting benchmark is not "I spawned 100 agents."

It is whether adding workers actually decreases time-to-verified-artifact without multiplying errors faster than output.
