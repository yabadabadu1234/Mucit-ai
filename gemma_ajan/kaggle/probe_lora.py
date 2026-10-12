#!/usr/bin/env python3
"""LoRA eğitilebilir mi? Tek koşuluk yoklama (yarışmaya bir şey göndermez).

usage: probe_lora.py [--dry]     (KAGGLE_API_TOKEN ortamda olmalı)
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

USER = "ulankaggle"
RUN = r'''
import glob, importlib, json, os, subprocess, sys, time, traceback
from pathlib import Path
T0 = time.time()
def log(*a): print(f"[{time.time()-T0:6.1f}s]", *a, flush=True)
WH = Path("/kaggle/input/datasets/metric/gemma-4-developer-agent-wheelhouse")
MODEL = "/kaggle/input/models/google/gemma-4/other/gemma-4-31b-it-qat-w4a16-ct/2"
OUT = Path("/kaggle/working"); AD = OUT / "adapter_probe"
res = {}
def save(): (OUT / "probe_result.json").write_text(json.dumps(res, indent=1))

for pat in ("/usr/local/lib/python*/dist-packages/*cutlass*.pth", "/usr/local/lib/python*/site-packages/*cutlass*.pth"):
    for q in glob.glob(pat): os.unlink(q)
tmp = Path("/tmp/wheelhouse"); tmp.mkdir(exist_ok=True)
for w in WH.glob("*.whl"):
    if "cutlass" in w.name.lower(): continue
    name = w.name.replace("cu128", "+cu128") if ("cu128" in w.name and "+" not in w.name) else w.name
    if not (tmp / name).exists(): os.symlink(w, tmp / name)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--no-deps", "--force-reinstall", *sorted(str(x) for x in tmp.glob("*.whl"))], check=True)
importlib.invalidate_caches(); log("wheelhouse kuruldu")
log("wheelhouse", sorted(p.name for p in WH.glob("*.whl")) if WH.exists() else "MISSING")
for m in ["torch", "transformers", "peft", "trl", "accelerate", "kernels", "compressed_tensors", "bitsandbytes", "vllm"]:
    try:
        mod = importlib.import_module(m); res[m] = getattr(mod, "__version__", "yok-sürüm")
    except Exception as e:
        res[m] = "YOK: " + type(e).__name__
log("paketler", json.dumps(res)); save()
subprocess.run("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader", shell=True)

STAGE2 = r"""
import json, time, torch, traceback
from pathlib import Path
T0 = time.time()
def log(*a): print(f"[s2 {time.time()-T0:6.1f}s]", *a, flush=True)
MODEL = "%s"; AD = "%s"
out = {}
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import LoraConfig, get_peft_model
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, device_map="auto", torch_dtype=torch.bfloat16)
    log("model yüklendi", type(model).__name__); out["yuklendi"] = True
    names = sorted({n.split(".")[-1] for n, m in model.named_modules() if m.__class__.__name__.endswith("Linear")})
    log("Linear adları", names[:20]); out["linear_adlari"] = names[:20]
    cfg = LoraConfig(r=8, lora_alpha=16, target_modules=r".*language_model.*\.(q_proj|v_proj)", task_type="CAUSAL_LM")
    model = get_peft_model(model, cfg); out["peft_sarildi"] = True
    model.print_trainable_parameters()
    model.gradient_checkpointing_enable() if hasattr(model, "gradient_checkpointing_enable") else None
    model.enable_input_require_grads() if hasattr(model, "enable_input_require_grads") else None
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=1e-4)
    x = tok("def add(a, b):\n    return a + b\n" * 8, return_tensors="pt").to(next(model.parameters()).device)
    losses = []
    for i in range(3):
        o = model(**x, labels=x["input_ids"]); o.loss.backward(); opt.step(); opt.zero_grad()
        losses.append(float(o.loss)); log("adım", i, float(o.loss))
    out["kayiplar"] = losses
    model.save_pretrained(AD); out["kaydedildi"] = sorted(p.name for p in Path(AD).glob("*"))
