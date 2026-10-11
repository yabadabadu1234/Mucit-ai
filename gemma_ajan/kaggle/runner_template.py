import asyncio
import base64
import glob
import importlib
import io
import json
import os
import shutil
import subprocess
import sys
import time
import traceback
import zipfile
from pathlib import Path

T0 = time.time()
LABEL = "__LABEL__"
TASK_IDS = __TASK_IDS__
SUBMISSION_ZIP_B64 = "__SUBMISSION_ZIP_B64__"


def log(*a):
    print(f"[{time.time() - T0:7.1f}s]", *a, flush=True)


for k, v in {
    "LITELLM_LOCAL_MODEL_COST_MAP": "True",
    "TRANSFORMERS_NO_TF": "1",
    "VLLM_WORKER_MULTIPROC_METHOD": "spawn",
    "VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS": "1",
    "VLLM_ENGINE_READY_TIMEOUT_S": "1200",
    "VLLM_NO_USAGE_STATS": "1",
    "OTEL_SDK_DISABLED": "true",
    "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
}.items():
    os.environ[k] = v

WORKING = Path("/kaggle/working")
SUB_DIR = WORKING / f"submission_{LABEL}"
RESULTS = WORKING / f"results_{LABEL}"
WHEELHOUSE = Path("/kaggle/input/datasets/metric/gemma-4-developer-agent-wheelhouse")
DATA_DIR = Path("/kaggle/input/competitions/gemma-4-developer-agent")
MODEL_PATH = Path("/kaggle/input/models/google/gemma-4/other/gemma-4-31b-it-qat-w4a16-ct/2")
TARGET_MODEL_NAME = "gemma-4-31b-it-qat-w4a16-ct"

for p in (WHEELHOUSE, DATA_DIR, MODEL_PATH):
    log("path", p, "exists" if p.exists() else "MISSING")
subprocess.run("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader", shell=True)

