---
title: "My AI got 30 of 30. Then there was the README."
slug: "fake-rsi-easy-test"
date: "2026-11-13"
summary: "I asked for a self-improving system. Its own README says the test is too easy."
series: "Running a company on AI agents"
status: "draft"
---

> **DRAFT.** Not yet published. This page is a working copy for review and is not indexed by search engines.

I asked for a self-improving system. Its own README says the test is too easy.

I build automation and AI agent systems, and on Nov 21 I drew up a plan for one that could change how it works and then make a case for keeping the change. The case had to include a better score. I also wanted to be able to swap out the model doing the work without having to draw up another plan.

On Nov 23 I put it this way in the owner decisions log.

> And don't forget, this entire system should be set up as a model agnostic fake RSI system.

RSI stands for recursive self-improvement. I call my version fake. The things it can change are fairly ordinary. A bot can get different instructions, a different skill, different settings or a different model. I can also change which bot gets the work. The interesting part of the blueprint was what would happen *after* a change. Something still had to decide whether to keep it.

For the model part, the first version has a table. Each role has a model listed beside it, and that entry is the one place where the choice lives. To try a different model in the same role, I change one line. The role stays put. That makes the comparison a fairly specific one. I can see how each model scored doing that particular job.

![The role stays the same as the model entry changes.](/blog-media/fake-rsi-easy-test/role-table.gif)

For the grading part, I specified a sealed test. A bot that can read the test while it edits its own instructions can get very good at those particular tasks. Under the rule I wrote, the tasks live somewhere the bots can neither read nor write. A change earns its place only if the score goes up and every safety check holds or improves.

The first version was built that day. It had the table, a small sealed task set for one role and a script that scores a role on a given model. I had a test and a rule that required the score to rise. The local model scored 30 of 30. No room there.

The Grok model scored 29 of 30. That was one run each. The system's own README says the test set is too easy.

![The local and Grok scores appear, followed by the README’s assessment of the test set.](/blog-media/fake-rsi-easy-test/test-results.gif)

The independent audit that day had a slightly different job. It was checking how much of the blueprint actually existed. Its verdict in the verification file was “Partly”. The auditor found the role table and the script for applying a change. The sealed task set sits in a documents folder, and the auditor did not check it. So the score is on record. Whether the bots could get at the tasks was still an open item in that audit.

The next step is a harder test set.