except Exception:
    out["hata"] = traceback.format_exc()[-1500:]; traceback.print_exc()
Path("/kaggle/working/stage2.json").write_text(json.dumps(out, indent=1))
""" % (MODEL, str(AD))
Path("/tmp/stage2.py").write_text(STAGE2)
if res.get("peft", "").startswith("YOK") or res.get("transformers", "").startswith("YOK"):
    res["sonuc"] = "peft/transformers yok: egitim yolu bu imajda kapali"; save(); log(res["sonuc"]); sys.exit(0)
p = subprocess.run([sys.executable, "/tmp/stage2.py"], timeout=900)
s2 = json.loads(Path("/kaggle/working/stage2.json").read_text()) if Path("/kaggle/working/stage2.json").exists() else {}
res["asama2"] = s2; save(); log("asama2", json.dumps(s2))
if "kaydedildi" not in s2:
    res["sonuc"] = "egitim asamasi gecmedi"; save(); sys.exit(0)

# aşama 3: vLLM adaptörü yükleyip cevap veriyor mu
try:
    for k, v in {"VLLM_WORKER_MULTIPROC_METHOD": "spawn", "VLLM_NO_USAGE_STATS": "1"}.items(): os.environ[k] = v
    import torch, requests
    from adk_submission import VllmConfig, VllmServer
    cfg = VllmConfig(model=MODEL, tool_call_parser="gemma4", reasoning_parser="gemma4", max_model_len=8192,
                     dtype="bfloat16", gpu_memory_utilization=0.90, tensor_parallel_size=4, startup_timeout=900,
                     enable_lora=True, max_lora_rank=8)
    srv = VllmServer(cfg, lora_modules={"probe": str(AD)})
    srv.start(); log("vLLM adaptörle ayakta")
    for mdl in ["probe", MODEL]:
        r = requests.post(srv.base_url + "/chat/completions", json={"model": mdl, "messages": [{"role": "user", "content": "Say hi in one word."}], "max_tokens": 16}, timeout=120)
        res["vllm_" + ("adaptor" if mdl == "probe" else "taban")] = (r.status_code, r.text[:200]); log(mdl, r.status_code, r.text[:200])
    srv.stop(); res["sonuc"] = "TAMAM: egit + kaydet + vLLM'de yukle"
except Exception:
    res["vllm_hata"] = traceback.format_exc()[-1500:]; res["sonuc"] = "vLLM asamasi gecmedi"
    traceback.print_exc()
save(); log("SONUC", res.get("sonuc"))
'''

def main():
    d = Path(tempfile.mkdtemp(prefix="gpu_probe_"))
    (d / "run.py").write_text(RUN)
    meta = {
        "id": f"{USER}/gemma4-lora-probe", "title": "Gemma4 LoRA Probe", "code_file": "run.py",
        "language": "python", "kernel_type": "script", "is_private": True, "enable_gpu": True,
        "enable_tpu": False, "enable_internet": False,
        "dataset_sources": ["metric/gemma-4-developer-agent-wheelhouse"],
        "competition_sources": ["gemma-4-developer-agent"], "kernel_sources": [],
        "model_sources": ["google/gemma-4/Other/gemma-4-31b-it-qat-w4a16-ct/2"],
        "docker_image": "gcr.io/kaggle-private-byod/python@sha256:37c64f7dd9c54116ecd1bcc88817c5469b88387388fade02bfa8bf3fc647d461",
        "machine_shape": "NvidiaL4",
    }
    (d / "kernel-metadata.json").write_text(json.dumps(meta, indent=2))
    print("kernel dir:", d)
    if "--dry" in sys.argv:
        return
    subprocess.run(["kaggle", "kernels", "push", "-p", str(d), "-t", "1500"], check=True)


if __name__ == "__main__":
    main()
