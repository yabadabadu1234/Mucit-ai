"""Eğitim kernel'ini tek dosyada derler: modülleri gömer, veriyi çalışma zamanında üretir, eğitimciyi çalıştırır.

Kullanım: python3 build_trainer_kernel.py ÇIKTI_DİZİNİ
Üretilen: ÇIKTI_DİZİNİ/gemma4-agent-fixed-trainer.py ve kernel-metadata.json

Gömülen modüller: kuvvet.py, mantik_veri.py, uret_mantik.py (zlib + base64). Kernel çalışırken
bunları /kaggle/working'e yazar, mantik_veri ile doğrulanmış eğitim verisini üretir ve
trainer_fixed.py'nin gövdesini aynı süreçte çalıştırır. Ağ erişimi gerekmez.
"""
import base64
import json
import os
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
VERI = os.path.join(HERE, "..", "..", "veri")
MODULES = {
    "kuvvet.py": os.path.join(HERE, "kuvvet.py"),
    "mantik_veri.py": os.path.join(VERI, "mantik_veri.py"),
    "uret_mantik.py": os.path.join(VERI, "uret_mantik.py"),
}
TRAINER = os.path.join(HERE, "trainer_fixed.py")
MARK = "# ---- TRAINER GÖVDESİ BAŞLANGICI ----"

PRELUDE = '''# -*- coding: utf-8 -*-
# Otomatik üretildi (build_trainer_kernel.py). Elle düzenlemeyin; kaynak: kaggle/fixed ve veri/.
import base64
import os
import sys
import zlib

FILES = {
__FILES__}

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

''' + MARK + "\n"


def blob(path):
    with open(path, "rb") as f:
        return base64.b64encode(zlib.compress(f.read(), 9)).decode("ascii")


def build(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    files = "".join(f'    "{name}": "{blob(path)}",\n' for name, path in MODULES.items())
    prelude = PRELUDE.replace("__FILES__", files)
    with open(TRAINER, encoding="utf-8") as f:
        body = f.read()
    script = prelude + body
    compile(script, "gemma4-agent-fixed-trainer.py", "exec")
    with open(os.path.join(out_dir, "gemma4-agent-fixed-trainer.py"), "w", encoding="utf-8") as f:
        f.write(script)
    meta = {
        "id": "ulankaggle/gemma4-agent-fixed-trainer",
        "title": "Gemma4 Agent Fixed Trainer",
        "code_file": "gemma4-agent-fixed-trainer.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": False,
        "keywords": ["gpu"],
        "dataset_sources": ["metric/gemma-4-developer-agent-wheelhouse"],
        "kernel_sources": [],
        "competition_sources": ["gemma-4-developer-agent"],
        "model_sources": ["google/gemma-4/Other/gemma-4-31b-it-qat-w4a16-ct/2"],
        "docker_image": "gcr.io/kaggle-private-byod/python@sha256:37c64f7dd9c54116ecd1bcc88817c5469b88387388fade02bfa8bf3fc647d461",
        "machine_shape": "NvidiaL4",
    }
    with open(os.path.join(out_dir, "kernel-metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    return os.path.join(out_dir, "gemma4-agent-fixed-trainer.py")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "trainer_kernel")
    print("yazıldı:", build(out))
