import os, subprocess, time, shutil, glob
t0 = time.time()
def sh(c):
    r = subprocess.run(c, shell=True, capture_output=True, text=True)
    print("$", c); print((r.stdout + r.stderr)[-3000:])
sh("nvidia-smi --query-gpu=index,name,memory.total,compute_cap --format=csv")
sh("nproc; free -g | head -2; df -h /kaggle/working | tail -1")
sh("python -c \"import torch;print(torch.__version__, torch.cuda.is_available(), torch.cuda.device_count())\"")
sh("pip list 2>/dev/null | grep -i -E 'vllm|transformers|peft|unsloth|flash|triton|bitsandbytes|accelerate'")
for p in sorted(glob.glob("/kaggle/input/*"))[:20]:
    print(p, os.listdir(p)[:8])
sh("ls /kaggle/input/competitions 2>&1 | head")
print("sure_sn", round(time.time() - t0, 1))
