import numpy as np, sys
import genc3, model
from genc3 import REJ, VARSAYILAN, nufus3, sok3, kos3, olc3, kalibre, W
from genc_model import PRIM_AYLIK
VAR={"eğri (F308 öncesi, 11.010 eşik, 6 asgaride tam)":"gelire",
     "A: asgari altı 0, üstü TAM prim (basamak)":"asgari_tam",
     "B: asgari altı 0, üstü min(tam, asgari üstü kısım)":"asgari_ust",
     "C: asgari altı 0, üstü min(tam, yarısı asgari üstü kısım)":"asgari_yari"}
ANAH=["canli12","acik_firma","gecim72","kalici","dip","yikim","net_son","devlet_pv"]
def kos(seedler,N=2000):
    sonuc={ad:{k:[] for k in ANAH} for ad in list(VAR)+["mevcut, kayıtlı","tarafsız"]}
    for sd in seedler:
        par=dict(VARSAYILAN); par["b0"]=kalibre(par,N,sd); P=nufus3(N,sd,par); S=sok3(N,72,sd+1)
        for ad,pr in VAR.items():
            rj=dict(REJ["teklif"]); rj["prim"]=pr
            o=olc3(kos3(rj,P,S,N,par))
            for k in ANAH: sonuc[ad][k].append(o[k])
        for ad in ("mevcut, kayıtlı","tarafsız"):
            o=olc3(kos3(REJ[ad],P,S,N,par))
            for k in ANAH: sonuc[ad][k].append(o[k])
    return sonuc
def genc():
    s=kos([20261101+100*i for i in range(6)])
    print("== GENÇ (6 tohum, N=2000, 72 ay) ==")
    print("%-62s"%"rejim"+"".join("%11s"%k for k in ANAH))
    for ad,d in s.items():
        print("%-62s"%ad+"".join("%11.3f"%np.mean(d[k]) for k in ANAH))
def devlet():
    print("\n== DEVLET: yeni prim geliri, 4. yıl (milyar TL), ortalama aylık gelire göre ==")
    orj=model.kisi_basi
    def yap(kural):
        def f(H,p):
            r=orj(H,p); y=(H-r['T'])/12.0
            if kural=="gelire": return r
            if kural=="tam": pr=np.where(y>W,p['prim_ay'],0.0)
            if kural=="ust": pr=np.minimum(p['prim_ay'],np.maximum(y-W,0))
            if kural=="yari": pr=np.minimum(p['prim_ay'],0.5*np.maximum(y-W,0))
            r=dict(r); r['yeni_prim']=12.0*p['prim_ay']*0+12.0*pr*p['prim_toplama']; return r
        return f
    for ad in model.SENARYO:
        p=model.sc(ad); satir=[]
        for kural in ("gelire","tam","ust","yari"):
            model.kisi_basi=yap(kural); ys=model.bes_yil(p); satir.append((kural,ys[3]['net']/1e9,ys[3]['yeni_prim']/1e9))
        model.kisi_basi=orj
        print(ad,"  ".join("%s: net %.2f (prim %.2f)"%x for x in satir))
def manipulasyon():
    print("\n== AYLIK ESİK İSTİSMARI: yıllık net gelir A, aylık eşik W=33.030 ==")
    g=np.random.default_rng(7)
    print("%-12s %-14s %-14s %-14s %-14s"%("A (yıllık)","dürüst(dalgalı)","düzleştirilmiş","aileye 3'e böl","kayıp/yıl"))
    for A in (200e3,396e3,600e3,800e3,1200e3):
        def tam(y): return np.where(y>W,PRIM_AYLIK,0.0).sum()
        def ust(y): return np.minimum(PRIM_AYLIK,np.maximum(y-W,0)).sum()
        d=[]; 
        for _ in range(2000):
            m=np.exp(g.normal(0,0.5,12)); m=m/m.sum()*A; d.append((tam(m),ust(m)))
        dur=np.mean(d,axis=0); duz=np.full(12,A/12); dz=(tam(duz),ust(duz)); ai=np.full(12,A/36); ai3=(3*tam(ai),3*ust(ai))
        print("%-12.0f A:%8.0f B:%8.0f  A:%8.0f B:%8.0f  A:%8.0f B:%8.0f  A:%8.0f B:%8.0f"%(A,dur[0],dur[1],dz[0],dz[1],ai3[0],ai3[1],dur[0]-dz[0],dur[1]-dz[1]))
def oran():
    print("\n== B KURALI: oran duyarlılığı, 4. yıl net (milyar TL) ==")
    orj=model.kisi_basi
    def f(H,p):
        r=orj(H,p); y=(H-r['T'])/12.0
        pr=np.minimum(p['prim_ay'],np.maximum(y-W,0)); r=dict(r); r['yeni_prim']=12.0*pr*p['prim_toplama']; return r
    model.kisi_basi=f
    for ad in model.SENARYO:
        p=model.sc(ad); satir=[]
        for o in (0.135,0.20,0.27):
            p['duz_oran']=o; satir.append("%%%.1f: %.2f"%(o*100,model.bes_yil(p)[3]['net']/1e9))
        p['duz_oran']=0.135; lo,hi=0.135,0.60
        if model.bes_yil(dict(p,duz_oran=hi))[3]['net']>0:
            for _ in range(40):
                m=(lo+hi)/2
                if model.bes_yil(dict(p,duz_oran=m))[3]['net']<0: lo=m
                else: hi=m
            kr="kırılma oranı %%%.1f"%(100*hi)
        else: kr="kırılma yok"
        if model.bes_yil(dict(p,duz_oran=0.135))[3]['net']>=0: kr="%13,5'te zaten pozitif"
        print(ad,"  ".join(satir),"|",kr)
    model.kisi_basi=orj
if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1]=="oran": oran()
    else: genc(); devlet(); manipulasyon(); oran()
