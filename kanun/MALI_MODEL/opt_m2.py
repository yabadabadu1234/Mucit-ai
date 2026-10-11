import itertools, json, numpy as np
from model_m import *
def oran_fark(p):
    H=np.array([2,5,10,24])*W; gel=(1-p['gider'])*H
    return float(((prim_e(p,H)-prim_y(p,H))/gel).max())
rows=[]
for d,r_y,e0,kul,lev,prog in itertools.product([0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0],[0.0,0.04,0.08,0.12,0.16,0.20],[0,2,4],[2,3],[0,0.01,0.02,0.03],[1.0,2.0]):
    kw=dict(prim_devam=d,r_y=r_y,e0=e0,kulucka=kul,levy=lev,prog=prog)
    po=pm("Orta",**kw); pk=pm("Kötümser",**kw)
    H=np.array([1,2,4,8,16,24])*W; gel=(1-po['gider'])*H
    top=float(((tevkifat(H,po['gider'])+np.maximum(prim_e(po,H),prim_y(po,H)))/gel).max())
    if top>1e9: continue
    rows.append((d,top,kos(po)[0]/1e9,kos(pk)[0]/1e9,kw))
# her süreklilik payı için Kötümser>0 olan en kârlı Orta; yük sınırı yok (yüksek gelirli oran)
out=[]
for d in [0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]:
    ok=[r for r in rows if r[0]==d and r[3]>0]
    if ok:
        b=max(ok,key=lambda r:r[2]); out.append(dict(prim_devam=d,orta=b[2],kot=b[3],kw=b[4])); print(d,"Orta %.2f Kötümser %.2f"%(b[2],b[3]),b[4])
    else: print(d,"Kötümser pozitif yok; en iyi Kötümser %.2f"%max(r[3] for r in rows if r[0]==d))
json.dump(out,open('sonuc_frontier2.json','w'),ensure_ascii=False,indent=1)
