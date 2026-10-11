import itertools, json, numpy as np
from model_m import *
def yuk(p):
    H=np.array([1,2,4,8,16,24])*W; gel=(1-p['gider'])*H
    vergi=tevkifat(H,p['gider']); pe=prim_e(p,H); py=prim_y(p,H)
    return float(((pe-py)/gel).max()), float(max(((vergi+pe)/gel).max(),((vergi+py)/gel).max()))
GRID=list(itertools.product([0.08,0.12,0.16,0.20,0.25,0.30,0.40,0.60],[0.04,0.06,0.08,0.10,0.12,0.15,0.20],[0,2,4],[2,3],[0,0.01,0.02,0.03],[1.0,1.5,2.0,3.0]))
ham=[]
for r_e,r_y,e0,kul,lev,prog in GRID:
    kw=dict(r_e=r_e,r_y=r_y,e0=e0,kulucka=kul,levy=lev,prog=prog)
    p=pm("Orta",**kw); fark,top=yuk(p)
    if top>0.50: continue
    ham.append((fark,top,kos(p)[0],kos(pm("Kötümser",**kw))[0],kw))
FR=[]
for tol in [0.08,0.12,0.16,0.20,0.25,0.30,0.40,0.60]:
    ok=[h for h in ham if h[0]<=tol and h[3]>0]
    if ok:
        b=max(ok,key=lambda h:h[2]); FR.append(dict(tol=tol,fark=b[0],yuk=b[1],orta=b[2]/1e9,kot=b[3]/1e9,kw=b[4]))
        print("tol %.2f  Orta %.2f Kötümser %.2f  fark %.3f yük %.3f"%(tol,b[2]/1e9,b[3]/1e9,b[0],b[1]),b[4])
    else: print("tol",tol,"uygun yok")
json.dump(FR,open('sonuc_frontier.json','w'),ensure_ascii=False,indent=1)
