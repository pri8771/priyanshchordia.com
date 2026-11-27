---
title: "A setting of 40,000 stopped my bots from starting. The minimum was 64,000."
slug: "the-number-i-picked"
date: "2026-11-12"
summary: "My AI assistant set the number. I run the fleet it broke."
series: "Running a company on AI agents"
status: "draft"
---

> **DRAFT.** Not yet published. This page is a working copy for review and is not indexed by search engines.

*My AI assistant set the number. I run the fleet it broke.*

I build automation and AI agent systems, and my company runs on bots. The free ones run on a local model: fourteen bot profiles share one model server that has four slots, so large requests from several bots at once can make it refuse or overflow. To protect it, my AI assistant set a limit on how much text each local bot could hold at once: 40,000.

The runtime that starts the bots has a minimum of 64,000. Below that, it does not start the bot at all.

It showed up when two research jobs had failed earlier, and my assistant relaunched them: each one exited after one second.

![the two relaunched jobs, one second each](/blog-media/the-number-i-picked/attempts.gif)

- 40,000: the cap my assistant set.
- 64,000: the least the runtime will accept.

![the two numbers side by side](/blog-media/the-number-i-picked/context.gif)

A one-second exit is an unusual symptom. A bot that fails halfway through a job is doing something wrong. A bot that fails in one second has not started doing anything. So the investigation went to the limits, not the model, and found the cap.

The fix was one number: 64,000 on every local profile. The check was one line, run on six bots, and all six started. Then the research jobs were relaunched.

The other rule from the same week is about the slots. Four slots are shared, so I run at most three local jobs at once, each in a fresh conversation, with a ledger row recording whether it left a file.

That ledger is how I can tell whether the research bot is working. For one research bot, the task log for November 23 shows four failed rows, none of which left a file. From 7:55 PM, the next fifteen rows each left a file.

I will keep the number at 64,000.

