---
title: "The hand-off note said nothing was live. Four things were."
slug: "the-handoff-was-wrong"
date: "2026-11-11"
summary: "Four checker bots and a lead bot went through the note's claims; the table has a verdict beside each one."
series: "Running a company on AI agents"
status: "draft"
---

> **DRAFT.** Not yet published. This page is a working copy for review and is not indexed by search engines.

*Four checker bots and a lead bot went through the note's claims; the table has a verdict beside each one.*

I build automation and AI agent systems, and I run a small company where AI bots do the work. When I handed the company to a new AI assistant, the hand-off note said: "nothing is live for customers."

Then four read-only checker bots, with a lead bot that ran the rest of the checks, went through the claims in the note. They did it from the machine, not from the note: files on disk, the computers, the servers and the public pages. The table they produced puts a verdict next to each claim, such as verified, partly, false, not yet or not checked. The checks ran from 12:35 to 12:55 Eastern on November 23.

That line was false. The shop was live, with zero orders ever. A notes site was live with 17 articles. A small digital product was on sale. A free app was on the App Store with no ratings. The note said nothing was live. Four things were.

![The hand-off line, then what the check found live](/blog-media/the-handoff-was-wrong/hand-off.gif)

The same table had a second row. My task log is meant to record how much work each job took: tokens, calls, session. For one job it had the wrong session attached and recorded zero calls. The table's verdict on the log was three words, "False for tokens". The output files were real. The token counts next to them were not reliable.

![The log's verdict next to the files that were fine](/blog-media/the-handoff-was-wrong/task-log.gif)

Research was duller. The research bot's three jobs earlier that day had all failed with no output file, and the table marked that "not yet".

Here is the technical part. In this table, "verified" means a command or a page proved it that day. So each verified row has something you can rerun: a query against the shop's admin interface for the order count, an Apple lookup for the app, a read of the ledger for the tokens. The bots did not need to trust each other's account of what existed, only the thing itself. The table does not hold up everywhere either: some rows say they were not checked or not rerun, and the table says so.

Most of its rows came back verified. The research bot's three failed jobs are still on the list.

