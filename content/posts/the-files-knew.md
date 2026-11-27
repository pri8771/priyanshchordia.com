---
title: "The files knew when they were made. I had not asked."
slug: "the-files-knew"
date: "2026-11-22"
summary: "392 audio files, four facts to find, and the fourth was in my account history."
series: "Running a company on AI agents"
status: "draft"
---

> **DRAFT.** Not yet published. This page is a working copy for review and is not indexed by search engines.

*392 audio files, four facts to find, and the fourth was in my account history.*

I have 392 AI-made audio files in an app I built, and I need four things before I can work out which ones I can release commercially: when each was made, when it was downloaded, whose words it uses, and which plan it was made under.

My earlier post was about 223 songs. That was the set with names starting with suno_. There are another 169 in meditation, sleep, energy and similar sets. All were made with Suno. Even the size of the problem had a naming convention.

The only provenance record I knew of was a log from June describing a run of 435 queued jobs. I had a record of the queue. The songs were a separate administrative matter.

On November 23, my AI assistant ran ffprobe on every file. All 392 contained a tag written by the tool itself, in this form:

> made with suno; created=<date and time>; id=<song id>

The creation dates ran from April 21 to June 2. I had built an app around files that introduced themselves with their date of birth, and my known source was a queue log.

![the creation tag format found in all 392 files](/blog-media/the-files-knew/creation-tag.gif)

The download evidence was also in the app. It is in git, so the history shows when each file first entered the repository. A file cannot enter git before it has been downloaded. This is a bound on the download date, not an exact download timestamp. Three files had no first-seen date.

The slightly technical part is a join on the file name. `ffprobe -show_entries format_tags` reads the generator's creation timestamp and song ID. `git log --diff-filter=A --name-only` finds the first addition to version control. Join those to the existing text inventory and there is a provenance record nobody had to design. The generator recorded its part and git recorded its part. My contribution was needing to be told.

The inventory already existed too. It had 1,166 rows and was made on June 19. Across the audio files, it left this list:

- 128 classed as AI-generated audio with original text.
- 16 classed as traditional or unknown.
- 248 absent from the inventory, the mantra and prayer recordings with traditional words, so those are out.

For 105 of the 128 candidates, creation and first addition to git were on the same day. All 128 were in git by May 28. Candidates, so far.

There were some other details. Every artist tag held my user name on the tool, so the copies prepared for release had every tag stripped and rewritten. The files were MP3 at about 176 to 192 kbps and 48 kHz. The distributor asks for FLAC or 320 kbps MP3 at 44.1 kHz.

An album has been assembled: ten tracks, 22 minutes 17 seconds, all made May 25 and in git that day. The artist is a labelled brand. The credits say AI for lyrics, composition and audio.

![the album's recorded release status: Released: nothing.](/blog-media/the-files-knew/release-status.gif)

I found the fourth fact in my own account history. That gives me all four.

Released: nothing.

