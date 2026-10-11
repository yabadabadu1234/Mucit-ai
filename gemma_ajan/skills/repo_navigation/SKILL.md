---
name: repo_navigation
description: Localize an issue to the files/symbols to edit in one call (locate.py) and gate a patch before submitting (verify.py).
---

# repo_navigation

Two standard-library Python tools. Keep the issue facts in `/tmp/issue.txt`
(outside `/workspace`, so they never end up in the patch).

## locate.py
`python3 scripts/locate.py /tmp/issue.txt --root /workspace --top 5`

Ranks files and functions by traceback frames, backticked names, quoted error
strings, file paths and identifier overlap against an AST index of the source
tree (tests and maintenance dirs are down-weighted). Prints `file:start-end`
ranges to read and the test files to run.

## verify.py
`python3 scripts/verify.py /tmp/issue.txt --root /workspace`

Fails if the diff is empty, touches test files, does not compile, or the related
tests fail. Lists issue strings/names that appear nowhere in your added lines.
