import glob
import subprocess

K = glob.glob("/kaggle/input/datasets/*/arc3-vllm-h100-wheelhouse-v3")[0]


def kos(komut, sure=420):
    try:
        p = subprocess.run(komut, shell=True, capture_output=True, text=True, timeout=sure)
        print("$", komut, "\n", (p.stdout + p.stderr)[-2500:], flush=True)
    except subprocess.TimeoutExpired:
        print("ZAMAN ASIMI", komut, flush=True)


kos("ls %s | grep -i -E '^vllm|outlines|xgrammar|triton|torch-|flashinfer'" % K)
kos("pip install --no-index --no-deps --find-links %s vllm 2>&1 | tail -5" % K)
kos("python -c \"import vllm,sys;print(vllm.__version__)\" 2>&1 | tail -15")
kos("python -c \"import vllm._C\" 2>&1 | tail -8")
