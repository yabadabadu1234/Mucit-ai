"""LoRA eğitimcisi: altı kuvvetli gradyan birleştirici (kuvvet.py).

Veri: VERIFIED_JSONL, her satır {"messages": [...], "verified": true, "route": 0..3,
"compiler_score": [0,1], "distance": [0,1]}. Eksik alan varsa satır reddedilir; dosya yoksa
eğitim BAŞLAMAZ. Sahte veri, sahte doğruluk, uydurma sayı yoktur.

Kuvvetler (ayrıntı kuvvet.py): K1 4 güzergâh · K2 uzaklık · K3 PCGrad · K4 taban katsayısı ·
K5 CLM (tüm token'lar) · K6 SFT (yalnız asistan token'ları).

Adım: BATCH örnek için her örnekte iki geri yayılım (CLM, SFT); akışlar katsayılarla
toplanır; PCGrad uygulanır; AdamW bir adım atar. DoRA yok (vLLM desteklemiyor, E3).
"""
import gc
import json
import os
import re
import signal
import sys
import time
from pathlib import Path

WORKING = Path(os.environ.get("WORKING", "/kaggle/working"))
WORKING.mkdir(parents=True, exist_ok=True)
MODEL_PATH = Path(os.environ.get("MODEL_PATH", "/kaggle/input/models/google/gemma-4/other/gemma-4-31b-it-qat-w4a16-ct/2"))
VERIFIED_JSONL = Path(os.environ.get("VERIFIED_JSONL", str(WORKING / "verified_trajectories.jsonl")))
AD = WORKING / "adapter_reasoning"
LR = float(os.environ.get("LR", "1e-4"))
W_TABAN = float(os.environ.get("W_TABAN", "0.1"))
BATCH = int(os.environ.get("BATCH", "8"))
RANK, ALPHA = 8, 16
TARGETS = ("q_proj", "v_proj")
GEN_N = int(os.environ.get("GEN_N", "2"))  # her partide model kendi yanıtını üretir (K2)
GEN_MAX_NEW = int(os.environ.get("GEN_MAX_NEW", "512"))
SCORE_FLOOR = float(os.environ.get("SCORE_FLOOR", "0.1"))  # güzergâh skoru bu değerin altına inmez
MAX_LEN = int(os.environ.get("MAX_LEN", "4096"))
sys.path.insert(0, os.environ.get("VERI_DIR", str(Path(__file__).resolve().parent.parent.parent / "veri")))
EPOCHS = int(os.environ.get("EPOCHS", "1"))
CKPT_EVERY = 5

T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:7.1f}s]", *a, flush=True)


def load_verified(path):
    from kuvvet import validate_row

    rows = []  # her satır: messages, route, compiler_score, distance, prompt, kayit
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
            if "FAIL_TO_PASS" in r:  # SWE görevi: mesafe test koşusundan gelir (swe_dogrula)
                if not r.get("prompt") or not r.get("repo") or not r.get("patch"):
                    raise ValueError(f"{path}:{i} SWE satırında prompt/repo/patch zorunlu")
                rows.append({"msgs": msgs, "route": REPO_ROUTE.get(r["repo"], 3), "compiler_score": 1.0,
                             "distance": 0.0, "prompt": r["prompt"], "gorev": r})
                continue
            route, score, dist = validate_row(r, where=f"{path}:{i}")
            if not r.get("prompt") or not isinstance(r.get("kayit"), dict):
                raise ValueError(f"{path}:{i} 'prompt' ve 'kayit' zorunlu (üretilen yanıtın mesafesi için)")
            rows.append({"msgs": msgs, "route": route, "compiler_score": score, "distance": dist,
                         "prompt": r["prompt"], "kayit": r["kayit"]})
    return rows


REPO_ROUTE = {"fastapi/fastapi": 0, "Textualize/rich": 1, "psf/requests": 2, "encode/httpx": 3}
SWE_TALIMAT = ("\n\nRespond with only a unified git diff (lines starting with 'diff --git', '--- a/', "
               "'+++ b/', '@@') that fixes this issue in the repository source.")
SWE_GEN_MAX_NEW = int(os.environ.get("SWE_GEN_MAX_NEW", "2048"))
SWE_ZAMAN = int(os.environ.get("SWE_ZAMAN", "900"))


