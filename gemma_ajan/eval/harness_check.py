#!/usr/bin/env python3
"""Compile a built submission with the REAL adk-submission compiler and run its skill
scripts through ADK's real run_skill_script wrapper (local executor).

usage (inside a venv with google-adk==1.36.1, adk-submission==0.2.13):
  harness_check.py SUBMISSION_ZIP

Needs: a throwaway git repo is created in a temp dir; no network, no GPU, no model call.
"""
import asyncio
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from adk_submission.compiler import compile_submission
from adk_submission.registry import ModelRegistry
from google.adk.code_executors import UnsafeLocalCodeExecutor
from google.adk.tools.skill_toolset import SkillToolset, _SkillScriptCodeExecutor

TOOLS = ["run_command", "read_file", "edit_file", "write_file", "get_status", "submit_patch",
         "get_code_neighbors", "search_similar_code", "get_code_subgraph"]


def make_tool(name):
    def f(*a, **k):
        return "{}"
    f.__name__ = name
    return f


def main():
    z = Path(sys.argv[1]).resolve()
    work = Path(tempfile.mkdtemp(prefix="harness_check_"))
    sub = work / "submission"
    with zipfile.ZipFile(z) as zf:
        zf.extractall(sub)

    models = ModelRegistry()
    models.register("gemma-4-31b-it-qat-w4a16-ct", "dummy-model")
    agent = compile_submission(sub, {n: make_tool(n) for n in TOOLS}, models,
                               code_executor=UnsafeLocalCodeExecutor())
    toolsets = [t for t in agent.tools if isinstance(t, SkillToolset)]
    print(f"COMPILED agent={agent.name} tools={len(agent.tools)} skill_toolsets={len(toolsets)}")
    if not toolsets:
        print("no skills declared in agent.yaml; nothing more to check")
        return
    ts = toolsets[0]
    skill = ts._skills["repo-navigation"]
    print("skill:", skill.name, "scripts:", list(skill.resources.list_scripts()))

    repo = work / "repo"
    (repo / "pkg").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "pkg" / "__init__.py").write_text("")
    (repo / "pkg" / "greet.py").write_text('def greet(name):\n    return "hello " + name\n')
    (repo / "tests" / "test_greet.py").write_text(
        "from pkg.greet import greet\n\ndef test_greet():\n    assert greet('a') == 'hello a'\n")
    env = dict(os.environ, GIT_AUTHOR_NAME="a", GIT_AUTHOR_EMAIL="a@b", GIT_COMMITTER_NAME="a", GIT_COMMITTER_EMAIL="a@b")
    for c in (["git", "init", "-q"], ["git", "add", "-A"], ["git", "commit", "-qm", "base"]):
        subprocess.run(c, cwd=repo, env=env, check=True)
    issue = work / "issue.txt"
    issue.write_text('greet() must raise ValueError("name must not be empty") when name is empty\n')

    ex = _SkillScriptCodeExecutor(UnsafeLocalCodeExecutor(), 300)

    def run(path, args):
        return asyncio.run(ex.execute_script_async(None, skill, path, args))

    r = run("scripts/locate.py", {"issue": str(issue), "root": str(repo)})
    print("--- locate status:", r.get("status"), r.get("error_code", ""))
    print(r.get("stdout", r))
    assert "pkg/greet.py" in r.get("stdout", ""), "locate did not find the file"

    r = run("scripts/verify.py", {"issue": str(issue), "root": str(repo)})
    print("--- verify (empty diff) status:", r.get("status"))
    print(r.get("stdout", r))
    assert "empty diff" in r.get("stdout", ""), "empty diff not reported"

    (repo / "pkg" / "greet.py").write_text('def greet(name):\n    raise ValueError("bad")\n')
    r = run("scripts/verify.py", {"issue": str(issue), "root": str(repo)})
    print("--- verify (wrong message) status:", r.get("status"))
    print(r.get("stdout", r))
    assert "CONTRACT HINT" in r.get("stdout", ""), "contract gap not reported"

    (repo / "pkg" / "greet.py").write_text('def greet(name:\n')
    r = run("scripts/verify.py", {"issue": str(issue), "root": str(repo)})
    print("--- verify (syntax error) status:", r.get("status"))
    print(r.get("stdout", r))
    assert "does not compile" in r.get("stdout", ""), "syntax error output lost"
    print("ALL HARNESS CHECKS PASSED")


if __name__ == "__main__":
    main()
