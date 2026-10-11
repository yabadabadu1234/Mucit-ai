#!/usr/bin/env python3
"""verify.py -- one-call post-edit gate.

usage: python3 verify.py [STATEMENT_FILE]   (keep the statement file OUTSIDE /workspace, e.g. /tmp/issue.txt) [--root /workspace] [--timeout 120]

Checks, in order, and prints a short verdict the agent can act on:
  1. the diff is non-empty and touches no test file
  2. every changed .py file compiles
  3. runs ONLY the tests that look related to the changed files (hard timeout)
  4. contract check: quoted strings / identifiers from the issue that appear
     nowhere in the added lines are listed (a hint that part of the request
     may be unimplemented)
Standard library only.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import locate as L  # noqa: E402


def sh(cmd, root, timeout=60):
    try:
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        p = subprocess.run(cmd, cwd=root, env=env, shell=isinstance(cmd, str), capture_output=True, text=True,
                           errors="replace", timeout=timeout)
        return p.returncode, (p.stdout + p.stderr)
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"


def main():
    a = sys.argv[1:]
    root, timeout = "/workspace", 120
    if "--root" in a:
        i = a.index("--root"); root = a[i + 1]; del a[i:i + 2]
    if "--timeout" in a:
        i = a.index("--timeout"); timeout = int(a[i + 1]); del a[i:i + 2]
    text = open(a[0], errors="replace").read() if a and os.path.exists(a[0]) else ""

    sh("git add -N . 2>/dev/null", root)
    _, names = sh("git diff HEAD --name-only", root)
    changed = [x for x in names.split("\n") if x.strip()]
    junk = [x for x in changed if "__pycache__" in x or x.endswith((".pyc", ".orig", ".rej")) or ".pytest_cache" in x]
    for x in junk:
        sh(["git", "rm", "-q", "--cached", "-f", "--ignore-unmatch", x], root)
        try:
            os.remove(os.path.join(root, x))
        except OSError:
            pass
    changed = [x for x in changed if x not in junk]
    problems = []
    if not changed:
        print("FAIL: empty diff. Make your best-guess edit now (top candidate from locate.py).")
        return 1
    tests_touched = [f for f in changed if L.is_test_path(f)]
    if tests_touched:
        problems.append("test files modified (automatic failure): " + ", ".join(tests_touched)
                        + " -> `git checkout HEAD -- <file>` to revert them")
    py = [f for f in changed if f.endswith(".py") and os.path.exists(os.path.join(root, f))]
    for f in py:
        try:
            compile(open(os.path.join(root, f), encoding="utf-8", errors="replace").read(), f, "exec")
        except SyntaxError as e:
            problems.append(f"does not compile: {f}:{e.lineno}: {e.msg}")
    src = [f for f in py if not L.is_test_path(f)]

    verdict_tests = "no related test found"
    if src and not problems:
        units = []
        for f in src:
            units += L.index_file(root, f)
        tf = L.tests_for(root, units[:8], L.extract_hints(text)) if units else []
        if tf:
            rc, out = sh(["python3", "-m", "pytest", "-x", "-q", "--no-header", "-p", "no:cacheprovider", *tf[:2]],
                         root, timeout)
            tail = "\n".join(out.strip().splitlines()[-6:])
            verdict_tests = f"pytest {' '.join(tf[:2])} -> rc={rc}\n{tail}"
            if "No module named pytest" in out:
                verdict_tests = "pytest not available; run the test file with `python3 -m unittest` or by hand"
            elif rc not in (0, 5):
                problems.append("related tests fail/timeout (existing failures may be unrelated; compare with `git stash`)")

    missing = []
    if text:
        _, added = sh("git diff HEAD -U0", root)
        added_l = "\n".join(l[1:] for l in added.split("\n") if l.startswith("+") and not l.startswith("+++")).lower()
        h = L.extract_hints(text)
        for s in h["strings"][:6]:
            sub = L.subtokens(s)
            frac = sum(w in added_l for w in sub) / len(sub) if sub else 1.0
            if s not in added_l and frac < 0.8:
                missing.append(f'string "{s[:60]}"')
        for n in sorted(h["names"]):
            if "." not in n and len(n) > 5 and n.lower() not in added_l and n in text and text.count(n) >= 2:
                missing.append(f"name {n}")
        missing = missing[:6]

    print(f"changed: {', '.join(changed)}")
    print(f"tests: {verdict_tests}")
    if missing:
        print("CONTRACT HINT (mentioned in the issue, absent from your added lines): " + "; ".join(missing))
    if problems:
        print("FIX BEFORE SUBMITTING:\n- " + "\n- ".join(problems))
        return 1
    print("OK: call submit_patch now.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