def yamayi_cikar(metin):
    """Modelin metninden unified diff'i çıkarır: ```diff bloğu ya da ilk 'diff --git'/'--- a/' satırından
    sona kadar. Bulunamazsa boş dize (sessiz ikame yok: çağıran mesafe 1 yazar)."""
    import re

    blok = re.search(r"```(?:diff|patch)?\s*\n(.*?)```", metin, re.S)
    if blok and ("--- a/" in blok.group(1) or "diff --git" in blok.group(1)):
        return blok.group(1) if blok.group(1).endswith("\n") else blok.group(1) + "\n"
    for satir_no, satir in enumerate(metin.splitlines()):
        if satir.startswith("diff --git") or satir.startswith("--- a/"):
            return "\n".join(metin.splitlines()[satir_no:]) + "\n"
    return ""


def generate_rows(model, tok, pool, start, k, torch):
    """K2: model kendi yanıtını üretir (açgözlü, zar yok). Mesafe program denetçisiyle ölçülür."""
    from mantik_veri import mesafe
    from swe_dogrula import dogrula

    out = []
    model.eval()
    with torch.no_grad():
        for j in range(k):
            src = pool[(start + j) % len(pool)]
            swe = "gorev" in src
            soru = src["prompt"]
            if swe:
                soru = soru + SWE_TALIMAT
            msgs = [{"role": "user", "content": soru}]
            txt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            dev = "cuda:0" if torch.cuda.is_available() else "cpu"
            enc = tok(txt, add_special_tokens=False, return_tensors="pt").input_ids.to(dev)
            gen = model.generate(enc, max_new_tokens=SWE_GEN_MAX_NEW if swe else GEN_MAX_NEW, do_sample=False)
            text = tok.decode(gen[0, enc.shape[1]:], skip_special_tokens=True)
            if swe:
                yama = yamayi_cikar(text)
                # Yama yoksa mesafe 1 (test koşulmaz); varsa gerçek test koşusu ölçer.
                d = dogrula(src["gorev"], yama, None, SWE_ZAMAN, kapi=False)["mesafe"] if yama else 1.0
                out.append({"msgs": msgs + [{"role": "assistant", "content": yama or text}], "route": src["route"],
                            "compiler_score": 0.0, "distance": d, "prompt": src["prompt"], "gorev": src["gorev"]})
                log(f"SWE {src['gorev']['instance_id']}: yama={'var' if yama else 'yok'} mesafe={d:.3f}")
                continue
            d = mesafe(src["kayit"], text)
            out.append({"msgs": msgs + [{"role": "assistant", "content": text}], "route": src["route"],
                        "compiler_score": 0.0, "distance": d, "prompt": src["prompt"], "kayit": src["kayit"]})
    model.train()
    return out


