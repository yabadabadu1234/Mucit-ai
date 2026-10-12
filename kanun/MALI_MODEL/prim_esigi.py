import numpy as np
from genc3 import *
KL=[3.0,4.0,5.0,6.0,8.0,12.0]
M=["acik_firma","gecim72","kalici","dip","yikim"]
def kos():
    par=dict(VARSAYILAN); sonuc={}
    for sd in range(8):
        seed=20261101+100*sd
        p=dict(par); p["b0"]=kalibre(p,2000,seed)
        P=nufus3(2000,seed,p); S=sok3(2000,72,seed+1)
        r0=dict(REJ["teklif"]); r0["prim"]="yok"
        sonuc.setdefault("yok",[]).append(olc3(kos3(r0,P,S,2000,p)))
        r1=dict(REJ["teklif"]); r1["prim"]="sabit"
        sonuc.setdefault("sabit",[]).append(olc3(kos3(r1,P,S,2000,p)))
        for k in KL:
            q=dict(p); q["prim_k"]=k
            sonuc.setdefault(k,[]).append(olc3(kos3(REJ["teklif"],P,S,2000,q)))
    return sonuc
if __name__=="__main__":
    s=kos()
    print("Teklif rejimi, prim eğrisi: G=%.0f TL (brüt asgari/3); tam prim %.0f TL/ay; K = k x brüt asgari (%.0f TL)"%(GECIM_HADDI,PRIM_AYLIK,W))
    print("%-8s"%"k"+"".join("%-18s"%m for m in M)+"fark(acik_firma) fark(gecim72)")
    b=np.array([x["acik_firma"] for x in s["yok"]]); bg=np.array([x["gecim72"] for x in s["yok"]])
    for key in ["yok"]+KL+["sabit"]:
        row="%-8s"%str(key)
        for m in M:
            v=np.array([x[m] for x in s[key]]); row+="%.3f±%.3f      "%(v.mean(),1.96*v.std()/np.sqrt(8))
        v=np.array([x["acik_firma"] for x in s[key]])-b; g=np.array([x["gecim72"] for x in s[key]])-bg
        row+="%+.3f±%.3f  %+.3f±%.3f"%(v.mean(),1.96*v.std()/np.sqrt(8),g.mean(),1.96*g.std()/np.sqrt(8))
        print(row)
