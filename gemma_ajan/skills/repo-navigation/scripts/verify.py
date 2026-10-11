#!/usr/bin/env python3
"""verify.py -- one-call post-edit gate (never modifies the repo or the git index).

usage: verify.py [--issue FILE] [--root DIR] [--timeout 60]
Always exits 0 so run_skill_script keeps the output.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import locate as L  # noqa: E402


def main():
    o = L.parse_args(sys.argv[1:])
    root, timeout = o["root"], int(o["timeout"])
    text = L.get_issue(o) or ""
    changed, added_l = L.git_changes(root)
    if not changed:
        print("FAIL: empty diff. Make your best-guess edit now (top candidate from locate.py).")
        return
    problems = []
    touched = [f for f in changed if L.is_test_path(f)]
    if touched:
        problems.append("test files modified (automatic failure): " + ", ".join(touched)
                        + " -> `git checkout HEAD -- <file>` to revert them")
    py = [f for f in changed if f.endswith(".py") and os.path.exists(os.path.join(root, f))]
    for f in py:
        try:
            compile(open(os.path.join(root, f), encoding="utf-8", errors="replace").read(), f, "exec")
        except SyntaxError as e:
            problems.append(f"does not compile: {f}:{e.lineno}: {e.msg}")
    verdict = "no related test found"
    if not problems:
        tf = L.related_tests(root, changed, text)
        if tf:
            status, failed, tail = L.run_tests(root, tf, timeout)
            verdict = f"pytest {' '.join(tf)} -> {status}\n{tail}"
            if status == "fail":
                problems.append("related tests fail (existing failures may be unrelated; compare with `git stash`)")
    gaps = L.contract_gaps(text, added_l) if text else []
    print(f"changed: {', '.join(changed)}")
    print(f"tests: {verdict}")
    if gaps:
        print("CONTRACT HINT (mentioned in the issue, absent from your added lines): " + "; ".join(gaps))
    if problems:
        print("FIX BEFORE SUBMITTING:\n- " + "\n- ".join(problems))
        return
    print("OK: call submit_patch now.")


if __name__ == "__main__":
    main()
