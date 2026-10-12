import numpy as np, math
from genc_model import tarife, TAVAN
print("Tavan üstü bölme: H hasılat, k=ceil(H/tavan) kimlik; normal rejim = tarife(0.7H)+yıllık 4/b primi; mikro = %13,5 H (kademesiz)")
for H in (1.5e6,3.0e6,6.0e6):
    k=math.ceil(H/TAVAN); normal=float(tarife(np.array([0.7*H]))[0])+141699.0; mikro=0.135*H
    print("  H=%.1f mn TL  k=%d  normal %d (%.1f%%)  mikro %d (%.1f%%)  kazanç %d TL (%.1f%% H), ortak başına %d"%(H/1e6,k,normal,100*normal/H,mikro,13.5,normal-mikro,100*(normal-mikro)/H,(normal-mikro)/k))
