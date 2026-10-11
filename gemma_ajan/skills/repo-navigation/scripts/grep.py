#!/usr/bin/env python3
"""grep.py -- bounded source search (no shell needed).

usage: grep.py --pattern REGEX [--glob '*.py'] [--max 20]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import locate as L  # noqa: E402


def main():
    o = L.parse_args(sys.argv[1:])
    pat = o["pattern"] or o["text"]
    if not pat:
        print("EMPTY: pass args {\"pattern\": \"regex\"}.")
        return
    rc, out = L.sh(["git", "grep", "-n", "-I", "-E", pat, "--", o["glob"]], o["root"], 20)
    lines = [l for l in out.split("\n") if l.strip()]
    if not lines:
        print("no matches")
        return
    n = int(o["max"])
    print("\n".join(l[:200] for l in lines[:n]) + (f"\n... {len(lines) - n} more" if len(lines) > n else ""))


if __name__ == "__main__":
    main()
