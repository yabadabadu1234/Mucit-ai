#!/usr/bin/env python3
"""propose.py -- save one candidate fix after checking that it applies to the real tree.

usage: propose.py --name a --text "<blocks>"      (or --file PATH)
Blocks (search/replace):
=== FILE: path/to/file.py
<<<<<<< OLD
exact old lines (copy from the CODE block of the brief or from context.py output; 2-3 lines of context so they match once)
=======
new lines
>>>>>>> NEW
Nothing is changed in the repo; a clean proposal is stored for choose.py. Always exits 0.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import locate as L  # noqa: E402
import choose as S  # noqa: E402


MAX_FAILS = 3


def _fail_count(name):
    p = os.path.join(L.tmpdir(), f"propose_fails_{name}.txt")
    try:
        return int(open(p).read().strip() or 0)
    except (OSError, ValueError):
        return 0


def _bump_fail(name):
    p = os.path.join(L.tmpdir(), f"propose_fails_{name}.txt")
    n = _fail_count(name) + 1  # read before open(..., "w") truncates the file
    with open(p, "w") as fh:
        fh.write(str(n))


def main():
    o = L.parse_args(sys.argv[1:])
    name = (o["name"] or "x").strip()[:12] or "x"
    if _fail_count(name) >= MAX_FAILS:
        print(f"STOP: {MAX_FAILS} attempts already failed for proposal {name}. Reply with one line: proposal {name} failed. Do not call propose.py again.")
        return
    text = o["text"] or (open(o["file"], encoding="utf-8", errors="replace").read() if o["file"] and os.path.exists(o["file"]) else "")
    text = text.replace("```diff", "").replace("```python", "").replace("```", "")
    if not text.strip():
        _bump_fail(name)
        print("EMPTY: pass the blocks in args {\"name\": \"a\", \"text\": \"=== FILE: ...\"}.")
        return
    try:
        edits = S.parse_proposal(text)
    except ValueError as e:
        _bump_fail(name)
        print(f"FORMAT ERROR: {e}. Use blocks: '=== FILE: path', '<<<<<<< OLD', old lines, '=======', new lines, '>>>>>>> NEW'.")
        return
    problems = []
    cache = {}
    for f, old, new in edits:
        if os.path.isabs(f) or ".." in f.split("/"):
            problems.append(f"bad path {f}")
            continue
        p = os.path.join(o["root"], f)
        cur = cache.get(f)
        if cur is None:
            cur = open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else ""
        out, how = S.apply_edit(cur, old, new)
        if out is None:
            problems.append(f"{f}: {how}")
            continue
        cache[f] = out
        if f.endswith(".py"):
            try:
                compile(out, f, "exec")
            except SyntaxError as e:
                problems.append(f"{f}: result does not compile ({e.msg} at line {e.lineno})")
        if L.is_test_path(f):
            problems.append(f"{f}: do not edit tests")
    if problems:
        _bump_fail(name)
        left = MAX_FAILS - _fail_count(name)
        print("NOT SAVED:\n- " + "\n- ".join(problems) + f"\nFix the blocks and call propose.py again ({left} attempt(s) left).")
        return
    path = os.path.join(L.tmpdir(), f"prop_{name}.txt")
    open(path, "w", encoding="utf-8").write(text.strip() + "\n")
    print(f"SAVED proposal {name}: {len(edits)} edit(s) in {', '.join(sorted({e[0] for e in edits}))}; it applies cleanly and compiles.")


if __name__ == "__main__":
    main()
