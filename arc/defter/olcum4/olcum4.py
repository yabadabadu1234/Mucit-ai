import glob
import os
import subprocess
import sys

print(sys.version, flush=True)
kos0 = subprocess.run("find /kaggle/input -maxdepth 4 | head -60", shell=True, capture_output=True, text=True).stdout
print(kos0, flush=True)
kok = [os.path.dirname(f) for f in glob.glob("/kaggle/input/**/vllm-*.whl", recursive=True)]
print("kok", kok, flush=True)
for d in kok:
    for f in sorted(glob.glob(d + "/**/*", recursive=True))[:80]:
        if os.path.isfile(f):
            print(os.path.getsize(f) // 1048576, "MB", f, flush=True)


def kos(komut):
    p = subprocess.run(komut, shell=True, capture_output=True, text=True, timeout=240)
    print("$", komut, "\n", (p.stdout + p.stderr)[-3000:], flush=True)


kos("pip --version; pip list 2>/dev/null | grep -i -E 'torch|vllm|triton|transformers|flashinfer|xformers'")
for d in kok:
    kos("pip install --no-index --find-links %s --dry-run vllm 2>&1 | tail -25" % d)
kos("nvidia-smi --query-gpu=name,memory.total --format=csv")
