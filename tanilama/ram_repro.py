import sys, os, gc, torch, torch.nn as nn
sys.path.insert(0, '/home/user/Mucit-ai/mucit_ai_esas/mucit_ai')
import logging
logging.disable(logging.INFO)
from checkpoint_manager import NPZCheckpointManager

def rss_mb():
    with open('/proc/self/status') as f:
        for l in f:
            if l.startswith('VmRSS'):
                return int(l.split()[1]) / 1024.0
    return -1.0

class Blok(nn.Module):
    def __init__(self, n):
        super().__init__()
        self.l = nn.Linear(n, n)

moduller = {f'm{i}': Blok(1400) for i in range(12)}
moduller['bos'] = nn.Module()
params = [p for m in moduller.values() for p in m.parameters()]
say = sum(p.numel() for p in params)
print(f'parametre sayisi: {say/1e6:.1f} M ({say*4/1024**2:.0f} MB fp32)')
opt = torch.optim.AdamW(params, lr=1e-4)
for p in params:
    p.grad = torch.randn_like(p)
opt.step()

mgr = NPZCheckpointManager(checkpoint_dir='/tmp/claude-0/-home-user-Mucit-ai/561ec71f-c30d-5584-97a4-b3f0a186b0a8/scratchpad/ckpt_repro')
mgr.max_mb = 1e9

print(f'{"adim":>5} {"RSS MB":>10} {"artis":>8}')
onceki = rss_mb()
print(f'{0:>5} {onceki:>10.1f} {0.0:>8.1f}')
for adim in range(1, 9):
    mgr.save_pytorch_model(step=adim, token_offset=adim * 256, model=moduller,
                           optimizer=opt, loss_history=[1.0], is_best=True, bekle=True)
    mgr.load_pytorch_model(moduller, opt)
    gc.collect()
    r = rss_mb()
    print(f'{adim:>5} {r:>10.1f} {r-onceki:>8.1f}')
    onceki = r
