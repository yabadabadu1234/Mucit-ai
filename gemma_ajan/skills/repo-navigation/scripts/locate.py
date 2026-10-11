#!/usr/bin/env python3
"""locate.py -- turn an issue text into a ranked list of files/symbols to edit.

usage: python3 locate.py STATEMENT_FILE|-  [--root /workspace] [--top 5]

One call replaces the usual 6-10 exploratory calls. It extracts hints from the
issue (traceback frames, backticked names, quoted error strings, file paths),
scores every function/class of the repository's source files (AST index) and
prints `file:start-end  symbol  score` plus likely test files.
Standard library only.
"""
import ast
import math
import os
import re
import sys
from collections import Counter, defaultdict

STOP = set("""a an the and or but if then else for from to of in on at by with without is are was were be been being
this that these those it its as not no yes can could should would will shall may might must do does did done have has had
i we you they he she them our your their my me us there here when where which who whom what why how also just only
get got set use used using make made need needs want wants like see seen note please thanks thank issue bug fix fixes
error errors exception raise raised raises return returns returned call called calls function method class module
file files line lines code test tests expected actual instead currently currently work works working work doesn
python pip install version versions example following above below happens happen happened""".split())

SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "build", "dist", ".tox", "__pycache__", "site-packages", ".eggs"}


def subtokens(s):
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)
    return [t for t in re.split(r"[^A-Za-z0-9]+", s.lower()) if len(t) > 1 and t not in STOP]


def is_test_path(p):
    parts = p.split("/")
    b = parts[-1]
    return (any(x in ("tests", "test", "testing") for x in parts[:-1])
            or b.startswith("test_") or b.endswith("_test.py") or b == "conftest.py")


def list_sources(root):
    out = []
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            if f.endswith(".py"):
                rel = os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/")
                out.append(rel)
    return out


class Unit:
    __slots__ = ("file", "qual", "name", "start", "end", "toks", "strs", "ids")


