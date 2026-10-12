import glob, json, os, subprocess, sys, time
T0 = time.time()
IC_HUDUT = 540


def gecen():
    return time.time() - T0


def yaz(*a):
    print("[%6.1f]" % gecen(), *a, flush=True)


tk = sorted(glob.glob("/kaggle/input/**/fla_core*.whl", recursive=True)) + sorted(glob.glob("/kaggle/input/**/flash_linear_attention*.whl", recursive=True))
r = subprocess.run([sys.executable, "-m", "pip", "install", "--no-index", "--no-deps"] + tk, capture_output=True, text=True)
yaz("fla kurulum", r.returncode)

import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, FineGrainedFP8Config, StoppingCriteria, StoppingCriteriaList
from accelerate import init_empty_weights
from transformers.quantizers.quantizer_finegrained_fp8 import FineGrainedFP8HfQuantizer
FineGrainedFP8HfQuantizer.update_tp_plan = lambda self, config: config

yaz("torch", torch.__version__, "gpu sayisi", torch.cuda.device_count())
yol = os.path.dirname(sorted(glob.glob("/kaggle/input/models/mikedan7/qwen3-8-27b-fp8-official/pytorch/hf-fp8/*/**/config.json", recursive=True))[0])
yaz("model yolu", yol)
cfg = AutoConfig.from_pretrained(yol)
tok = AutoTokenizer.from_pretrained(yol)

with init_empty_weights():
    bos = AutoModelForCausalLM.from_config(cfg)
yaz("sinif", type(bos).__name__)
ust = sorted({".".join(n.split(".")[:2]) if n.startswith("model.layers") else (".".join(n.split(".")[:2]) if n.startswith("model.") else n.split(".")[0]) for n, _ in bos.named_modules() if n})
yaz("ust modul adlari", [x for x in ust if "layers." not in x][:20], "katman sayisi", cfg.get_text_config().num_hidden_layers)
nl = cfg.get_text_config().num_hidden_layers
parca = [(i * nl) // 4 for i in range(5)]
hrt = {}
for n, _ in bos.named_modules():
    if n.startswith("model.layers.") and n.count(".") == 2:
        i = int(n.split(".")[2])
        hrt[n] = [g for g in range(4) if parca[g] <= i < parca[g + 1]][0]
for n, _ in bos.named_children():
    pass
for n, m in bos.named_modules():
    if n and n.count(".") <= 1 and not n.startswith("model.layers"):
        hrt[n] = 0 if ("embed" in n or "visual" in n or "rotary" in n) else 3
hrt["lm_head"] = 3
for k in list(hrt):
    if k == "model":
        del hrt[k]
yaz("elle yerlesim ozeti", {g: sum(1 for v in hrt.values() if v == g) for g in range(4)}, "parca", parca)
del bos

t = time.time()
model = AutoModelForCausalLM.from_pretrained(yol, dtype=torch.bfloat16, device_map=hrt, quantization_config=FineGrainedFP8Config(dequantize=True))
yaz("yuklendi sn", round(time.time() - t, 1), type(model).__name__, "GPU bellek GB", [round(torch.cuda.memory_allocated(g) / 1e9, 1) for g in range(4)])

KAYNAK = sorted(glob.glob("/kaggle/input/**/arc-agi_evaluation_challenges.json", recursive=True))[0]
ev = json.load(open(KAYNAK))
sol = json.load(open(KAYNAK.replace("challenges", "solutions")))


def metin(g):
    return "\n".join("".join(str(int(x)) for x in r) for r in g)


def istem(g):
    s = "Each puzzle below has example input/output grids (digits are colors, 0 is background). Find the transformation rule from the examples, then apply it to the test input. Think it through, then give the final output grid as rows of digits inside <output></output>.\n\n"
    for i, d in enumerate(g["train"]):
        s += "Example %d input:\n%s\nExample %d output:\n%s\n\n" % (i + 1, metin(d["input"]), i + 1, metin(d["output"]))
    return s + "Test input:\n" + metin(g["test"][0]["input"]) + "\n"


class Sure(StoppingCriteria):
    def __init__(self, son):
        self.son = son

    def __call__(self, ids, scores, **kw):
        return time.time() > self.son


adaylar = sorted((len(tok(istem(g))["input_ids"]), k) for k, g in ev.items() if len(g["test"]) == 1)
os.makedirs("/kaggle/working/ciktilar", exist_ok=True)
for n, k in adaylar[:2]:
    kalan = IC_HUDUT - gecen()
    if kalan < 90:
        yaz("ic hudut: gorev atlandi", k)
        break
    mesaj = [{"role": "user", "content": istem(ev[k])}]
    p = tok.apply_chat_template(mesaj, tokenize=False, add_generation_prompt=True, enable_thinking=True)
    girdi = tok(p, return_tensors="pt").to("cuda:0")
    t = time.time()
    with torch.no_grad():
        o = model.generate(**girdi, max_new_tokens=4000, do_sample=False, stopping_criteria=StoppingCriteriaList([Sure(time.time() + min(kalan - 40, 230))]))
    sn = time.time() - t
    yeni = o[0][girdi["input_ids"].shape[1]:]
    cikti = tok.decode(yeni, skip_special_tokens=False)
    open("/kaggle/working/ciktilar/%s.txt" % k, "w").write(cikti)
    yaz("GOREV", k, "istem belirteci", girdi["input_ids"].shape[1], "uretilen", len(yeni), "sn", round(sn, 1), "belirtec/sn", round(len(yeni) / sn, 2))
    yaz("DOGRU CEVAP:\n" + metin(sol[k][0]))
    print("----- MODELIN URETTIGI (ilk 3500 + son 1500 karakter) -----")
    print(cikti[:3500])
    print(" [...] ")
    print(cikti[-1500:])
    print("----- BITTI -----", flush=True)
yaz("toplam sn", round(gecen(), 1))
