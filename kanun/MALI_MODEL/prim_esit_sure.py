import numpy as np
from model import *
P=11808.25; G=W/3.0; GUN=P/30.0
def dagilim(sc_ad='Orta'):
    p=sc(sc_ad); H,w=agirliklar(p); y=(H-0.135*H)/12.0; return y,w
def mevcut(y):
    o=np.clip((y-G)/(6*W-G),0,1); return P*o,30*o
def tasarim(y,T,theta=None):
    c0=9000.0/(12*T); katki=(y>G)
    if theta is None:
        lo,hi=0.0,5.0
        for _ in range(80):
            m=(lo+hi)/2; pr=np.where(katki,np.minimum(P,m*(y-G)),0.0)
            if (w_*pr).sum()<GUN*c0*(w_*katki).sum(): lo=m
            else: hi=m
        theta=(lo+hi)/2
    pr=np.where(katki,np.minimum(P,theta*(y-G)),0.0)
    return theta,pr,np.where(katki,c0,0.0)
y,w_=dagilim()
pm,gm=mevcut(y)
print("Gün fiyatı = tam prim/30 = %.2f TL; katkı yapan (y>G) payı %.3f"%(GUN,(w_*(y>G)).sum()))
print("MEVCUT (orantılı gün): ort. aylık prim %.0f TL, ort. gün %.2f; denge: prim = gün x fiyat -> %.0f"%((w_*pm).sum(),(w_*gm).sum(),(w_*gm).sum()*GUN))
for T in (85,75,65,55,45,35,25):
    th,pr,c=tasarim(y,T)
    d=lambda yy:float(np.minimum(P,th*(yy-G)) if yy>G else 0)
    print("T=%2d yıl: gün/ay %.2f (herkese eşit)  marjinal prim oranı θ=%.3f  prim: y=15k %5.0f | 22k %5.0f | 33k %5.0f | 45k %5.0f | 57k %5.0f  (tavan prim %.0f ulaşılan y=%s)"%(T,9000/(12*T),th,d(15000),d(22000),d(33030),d(45000),d(57000),P,("%.0f"%(G+P/th) if th>0 else '-')))
