"""Doğrulanmış görev üretim kernel'ini tek dosyada derler (Kaggle CPU, internet açık).

Kullanım: python3 build_uret_kernel.py ÇIKTI_DİZİNİ
Gömülen modüller: swe_dogrula.py, yarisma_ortam.py, yarisma_uret.py.
Kernel: Python 3.13'ü uv ile kurar; yarışma verisini (tasks.jsonl, snapshots, wheels, docker)
/kaggle/input altında bulur; yarisma_uret.main() çalışır.
"""
import base64
import json
import os
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
MODULES = ["swe_dogrula.py", "yarisma_ortam.py", "yarisma_uret.py"]
MARK = "# ---- KOŞU ----"

PRELUDE = '''# -*- coding: utf-8 -*-
# Otomatik üretildi (build_uret_kernel.py). Elle düzenlemeyin; kaynak: gemma_ajan/veri.
import base64
import glob
import os
import shutil
import subprocess
import sys
import zlib

FILES = {
__FILES__}

W = "/kaggle/working/kod"
os.makedirs(W, exist_ok=True)
for _name, _blob in FILES.items():
    with open(os.path.join(W, _name), "wb") as _fh:
        _fh.write(zlib.decompress(base64.b64decode(_blob)))
sys.path.insert(0, W)


def _bul(kalip):
    for _yol in glob.glob(kalip, recursive=True):
        return _yol
    raise SystemExit("yarışma verisi bulunamadı: " + kalip)


# Yarışma verisi (competition_sources ile bağlanır)
os.environ["YARISMA_TASKS"] = _bul("/kaggle/input/**/tasks.jsonl")
os.environ["SWE_SNAPSHOTS"] = os.path.dirname(_bul("/kaggle/input/**/snapshots/*.tgz"))
os.environ["YARISMA_WHEELS"] = os.path.dirname(_bul("/kaggle/input/**/wheels/*.whl"))
os.environ["YARISMA_DOCKER"] = os.path.dirname(_bul("/kaggle/input/**/docker/imp.py"))
os.environ["YARISMA_OUT"] = "/kaggle/working/uretim"

# Python 3.13 (yarışma imajıyla aynı sürüm): uv ile
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "uv"], check=True)
_uv = shutil.which("uv") or os.path.join(os.path.dirname(sys.executable), "uv")
subprocess.run([_uv, "python", "install", "3.13"], check=True)
_py313 = subprocess.run([_uv, "python", "find", "3.13"], capture_output=True, text=True, check=True).stdout.strip()
os.environ["YARISMA_PYTHON313"] = _py313
print("python 3.13:", _py313, flush=True)

import yarisma_uret  # noqa: E402

''' + MARK + "\n"

SON = '''
if __name__ == "__main__":
    yarisma_uret.main()
'''


def blob(path):
    with open(path, "rb") as f:
        return base64.b64encode(zlib.compress(f.read(), 9)).decode("ascii")


def build(out_dir, kimlikler=None):
    os.makedirs(out_dir, exist_ok=True)
    files = "".join(f'    "{m}": "{blob(os.path.join(HERE, m))}",\n' for m in MODULES)
    if kimlikler:
        files += f'    "kimlikler.txt": "{base64.b64encode(zlib.compress(chr(10).join(kimlikler).encode(), 9)).decode("ascii")}",\n'
    script = PRELUDE.replace("__FILES__", files) + SON
    if kimlikler:
        script = script.replace('os.environ["YARISMA_OUT"]', 'os.environ["YARISMA_IDS"] = os.path.join(W, "kimlikler.txt")\nos.environ["YARISMA_OUT"]', 1)
    compile(script, "gemma4-verified-producer.py", "exec")
    yol = os.path.join(out_dir, "gemma4-verified-producer.py")
    with open(yol, "w", encoding="utf-8") as f:
        f.write(script)
    meta = {
        "id": "ulankaggle/gemma4-verified-producer",
        "title": "Gemma4 Verified Producer",
        "code_file": "gemma4-verified-producer.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": False,
        "enable_tpu": False,
        "enable_internet": True,
        "dataset_sources": [],
        "kernel_sources": [],
        "competition_sources": ["gemma-4-developer-agent"],
        "model_sources": [],
    }
    with open(os.path.join(out_dir, "kernel-metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    return yol


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "uret_kernel")
    kimlik_dosyasi = sys.argv[2] if len(sys.argv) > 2 else None
    kimlikler = [s.strip() for s in open(kimlik_dosyasi, encoding="utf-8") if s.strip()] if kimlik_dosyasi else None
    print("yazıldı:", build(out, kimlikler))
