#!/usr/bin/env python3
"""Push a GPU test run of a built submission to Kaggle (never submits to the competition).

usage: gpu_run.py SUBMISSION_ZIP LABEL TASK_ID[,TASK_ID...] [--dry]
Every run is capped at 30 minutes (vLLM start-up included), so keep it to ~2 tasks.
Needs KAGGLE_API_TOKEN in the environment (never written to disk by this script).
"""
import base64
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
USER = "ulankaggle"


def main():
    zip_path, label, ids = Path(sys.argv[1]), sys.argv[2], sys.argv[3].split(",")
    b64 = base64.b64encode(zip_path.read_bytes()).decode()
    code = (HERE / "runner_template.py").read_text()
    code = code.replace("__LABEL__", label).replace("__TASK_IDS__", json.dumps(ids)).replace("__SUBMISSION_ZIP_B64__", b64)
    d = Path(tempfile.mkdtemp(prefix=f"gpu_{label}_"))
    (d / "run.py").write_text(code)
    meta = {
        "id": f"{USER}/gemma4-agent-test-{label}",
        "title": f"Gemma4 Agent Test {label}",
        "code_file": "run.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": False,
        "dataset_sources": ["metric/gemma-4-developer-agent-wheelhouse"],
        "competition_sources": ["gemma-4-developer-agent"],
        "kernel_sources": [],
        "model_sources": ["google/gemma-4/Other/gemma-4-31b-it-qat-w4a16-ct/2"],
        "docker_image": "gcr.io/kaggle-private-byod/python@sha256:37c64f7dd9c54116ecd1bcc88817c5469b88387388fade02bfa8bf3fc647d461",
        "machine_shape": "NvidiaL4",
    }
    (d / "kernel-metadata.json").write_text(json.dumps(meta, indent=2))
    print("kernel dir:", d, "script bytes:", len(code))
    if "--dry" in sys.argv:
        return
    subprocess.run(["kaggle", "kernels", "push", "-p", str(d), "-t", "1800"], check=True)  # 30-min cap per run
    print("pushed:", meta["id"])


if __name__ == "__main__":
    main()
