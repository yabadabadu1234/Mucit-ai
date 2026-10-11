#!/usr/bin/env python3
"""propose.py -- save one candidate fix after checking that it applies to the real tree.

usage: propose.py --name a --text "<blocks>"      (or --file PATH)
Blocks (search/replace):
=== FILE: path/to/file.py
<<<<<<< OLD
exact old lines (copy from read_file; 2-3 lines of context so they match once)
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


def main():
    o = L.parse_args(sys.argv[1:])
    name = (o["name"] or "x").strip()[:12] or "x"
    text = o["text"] or (open(o["file"], encoding="utf-8", errors="replace").read() if o["file"] and os.path.exists(o["file"]) else "")
    text = text.replace("```diff", "").replace("```python", "").replace("```", "")
    if not text.strip():
        print("EMPTY: pass the blocks in args {\"name\": \"a\", \"text\": \"=== FILE: ...\"}.")
        return
    try:
        edits = S.parse_proposal(text)
    except ValueError as e:
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
        print("NOT SAVED:\n- " + "\n- ".join(problems) + "\nFix the blocks and call propose.py again.")
        return
    path = os.path.join(L.tmpdir(), f"prop_{name}.txt")
    open(path, "w", encoding="utf-8").write(text.strip() + "\n")
    print(f"SAVED proposal {name}: {len(edits)} edit(s) in {', '.join(sorted({e[0] for e in edits}))}; it applies cleanly and compiles.")


if __name__ == "__main__":
    main()
