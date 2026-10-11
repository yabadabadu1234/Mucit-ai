#!/usr/bin/env python3
"""Offline localization benchmark mined from real fix commits.

usage: localization_bench.py REPOS_DIR [per_repo=60] [scrub=0|1]

For each repo clone in REPOS_DIR, picks non-merge commits since 2021 that change
1-3 source .py files AND at least one test file; the commit message is the
"issue", the changed source files are the ground truth, and the tree is the
PARENT commit. Reports hit@1/3/5 of locate.py vs a whole-file TF-IDF baseline.
scrub=1 deletes every `*.py` path mention from the statement (harder).
"""
import math
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import io
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "repo-navigation", "scripts"))
import locate as L  # noqa: E402


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, errors="replace").stdout


def mine(repo, n):
    out = git(repo, "log", "--no-merges", "--since=2021-01-01", "--name-only", "--format=@@%H")
    cands = []
    for blk in out.split("@@")[1:]:
        lines = [x for x in blk.split("\n") if x.strip()]
        sha, files = lines[0], lines[1:]
        src = [f for f in files if f.endswith(".py") and not L.is_test_path(f)
               and not f.startswith("docs/") and f != "setup.py" and "/scripts/" not in f]
        tst = [f for f in files if f.endswith(".py") and L.is_test_path(f)]
        if 1 <= len(src) <= 3 and tst:
            cands.append((sha, src))
    step = max(len(cands) // (n * 2), 1)
    res = []
    for sha, src in cands[::step]:
        msg = git(repo, "show", "-s", "--format=%B", sha).strip()
        if len(msg) >= 40:
            res.append((sha, msg, src))
        if len(res) >= n:
            break
    return res


def checkout_py(repo, sha, dest):
    data = subprocess.run(["git", "-C", repo, "archive", sha + "^", "--", "*.py"], capture_output=True).stdout
    if not data:
        return False
    with tarfile.open(fileobj=io.BytesIO(data)) as t:
        t.extractall(dest, filter="data")
    return True


def tfidf_rank(root, text, top=5):
    files = [f for f in L.list_sources(root) if not L.is_test_path(f)]
    docs = {}
    for f in files:
        try:
            docs[f] = Counter(L.subtokens(open(os.path.join(root, f), errors="replace").read()))
        except OSError:
            pass
    df = Counter()
    for c in docs.values():
        df.update(c.keys())
    n = len(docs)
    q = Counter(L.subtokens(text))
    sc = []
    for f, c in docs.items():
        tot = sum(c.values()) + 1
        s = sum(math.log(1 + n / (1 + df[t])) * (c[t] / tot ** 0.5) * qc for t, qc in q.items() if t in c)
        sc.append((s, f))
    sc.sort(reverse=True)
    return [f for _, f in sc[:top]]


def main():
    repos_dir = sys.argv[1]
    per = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    scrub = len(sys.argv) > 3 and sys.argv[3] == "1"
    tot = Counter()
    base = Counter()
    N = 0
    for name in sorted(os.listdir(repos_dir)):
        repo = os.path.join(repos_dir, name)
        if not os.path.isdir(os.path.join(repo, ".git")):
            continue
        cs = mine(repo, per)
        rt, rb, rn = Counter(), Counter(), 0
        for sha, msg, gt in cs:
            if scrub:
                msg = re.sub(r"[\w./-]+\.py\b", " ", msg)
            with tempfile.TemporaryDirectory() as d:
                if not checkout_py(repo, sha, d):
                    continue
                ranked, _ = L.locate(d, msg, 5)
                got = [f for _, f, _ in ranked]
                bl = tfidf_rank(d, msg, 5)
            rn += 1
            for k in (1, 3, 5):
                rt[k] += any(g in got[:k] for g in gt)
                rb[k] += any(g in bl[:k] for g in gt)
        print(f"{name:9s} n={rn:3d} | locate hit@1/3/5 = " + "/".join(f"{rt[k]/max(rn,1):.2f}" for k in (1, 3, 5))
              + " | tfidf = " + "/".join(f"{rb[k]/max(rn,1):.2f}" for k in (1, 3, 5)), flush=True)
        for k in (1, 3, 5):
            tot[k] += rt[k]
            base[k] += rb[k]
        N += rn
    print(f"ALL       n={N:3d} | locate hit@1/3/5 = " + "/".join(f"{tot[k]/max(N,1):.2f}" for k in (1, 3, 5))
          + " | tfidf = " + "/".join(f"{base[k]/max(N,1):.2f}" for k in (1, 3, 5)))


if __name__ == "__main__":
    main()
