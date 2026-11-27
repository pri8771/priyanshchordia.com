---
title: "My research bots cited 15 DOIs. Four were the paper they said."
slug: "three-of-fifteen-citations"
date: "2026-11-19"
summary: "The checker also needed checking. Its mistake did not improve the result."
series: "Running a company on AI agents"
status: "draft"
---

> **DRAFT.** Not yet published. This page is a working copy for review and is not indexed by search engines.

*The checker also needed checking. Its mistake did not improve the result.*

My research bots wrote two summaries for my company's public research library on November 23. Pricing psychology at 1:31 PM EST, then what drives ad click-through at 1:35 PM EST. Together they cited 15 DOIs, the identifiers attached to papers so you can find the research behind a claim.

There was research behind some of the identifiers. It was just different research.

Before putting the library online, a 29-line Python script asked Crossref's free public API whether each DOI existed and whether the title attached to it matched the title in our file. Standard library only. My public research library was being inspected by something shorter than this post.

The results:

- Ad summary: 10 cited, 6 with a Crossref record, 2 title matches.
- Pricing summary: 5 cited, 3 with a Crossref record, 2 title matches.
- Together: 4 of 15.

Nine identifiers had records. That was the more encouraging count, provided I stopped reading before finding out what they identified.

One citation was titled:

> Choice Based Reasons to Prefer the Options We Do

Crossref had that DOI under:

> Heaven on Earth: Consumption at Heritage Village, USA

![two cited titles, each followed by the title Crossref holds for that DOI](/blog-media/three-of-fifteen-citations/cited-vs-crossref.gif)

Another cited title was:

> Word of Mouth and Interpersonal Communication: A Review and Directions for Future Research

The DOI belonged to:

> Decision Difficulty in the Age of Consumer Empowerment

The identifiers were doing their job. My summaries had given them other jobs.

Checking that a DOI resolves is not enough: a made-up citation can borrow a real DOI. The script used `api.crossref.org/works/<doi>`, free and requiring no key, to compare titles. It took the words longer than three letters in Crossref's title and counted a match if at least half appeared in the 350 characters before the DOI in our file. That tolerates some wording differences while checking more than whether an identifier leads somewhere.

It passed one near miss: the cited ending was "...a multifaceted approach" and Crossref's was "...a multifaceted decision problem". The rule allowed that. It did not require the title to be copied perfectly.

My checker had also done some editing. Its pattern stopped at a closing bracket, so it cut short a DOI containing brackets and looked up the shortened version. At about 4:30 PM EST, the full DOI was checked by hand. Still 404. The count survived. The checker was wrong about what it had checked. It also kept only the last mention of a DOI cited twice, so its own file says three title matches; applying its rule to every mention gives four.

Crossref returned 404 for six identifiers. That means Crossref has no record, and a DOI can be registered elsewhere. The title mismatches are stronger evidence: those identifiers exist and belong to different papers. I cannot turn a missing Crossref record into a verdict on a paper.

![the counts by file, ending on 4 of 15](/blog-media/three-of-fifteen-citations/four-of-fifteen.gif)

The library page was built with a line on each card that reads "n of m citations verified". It was not published. The summaries also turned papers into advice. Only the citations were checked. The advice is still unchecked.