server = None
rows = []
try:
    for pat in ("/usr/local/lib/python*/dist-packages/*cutlass*.pth", "/usr/local/lib/python*/site-packages/*cutlass*.pth"):
        for pth in glob.glob(pat):
            try:
                os.unlink(pth)
            except OSError:
                pass
    tmp_whl = Path("/tmp/wheelhouse")
    tmp_whl.mkdir(parents=True, exist_ok=True)
    for w in WHEELHOUSE.glob("*.whl"):
        if "cutlass" in w.name.lower():
            continue
        name = w.name.replace("cu128", "+cu128") if ("cu128" in w.name and "+" not in w.name) else w.name
        tgt = tmp_whl / name
        if not tgt.exists():
            os.symlink(w, tgt)
    wheels = sorted(str(w) for w in tmp_whl.glob("*.whl"))
    log(f"installing {len(wheels)} wheels")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "--force-reinstall", *wheels], check=True)
    importlib.invalidate_caches()
    log("wheelhouse installed")

    if SUB_DIR.exists():
        shutil.rmtree(SUB_DIR)
    SUB_DIR.mkdir(parents=True)
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(SUBMISSION_ZIP_B64))) as zf:
        zf.extractall(SUB_DIR)
    log("submission files:", sorted(str(p.relative_to(SUB_DIR)) for p in SUB_DIR.rglob("*") if p.is_file()))

    import litellm
    import pandas as pd  # noqa: F401
    import torch
    import yaml
    from adk_submission import VllmConfig, VllmServer, discover_adapters
    from google.adk.agents.context_cache_config import ContextCacheConfig
    from google.adk.apps._configs import EventsCompactionConfig
    from swegemma.config import ALLOWED_ADAPTER_EXTENSIONS, EvalConfig, build_submission_limits
    from swegemma.evaluate import Evaluator
    from swegemma.models import load_tasks
    from adk_submission import discover_declared_models

    litellm.drop_params = True
    tasks_all = load_tasks(DATA_DIR / "tasks.jsonl")
    tasks = [t for t in tasks_all if t.instance_id in TASK_IDS]
    tasks.sort(key=lambda t: TASK_IDS.index(t.instance_id))
    log("tasks:", [t.instance_id for t in tasks])

    declared = sorted(discover_declared_models(SUB_DIR))
    log('declared models:', declared)
    adapters = discover_adapters(str(SUB_DIR), adapter_extensions=ALLOWED_ADAPTER_EXTENSIONS)
    gpu_count = torch.cuda.device_count() if torch.cuda.is_available() else 1
    tp = 4 if gpu_count >= 4 else (2 if gpu_count >= 2 else 1)
    log(f"gpus={gpu_count} tp={tp}")
    cfg = VllmConfig(
        model=str(MODEL_PATH), port=8000, host="127.0.0.1",
        tool_call_parser="gemma4", reasoning_parser="gemma4", max_model_len=32768,
        dtype="bfloat16" if (torch.cuda.is_available() and torch.cuda.is_bf16_supported()) else "auto",
        gpu_memory_utilization=0.90, enable_auto_tool_choice=True,
        enable_lora=True, max_loras=8, max_lora_rank=128, tensor_parallel_size=tp, startup_timeout=60 * 25,
    )
    server = VllmServer(cfg, adapter_manifest=adapters)
    server.start()
    log("vLLM up at", server.base_url)
    models = server.create_model_registry(aliases=sorted(set(declared) | {TARGET_MODEL_NAME}), model_prefix="openai/", api_key="EMPTY")

    raw = yaml.safe_load((SUB_DIR / "eval_config.yaml").read_text(encoding="utf-8"))
    ev = raw.get("evaluation", raw)
    limits, gen_constraints = build_submission_limits()
    eval_config = EvalConfig(
        tasks_path=DATA_DIR / "tasks.jsonl", snapshots_dir=DATA_DIR / "snapshots", results_dir=RESULTS,
        submission_dir=SUB_DIR, models=models, sandbox="subprocess",
        timeout_seconds=int(ev.get("timeout_seconds", 300)),
        max_time_minutes=float(ev.get("max_time_minutes", 60.0)),
        max_tool_calls=int(ev.get("max_tool_calls", 100)),
        max_turns=int(ev["max_turns"]) if ev.get("max_turns") is not None else None,
        limits=limits, generation_constraints=gen_constraints, adapter_manifest=adapters,
        context_cache_config=ContextCacheConfig(min_tokens=2048, ttl_seconds=1800, cache_intervals=10),
        events_compaction_config=EventsCompactionConfig(compaction_interval=15, overlap_size=2, token_threshold=14336, event_retention_size=5),
        graph_dir=str(DATA_DIR / "graphs"), embeddings_dir=str(DATA_DIR / "embeddings"),
        wheels_dir=DATA_DIR / "wheels", verbose=False,
    )
    evaluator = Evaluator(eval_config)
    for i, t in enumerate(tasks, 1):
        log(f"[{i}/{len(tasks)}] {t.instance_id} start")
        t1 = time.time()
        try:
            r = asyncio.run(evaluator.evaluate_task(task=t, task_index=i, total_tasks=len(tasks)))
            row = dict(id=t.instance_id, resolved=bool(r.resolved), exit=r.test_exit_code,
                       patch_chars=len(r.agent_patch or ""), tool_calls=r.tool_calls,
                       seconds=round(r.duration_seconds, 1), error=str(getattr(r, "error", "") or "")[:300])
        except Exception as e:  # noqa: BLE001
            row = dict(id=t.instance_id, resolved=False, error=f"{type(e).__name__}: {e}"[:400], seconds=round(time.time() - t1, 1))
            traceback.print_exc()
        rows.append(row)
        log("RESULT", json.dumps(row))
except Exception:  # noqa: BLE001
    traceback.print_exc()
finally:
    try:
        if server is not None:
            server.stop()
    except Exception:  # noqa: BLE001
        pass
    (WORKING / f"summary_{LABEL}.json").write_text(json.dumps(rows, indent=1))
    log("SUMMARY", json.dumps(rows))
    n = sum(1 for r in rows if r.get("resolved"))
    log(f"RESOLVED {n}/{len(rows)}")
