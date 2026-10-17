# Üç senaryonun her biri için tornado (4. yıl net, milyar TL; düşük/yüksek uç)
# Parametre aralıkları analiz.py ile aynıdır; taban her senaryonun kendi değeridir.
from model import *
ARALIK={'n_toplam':(255000,1047000),'s_kayitli':(0.0,0.489),'prim_k':(3.0,12.0),'prim_toplama':(0.5,1.0),'u_ucretli':(0.0,0.4),'duz_oran':(0.105,0.27),'medyan_W':(3.0,8.0),'prim_odeme':(0.4,1.0),'phi':(0.0,0.03),'onlem':(0.2,0.8),
 'myo_uygun':(0.1,0.6),'bes_vazgecme':(0.1,0.6),'kdv_donanim_pay':(0.2,0.6),'kgf_alim':(0.02,0.10),'kgf_temerrut':(0.05,0.20),'marj':(0.35,0.65),'sigma':(0.6,1.2)}
def net4(p): return npv(p)[1][3]['net']
out={}
for ad in SENARYO:
    base=sc(ad); b0=net4(base)
    T=[]
    for k,(a,b) in ARALIK.items():
        pa=dict(base); pa[k]=a; pb=dict(base); pb[k]=b
        T.append((k,a,b,(net4(pa)-b0)/1e9,(net4(pb)-b0)/1e9))
    T.sort(key=lambda x:-max(abs(x[3]),abs(x[4])))
    out[ad]=(b0/1e9,T)
    print(ad,"taban net %.2f"%(b0/1e9))
    for k,a,b,lo,hi in T: print("  %-16s %10g %10g  %8.2f %8.2f"%(k,a,b,lo,hi))
import json; json.dump({ad:{'taban':v[0],'tornado':v[1]} for ad,v in out.items()},open('tornado_senaryo.json','w'),ensure_ascii=False,indent=1)
