#!/usr/bin/env python3
"""context.py -- print the scout's best locate output (candidates and code), without recomputing.

usage: context.py        Always exits 0.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import locate as L  # noqa: E402


def main():
    p = os.path.join(L.tmpdir(), "locate_last.txt")
    if os.path.exists(p):
        print(open(p, encoding="utf-8", errors="replace").read())
    else:
        print("No scout output was stored; work from the brief and the issue text.")


if __name__ == "__main__":
    main()
