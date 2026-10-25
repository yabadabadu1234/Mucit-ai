import sys
import time

import numpy as np

from korpus import sureler
from vektor import ONBELLEK, Zemin

ONBELLEK.mkdir(parents=True, exist_ok=True)
z = Zemin()
s_hepsi = sureler()
sira = [int(x) for x in sys.argv[1:]] or [1, 2] + sorted(s_hepsi, key=lambda s: sum(len(k) for _, k in s_hepsi[s]))
gorulen = set()
for s in sira:
    if s in gorulen:
        continue
    gorulen.add(s)
    yol = ONBELLEK / ("sure%03d.npz" % s)
    if yol.exists():
        continue
    t0 = time.time()
    ayet, surp, tok, gizli = z.sure(s_hepsi[s])
    np.savez(yol, ayet=ayet, surp=surp, tok=tok, gizli=gizli)
    print(s, len(ayet), "kelime", int(tok.sum()), "token", round(time.time() - t0, 1), "sn", flush=True)
