import numpy as np
from model import *
GUN=11808.25/30
def oran(y):
    k=y/W
    return np.where(k<1,0.0,np.where(k<2,0.025*(k-1),np.where(k<5,0.025+0.035*(k-2)/3,0.06)))
p=sc('Orta'); H,w=agirliklar(p); y=0.865*H/12
pr=oran(y)*y; od=pr>0
print("Net aylık gelir azami (tavan): %.0f TL = %.2f brüt asgari"%(y.max(),y.max()/W))
print("Prim ödeyenlerin payı (y>1 asgari): %.3f"%(w*od).sum())
print("Ort. prim, tüm katılımcı: %.1f TL/ay; ödeyen başına: %.1f TL"%((w*pr).sum(),(w*pr).sum()/(w*od).sum()))
for k in (1.0,1.2,1.4,1.5,1.73):
    yy=k*W; r=float(oran(yy)); pp=r*yy
    gun=pp/GUN
    print("y=%.2f asgari (%.0f TL): oran %%%.2f prim %.0f TL; gün fiyatıyla karşılığı %.2f gün/ay -> 9000 güne %.0f yıl; orantılı gün %.1f gün/ay"%(k,yy,r*100,pp,gun,(9000/(12*gun) if gun>0 else float('inf')),30*pp/11808.25))
print("65 yıl için (11,54 gün/ay) ödeyen başına gereken prim: %.0f TL"%(GUN*9000/(12*65)))
print("Denge: ödeyenlere ort. verilebilecek gün/ay = %.2f -> yıl %.0f"%((w*pr).sum()/(w*od).sum()/GUN, 9000/(12*(w*pr).sum()/(w*od).sum()/GUN)))
print("--- Aynı biçim, eşikler asgarinin 1/3, 2/3, 5/3'üne çekilirse; plato oranı a (65 yıl denge için) ---")
def oran2(y,a,b=1/3):
    k=y/(W*b*3)
    return np.where(k<b*3*0+1/3*3*b if False else k<1,0.0,0.0)
def sema(y,plato,G0):
    k=y/G0
    return np.where(k<1,0.0,np.where(k<2,plato*(0.025/0.06)*(k-1),np.where(k<5,plato*(0.025+0.035*(k-2)/3)/0.06,plato)))
G0=W/3
for plato in (0.06,0.10,0.15,0.20,0.25,0.30):
    pr=sema(y,plato,G0)*y; od=pr>0
    ort=(w*pr).sum()/(w*od).sum(); gun=ort/GUN
    print("plato %%%2.0f: ödeyen payı %.2f, ödeyen başına ort. prim %.0f TL, verilebilecek gün %.2f/ay -> 9000 güne %.0f yıl; y=15k prim %.0f, y=33k prim %.0f, y=54k prim %.0f"%(plato*100,(w*od).sum(),ort,gun,9000/(12*gun),float(sema(15000,plato,G0)*15000),float(sema(33030,plato,G0)*33030),float(sema(54000,plato,G0)*54000)))
