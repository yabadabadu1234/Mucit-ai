"""Düzeltilmiş LoRA eğitimcisi (gemma4-agent-iterative-trainer'ın yerine).

Düzeltilen hatalar (HATA_ENVANTERI.md, E1-E9):
  E1 sahte doğruluk (exit_code/patch_overlap formülden) -> kaldırıldı; doğruluk yalnız gerçek sonuçtan gelir
  E2 gradyan çarpanı (toplamı her zaman 1.0) -> kaldırıldı
  E3 DoRA (m, dora_m, peft_type DORA; vLLM desteklemiyor) -> düz LoRA
  E4 sohbet şablonu yok, kayıp tüm token'larda -> apply_chat_template + yalnız asistan token'larına kayıp
  E5 dört uyumsuz veri kümesi (glaive/moatless/openhands/swe_agent) -> kaldırıldı; yalnız doğrulanmış yörünge
  E6 adım sayısı zorla 2060'a kilitleniyor, DoRA ağırlıkları devralınıyor -> kaldırıldı
  E7 "ustalık/ZAFER" durma koşulları formülden -> kaldırıldı; durma: veri bitince
Veri kaynağı: VERIFIED_JSONL (her satır {"messages": [{"role":..,"content":..}, ...]}), yalnız gerçek
test sonucuyla doğrulanmış yörüngeler. Dosya yoksa eğitim BAŞLAMAZ (sahte eğitim yok).
"""
import gc
import json
import math
import os
import signal
import sys
import time
import traceback
from pathlib import Path

WORKING = Path(os.environ.get("WORKING", "/kaggle/working"))
WORKING.mkdir(parents=True, exist_ok=True)
MODEL_PATH = Path(os.environ.get("MODEL_PATH", "/kaggle/input/models/google/gemma-4/other/gemma-4-31b-it-qat-w4a16-ct/2"))
VERIFIED_JSONL = Path(os.environ.get("VERIFIED_JSONL", str(WORKING / "verified_trajectories.jsonl")))
AD = WORKING / "adapter_reasoning"
STATE_FILE = WORKING / "stream_state.json"
LR = float(os.environ.get("LR", "1e-4"))
RANK, ALPHA = 8, 16
TARGETS = ("q_proj", "v_proj")
MAX_LEN = int(os.environ.get("MAX_LEN", "4096"))
EPOCHS = int(os.environ.get("EPOCHS", "1"))
CKPT_EVERY = 5

T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:7.1f}s]", *a, flush=True)


