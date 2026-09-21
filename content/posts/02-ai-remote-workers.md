---
title: "I Turned ChatGPT, Claude, Cursor and My Computers Into Remote Workers"
slug: "ai-remote-workers"
date: "2026-09-20"
summary: "Remote AI work is more interesting than remote control: give every machine a repo, a queue, a heartbeat, and a handoff contract."
series: "Own Your AI Stack"
status: "published"
internal_status: "working-draft"
---

I do not want remote control software for my AI tools.

I want remote workers.

There is a meaningful difference.

Remote control means I open another computer and click around on it myself. A remote worker means I give a machine a bounded assignment, it pulls the current project state, does authorized work, leaves evidence, and checks back in.

That changes how I look at the computers around me.

A Mac is not just the computer I am sitting in front of. A Windows desktop is not just a second workstation. My Dell PowerEdge R730 is not just an old server.

They are potential worker hosts.

## My current mental model

The setup I am building toward looks like this:

```text
                         Git repository
                              │
                  coordination + evidence
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
         Mac               Windows              R730
          │                   │                   │
     AI sessions          coding workers      always-on
     implementation       review / tests      services
     coordination                              local inference
                                                queues
```

The machine is not the intelligence.

It is a place where one or more workers can run.

The intelligence can come from ChatGPT, Claude, Cursor, Gemini, a local model, or another provider. What makes the host useful is the protocol around the worker.

## Give every worker the same boring startup ritual

A worker should not wake up and improvise its understanding of the project.

I want a startup contract closer to:

```yaml
worker:
  id: windows-01
  role: implementation

startup:
  - fetch_current_repo
  - read_agent_rules
  - read_project_state
  - read_work_queue
  - read_unread_handoffs

before_work:
  - confirm_authority
  - confirm_branch
  - claim_one_task

completion:
  - run_required_checks
  - record_evidence
  - update_state_if_authorized
  - leave_handoff
  - push_changes
```

This is deliberately not very "AI."

That is the point.

Anything I can encode as Git, a schema, a lock, a test, or a deterministic script is something I do not need to spend model intelligence on.

## The worker loop can be simple

At the highest level:

```python
while True:
    repo.fetch()

    state = repo.read_state()
    queue = repo.read_queue()

    task = claim_next_authorized_task(queue, state)

    if task:
        result = worker.execute(task)
        evidence = verify(result)
        repo.write_handoff(task, result, evidence)
        repo.push()

    heartbeat.publish(current_status())
    sleep(current_interval())
```

Obviously, `worker.execute` is the hard part.

But the coordination loop does not have to be mysterious.

## Heartbeats turned out to be more interesting than I expected

My first heartbeat test had a very simple rule:

- check every 15 minutes;
- require three healthy scheduled check-ins in a row;
- after the system proves it can do that, relax the cadence to hourly.

The heartbeat itself can be tiny:

```json
{
  "worker": "mac-worker-01",
  "trigger": "scheduler",
  "timestamp": "2026-09-20T22:30:00-04:00",
  "commit": "abc123",
  "task": "LIVE-TEST-001",
  "state": "working",
  "blocked": false
}
```

What I wanted to prove was not just "the process is alive."

I wanted to know:

- did the scheduler really wake it;
- what commit is it working from;
- what task does it think it owns;
- is it blocked;
- did it produce anything;
- can I reconstruct what happened later?

The first implementation exposed a useful bug: a manual status update could interfere with the timing of a scheduled heartbeat and make the system look healthier than it really was.

That is exactly why I wanted the bootstrap proof.

The fix was conceptual as much as technical:

**manual activity does not count as scheduler liveness.**

Only a heartbeat that identifies itself as scheduler-triggered advances the streak.

That sounds small, but it is a good example of why autonomous systems need evidence categories. "I saw activity" is not the same claim as "the unattended scheduler works."

## A heartbeat is not a progress report

I also do not want every check-in to become a giant LLM-written status essay.

The heartbeat should answer operational questions. The handoff should answer work questions.

Those are different artifacts.

```text
heartbeat
  → "I am alive, on this commit, owning this task."

handoff
  → "Here is what changed, what passed, what failed, and what is next."
```

Keeping them separate makes the system easier to audit.

It also means a scheduler can check liveness without parsing prose.

## Multiple providers are useful because they fail differently

I do not want every worker to be the same model.

One model can implement. Another can review. A cheaper model can handle mechanical work. A stronger reasoning model can be reserved for ambiguous failures or architecture.

A useful pattern is:

```text
plan
  ↓
implement
  ↓
deterministic checks
  ↓
independent review
  ↓
accept / retry / escalate
```

When possible, I prefer the reviewer to come from a different provider than the author.

That is not because cross-provider review magically guarantees correctness. It simply reduces the chance that every step shares the exact same model-specific blind spots.

## The repository is still the coordination bus

I am intentionally resisting the urge to make a giant central brain hold everything.

If the orchestration service dies, I want another worker to reconstruct the important project state from durable evidence.

That means:

- tasks have IDs;
- artifacts have versions;
- handoffs are committed;
- acceptance criteria are inspectable;
- a worker cannot "remember" that something passed if the repository says otherwise.

This also gives me an escape hatch.

If Claude hits a limit, Cursor can pull the branch.

If the Mac goes offline, the Windows worker can still see the queue.

If I replace an orchestration tool six months from now, the project does not have to be rewritten around the old control plane.

## Where the R730 fits

The R730 is interesting because it can become the always-on part of the system.

I do not need it to be the smartest machine.

I need it to be available.

That makes it a natural place for boring infrastructure:

- queues;
- schedulers;
- worker containers;
- artifact storage;
- monitoring;
- local model endpoints;
- test runners;
- routing services.

I still want the project to remain usable when the server is unavailable. That is why Git and portable project state come first.

The server adds capacity. It should not become the only place truth exists.

## What is not solved yet

The hardest part is not SSH, remote desktop, or starting another AI session.

It is making unattended work trustworthy.

A worker that can run for an hour without me watching it needs tighter boundaries than a chatbot I am supervising interactively.

The system has to distinguish:

- a real scheduled heartbeat from a manual one;
- a claimed task from an accidentally duplicated task;
- a passing test from a complete acceptance gate;
- a model response from a material code change;
- a useful retry from an infinite loop.

I am finding that the less glamorous pieces — locks, state, evidence, retries, cancellation, leases — matter more as autonomy increases.

That observation leads directly to the next idea: [artifact-first development](/blogs/artifact-first-development/).

If workers are cheap and plentiful, the real bottleneck becomes the dependency graph.

## What I may open-source

There is a small reusable package hiding here too:

```text
worker-protocol/
├── heartbeat.schema.json
├── handoff.schema.json
├── task-claim.schema.json
├── scheduler/
│   ├── install-macos.sh
│   └── install-windows.ps1
└── examples/
    └── repo-backed-worker-loop.py
```

If the protocol survives enough real use, I would rather publish that as a boring, inspectable building block than hide it inside one giant "autonomous agent" demo.

The goal is not to make my computers look busy.

The goal is to make them produce **reconstructable, verified work without me babysitting every screen**.