def index_file(root, rel):
    try:
        src = open(os.path.join(root, rel), encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except (SyntaxError, ValueError, OSError):
        return []
    units = []

    def visit(node, prefix):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                u = Unit()
                u.file, u.name = rel, ch.name
                u.qual = (prefix + "." if prefix else "") + ch.name
                u.start, u.end = ch.lineno, getattr(ch, "end_lineno", ch.lineno)
                ids, strs = [], []
                body = ch.body if not isinstance(ch, ast.ClassDef) else [
                    n for n in ch.body if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
                for b in body:
                    for n in ast.walk(b):
                        if isinstance(n, ast.Name):
                            ids.append(n.id)
                        elif isinstance(n, ast.Attribute):
                            ids.append(n.attr)
                        elif isinstance(n, ast.arg):
                            ids.append(n.arg)
                        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and len(n.value) > 3:
                            strs.append(n.value.lower())
                if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for a in ch.args.args + ch.args.kwonlyargs:
                        ids.append(a.arg)
                u.ids = set(i.lower() for i in ids)
                u.strs = strs
                toks = []
                for i in ids:
                    toks += subtokens(i)
                for s in strs:
                    toks += subtokens(s)
                u.toks = Counter(toks)
                units.append(u)
                visit(ch, u.qual)
            else:
                visit(ch, prefix)

    visit(tree, os.path.splitext(rel)[0].replace("/", "."))
    # module-level pseudo unit so files with only constants/config are reachable
    return units


NOISE = [r"(?im)^\s*co-authored-by:.*$", r"https?://\S+", r"[\w.+-]+@[\w-]+\.[\w.-]+", r"\b[0-9a-f]{7,40}\b", r"\(#\d+\)"]
AUX_DIRS = ("scripts/", "docs/", "doc/", "examples/", "benchmarks/", "tools/", "tasks/", "bin/", ".github/")


def clean(text):
    for p in NOISE:
        text = re.sub(p, " ", text)
    return text


def extract_hints(text):
    text = clean(text)
    h = {"frames": [], "paths": set(), "names": set(), "strings": [], "words": Counter()}
    for m in re.finditer(r'File "([^"]+\.py)", line (\d+), in (\w+)', text):
        f = m.group(1)
        if "site-packages" in f or "/lib/python" in f:
            continue
        h["frames"].append((f.replace("\\", "/"), m.group(3)))
    for m in re.finditer(r"[\w./-]+\.py\b", text):
        h["paths"].add(m.group(0).lstrip("./"))
    for m in re.finditer(r"`([^`\n]{2,80})`", text):
        for t in re.findall(r"[A-Za-z_][\w.]*", m.group(1)):
            h["names"].add(t)
    for m in re.finditer(r"\b([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+)\b", text):
        h["names"].add(m.group(1))
    for m in re.finditer(r"\b([A-Za-z_]\w*)\(", text):
        h["names"].add(m.group(1))
    for m in re.finditer(r"\b([a-z]+_[a-z0-9_]+|[a-z]+[A-Z]\w*|[A-Z][a-z]+[A-Z]\w*)\b", text):
        h["names"].add(m.group(1))
    for m in re.finditer(r"""(?:"([^"\n]{6,200})"|'([^'\n]{6,200})')""", text):
        h["strings"].append((m.group(1) or m.group(2)).lower())
    for m in re.finditer(r"^\s*\w*(?:Error|Exception|Warning)\w*:\s*(.{6,200})$", text, re.M):
        h["strings"].append(m.group(1).strip().lower())
    for w in subtokens(text):
        h["words"][w] += 1
    return h


def build_index(root):
    files = [f for f in list_sources(root) if not is_test_path(f)]
    units = []
    for f in files:
        units += index_file(root, f)
    df = Counter()
    for u in units:
        for t in set(u.toks):
            df[t] += 1
        for t in subtokens(u.name):
            df[t] += 0
    return files, units, df


def score(units, df, hints, files):
    n = max(len(units), 1)
    idf = lambda t: math.log(1 + (n - df.get(t, 0) + 0.5) / (df.get(t, 0) + 0.5))
    names = hints["names"]
    name_l = {x.lower() for x in names}
    name_last = {x.split(".")[-1].lower() for x in names}
    name_sub = set()
    for x in names:
        name_sub.update(subtokens(x))
    path_hints = hints["paths"]
    frame_funcs = {fn for _, fn in hints["frames"]}
    frame_bases = {os.path.basename(f) for f, _ in hints["frames"]}
    qwords = hints["words"]
    res = []
    for u in units:
        s = 0.0
        low = u.name.lower()
        if low in name_last:
            s += 10
        elif any(low == x or x.endswith("." + low) for x in name_l):
            s += 10
        usub = set(subtokens(u.name))
        if usub:
            ov = usub & (name_sub | set(qwords))
            s += 4.0 * sum(idf(t) for t in ov) / max(len(usub), 1) ** 0.5
        hit_ids = u.ids & name_last
        s += 2.5 * min(len(hit_ids), 4)
        # body BM25-ish over words
        b = 0.0
        L = sum(u.toks.values()) + 1
        for t, qc in qwords.items():
            tf = u.toks.get(t, 0)
            if tf:
                b += idf(t) * (tf * 2.2) / (tf + 1.2 * (0.25 + 0.75 * L / 150)) * (1 + 0.3 * min(qc, 3))
        s += 0.9 * b
        for sq in hints["strings"]:
            sw = [w for w in subtokens(sq)]
            if not sw:
                continue
            best = 0.0
            for lit in u.strs:
                if sq in lit or (len(lit) > 8 and lit in sq):
                    best = 1.0
                    break
                lw = set(subtokens(lit))
                if lw:
                    best = max(best, len(set(sw) & lw) / len(set(sw)))
            if best >= 0.6:
                s += 9 * best
        base = os.path.basename(u.file)
        if u.name in frame_funcs:
            s += 12 if base in frame_bases else 5
        elif base in frame_bases:
            s += 3
        for p in path_hints:
            if u.file.endswith(p) or (os.path.basename(p) == base):
                s += 6
                break
        if u.file.startswith(AUX_DIRS) and not any(u.file.endswith(p) for p in path_hints) and base not in frame_bases:
            s *= 0.3
        res.append((s, u))
    return res


def tests_for(root, top_units, hints):
    tfiles = []
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in fs:
            if f.endswith(".py"):
                rel = os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/")
                if is_test_path(rel):
                    tfiles.append(rel)
    keys = {u.name.lower() for u in top_units if len(u.name) > 3}
    mods = {os.path.splitext(os.path.basename(u.file))[0].lower() for u in top_units}
    scored = []
    for t in tfiles:
        try:
            txt = open(os.path.join(root, t), encoding="utf-8", errors="replace").read().lower()
        except OSError:
            continue
        sc = sum(3 for k in keys if k in txt) + sum(2 for m in mods if m in os.path.basename(t).lower())
        sc += sum(1 for w in list(hints["words"])[:30] if len(w) > 4 and w in txt) * 0.2
        if sc:
            scored.append((sc, t))
    scored.sort(reverse=True)
    return [t for _, t in scored[:3]]


def locate(root, text, top=5):
    files, units, df = build_index(root)
    hints = extract_hints(text)
    scored = score(units, df, hints, files)
    byfile = defaultdict(list)
    for s, u in scored:
        byfile[u.file].append((s, u))
    ranked = []
    for f, lst in byfile.items():
        lst.sort(key=lambda x: -x[0])
        fs = lst[0][0] + 0.25 * (lst[1][0] if len(lst) > 1 else 0)
        # lightweight path prior: words of the issue appearing in the path
        ps = set(subtokens(f))
        fs += 2.0 * len(ps & set(hints["words"]))
        ranked.append((fs, f, lst[:3]))
    ranked.sort(key=lambda x: -x[0])
    return ranked[:top], hints


def find_workspace():
    f = sys._getframe()
    while f is not None:
        oc = f.f_locals.get("_orig_cwd")
        if oc and os.path.isdir(os.path.join(oc, ".git")):
            return oc
        f = f.f_back
    cands = ["/workspace"] + [p for p in os.environ.get("PYTHONPATH", "").split(os.pathsep) if p] + [os.getcwd()]
    for c in cands:
        if os.path.isdir(os.path.join(c, ".git")):
            return c
    return "/workspace"


def tmpdir():
    import tempfile
    return tempfile.gettempdir()


def parse_args(a):
    """Tolerant of every run_skill_script argument style (args dict, positional list, stray `--`)."""
    opts = {"root": "", "top": "5", "issue": "", "text": "", "timeout": "120", "budget": "170",
            "name": "", "file": "", "pattern": "", "glob": "*.py", "max": "20"}
    pos, i = [], 0
    toks = [t for t in a if t != "--"]
    while i < len(toks):
        t = toks[i]
        key = t[2:] if t.startswith("--") else ""
        if key in opts and i + 1 < len(toks):
            opts[key] = toks[i + 1]
            i += 2
        else:
            pos.append(t)
            i += 1
    for p in pos:
        if not opts["issue"] and not opts["text"] and os.path.isfile(p):
            opts["issue"] = p
        elif not opts["text"] and (" " in p or "\n" in p):
            opts["text"] = p
    if not opts["root"]:
        opts["root"] = find_workspace()
    if not opts["issue"]:
        opts["issue"] = os.path.join(tmpdir(), "issue.txt")
    return opts


def sh(cmd, root, timeout=60, env_extra=None):
    import subprocess
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    if env_extra:
        env.update(env_extra)
    try:
        p = subprocess.run(cmd, cwd=root, env=env, shell=isinstance(cmd, str), capture_output=True, text=True,
                           errors="replace", timeout=timeout)
        return p.returncode, (p.stdout + p.stderr)
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"


def is_junk(f):
    b = os.path.basename(f)
    return (b.startswith(".adk_exec_") or "__pycache__" in f or b.endswith((".pyc", ".orig", ".rej"))
            or ".pytest_cache" in f)


def git_changes(root):
    """Changed files and added text WITHOUT touching the git index (no `git add -N`)."""
    _, tracked = sh(["git", "diff", "HEAD", "--name-only"], root)
    _, untracked = sh(["git", "ls-files", "--others", "--exclude-standard"], root)
    files = [x for x in (tracked + "\n" + untracked).split("\n") if x.strip() and not is_junk(x.strip())]
    _, diff = sh(["git", "diff", "HEAD", "-U0"], root)
    added = [l[1:] for l in diff.split("\n") if l.startswith("+") and not l.startswith("+++")]
    for f in untracked.split("\n"):
        f = f.strip()
        if f and not is_junk(f):
            try:
                added += open(os.path.join(root, f), encoding="utf-8", errors="replace").read().split("\n")
            except OSError:
                pass
    return files, "\n".join(added).lower()


def contract_gaps(text, added_l):
    h = extract_hints(text)
    missing = []
    for s_ in h["strings"][:6]:
        sub = subtokens(s_)
        frac = sum(w in added_l for w in sub) / len(sub) if sub else 1.0
        if s_ not in added_l and frac < 0.8:
            missing.append(f'string "{s_[:60]}"')
    for n in sorted(h["names"]):
        if "." not in n and len(n) > 5 and n.lower() not in added_l and n in text and text.count(n) >= 2:
            missing.append(f"name {n}")
    return missing[:6]


def related_tests(root, files, text, limit=2):
    units = []
    for f in files:
        if f.endswith(".py") and not is_test_path(f) and os.path.exists(os.path.join(root, f)):
            units += index_file(root, f)
    return tests_for(root, units[:8], extract_hints(text))[:limit] if units else []


def failing_ids(out):
    return {l.split(" ", 1)[1].split(" - ")[0].strip() for l in out.split("\n") if l.startswith("FAILED ")}


def run_tests(root, tests, timeout):
    """-> (status, failed_ids, tail). status: pass | fail | timeout | unavailable"""
    rc, out = sh(["python3", "-m", "pytest", "-q", "--no-header", "--tb=no", "-rf", "-p", "no:cacheprovider", *tests],
                 root, timeout)
    if "No module named pytest" in out:
        return "unavailable", set(), out[-200:]
    if rc == 124:
        return "timeout", set(), "TIMEOUT"
    tail = "\n".join(out.strip().splitlines()[-4:])
    if rc in (0, 5):
        return "pass", set(), tail
    return "fail", failing_ids(out), tail


def read_issue(path):
    if path == "-":
        return sys.stdin.read()
    if not os.path.exists(path):
        return None
    return open(path, encoding="utf-8", errors="replace").read()


def get_issue(o):
    if o.get("text"):
        return o["text"]
    return read_issue(o["issue"])


def span(u, cap=140):
    end = min(u.end, u.start + cap - 1)
    more = u.end - end
    return f"{u.start}-{end}" + (f" (+{more} more lines)" if more > 0 else "")


def excerpt(root, u, cap=45):
    try:
        lines = open(os.path.join(root, u.file), encoding="utf-8", errors="replace").read().split("\n")
    except OSError:
        return ""
    end = min(u.end, u.start + cap - 1)
    body = "\n".join(f"{n:5d}  {lines[n - 1]}" for n in range(u.start, end + 1))
    return body + (f"\n       ... (+{u.end - end} more lines)" if u.end > end else "")


def main():
    o = parse_args(sys.argv[1:])
    text = get_issue(o)
    if text is None:
        print("NO ISSUE TEXT: call again with args {\"text\": \"<key facts of the issue>\"}.")
        return 0
    ranked, hints = locate(o["root"], text, int(o["top"]))
    if not ranked:
        print("NO CANDIDATES: the issue has no usable hints; name the file or symbol you suspect in text.")
        return 0
    print("CANDIDATES (best first):")
    topu = []
    for i, (fs, f, lst) in enumerate(ranked, 1):
        print(f"{i}. {f}  [{fs:.1f}]")
        for s, u in lst:
            print(f"     {f} lines {span(u)}  {u.qual}  ({s:.1f})")
            topu.append(u)
    print("\nCODE OF THE TOP CANDIDATES:")
    shown = 0
    for fs, f, lst in ranked[:2]:
        for s, u in lst[:1]:
            print(f"--- {f} lines {span(u, 45)}  {u.qual}")
            print(excerpt(o["root"], u))
            shown += 1
    tf = tests_for(o["root"], topu[:6], hints)
    if tf:
        print("\nLIKELY TESTS:", ", ".join(tf))
    return 0


if __name__ == "__main__":
    main()
