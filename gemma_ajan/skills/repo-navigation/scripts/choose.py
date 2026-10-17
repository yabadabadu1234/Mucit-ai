#!/usr/bin/env python3
"""choose.py -- try every proposal on the real tree, keep the one that executes best.

Proposals are text files prop_*.txt in the temp dir (written by the proposer agents), each made
of search/replace blocks:

=== FILE: path/to/file.py
<<<<<<< OLD
exact old lines (empty OLD creates a new file)
=======
new lines
>>>>>>> NEW

For each proposal, in order: apply -> compile -> run the related tests -> revert. Ranking (best
first): applies and compiles, fewest NEW test failures versus the untouched tree, issue strings
covered, agreement with other proposals, smallest change. The winner is re-applied and left in
the working tree. Never touches the git index. Always exits 0.

usage: choose.py [--issue FILE] [--root DIR] [--timeout 40] [--budget 170]
"""
import glob
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import budget  # noqa: E402
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import locate as L  # noqa: E402

START, SEP, END = "<<<<<<< OLD", "=======", ">>>>>>> NEW"


def parse_proposal(text):
    """-> list of (file, old, new) or raises ValueError."""
    edits, cur, mode, old, new = [], None, None, [], []
    for line in text.split("\n"):
        if line.startswith("=== FILE:"):
            cur = line[len("=== FILE:"):].strip().strip("`")
            continue
        if line.strip() == START and cur:
            mode, old, new = "old", [], []
        elif line.strip() == SEP and mode == "old":
            mode = "new"
        elif line.strip() == END and mode == "new":
            edits.append((cur, "\n".join(old), "\n".join(new)))
            mode = None
        elif mode == "old":
            old.append(line)
        elif mode == "new":
            new.append(line)
    if mode is not None:
        raise ValueError("unterminated block")
    if not edits:
        raise ValueError("no edit blocks found")
    return edits


def _indent(s):
    return len(s) - len(s.lstrip(" \t"))


def apply_edit(text, old, new):
    """-> (new_text, how) or (None, reason)."""
    if old.strip() == "":
        return (new if text.strip() == "" else None), ("create" if text.strip() == "" else "file exists; OLD is empty")
    c = text.count(old)
    if c == 1:
        return text.replace(old, new, 1), "exact"
    if c > 1:
        return None, f"OLD matches {c} places; add more context lines"
    lines, ol = text.split("\n"), [x for x in old.split("\n")]
    while ol and ol[0].strip() == "":
        ol.pop(0)
    while ol and ol[-1].strip() == "":
        ol.pop()
    if not ol:
        return None, "empty OLD"
    key = [x.strip() for x in ol]
    hits = [i for i in range(len(lines) - len(ol) + 1) if [x.strip() for x in lines[i:i + len(ol)]] == key]
    if len(hits) != 1:
        return None, ("OLD not found (copy lines exactly from the CODE block of the brief or from context.py output)" if not hits else f"OLD matches {len(hits)} places")
    i = hits[0]
    delta = _indent(lines[i]) - _indent(ol[0])
    nl = new.split("\n")
    if delta:
        nl = [((" " * delta + x) if delta > 0 and x.strip() else (x[-delta:] if delta < 0 and x[:-delta].strip() == "" else x)) for x in nl]
    return "\n".join(lines[:i] + nl + lines[i + len(ol):]), "flexible"


def apply_all(root, edits):
    """Apply edits in the tree. -> (touched, created, error)"""
    touched, created = [], []
    for f, old, new in edits:
        if os.path.isabs(f) or ".." in f.split("/"):
            return touched, created, f"bad path {f}"
        p = os.path.join(root, f)
        exists = os.path.exists(p)
        text = open(p, encoding="utf-8", errors="replace").read() if exists else ""
        out, how = apply_edit(text, old, new)
        if out is None:
            return touched, created, f"{f}: {how}"
        os.makedirs(os.path.dirname(p) or root, exist_ok=True)
        open(p, "w", encoding="utf-8").write(out)
        (touched if exists else created).append(f)
    return touched, created, None


def revert(root, touched, created):
    if touched:
        L.sh(["git", "checkout", "HEAD", "--"] + sorted(set(touched)), root)
    for f in created:
        try:
            os.remove(os.path.join(root, f))
        except OSError:
            pass


