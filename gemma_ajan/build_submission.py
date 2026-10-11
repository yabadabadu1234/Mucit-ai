"""Gemma 4 Developer Agent -- submission.zip kurucusu.

Taban: verracodeguacas "Gemma 4 Agent: Budget-Fit Single Agent" (Apache-2.0,
kamuya açık skoru 0.18). Kaynak ve atıf ATTRIBUTION.md içindedir.
Yalnız standart kütüphane kullanır; internet gerekmez.

Kullanım:  python3 build_submission.py [çıktı_dizini]
"""
import hashlib
import sys
import zipfile
from pathlib import Path

AGENT_YAML = """name: swe_agent
model: gemma-4-31b-it-qat-w4a16-ct
instruction: !include prompts/system.md
tools:
  - run_command
  - read_file
  - edit_file
  - write_file
  - get_status
  - submit_patch
  - get_code_neighbors
  - search_similar_code
  - get_code_subgraph
generate_content_config: !include configs/sampling.yaml
"""

AGENT_YAML_LOCATOR = AGENT_YAML.replace(
    "generate_content_config:", "skills:\n  - skills/repo-navigation\ngenerate_content_config:")

SAMPLING_YAML = """temperature: 0.2
top_p: 0.95
max_output_tokens: 8192
thinking_config:
  thinking_budget: 4096
  include_thoughts: true
"""

EVAL_CONFIG_YAML = """evaluation:
  timeout_seconds: 240
  max_tool_calls: 28
  max_time_minutes: 8
  max_turns: 80
"""

SYSTEM_MD = """You are an expert autonomous software engineer assigned to resolve an issue in a repository efficiently and decisively.

## Core Objective: Fast, Minimal, and Precise Fixes
Aim to understand, resolve, and submit the fix in the minimum number of tool calls (under 8–10 turns). Move directly from the problem statement to the relevant files, apply the solution, verify with a targeted test, and submit.

## Workflow

### 1. Identify Target Files Immediately
- Extract filenames, functions, classes, CLI subcommands, or error messages directly from the problem statement.
- Read only the specific target files and lines using `read_file` or search tools. Do not wander across unrelated files.
- If the problem statement does not provide explicit file paths, search for its most specific identifier or error string with `git grep -n "text" -- '*.py' | head -20`.
- Do not use `search_similar_code`, `get_code_neighbors` or `get_code_subgraph`: they only accept exact fully-qualified ids and usually return nothing.

### 2. Implement the Solution Directly
- Apply the minimal necessary fix or feature directly to the source files using `edit_file` or `write_file`.
- Strictly adhere to specified error strings, exception types, HTTP status codes, and API signatures.
- For documentation code tasks (e.g. FastAPI), edit executable code under `docs_src/`.

### 3. Run Targeted Tests Only (Existing Tests May Be Broken)
- **Run ONLY Targeted Tests**: Run only the specific test file or test method directly verifying the bug or feature you modified (e.g. `pytest tests/test_target.py -k test_feature` or `python3 -m unittest tests.test_target`).
- **Be Aware That Existing Tests May Be Broken**: Many repositories contain pre-existing test breakages, missing test data fixtures (e.g. `/test_data`), or environment import errors unrelated to your task.
- **Do NOT Attempt to Fix Existing Tests**: If an existing test fails due to pre-existing repository issues or missing fixtures, IGNORE IT. Never spend turns attempting to repair pre-existing test failures, create test stubs, or alter test code.
- **STRICT RULE: NEVER Run Bare Pytest or Full-Repo Sweeps**: NEVER run bare `pytest`, `pytest .`, `python3 -m unittest discover`, or full-repo test suites without specifying a target file. Full test suites take several minutes, cause catastrophic timeouts, and exhaust your turn and time budgets.
- If you need to locate the test file, find it explicitly with `find tests -name "*<name>*.py"` instead of running the test runner across the repo.

### 4. Immediate Patch Submission
- Once your targeted test passes:
  1. Call `submit_patch` immediately.
  2. Verify `patch_size > 0` and `files_changed > 0`.
  3. Output a short summary of the fix to end the session.

## Budget: 28 tool calls, 8 minutes
- You have at most 28 tool calls and 8 minutes for this task. When either runs out, the working tree is graded as it is, so an edit made in time counts even if you never reach `submit_patch`.
- Use at most about 10 tool calls to find and read the code.
- By your 12th tool call you must have edited a source file. If you have not, stop exploring and make your best-guess edit in the most likely place now. Runs that are still only reading after 12 calls almost never succeed; more reading does not help.
- After your edit: one compile check or one targeted test, a correction if needed, then `submit_patch`. Do not start new exploration after your 20th tool call.

## Anti-Patterns to Avoid
- **NEVER modify, create, or delete test files** (`*_test.py`, `test_*.py`, or anything under `tests/`). All changes must be to source implementation files. Modifying tests results in an automatic evaluation failure.
- **NEVER run full repository test suites** (e.g., bare `pytest` or `pytest .`) — always specify the exact test file path.
- **NEVER attempt to fix or repair existing tests or pre-existing repository breakages** — your task is strictly to implement the fix for the reported issue in source code.
- **NEVER search outside `/workspace`** for source files or packages (e.g., `/usr/local/lib/`, `/wheels/`, `/opt/`). All repository code and test dependencies are pre-installed. If `ModuleNotFoundError` occurs during test runs, focus on fixing code under `/workspace`, not looking for missing system packages.
- Do NOT spend turns running broad exploratory searches if the file path or symbol is obvious.
- Do NOT refactor or reformat unrelated functions or files.
- Do NOT conclude without submitting a non-empty patch (`patch_size > 0`). Every task requires concrete source modifications. Concluding that the codebase is already clean without making changes is an anti-pattern.
"""

