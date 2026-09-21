---
title: "I Turned ChatGPT, Claude, Cursor and My Computers Into Remote Workers"
slug: "ai-remote-workers"
date: "2026-09-20"
summary: "Remote AI work is more interesting than remote control: give every machine a repo, a queue, a heartbeat, and a handoff contract."
series: "Own Your AI Stack"
status: "draft"
---

I do not want remote control software for my AI tools.

I want remote workers.

There is a meaningful difference.

Remote control means I open another computer and click around on it myself. A remote worker means I give a machine a project contract, it pulls the current repository, does authorized work, leaves evidence, and checks back in.

My current environment is moving toward three types of worker hosts:

```text
                     Git repository
                          │
              ┌───────────┼───────────┐
              │           │           │
             Mac        Windows      Server
              │           │           │
          ChatGPT       coding       local /
          Claude        workers      container
          Cursor                     workers
          Gemini
```

The machine is not the intelligence. It is a place where one or more workers can run.

## The repository is the coordination bus

Every worker gets the same basic rule:

```yaml
worker:
  id: windows-01
  role: implementation
  repository: current-project
  heartbeat_minutes: 15

startup:
  - git_pull
  - read_agents
  - read_project_state
  - read_work_queue
  - read_unread_messages

completion:
  - run_tests
  - record_evidence
  - update_state
  - leave_handoff
  - push_changes
```

This is deliberately boring.

That is a feature.

The more coordination can be represented as Git, files, tests, and deterministic rules, the less intelligence I have to waste on orchestration.

## A heartbeat is not "are you alive?"

The first heartbeat system I am testing is intentionally simple.

I want to know:

- did the worker check in;
- what commit is it on;
- what task does it think it owns;
- is it blocked;
- did it produce new work;
- when should I expect the next check-in?

A heartbeat can be as small as:

```json
{
  "worker": "mac-claude-01",
  "timestamp": "2026-09-20T22:30:00-04:00",
  "commit": "abc123",
  "task": "LIVE-TEST-001",
  "state": "working",
  "blocked": false
}
```

For early testing I prefer frequent heartbeats. Once I see repeated healthy check-ins, the cadence can become less aggressive.

The point is not to generate noise forever. The point is to prove that a worker can disappear from my screen without disappearing from the project.

## A worker loop can be almost embarrassingly small

The conceptual loop is:

```python
while True:
    repo.pull()

    state = repo.read_state()
    queue = repo.read_queue()

    task = claim_next_authorized_task(queue, state)

    if task:
        result = execute(task)
        verify(result)
        repo.write_handoff(result)
        repo.push()

    heartbeat.send(current_status())
    sleep(heartbeat_interval)
```

The hard parts are hidden in `execute` and `verify`, obviously.

But coordination does not have to be hidden.

## Multiple providers are useful because they fail differently

I do not want every worker to be the same model.

A coding model can implement. Another provider can review. A cheaper worker can run through mechanical tasks. A stronger model can be reserved for architecture or ambiguous failures.

Even better, a reviewer from a different provider is less likely to share exactly the same blind spots as the authoring session.

That gives me a pattern like:

```text
Plan → implement → test → independent review → accept/retry
```

The workers can live on different computers. They can even be different products.

The shared requirement is that they understand the same contracts.

## The server changes the economics later

My Dell PowerEdge R730 is interesting here because it is always-on infrastructure.

Today, I am deliberately separating this "remote workers" idea from my SwarmAI product and from local inference. I want the basic worker protocol to function before I pile on orchestration.

Later, an always-on server can host:

- queue services;
- worker containers;
- local model endpoints;
- test runners;
- artifact stores;
- monitoring;
- schedulers.

But the architecture should still work if the server is temporarily gone.

The repo is the durable layer.

## What I am testing next

The practical success criteria are not "look, I have a dashboard."

They are:

- a worker checks in without me touching its machine;
- it claims only authorized work;
- it produces a real change;
- another worker can understand the handoff;
- the system survives switching providers;
- I can reconstruct what happened from repository evidence.

Once those are boring and repeatable, then it makes sense to add smarter orchestration.

That is where SwarmAI starts to become useful.