def size(edits):
    return sum(len(o.split("\n")) + len(n.split("\n")) for _, o, n in edits)


def main():
    o = L.parse_args(sys.argv[1:])
    root, per_run, budget = o["root"], int(o["timeout"] if o["timeout"] != "120" else 40), float(o["budget"])
    t0 = time.monotonic()
    text = L.get_issue(o) or ""
    files = sorted(glob.glob(os.path.join(L.tmpdir(), "prop_*.txt")))
    if not files:
        print("NO PROPOSALS found (prop_*.txt). Make the fix yourself with edit_file.")
        return
    props = []
    for i, f in enumerate(files):
        name = os.path.basename(f)[5:-4]
        try:
            props.append(dict(name=name, edits=parse_proposal(open(f, encoding="utf-8", errors="replace").read())))
        except ValueError as e:
            props.append(dict(name=name, edits=None, err=f"parse: {e}"))
    all_files = sorted({e[0] for p in props if p["edits"] for e in p["edits"]})
    tests = L.related_tests(root, all_files, text) if all_files else []
    base_status, base_fail = "none", set()
    runs_left = 1 + len([p for p in props if p["edits"]])
    if tests:
        base_status, base_fail, _ = L.run_tests(root, tests, min(per_run, max(10, int((budget - (time.monotonic() - t0)) / runs_left))))
    for p in props:
        if not p["edits"]:
            p.update(valid=False)
            continue
        touched, created, err = apply_all(root, p["edits"])
        p.update(touched=touched, created=created)
        if err:
            p.update(valid=False, err=err)
            revert(root, touched, created)
            continue
        py = [f for f, _, _ in p["edits"] if f.endswith(".py")]
        bad = None
        for f in py:
            try:
                compile(open(os.path.join(root, f), encoding="utf-8", errors="replace").read(), f, "exec")
            except SyntaxError as e:
                bad = f"{f}:{e.lineno}: {e.msg}"
        if bad:
            p.update(valid=False, err="does not compile: " + bad)
            revert(root, touched, created)
            continue
        added_l = "\n".join(n for _, _, n in p["edits"]).lower()
        p["gaps"] = L.contract_gaps(text, added_l) if text else []
        status, failed, tail = ("none", set(), "")
        if tests:
            runs_left -= 1
            status, failed, tail = L.run_tests(root, tests, min(per_run, max(10, int((budget - (time.monotonic() - t0)) / max(runs_left, 1)))))
        p.update(valid=True, status=status, newfail=len(failed - base_fail) if base_status in ("pass", "fail") else 0,
                 size=size(p["edits"]))
        revert(root, touched, created)
    valid = [p for p in props if p.get("valid")]
    for p in valid:
        sig = {(f, old.strip().split("\n")[0].strip()) for f, old, _ in p["edits"]}
        p["agree"] = sum(1 for q in valid if q is not p and sig & {(f, old.strip().split("\n")[0].strip()) for f, old, _ in q["edits"]})
    rank = {"pass": 0, "none": 0, "unavailable": 1, "timeout": 1, "fail": 2}
    valid.sort(key=lambda p: (p["newfail"], rank.get(p["status"], 1), len(p["gaps"]), -p["agree"], p["size"], p["name"]))
    print(f"related tests: {tests or 'none found'}; untouched tree: {base_status}")
    for p in props:
        if p.get("valid"):
            print(f"  proposal {p['name']}: applies, compiles, tests={p['status']}, new failures={p['newfail']}, "
                  f"issue gaps={len(p['gaps'])}, agrees with {p['agree']}, size={p['size']}")
        else:
            print(f"  proposal {p['name']}: INVALID - {p.get('err')}")
    if not valid:
        print("NO VALID PROPOSAL. Make the fix yourself with edit_file, using the scout brief.")
        return
    w = valid[0]
    _, _, err = apply_all(root, w["edits"])
    if err:
        print("could not re-apply winner:", err)
        return
    print(f"WINNER {w['name']} applied to the working tree. Files: {', '.join(sorted({f for f, _, _ in w['edits']}))}")
    if w["gaps"]:
        print("CONTRACT HINT (issue mentions, patch lacks): " + "; ".join(w["gaps"]) + " -> consider one small edit_file to cover it.")
    if w["status"] == "fail":
        print("NOTE: every candidate still fails related tests; review before submitting.")


if __name__ == "__main__":
    budget.guard(main)