def encode_with_mask(tok, msgs):
    """Konuşmayı şablonla kodla. Dönüş: (ids, asistan_maskesi). Maske her token için True/False:
    True yalnız asistan turunun token'larıdır. CLM kaybı ids'in tamamını, SFT kaybı yalnız
    maskeyi kullanır. Önek tutarlılığı bozulursa örnek atlanır (sessiz ikame yok: hata fırlar)."""
    ids, mask = [], []
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
        mask = mask + [False] * (len(ctx) - len(mask)) + [True] * (len(full) - len(ctx))
        ids = full
        prev.append(m)
    mask = mask[:len(ids)] + [False] * (len(ids) - len(mask))
    return ids[:MAX_LEN], mask[:MAX_LEN]


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
    keys = list(meta.state_dict().keys())
    nl = 1 + max(int(re.search(r"layers\.(\d+)\.", k).group(1)) for k in keys if re.search(r"layers\.(\d+)\.", k))
    dmap = {}
    for k in keys:
        mod = k.rsplit(".", 1)[0]
        mm = re.search(r"^(.*layers\.(\d+))\.", k)
        if mm and "vision" not in k.lower():
            dmap[mm.group(1)] = min(int(mm.group(2)) * ng // nl, ng - 1)
        else:
            dmap[mod] = 0
    return dmap, nl


def batch_plan(batch):
    """Bir mini-parti (doğrulanmış + üretilmiş örnekler). Katsayılar bu partinin n'i ile normalize edilir."""
    from kuvvet import katsayilar

    A, B = katsayilar([{"route": r["route"], "compiler_score": r["compiler_score"], "distance": r["distance"]} for r in batch], W_TABAN)
    return A, B


def main():
    import torch
    import torch.nn.functional as F
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
    from accelerate import init_empty_weights
    from kuvvet import STREAMS, guzergah_skorlari, pcgrad

    if not VERIFIED_JSONL.exists():
        log(f"DURDU: doğrulanmış veri yok ({VERIFIED_JSONL}). Sahte veriyle eğitim yapılmaz.")
        return 2
    rows = load_verified(VERIFIED_JSONL)
    log(f"doğrulanmış yörünge: {len(rows)}; güzergâh dağılımı: {[sum(1 for r in rows if r['route'] == g) for g in range(4)]}")

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

    def flat(gs):
        return torch.cat([g.detach().float().reshape(-1).cpu() for g in gs])

    model.train()
    step = 0
    route_score = [1.0] * 4  # K1 derleyici skoru: güzergâh başına, üretilen çıktıdan güncellenir
    for ep in range(EPOCHS):
        for start in range(0, len(rows), BATCH):
            t_gen = time.time()
            gen = generate_rows(model, tok, rows, start, GEN_N, torch) if GEN_N > 0 else []
            route_score = guzergah_skorlari(route_score, gen, SCORE_FLOOR)
            part = [dict(r, compiler_score=route_score[r["route"]]) for r in rows[start:start + BATCH]]
            log(f"parti {start // BATCH + 1}: {len(gen)} yanıt üretildi ({time.time() - t_gen:.1f}s), "
                f"ortalama mesafe={sum(g['distance'] for g in gen) / max(1, len(gen)):.3f}, "
                f"güzergâh skorları={[round(s, 3) for s in route_score]}")
            batch = part + gen
            A, B = batch_plan(batch)
            streams = [torch.zeros(sum(p.numel() for p in params)) for _ in range(STREAMS)]
            used = 0
            for row, a, b in zip(batch, A, B):
                ids, mask = encode_with_mask(tok, row["msgs"])
                if len(ids) < 2:
                    raise ValueError("kısa örnek: kayıp hesaplanamaz")
                x = torch.tensor([ids], device="cuda:0")
                logits = model(input_ids=x).logits[0, :-1]
                tgt = torch.tensor(ids[1:], device=logits.device)
                nll = F.cross_entropy(logits.float(), tgt, reduction="none")
                m = torch.tensor(mask[1:], device=nll.device, dtype=nll.dtype)
                if float(m.sum()) == 0.0:
                    raise ValueError("asistan token'ı yok: SFT kaybı tanımsız")
                clm = nll.mean()  # K5
                sft = (nll * m).sum() / m.sum()  # K6
                if not torch.isfinite(clm) or not torch.isfinite(sft):
                    log("geçersiz kayıp, örnek atlandı")
                    continue
                gc_clm = torch.autograd.grad(clm, params, retain_graph=True, allow_unused=True)
                gc_sft = torch.autograd.grad(sft, params, allow_unused=True)
                fc = flat([g if g is not None else torch.zeros_like(p) for g, p in zip(gc_clm, params)])
                fs = flat([g if g is not None else torch.zeros_like(p) for g, p in zip(gc_sft, params)])
                for k in range(STREAMS):
                    if a[k] != 0.0:
                        streams[k] += a[k] * fc
                    if b[k] != 0.0:
                        streams[k] += b[k] * fs
                used += 1
                del logits, nll, clm, sft, gc_clm, gc_sft
            if used == 0:
                continue
            total = pcgrad(streams)  # K3
            off = 0
            for p in params:
                n_el = p.numel()
                p.grad = total[off:off + n_el].reshape(p.shape).to(device=p.device, dtype=p.dtype)
                off += n_el
            opt.step()
            opt.zero_grad(set_to_none=True)
            step += 1
            log(f"adım {step} örnek {used} (parti {start // BATCH + 1})")
            if step % CKPT_EVERY == 0:
                save_adapter()
            gc.collect()
    save_adapter("son ")
    log(f"BİTTİ: {step} adım")
    return 0


if __name__ == "__main__":
    sys.exit(main())
