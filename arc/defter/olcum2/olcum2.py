import numpy as np

D8_ADEDI = 8
RENK_KAYMA_ADEDI = 9


def d8(g, k):
    a = np.asarray(g)
    if k >= 4:
        a = a.T
    return np.rot90(a, k % 4)


def d8_ters(g, k):
    a = np.rot90(np.asarray(g), -(k % 4))
    if k >= 4:
        a = a.T
    return a


def renk_kaydir(g, s):
    a = np.asarray(g)
    return np.where(a == 0, 0, (a - 1 + s) % RENK_KAYMA_ADEDI + 1)


def renk_kaydir_ters(g, s):
    return renk_kaydir(g, (-s) % RENK_KAYMA_ADEDI)


def donustur(g, k, s):
    return renk_kaydir(d8(g, k), s)


def donustur_ters(g, k, s):
    return d8_ters(renk_kaydir_ters(g, s), k)


def _cift(p, k, s):
    return {"input": donustur(p["input"], k, s).tolist(), "output": donustur(p["output"], k, s).tolist()}


def birakma_turetmeleri(gorev, adet):
    ornekler = gorev["train"]
    n = len(ornekler)
    if n < 2:
        return []
    cikti = []
    for i in range(adet):
        j = i % n
        k = (i // n) % D8_ADEDI
        s = (i // (n * D8_ADEDI)) % RENK_KAYMA_ADEDI
        sira = [(j + 1 + m) % n for m in range(n - 1)]
        cikti.append({
            "train": [_cift(ornekler[m], k, s) for m in sira],
            "test": [_cift(ornekler[j], k, s)],
            "kaynak": {"birakilan": j, "d8": k, "kayma": s},
        })
    return cikti


def program_ile_cogalt(sinayici, gorev, adet):
    taban = [p["input"] for p in gorev["train"]] + [t["input"] for t in gorev.get("test", [])]
    cikti = []
    for i in range(adet):
        g = taban[i % len(taban)]
        k = (i // len(taban)) % D8_ADEDI
        s = (i // (len(taban) * D8_ADEDI)) % RENK_KAYMA_ADEDI
        girdi = donustur(g, k, s).tolist()
        sonuc = sinayici(girdi)
        if sonuc is not None:
            cikti.append({"input": girdi, "output": np.asarray(sonuc).tolist(), "kaynak": {"d8": k, "kayma": s, "girdi": i % len(taban)}})
    return cikti


import glob, json, os, subprocess, sys, time, traceback
GPU = os.environ.get("MUCIT_GPU")
if GPU is None:
    T = time.time()
    tk = sorted(__import__("glob").glob("/kaggle/input/**/fla_core*.whl", recursive=True)) + sorted(__import__("glob").glob("/kaggle/input/**/flash_linear_attention*.whl", recursive=True))
    r = subprocess.run([sys.executable, "-m", "pip", "install", "--no-index", "--no-deps"] + tk, capture_output=True, text=True)
    print("fla kurulum", tk, r.returncode, (r.stdout + r.stderr)[-300:], flush=True)
    isciler = []
    for i in range(4):
        e = dict(os.environ, MUCIT_GPU=str(i), CUDA_VISIBLE_DEVICES=str(i))
        isciler.append(subprocess.Popen([sys.executable, os.path.abspath(__file__)], env=e, stdout=open("/kaggle/working/isci%d.log" % i, "w"), stderr=subprocess.STDOUT))
    for p in isciler:
        p.wait(timeout=540)
    for i in range(4):
        print("=== ISCI", i, "GPU", i, "===")
        print(open("/kaggle/working/isci%d.log" % i).read()[-4500:])
    print("TOPLAM SN", round(time.time() - T, 1))
    sys.exit(0)
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import peft.import_utils as _iu
_iu.is_torchao_available = lambda: False
import peft.tuners.lora.torchao as _tt
_tt.is_torchao_available = lambda: False
from peft import LoraConfig, get_peft_model

T0 = time.time()
IC_HUDUT = 450
EGITIM_SN = 45
KAYNAK = "/kaggle/input/competitions/arc-prize-2026-arc-agi-2/"


def gecen():
    return time.time() - T0


def yaz(*a):
    print("[%6.1f]" % gecen(), *a, flush=True)


def metin(g):
    return "\n".join("".join(str(int(x)) for x in r) for r in g)


def istem(demolar, girdi):
    s = ""
    for d in demolar:
        s += "I\n" + metin(d["input"]) + "\nO\n" + metin(d["output"]) + "\n\n"
    return s + "I\n" + metin(girdi) + "\nO\n"


def coz(metni):
    sat = [x for x in metni.strip().split("\n") if x.strip() != ""]
    try:
        return [[int(c) for c in x if c.isdigit()] for x in sat]
    except Exception:
        return None


yaz("torch", torch.__version__, "gpu", torch.cuda.device_count())
try:
    import fla
    yaz("fla", getattr(fla, "__version__", "?"))
except Exception as e:
    yaz("fla yok", repr(e)[:200])
yol = os.path.dirname(sorted(glob.glob("/kaggle/input/models/limamateus/qwen3-5-4b/pytorch/default/*/**/config.json", recursive=True))[0])
yaz("model yolu", yol, os.listdir(yol))
cfg = json.load(open(os.path.join(yol, "config.json")))
tc = cfg.get("text_config", cfg)
yaz("config", json.dumps({k: tc.get(k) for k in ("model_type", "num_hidden_layers", "hidden_size", "num_attention_heads", "num_key_value_heads", "head_dim", "layer_types", "full_attention_interval", "linear_num_value_heads", "linear_key_head_dim", "max_position_embeddings")}))
tok = AutoTokenizer.from_pretrained(yol)
t = time.time()
model = AutoModelForCausalLM.from_pretrained(yol, dtype=torch.bfloat16).to("cuda:0")
yaz("model yuklendi sn", round(time.time() - t, 1), type(model).__name__, "bellek GB", round(torch.cuda.memory_allocated() / 1e9, 2))

bul = lambda ad: sorted(glob.glob("/kaggle/input/**/" + ad, recursive=True))
yaz("veri dizini", sorted(os.listdir("/kaggle/input")), [os.listdir(x)[:6] for x in glob.glob("/kaggle/input/competitions/*")])
ev = json.load(open(bul("arc-agi_evaluation_challenges.json")[0]))
sol = json.load(open(bul("arc-agi_evaluation_solutions.json")[0]))
adaylar = []
for k, g in ev.items():
    if len(g["test"]) == 1:
        n = len(tok(istem(g["train"], g["test"][0]["input"]) + metin(sol[k][0]))["input_ids"])
        adaylar.append((n, k))
adaylar.sort()
secilen = [k for n, k in adaylar[:8]][int(GPU)::4]
yaz("isci", GPU, "secilen gorevler", secilen)


def uret(m, p, azami):
    girdi = tok(p, return_tensors="pt").to("cuda:0")
    with torch.no_grad():
        o = m.generate(**girdi, max_new_tokens=azami, do_sample=False)
    return tok.decode(o[0][girdi["input_ids"].shape[1]:], skip_special_tokens=True)


sonuc = []
for k in secilen:
    if gecen() > IC_HUDUT - 90:
        yaz("ic hudut: kalan gorevler atlandi")
        break
    g = ev[k]
    dogru = sol[k][0]
    azami = int(len(tok(metin(dogru) + "\n")["input_ids"]) * 1.3) + 8
    p = istem(g["train"], g["test"][0]["input"])
    t = time.time()
    c0 = coz(uret(model, p, azami))
    s0 = time.time() - t
    yaz(k, "LoRA ONCESI dogru" if c0 == dogru else "LoRA ONCESI yanlis", "uretim sn", round(s0, 1), "istem belirteci", len(tok(p)["input_ids"]))
    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()
    pm = get_peft_model(model, LoraConfig(r=16, lora_alpha=32, target_modules="all-linear", task_type="CAUSAL_LM"))
    opt = torch.optim.AdamW([x for x in pm.parameters() if x.requires_grad], lr=2e-4)
    tu = birakma_turetmeleri(g, 72 * len(g["train"]))
    pm.train()
    t = time.time()
    adim = 0
    belirtec = 0
    zirve = 0
    while time.time() - t < EGITIM_SN and gecen() < IC_HUDUT:
        d = tu[adim % len(tu)]
        pr = istem(d["train"], d["test"][0]["input"])
        cev = metin(d["test"][0]["output"]) + "\n"
        a = tok(pr, return_tensors="pt")["input_ids"]
        b = tok(cev, return_tensors="pt")["input_ids"]
        ids = torch.cat([a, b], 1).to("cuda:0")
        etiket = ids.clone()
        etiket[:, : a.shape[1]] = -100
        lg = pm(input_ids=ids, logits_to_keep=b.shape[1] + 1).logits
        kayip = torch.nn.functional.cross_entropy(lg[0, :-1].float(), b[0].to("cuda:0"))
        kayip.backward()
        opt.step()
        opt.zero_grad()
        adim += 1
        belirtec += ids.shape[1]
        zirve = max(zirve, torch.cuda.max_memory_allocated() / 1e9)
    yaz(k, "egitim adim", adim, "sn", round(time.time() - t, 1), "belirtec/sn", round(belirtec / (time.time() - t)), "son kayip", round(kayip.item(), 4), "zirve GB", round(zirve, 2))
    pm.eval()
    t = time.time()
    c1 = coz(uret(pm, p, azami))
    s1 = time.time() - t
    yaz(k, "LoRA SONRASI dogru" if c1 == dogru else "LoRA SONRASI yanlis", "uretim sn", round(s1, 1))
    sonuc.append({"gorev": k, "once": c0 == dogru, "sonra": c1 == dogru, "adim": adim})
    model = pm.unload()
    del pm, opt
    torch.cuda.empty_cache()
yaz("OZET", json.dumps(sonuc), "toplam sn", round(gecen(), 1))