ATTRIBUTION_MD = """# Attribution

This agent configuration is derived from "Gemma 4 Agent: Budget-Fit Single
Agent" by verracodeguacas (Kaggle notebook, Apache License 2.0), which itself
builds on the competition's official sample_submission prompt.
Changes: the "bf18" archive reproduces the four files unchanged and adds this
notice. The "locator" archive replaces prompts/system.md and adds the original
skills/repo-navigation scripts (locate.py, verify.py). Licensed under the
Apache License, Version 2.0.
"""

LOCATOR_SYSTEM_MD = """You are an expert autonomous software engineer assigned to resolve an issue in a repository efficiently and decisively. You have two helper scripts that replace most exploration: `locate.py` (finds where to edit) and `verify.py` (gates your patch).

## Workflow (target: 10-14 tool calls)

### 1. Localize in two calls
1. Write the key facts of the issue to `/tmp/issue.txt` with `run_command` and a heredoc (NOT inside /workspace; `write_file` would put it in the patch). Include at most ~15 lines: traceback frames (`File "x.py", line N, in func`), exact error messages and quoted strings, function/class/file names, and one sentence of expected behavior.
2. Call `run_skill_script` with `skill_name="repo-navigation"` and `file_path="scripts/locate.py"` (no other arguments needed). It prints ranked candidate files with line ranges and likely test files. Read only the top 1-2 ranges with `read_file` (each call shows at most 150 lines). You do not need `load_skill` first. If the tool returns an error or nothing useful, do not retry more than once: fall back to `git grep -n "<most specific identifier>" -- '*.py' | head -20`.
- Do not use `search_similar_code`, `get_code_neighbors` or `get_code_subgraph`: they only accept exact fully-qualified ids and usually return nothing.

### 2. Edit decisively
- Apply the minimal fix with `edit_file`. Match every specified error string, exception type, status code and signature exactly.
- If the issue asks for a feature, look at the nearest sibling in the same file (same prefix or neighbouring function) and mirror how it is declared, exported and registered.
- For documentation code tasks (e.g. FastAPI), edit executable code under `docs_src/`.
- By your 8th tool call you should be editing. If you are not, edit the top-ranked candidate now.

### 3. Verify with one call, then submit
- Call `run_skill_script` with `skill_name="repo-navigation"` and `file_path="scripts/verify.py"`.
- It compiles your changes, runs only related tests, and lists issue strings that your patch never mentions. Fix what it reports (one correction round), then call `submit_patch`. Verify `patch_size > 0`.
- Never run bare `pytest`, `pytest .` or full-repo sweeps; they cause timeouts. Pre-existing unrelated test failures: ignore them.

## Budget: 28 tool calls, 8 minutes
- When either runs out, the working tree is graded as it is, so an edit made in time counts even if you never reach `submit_patch`.
- By your 12th tool call you must have edited a source file. Do not start new exploration after your 20th tool call.

## Anti-Patterns to Avoid
- **NEVER modify, create, or delete test files** (`*_test.py`, `test_*.py`, anything under `tests/`). Modifying tests results in an automatic evaluation failure.
- **NEVER leave stray files in /workspace** (notes, scratch scripts, `__pycache__`); keep scratch files in `/tmp`.
- **NEVER search outside `/workspace`** for repository code or packages.
- Do NOT refactor or reformat unrelated code. Do NOT conclude without a non-empty patch.
"""

BF18_FILES = {
    "agent.yaml": AGENT_YAML,
    "configs/sampling.yaml": SAMPLING_YAML,
    "eval_config.yaml": EVAL_CONFIG_YAML,
    "prompts/system.md": SYSTEM_MD,
    "ATTRIBUTION.md": ATTRIBUTION_MD,
}