def load_verified(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            msgs = r.get("messages")
            if not msgs or not any(m.get("role") == "assistant" for m in msgs):
                raise ValueError(f"{path}:{i} messages alanı eksik ya da asistan turu yok")
            if r.get("verified") is not True:
                raise ValueError(f"{path}:{i} 'verified': true değil; yalnız gerçek test sonucuyla doğrulanmış yörünge kabul edilir")
            rows.append(msgs)
    return rows


def encode_with_mask(tok, msgs):
    """Konuşmayı şablonla kodla. Kayıp yalnız asistan turlarında; önceki bağlam -100 (kayıp dışı).
    Metin üzerinden çalışır (apply_chat_template sürüme göre dict/liste dönebildiği için)."""
    ids, labels = [], []
    prev = []
    for m in msgs:
        if m["role"] != "assistant":
            prev.append(m)
            continue
        ctx_txt = tok.apply_chat_template(prev, tokenize=False, add_generation_prompt=True)
        full_txt = tok.apply_chat_template(prev + [m], tokenize=False, add_generation_prompt=False)
        ctx = tok.encode(ctx_txt, add_special_tokens=False)
        full = tok.encode(full_txt, add_special_tokens=False)
        if full[:len(ids)] != ids[:len(full)] or len(ctx) < len(ids):
            raise ValueError("şablon önek tutarlılığı bozuk; yörünge atlanıyor")
        ids = full
        labels = labels + [-100] * (len(ctx) - len(labels)) + full[len(ctx):]
        labels = labels[:len(ids)] + [-100] * (len(ids) - len(labels))
        prev.append(m)
    return ids[:MAX_LEN], labels[:MAX_LEN]


class LoraWrap:
    """Düz LoRA sargısı: y = base(x) + (alpha/r) * B(A(x)). Taban ağırlık dondurulur."""
    def __init__(self, torch, base, r=RANK, alpha=ALPHA):
        class _M(torch.nn.Module):
            def __init__(s):
                super().__init__()
                s.base = base
                s.scale = alpha / r
                s.A = torch.nn.Parameter(torch.randn(r, base.in_features, dtype=torch.float32) * 0.01)
                s.B = torch.nn.Parameter(torch.zeros(base.out_features, r, dtype=torch.float32))

            def forward(s, x):
                y = s.base(x)
                d = (x.to(torch.float32) @ s.A.t()) @ s.B.t() * s.scale
                return y + d.to(y.dtype)
        self.mod = _M()


def build_device_map(torch, meta, ng):
    """Dil katmanlarını GPU'lara eşit dağıt (4 kart: 0-14, 15-29, 30-44, 45-59)."""
    import re
    keys = list(meta.state_dict().keys())
    nl = 1 + max(int(re.search(r"layers\.(\d+)\.", k).group(1)) for k in keys if re.search(r"layers\.(\d+)\.", k))
    dmap = {}
    for k in keys:
        mod = k.rsplit(".", 1)[0]
        mm = re.search(r"^(.*layers\.(\d+))\.", k)
        if mm and "vision" not in k.lower():
            dmap[mm.group(1)] = min(int(mm.group(2)) * ng // nl, ng - 1)
        elif "vision" in k.lower():
            dmap[mod] = 0
        else:
            dmap[mod] = 0
    return dmap, nl


def main():
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
    from accelerate import init_empty_weights

    if not VERIFIED_JSONL.exists():
        log(f"DURDU: doğrulanmış veri yok ({VERIFIED_JSONL}). Sahte veriyle eğitim yapılmaz.")
        return 2
    rows = load_verified(VERIFIED_JSONL)
    log(f"doğrulanmış yörünge: {len(rows)}")

    tok = AutoTokenizer.from_pretrained(str(MODEL_PATH))
    cfg = AutoConfig.from_pretrained(str(MODEL_PATH))
    ng = torch.cuda.device_count()
    with init_empty_weights():
        meta = AutoModelForCausalLM.from_config(cfg)
    dmap, nl = build_device_map(torch, meta, ng)
    log(f"katman={nl} GPU={ng} katman/GPU={[sum(1 for v in dmap.values() if v == g) for g in range(ng)]}")
    model = AutoModelForCausalLM.from_pretrained(str(MODEL_PATH), device_map=dmap, torch_dtype=torch.bfloat16)
    for g in range(ng):
        log(f"GPU {g} ayrılan bellek: {torch.cuda.memory_allocated(g) / 2**30:.2f} GB")
    for p in model.parameters():
        p.requires_grad_(False)
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()

    import re
    wraps = {}
    pat = re.compile(r".*language_model.*\.(q_proj|v_proj)$")
    for n, m in list(model.named_modules()):
        if pat.match(n) and hasattr(m, "in_features"):
            parent = model.get_submodule(n.rsplit(".", 1)[0])
            dev = next(iter(list(m.parameters()) + list(m.buffers()))).device
            w = LoraWrap(torch, m).mod.to(dev)
            setattr(parent, n.rsplit(".", 1)[1], w)
            wraps[n] = w
    log(f"LoRA hedef katmanı: {len(wraps)}")
    params = [p for w in wraps.values() for p in (w.A, w.B)]
    opt = torch.optim.AdamW(params, lr=LR)

    def save_adapter(tag=""):
        from safetensors.torch import save_file
        AD.mkdir(parents=True, exist_ok=True)
        tensors = {}
        for n, w in wraps.items():
            tensors[f"base_model.model.{n}.lora_A.weight"] = w.A.detach().to(torch.bfloat16).cpu().contiguous()
            tensors[f"base_model.model.{n}.lora_B.weight"] = w.B.detach().to(torch.bfloat16).cpu().contiguous()
        save_file(tensors, str(AD / "adapter_model.safetensors"))
        (AD / "adapter_config.json").write_text(json.dumps({
            "peft_type": "LORA", "task_type": "CAUSAL_LM", "r": RANK, "lora_alpha": ALPHA,
            "lora_dropout": 0.0, "bias": "none", "target_modules": list(TARGETS), "use_dora": False,
            "base_model_name_or_path": str(MODEL_PATH), "inference_mode": True}, indent=2))
        log(f"adaptör kaydedildi {tag}-> {AD}")

    def on_signal(signum, frame):
        log("sinyal alındı, adaptör kaydediliyor")
        save_adapter("acil ")
        os._exit(0)
    signal.signal(signal.SIGTERM, on_signal)

    model.train()
    step = 0
    for ep in range(EPOCHS):
        for msgs in rows:
            ids, labels = encode_with_mask(tok, msgs)
            if sum(1 for x in labels if x != -100) == 0:
                continue
            x = torch.tensor([ids], device="cuda:0")
            y = torch.tensor([labels], device="cuda:0")
            out = model(input_ids=x, labels=y)
            if not torch.isfinite(out.loss):
                log("geçersiz kayıp, adım atlandı")
                continue
            opt.zero_grad(set_to_none=True)
            out.loss.backward()
            opt.step()
            step += 1
            if step % CKPT_EVERY == 0:
                log(f"adım {step} kayıp {float(out.loss):.4f}")
                save_adapter()
            del out
            gc.collect()
    save_adapter("son ")
    log(f"BİTTİ: {step} adım")
    return 0


if __name__ == "__main__":
    sys.exit(main())
