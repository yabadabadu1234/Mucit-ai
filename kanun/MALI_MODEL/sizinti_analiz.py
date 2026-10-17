# Tevkifatı atlatan sahte fatura sızıntısı (sizinti) ve kimlik kiralama (kiralama) analizi.
# sizinti: kurumsal akışın tevkifatı hiç ödenmeden dolaşan payı; kayıp = sizinti*kurumsal_pay*N*EH*kv (alıcının gider indirimi)
# kiralama: kiralanan kimlikle yapılan, tevkifatsız gelir payı; kayıp = kiralama*N*ET
import json
from model import *
def uc(p): p=dict(p); p['n_yeni_pay']=1-p['s_kayitli']-p['u_ucretli']; return npv(p)[1][3]['net']/1e9
S=[0,0.02,0.05,0.10,0.20,0.30]; K=[0,0.02,0.05,0.10,0.20]
out={}
for ad in SENARYO:
    base=sc(ad)
    g=[[round(uc(dict(base,sizinti=z,kiralama=k)),2) for z in S] for k in K]
    def kir(key,grid):
        for x in grid:
            if uc(dict(base,**{key:x}))<0: return x
        return None
    # ikili kırılma: sizinti (kiralama=0)
    out[ad]=dict(grid_sizinti=S,grid_kiralama=K,net=g,sizinti_kirilma=kir('sizinti',[i/1000 for i in range(0,1001)]),kiralama_kirilma=kir('kiralama',[i/1000 for i in range(0,1001)]))
    print(ad,"taban",round(uc(base),2),"| sızıntı kırılma:",out[ad]['sizinti_kirilma'],"| kiralama kırılma:",out[ad]['kiralama_kirilma'])
    print("  kiralama\\sizinti "+" ".join("%6.2f"%z for z in S))
    for k,row in zip(K,g): print("  %6.2f           "%k+" ".join("%6.2f"%x for x in row))
json.dump(out,open('sizinti_analiz.json','w'),indent=1,ensure_ascii=False)
