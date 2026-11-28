#!/usr/bin/env python3
"""Required check (RULES A5, 28 Nov 2026): a PR that would make a blog post live must carry
the owner-approved hash from the dashboard queue.

For every content/posts/<slug>.md added or changed by the PR whose new text is not
status "draft", the PR body must contain "sha256 <hex>" where <hex> equals the queue's
content hash of that exact file text (posting-queue approvals.content_sha with channel
"blog", account ACCOUNT, parts [text], no media, link SITE/<slug>/). blog_publish.py writes
that line ("text sha256 <hex>") when it opens the PR.

Usage: check_approved_posts.py BASE_SHA HEAD_SHA  (PR body in env PR_BODY). Exit 1 = block.
Limit: the hash is computed from public text, so this proves the PR text matches a hash
written into the PR, not that the owner approved it; only the dashboard (passkey) proves that.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ACCOUNT = "priyanshchordia.com/blogs (his site)"
SITE = "https://priyanshchordia.com/blogs/"
DRAFT = re.compile(r'^status:\s*"?draft"?\s*$', re.M)


def content_sha(text, slug):
    blob = json.dumps({"channel": "blog", "account": ACCOUNT, "parts": [text], "media": [],
                       "link": SITE + slug + "/"}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def main(base, head, body):
    hashes = set(re.findall(r"sha256[:\s]+([0-9a-f]{64})", body or "", re.I))
    changed = git("diff", "--name-only", "--diff-filter=AMR", f"{base}...{head}", "--", "content/posts/").split()
    bad = []
    for path in changed:
        name = os.path.basename(path)
        if not name.endswith(".md") or name == "README.md":
            continue
        text = git("show", f"{head}:{path}")
        if DRAFT.search(text):
            print(f"ok   {path}: still a draft")
            continue
        want = content_sha(text, name[:-3])
        if want.lower() in {h.lower() for h in hashes}:
            print(f"ok   {path}: approved sha256 {want[:12]}")
        else:
            bad.append(path)
            print(f"FAIL {path}: goes live but the PR body has no approved sha256 {want}")
    if bad:
        print("Blocked (A5): approve this exact text on the dashboard and publish with blog_publish.py.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], os.environ.get("PR_BODY", "")))
