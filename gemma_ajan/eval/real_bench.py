#!/usr/bin/env python3
"""Localization on the REAL public tasks (tasks.jsonl) using local clones for the base_commit tree.

usage: real_bench.py TASKS_JSONL REPOS_DIR [use_hints=0|1]
Ground truth = non-test .py files in the reference `patch`. Reports hit@1/3/5 and
mean files-in-patch, per repo, locate.py vs whole-file TF-IDF.
"""
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import localization_bench as B  # noqa: E402

L = B.L


def gt_files(patch):
    fs = re.findall(r"^\+\+\+ b/(\S+)", patch, re.M)
    return [f for f in fs if f.endswith(".py") and not L.is_test_path(f)]


def main():
    tasks_path, repos_dir = sys.argv[1], sys.argv[2]
    use_hints = len(sys.argv) > 3 and sys.argv[3] == "1"
    stats = defaultdict(Counter)
    misses = []
    for line in open(tasks_path):
        t = json.loads(line)
        repo = os.path.join(repos_dir, t["repo"].split("/")[1])
        gt = gt_files(t["patch"])
        if not gt or not os.path.isdir(repo):
            continue
        text = t["problem_statement"] + ("\n" + t["hints_text"] if use_hints and t.get("hints_text") else "")
        data = subprocess.run(["git", "-C", repo, "archive", t["base_commit"], "--", "*.py"], capture_output=True).stdout
        if not data:
            stats[t["repo"]]["nocheckout"] += 1
            continue
        with tempfile.TemporaryDirectory() as d:
            with tarfile.open(fileobj=io.BytesIO(data)) as tf:
                tf.extractall(d, filter="data")
            ranked, _ = L.locate(d, text, 5)
            got = [f for _, f, _ in ranked]
            bl = B.tfidf_rank(d, text, 5)
        s = stats[t["repo"]]
        s["n"] += 1
        for k in (1, 3, 5):
            s[f"loc{k}"] += any(g in got[:k] for g in gt)
            s[f"tf{k}"] += any(g in bl[:k] for g in gt)
            s[f"locall{k}"] += all(g in got[:k] for g in gt)
        if not any(g in got[:3] for g in gt):
            misses.append((t["instance_id"], gt, got[:3]))
    tot = Counter()
    for r, s in sorted(stats.items()):
        tot.update(s)
        n = max(s["n"], 1)
        print(f"{r:20s} n={s['n']:3d} nocheckout={s['nocheckout']} | locate@1/3/5 " + "/".join(f"{s[f'loc{k}']/n:.2f}" for k in (1, 3, 5))
              + " | tfidf " + "/".join(f"{s[f'tf{k}']/n:.2f}" for k in (1, 3, 5)))
    n = max(tot["n"], 1)
    print(f"{'ALL':20s} n={tot['n']:3d} | locate@1/3/5 " + "/".join(f"{tot[f'loc{k}']/n:.2f}" for k in (1, 3, 5))
          + " | tfidf " + "/".join(f"{tot[f'tf{k}']/n:.2f}" for k in (1, 3, 5))
          + " | all-files-in-top5 " + f"{tot['locall5']/n:.2f}")
    print("MISSES (not in top3):")
    for m in misses[:40]:
        print("  ", m)


if __name__ == "__main__":
    main()
