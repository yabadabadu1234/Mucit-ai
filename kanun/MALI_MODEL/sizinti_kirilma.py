import model
from model import sc, yil
def net4(ad,**kw):
    p=sc(ad); p.update(duz_oran=0.135); p.update(kw)
    return yil(p,p['ramp'][3])['net']/1e9
def kirilma(ad,onlem):
    lo,hi=0.0,1.0
    for _ in range(60):
        m=(lo+hi)/2
        if net4(ad,phi=m,onlem=onlem)>0: lo=m
        else: hi=m
    return lo
print("Düz %13,5 tevkifat, yıl-4 net (mlr TL); phi = hasılatın sahte fatura payı; onlem = tedbirin kestiği pay")
for ad in ("Kötümser","Orta","İyimser"):
    p=sc(ad)
    print("%-9s taban phi=%.3f onlem=%.2f net %.2f | phi=0.01 onlem=0 net %.2f | kırılma phi: onlem 0 -> %.3f, onlem 0.37 -> %.3f, onlem 0.5 -> %.3f"%(ad,p['phi'],p['onlem'],net4(ad),net4(ad,phi=0.01,onlem=0.0),kirilma(ad,0.0),kirilma(ad,0.372),kirilma(ad,0.5)))
