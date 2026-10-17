# -*- coding: utf-8 -*-
# Otomatik üretildi (build_trainer_kernel.py). Elle düzenlemeyin; kaynak: kaggle/fixed ve veri/.
import base64
import os
import sys
import zlib

FILES = {
    "kuvvet.py": "eNqdWMtuG8kV3fMrbhgg7o7aHVJ+LOhRAGnsSRx5PIGlDBAQBFFkl+hWv4jqbsqkoP2s8wERkCy8HW280o70Nh+RL8m5VdXsbuoxgyxMkVX3fc99lLvd7mFcbG4oKhcLWcQhzZQIliKlSahi+fW6CFU4Dcl5l3049ChY364oEsvNzfwVvcYRLbPI9TudY8MuFTkf8QHmkD+20kS0ufl6vbkJNjfKHXSIjvtEE7HBUZJvbla0kOBYZnEs1OZmQM9pBlVSzdb/+kiOyspCUs/3n7keVfLTMKVAwsglG5hHmSpJC1Tx5iaCT4rV7BMVMgc3K4hlSlO5EPMBBdnmWpVxubkWlMWwsFyJiBkpGIcEyoYs/LMOsMRnRPMyL2MxsIcwmYQScIPWn0XBR4mg9Zc0lokk56/f/glB8CgXk7AgUCnh0Qo8HDoW+JwQ0gC0iD5sDdWALmDDAT4LMYFpe+T06Wn106Xfm98wFOGoiP5IPRb2gujbd98PqFjfJlRkkUyfsH06mGEaIAAmfeQkIo+gbaVteEl08t3pgJYiTjkdIg/zAlK3Eti5XRmdzmEVgIHOTiNpHlJYhdSjF2yURy9ZiU9/RgbXX1QqIwrXn5HGSmsYAX8aCCwfrEkHP2UEIDkQgByyAKtdG+W+aiRhUhoJBnObG7azyK0ouAKWxEDQ7/zIamSUhxEJTj8MwckyU7kgJYNABmEcqldULoNSIZ2B3FxLnbOiBHu32+18+OFvp29OkKfnnZPTD28Ov+fv9nCPAJPftmG8V2Nsj+OBT3hjecev356cbvmrQ6ZqyOxX5xyFxvl+p9MJ5BktRBwGopBjlV2gaC6ADlSLPOh2dc0RwWwOfs4oZVCsPxvvC8HFmYiYa89Um2PLbZolc5SDGufTTEn6708/0bDn9UdoBhoi08aZz2FhPQrWQb8/k4XT1fK6rr6YNi/aoi1F0KSoVNi78AyS06wgYEaJdCYdEwLrndYswlzSjyIu5RulMuWcdS91EK6sXybnS2RUGMwGpjOlAQr6Uv1GXVllZxl0iUR6tGB9zh17ERvEp2EkQuI2TIG12tY8TA2BswB5mBYencWZKFyXoKJ9PcmyWB8zJ1LQo28ODLWzcPl73+81VPyCx5ds/1XLZZ2nts+L2mclgW4UQ1o4yrVmOtPtt8C1QJuVDGrxccxtF6UXOhkciEKPSojgPuuRbksHPb9fYw9Nf6djD3Q7bxSJaQh9YOofCEMBdKL4EpmLM0CypuP+usJPyEtlAZ4lOvb6S7z+vL6N17eKZxIrrcwZUJIFMkaDNrPBdLThpQWnR3UWr0Y+HZU0F6oIA0lZwzruiJUEbgW5bvPsuIGu6RERl5HyaduXB9pX6j0RiGwiV17T4eP+E+6oBfxM8BcTFuNDrvwqZp0GlAwgrOA7YLgDhK4hdHoeIecYUbBrY9KOmaer3eZ9KVMeODFiYDNZ14B6pNqCHFxDA47ZsI7hyNWsM2atUsBOgMYEfEQHKPNRs1aCvI1rtmmoQEiJ+ORoVzz2GJMvLxMnyF36A0Euf2uhlxktTjXXWMywy4SRU5m3HZoNZD4f1N25R45ZD1zMExje9+q7vjmyAswsWyF3aXMQ+/fnraL4FZmrSH9F7rhhJmHqcJRsmVo/UbdQ7OqotSLUXCx0QFurhT7ZlroZoSEKhidKfk/s7oxzHsLV5MXMjgrcrm8HdKinuMtj/IgczLDGNkfVCC1XZcprWQlPbRGbLYMiOPqff2Mzcg6H4WgYjWDtbDyNExzt0VHjLD8rsBv59D7D6I7DlciXGVpACgHWUG0bdjFPK0jHPLAaRalQk3BihxjZIE5UZncOXubOeKFtFyurYVxyuLZzK2XA9x5L+SRjH7G2VdMOVumJhQrrsV92NeArNKdccuKHo22dovlCI1ecTMtEKuwBxoSGUowsTwPmoU3hrGt3g8vwamDtsB5MNbJ77SK1NnKd7gHVvPNUy9zubq63bFtY+JpwBF0bYn44oBFKQqVKtdVg3PTFfC7TwHGs+bba8Rw50hHwmlGoXEQYDHdt7wWodxpCjeYtldDx9nXELSa3d5NH7h6KkDA9bAqWCzSsRsAQKwzEPTwAauXDxjbIbEHFpqn3H6BGVTExV25F+qI2elgvjbtUL7dUh1WURR2Ko+ps0uoeHHjbHOZTXrbRdkQxzgslRZI3euqzAf29pN/RcZlgO3f2e/s9l8xzyKcmz2Bb/XgHFeaVafsGOTyUZDXPudeY4uP9U4/bw+O3X//59j398GHz8182P78/fFe/AJaxoFTORIHsoDfx+0zNsehyXwI68BDLms+FVPcLrWgS8uuXx6Ie+LwuoAWKiOYqO4dpWCT1C8GnE37RmdddwQ8VfiFFuXno4QNt6DWWBB7rA/sGqXxrt43Ito1WME2HD5N77tAUzDVbxMDU03vWmLxN6kafqOd51OgNfHV+/5WFd8gt7Lx9rHf6LC3CtJStixna0YzNYuvQmr2WNcPzUYs6wJA80GP9EwC/1MZ88vAF9qzCuWOkue6uScz3zd2a053p3EpcbiVqcRBzh5b78/l9xVu7CLAfaHUonfN7aayjnIlPGKCa5RFfTACKDCtuo6sg1dtE6Ryy1HaSGq8fUO+kScsbFrobz/C3Wbf6rlW448IxCRkXMs3x9q2L9zRT04+UY5XGRMKe7Yhlqv+bCJsIIN1m26nf/tPXZG70RinzsF6Ikjm2epgC6Z0Wemf+NM5S6TTw21ZyL4K5KHZceBjTjxP/XyjXIGuJvB/a2mEf351tPewCsYbzA2CuZczOvcdxPPgFhFbfnvJANpjm3W923sYL68MqOY201a6v9+4wOcA2+T/iU3UE",
    "mantik_veri.py": "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",
    "uret_mantik.py": "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",
}

