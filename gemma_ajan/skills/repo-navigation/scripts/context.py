#!/usr/bin/env python3
"""context.py -- print the scout's best locate output (candidates and code), without recomputing.

usage: context.py        Always exits 0.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import budget  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import locate as L  # noqa: E402


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--full":
        path = os.path.join(budget._dir(), os.path.basename(sys.argv[2]))
        print(open(path, encoding="utf-8").read() if os.path.exists(path) else "NO SUCH OUTPUT")
        return
    p = os.path.join(L.tmpdir(), "locate_last.txt")
    if os.path.exists(p):
        print(open(p, encoding="utf-8", errors="replace").read())
    else:
        print("No scout output was stored; work from the brief and the issue text.")


if __name__ == "__main__":
    budget.guard(main)