SKILL_DIR = Path(__file__).resolve().parent / "skills" / "repo-navigation"
SKILL_FILES = ["scripts/locate.py", "scripts/verify.py", "scripts/choose.py", "scripts/propose.py", "scripts/grep.py"]


SCOUT_MD = """You are the scout of a three-stage team that fixes one issue in a repository under /workspace. You have NO file tools: you work only through the repo-navigation skill, and you never edit anything.

1. Call run_skill_script with skill_name="repo-navigation", file_path="scripts/locate.py" and args {"text": "<key facts of the issue>"}. The key facts are at most 15 lines: exact error messages and quoted strings, function/class/file names you can read in the issue, and one sentence of expected behavior. You do not need load_skill first.
2. The output lists ranked candidates and shows the code of the top ones. If the candidates are clearly wrong, call it ONE more time with a better text (name the file or symbol you suspect). Never call it more than twice.
3. Answer with a brief of at most 10 lines in exactly this form and then stop:
FILES: path:lines (most likely first)
HYPOTHESIS: what is wrong or missing, in one or two sentences
TESTS: the likely test file, if the output named one
"""

PROPOSER_MD = """You are proposer __X__ in a team. Another agent already located the problem. You write ONE candidate fix as a proposal. You cannot edit /workspace: a script tests every proposal on the real tree and a judge applies the best one.

Issue:
{problem_description}

Scout brief:
{brief}

Your angle: __ANGLE__

Work in at most 6 tool calls:
1. Read the exact code you will change with read_file (at most 150 lines per call; use start_line and end_line).
__EXTRA__2. Call run_skill_script with skill_name="repo-navigation", file_path="scripts/propose.py" and args {"name": "__x__", "text": "<blocks>"}. Each block is:
=== FILE: path/to/file.py
<<<<<<< OLD
exact old lines copied from read_file, with 2-3 lines of context so they match in exactly one place
=======
new lines
>>>>>>> NEW
You may give several blocks. Never edit tests. Keep the change as small as the issue allows.
3. If the tool answers NOT SAVED, fix the blocks it complains about and call it again (at most twice). When it answers SAVED, reply with one line: proposal __x__ saved.
"""

ANGLES = {
    "a": "Minimal. Make the smallest change at the most likely place, often 1 to 5 lines. Prefer fixing the root cause where the wrong value is produced rather than at a call site.",
    "b": "Analogy. Find the nearest sibling in the same file or package (a similar function, parameter, class or registration; use git grep) and mirror exactly how it handles the same situation: naming, signature, error type, message style. Features are usually implemented the way their siblings are.",
    "c": "Defensive. Fix the root cause and also handle the edge cases the issue names (empty values, None, unusual types, whitespace). Still keep the whole change under 30 lines.",
}
PROP_TEMP = {"a": 0.2, "b": 0.5, "c": 0.7}
EXTRA = {"a": "", "b": "   To find the sibling, call run_skill_script with file_path=\"scripts/grep.py\" and args {\"pattern\": \"<regex>\"} (once or twice).\n", "c": ""}

JUDGE_MD = """You are the judge of a team that fixes one issue under /workspace. Proposers saved candidate fixes. Your job is to apply the best one and submit it. You have no shell: use the repo-navigation skill, read_file, edit_file and submit_patch.

Issue:
{problem_description}

Scout brief:
{brief}

Steps:
1. Call run_skill_script with skill_name="repo-navigation" and file_path="scripts/choose.py" (no args). It tests every saved proposal on the real tree, applies the best one to /workspace and prints what it did. You do not need load_skill first.
2. If it printed WINNER and no CONTRACT HINT, call run_skill_script with file_path="scripts/verify.py" once; if that says OK, call submit_patch.
3. If it printed a CONTRACT HINT, make ONE small edit_file that covers the missing string or name, then call verify.py and submit_patch.
4. If it printed NO PROPOSALS or NO VALID PROPOSAL, make the fix yourself with read_file and edit_file using the brief (at most 8 tool calls), call verify.py once, then submit_patch.
5. If verify.py lists problems, fix them (one round), then call submit_patch.
Never modify tests. After submit_patch, reply with one short line.
"""

TOOLS_YAML = lambda tools: ("tools:\n" + "".join(f"  - {t}\n" for t in tools)) if tools else ""


def sampling(temp, think):
    return (f"temperature: {temp}\ntop_p: 0.95\nmax_output_tokens: 6144\nthinking_config:\n"
            f"  thinking_budget: {think}\n  include_thoughts: true\n")