W = os.environ.get("WORKING", "/kaggle/working")
os.makedirs(W, exist_ok=True)
for _name, _blob in FILES.items():
    with open(os.path.join(W, _name), "wb") as _fh:
        _fh.write(zlib.decompress(base64.b64decode(_blob)))
sys.path.insert(0, W)
os.environ["WORKING"] = W
os.environ["VERI_DIR"] = W

import mantik_veri  # noqa: E402

VERI_N = int(os.environ.get("VERI_N", "150"))
VERI_SEED = int(os.environ.get("VERI_SEED", "7"))
_veri_cikti = os.path.join(W, "veri_out")
_sys_argv = sys.argv
sys.argv = ["mantik_veri.py", str(VERI_N), str(VERI_SEED), _veri_cikti]
mantik_veri.main()
sys.argv = _sys_argv
os.environ["VERIFIED_JSONL"] = os.path.join(_veri_cikti, "train.jsonl")

# ---- TRAINER GÖVDESİ BAŞLANGICI ----
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
            route, score, dist = validate_row(r, where=f"{path}:{i}")
            if not r.get("prompt") or not isinstance(r.get("kayit"), dict):
                raise ValueError(f"{path}:{i} 'prompt' ve 'kayit' zorunlu (üretilen yanıtın mesafesi için)")
            rows.append({"msgs": msgs, "route": route, "compiler_score": score, "distance": dist,
                         "prompt": r["prompt"], "kayit": r["kayit"]})
    return rows


def generate_rows(model, tok, pool, start, k, torch):
    """K2: model kendi yanıtını üretir (açgözlü, zar yok). Mesafe program denetçisiyle ölçülür."""
    from mantik_veri import mesafe

    out = []
    model.eval()
    with torch.no_grad():
        for j in range(k):
            src = pool[(start + j) % len(pool)]
            msgs = [{"role": "user", "content": src["prompt"]}]
            txt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            dev = "cuda:0" if torch.cuda.is_available() else "cpu"
            enc = tok(txt, add_special_tokens=False, return_tensors="pt").input_ids.to(dev)
            gen = model.generate(enc, max_new_tokens=GEN_MAX_NEW, do_sample=False)
            text = tok.decode(gen[0, enc.shape[1]:], skip_special_tokens=True)
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
