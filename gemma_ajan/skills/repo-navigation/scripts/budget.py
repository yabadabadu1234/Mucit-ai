"""budget.py -- token-budgeted output for the repo-navigation scripts (code-based compaction).

Why code and not an LLM summary: deterministic, testable, no extra model call, and no
invented facts. Every script's stdout passes through guard() before it reaches the model:

  1. Estimate tokens (ceil(chars / 3): conservative for code and Turkish text).
  2. A single output above PER_CALL tokens keeps its head and tail and a pointer to the
     full text (stored in the task tmpdir, readable with context.py --full).
  3. A per-task ledger counts everything emitted so far. Past SOFT_TOTAL, each new output
     is cut to DIGEST tokens; past HARD_TOTAL, the script answers with a stop line instead.

Standard library only. Always returns normally so stdout is never lost (see locate.py).
"""
import contextlib
import io
import json
import math
import os
import sys
import tempfile
import traceback

PER_CALL = 700
SOFT_TOTAL = 6000
HARD_TOTAL = 9000
DIGEST = 200


def est_tokens(s):
    return math.ceil(len(s) / 3)


def _dir():
    d = os.path.join(tempfile.gettempdir(), "repo_nav_out")
    os.makedirs(d, exist_ok=True)
    return d


def _ledger_path():
    return os.path.join(_dir(), "ledger.json")


def _load():
    try:
        return json.load(open(_ledger_path()))
    except (OSError, ValueError):
        return {"total": 0, "n": 0}


def _save(led):
    with open(_ledger_path(), "w") as fh:
        json.dump(led, fh)


def _cut(text, max_tokens, full_path):
    """Keep head (60%) and tail (30%) of the allowed size; say what was dropped."""
    max_chars = max_tokens * 3
    if len(text) <= max_chars:
        return text
    head = text[: int(max_chars * 0.6)]
    tail = text[-int(max_chars * 0.3):]
    dropped = est_tokens(text) - est_tokens(head) - est_tokens(tail)
    return (f"{head}\n... [{dropped} tokens cut; full output: {full_path}; "
            f"read it with: context.py --full {os.path.basename(full_path)}] ...\n{tail}")


def emit_text(text):
    """Apply the budget to one output and return what the model should see."""
    led = _load()
    led["n"] += 1
    full_path = os.path.join(_dir(), f"out_{led['n']:03d}.txt")
    with open(full_path, "w", encoding="utf-8") as fh:
        fh.write(text)
    tok = est_tokens(text)
    if led["total"] >= HARD_TOTAL:
        shown = (f"BUDGET EXHAUSTED ({led['total']} tokens used on skill output). "
                 f"Stop searching: use what you already have and edit or submit now.")
    elif led["total"] >= SOFT_TOTAL:
        shown = _cut(text, DIGEST, full_path)
    else:
        shown = _cut(text, PER_CALL, full_path)
    led["total"] += est_tokens(shown)
    _save(led)
    return shown


def guard(main):
    """Run a script's main(), budget its stdout, and always exit 0."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            main()
    except SystemExit:
        pass
    except Exception:  # noqa: BLE001 -- report, never lose the output that was produced
        buf.write("\nERROR in script: " + traceback.format_exc(limit=2))
    out = buf.getvalue()
    if out:
        sys.stdout.write(emit_text(out) + ("" if out.endswith("\n") else "\n"))
    sys.stdout.flush()
    return 0