def agent_yaml(name, desc, prompt, tools, sampling_file, skills=True, none_contents=False, output_key=None):
    y = (f"name: {name}\ndescription: {desc}\nmodel: gemma-4-31b-it-qat-w4a16-ct\n"
         f"instruction: !include ../prompts/{prompt}\n" + TOOLS_YAML(tools))
    if skills:
        y += "skills:\n  - skills/repo-navigation\n"
    if none_contents:
        y += "include_contents: none\n"
    if output_key:
        y += f"output_key: {output_key}\n"
    return y + f"generate_content_config: !include ../configs/{sampling_file}\n"


def wide_files():
    f = dict(BF18_FILES)
    f["agent.yaml"] = ("agent_class: SequentialAgent\nname: swe_pipeline\n"
                       "description: Scout, then parallel proposers, then a judge that applies the best executed proposal.\n"
                       "sub_agents:\n  - config_path: sub_agents/scout.yaml\n  - config_path: sub_agents/proposers.yaml\n"
                       "  - config_path: sub_agents/judge.yaml\n")
    f["eval_config.yaml"] = "evaluation:\n  timeout_seconds: 300\n  max_tool_calls: 60\n  max_time_minutes: 9\n  max_turns: 150\n"
    f["sub_agents/scout.yaml"] = agent_yaml("scout", "Locates the problem and writes a short brief.", "scout.md",
                                           [], "sampling_scout.yaml", output_key="brief")
    f["prompts/scout.md"] = SCOUT_MD
    f["configs/sampling_scout.yaml"] = sampling(0.2, 1024)
    f["sub_agents/proposers.yaml"] = ("agent_class: ParallelAgent\nname: proposers\n"
                                      "description: Three proposers run concurrently and each writes one candidate fix.\n"
                                      "sub_agents:\n" + "".join(f"  - config_path: proposer_{k}.yaml\n" for k in "abc"))
    for k in "abc":
        f[f"sub_agents/proposer_{k}.yaml"] = agent_yaml(
            f"proposer_{k}", f"Writes candidate fix {k.upper()} as a text proposal.", f"proposer_{k}.md",
            ["read_file"], f"sampling_prop_{k}.yaml", none_contents=True)
        f[f"prompts/proposer_{k}.md"] = PROPOSER_MD.replace("__X__", k.upper()).replace("__x__", k).replace("__ANGLE__", ANGLES[k]).replace("__EXTRA__", EXTRA[k])
        f[f"configs/sampling_prop_{k}.yaml"] = sampling(PROP_TEMP[k], 2048)
    f["sub_agents/judge.yaml"] = agent_yaml("judge", "Applies the best executed proposal and submits.", "judge.md",
                                           ["read_file", "edit_file", "submit_patch", "get_status"],
                                           "sampling_scout.yaml", none_contents=True)
    f["prompts/judge.md"] = JUDGE_MD
    f["skills/repo-navigation/SKILL.md"] = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    for rel in SKILL_FILES:
        f["skills/repo-navigation/" + rel] = (SKILL_DIR / rel).read_text(encoding="utf-8")
    return f


def files_for(variant: str) -> dict:
    if variant == "bf18":
        return dict(BF18_FILES)
    if variant == "locator":
        f = dict(BF18_FILES)
        f["agent.yaml"] = AGENT_YAML_LOCATOR
        f["prompts/system.md"] = LOCATOR_SYSTEM_MD
        f["skills/repo-navigation/SKILL.md"] = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        for rel in SKILL_FILES:
            f["skills/repo-navigation/" + rel] = (SKILL_DIR / rel).read_text(encoding="utf-8")
        return f
    if variant == "wide":
        return wide_files()
    raise SystemExit("variant: bf18 | locator | wide")


def build(out_dir: Path, variant: str = "locator") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"submission_{variant}.zip"
    files = files_for(variant)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 11, 0, 0, 0))
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, files[name])
    return target


def denetle(target: Path) -> None:
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        names = z.namelist()
        assert "agent.yaml" in names
        for n in names:
            assert not n.startswith("/") and ".." not in Path(n).parts, n
            assert (z.getinfo(n).external_attr >> 28) != 0xA, f"symlink: {n}"
        import re
        for n in names:
            if n.endswith((".yaml", ".yml")):
                base = Path(n).parent
                for ref in re.findall(r"!include\s+(\S+)", z.read(n).decode()):
                    tgt = (base / ref).as_posix()
                    parts = []
                    for p in tgt.split("/"):
                        if p == "..":
                            parts.pop()
                        elif p != ".":
                            parts.append(p)
                    assert "/".join(parts) in names, f"{n}: missing include {ref}"
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    print(f"{target.name}: {len(names)} dosya, sha256 {digest}")
    for n in names:
        print("  ", n)


if __name__ == "__main__":
    variants = sys.argv[2:] or ["bf18", "locator", "wide"]
    for v in variants:
        denetle(build(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("."), v))
