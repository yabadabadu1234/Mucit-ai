import numpy as np, json, sys
from genc_model import tarife, W, ASGARI_NET, TAVAN, PRIM_AYLIK, SABIT_AYLIK, GIDER
SMIN=ASGARI_NET/3
GSS_AYLIK=0.06*W
GSS_GELIR_ESIGI=W/3.0
YAS=np.arange(16,30)
KOHORT=np.array([1.283e6,1.283e6,1.295e6,1.295e6,1.237e6,1.237e6,1.237e6,1.276e6,1.276e6]+[1.35e6]*5)
def giris_orani(a):
    return np.where(a<22,0.025*(a-16)/6.0,0.056)
TIP_AD=["okuyor, lise","okuyor, üniversite","okumuyor, lise altı","okumuyor, lise","okumuyor, lisans+"]
def tip_dagilim(a):
    if a<=17: return np.array([0.75,0,0.25,0,0])
    if a<=22: u=0.45; la=0.12; return np.array([0,u,la,1-u-la,0])
    if a<=24: u=0.20; ls=0.15; la=0.12; return np.array([0,u,la,1-u-ls-la,ls])
    u=0.10; ls=0.35; la=0.12; return np.array([0,u,la,1-u-ls-la,ls])
TIP_PAR={
 "okuyor, lise":dict(okuyor=1,vakit=0.35,erisim=0.20,beceri=1.0,aile=0.7,burs=0.4),
 "okuyor, üniversite":dict(okuyor=1,vakit=0.45,erisim=0.50,beceri=1.2,aile=0.7,burs=0.4),
 "okumuyor, lise altı":dict(okuyor=0,vakit=1.0,erisim=0.25,beceri=0.9,aile=0.35,burs=0.0),
 "okumuyor, lise":dict(okuyor=0,vakit=1.0,erisim=0.45,beceri=1.0,aile=0.35,burs=0.0),
 "okumuyor, lisans+":dict(okuyor=0,vakit=1.0,erisim=1.0,beceri=1.2,aile=0.35,burs=0.0)}
YOL_PAY={"okuyor, lise":(0.30,0.60,0.10),"okuyor, üniversite":(0.45,0.40,0.15),"okumuyor, lise altı":(0.10,0.75,0.15),"okumuyor, lise":(0.20,0.65,0.15),"okumuyor, lisans+":(0.65,0.20,0.15)}
def nufus3(N,seed,par):
    g=np.random.default_rng(seed)
    w=KOHORT*giris_orani(YAS); w=w/w.sum()
    yas=g.choice(YAS,N,p=w)
    tip=np.zeros(N,dtype=int)
    for a in YAS:
        m=yas==a
        if m.any(): tip[m]=g.choice(5,m.sum(),p=tip_dagilim(a))
    yol=np.zeros(N,dtype=int)
    for i,t in enumerate(TIP_AD):
        m=tip==i; yol[m]=g.choice(3,m.sum(),p=YOL_PAY[t])
    P={k:np.array([TIP_PAR[TIP_AD[i]][k] for i in tip],dtype=float) for k in TIP_PAR[TIP_AD[0]]}
    P["aile"]=(g.random(N)<np.clip(P["aile"]*par["aile_olcek"],0,1)).astype(float)
    P["burs"]=(g.random(N)<P["burs"]).astype(float)
    P["tip"]=tip; P["yol"]=yol; P["yas"]=yas
    P["mal"]=(g.random(N)<par["mal_pay"])
    return P
def sok3(N,T,seed):
    g=np.random.default_rng(seed); x=np.zeros(T)
    for t in range(1,T): x[t]=0.9*x[t-1]+g.normal(0,0.06)
    return dict(makro=np.exp(x),beceri=np.exp(g.normal(0,0.35,N)),yeni_u=g.random((T,N)),birim=np.exp(g.normal(0,0.3,(T,N))),
      kayip=g.normal(0,0.04,(T,N)),gurultu=np.exp(g.normal(0,0.15,(T,N))),olay=g.random((T,N))<0.015,denetim=g.random((T,N)),pazar=g.random((T,N))<0.04)
REJ={
 "tarafsız":dict(erisim=1.0,kayip=0.08,vergi="yok",prim="yok",sabit=False,tavan=False,istisna=False,denetim=0.0,z=0.0,gss=False),
 "mevcut, kayıtlı":dict(erisim=1.0,kayip=0.08,vergi="kar",prim="sabit",sabit=True,tavan=False,istisna=True,denetim=0.0,z=0.0,gss=False),
 "mevcut, kayıt dışı":dict(erisim=0.55,kayip=0.12,vergi="yok",prim="yok",sabit=False,tavan=False,istisna=False,denetim=0.004,z=0.3,gss=False),
 "teklif":dict(erisim=1.0,kayip=0.08,vergi="tevk",prim="yok",sabit=False,tavan=True,istisna=True,denetim=0.0,z=1.0,gss=True)}
def kos3(rj,P,S,N,par,T=72):
    yol=P["yol"]; mal=P["mal"]
    c_real=np.where(mal,par["c_mal"],par["c_hiz"])
    s=S["beceri"]*P["beceri"]
    lam_yol=np.where(yol==0,P["erisim"],np.where(yol==1,0.9,0.3))
    b_yol=np.where(yol==0,1.0,np.where(yol==1,0.6,1.8))
    erisim_rj=rj["erisim"]
    if rj["vergi"]=="yok" and rj["erisim"]<1.0: erisim_rj=par["erisim_kd"]
    kapasite=1.0/(1.0+par["kappa"]*rj["z"])*par["talep_bolge"]
    K=np.zeros(N); B=par["b_ilk"]*par["b0"]*b_yol*s*(lam_yol>0.3)
    aktif=np.zeros(N); harap=np.zeros(N,dtype=int); yil=np.zeros(N); genel=np.zeros(N,dtype=bool)
    net=np.zeros((T,N)); devlet=np.zeros((T,N)); iflas=np.zeros(N,dtype=bool); canli=np.zeros((T,N),dtype=bool); ac_ay=np.zeros(N)
    gss_toplam=np.zeros(N)
    for t in range(T):
        ay=t%12
        if ay==0:
            genel=(yil>TAVAN) if (t>0 and rj["tavan"]) else np.zeros(N,dtype=bool); yil=np.zeros(N)
        buf=np.clip(K/(6*SMIN),0,1)
        zor=np.where(yol==2,1/(1+np.exp(-(s-1.15)/0.2)),1.0)
        lam=par["L"]*erisim_rj*lam_yol*P["vakit"]*zor*(1+0.5*buf)*(1+0.02*np.minimum(aktif,36))
        yeni=(S["yeni_u"][t]<np.minimum(lam,0.95)).astype(float)
        kay=np.clip((rj["kayip"] if rj["vergi"]!="yok" or rj["erisim"]>=1.0 else par["kayip_kd"])-0.03*buf+S["kayip"][t],0.0,0.6)
        B=np.where(harap>0,0.0,B*(1-kay)+yeni*par["b0"]*b_yol*s*S["birim"][t])
        B=np.where((yol>0)&S["pazar"][t],B*0.5,B)
        aktif=np.where(harap>0,0,aktif+1)
        s=s*(1+0.003+0.006*buf)
        R=B*S["makro"][t]*S["gurultu"][t]*kapasite
        gig=np.where(harap>0,0.5*ASGARI_NET*P["vakit"]**0.5,0.0)
        destek=SMIN*P["aile"]*(t<(36))*np.where(P["okuyor"]>0,1.0,(t<12)*1.0)
        yil=yil+R
        if rj["tavan"]: genel=genel|(yil>TAVAN)
        ist=(t<36) if rj["istisna"] else False
        kar_modu=(rj["vergi"]=="kar")|genel
        vergi=np.zeros(N); prim=np.zeros(N); sabit=np.zeros(N)
        if rj["vergi"]=="tevk": vergi=np.where(genel,0.0,par["duz_oran"]*R)
        drag=(1.0+par["drag"])**(t//12)
        pm=PRIM_AYLIK+SABIT_AYLIK
        kar_ytd=np.maximum((1-GIDER)*yil-pm*(ay+1)-(1737500.0 if ist else 0),0)*drag
        kar_prev=np.maximum((1-GIDER)*(yil-R)-pm*ay-(1737500.0 if ist else 0),0)*drag
        vergi=np.where(kar_modu,tarife(kar_ytd)-tarife(kar_prev),vergi)
        if rj["prim"]=="sabit": prim=np.full(N,PRIM_AYLIK)
        prim=np.where(genel&(rj["prim"]!="sabit"),PRIM_AYLIK,prim)
        if rj["sabit"]: sabit=np.full(N,SABIT_AYLIK)
        sabit=np.where(genel,SABIT_AYLIK,sabit)
        ceza=np.zeros(N)
        if rj["denetim"]>0: ceza=np.where((S["denetim"][t]<rj["denetim"])&(R>0),3*R,0.0)
        odeme=(harap==0)
        prim=np.where(odeme,prim,0.0); sabit=np.where(odeme,sabit,0.0); vergi=np.where(odeme,vergi,0.0)
        onceki=(1-c_real)*R-vergi-prim-sabit-ceza+gig
        gss=np.zeros(N)
        if rj["gss"] and par["gss_ac"]:
            kapsam_disi=(P["okuyor"]>0)&(P["yas"]<25)
            gss=np.where((~kapsam_disi)&odeme&(onceki>GSS_GELIR_ESIGI*par["gss_esik_katsayi"]),GSS_AYLIK,0.0)
        gel=onceki-gss
        gss_toplam+=gss
        burs_kaybi=0.25*ASGARI_NET*P["burs"]*(rj["vergi"]=="kar")*(R>0)
        eldeki=gel+destek-burs_kaybi
        olay=np.where(S["olay"][t],2*SMIN,0.0)
        K=K+np.where(eldeki>=SMIN,par["sv"]*(eldeki-SMIN),eldeki-SMIN)-olay
        K=np.where(K<0,K*(1+par["faiz"]),K)
        ac_ay=ac_ay+((eldeki<SMIN)&(K<0))
        yeni_iflas=(K<-6*SMIN)&(harap==0)
        iflas=iflas|yeni_iflas
        harap=np.where(yeni_iflas,6,np.maximum(harap-1,0)); K=np.where(yeni_iflas,-2*SMIN,K); B=np.where(yeni_iflas,0.0,B)
        net[t]=gel; devlet[t]=vergi+prim+gss; canli[t]=(harap==0)&(R>0.05*ASGARI_NET)
    return dict(net=net,devlet=devlet,iflas=iflas,canli=canli,ac_ay=ac_ay,gss=gss_toplam)
def olc3(r):
    net=r["net"]; T=net.shape[0]
    o=np.zeros_like(net)
    for t in range(T):
        a=max(0,t-11); o[t]=net[a:t+1].mean(axis=0)/ASGARI_NET
    b=np.digitize(o,np.array([1/3,1.0,2.0]))
    kalici=(b[48:]>=2).all(axis=0); degisim=(np.diff(b[24:],axis=0)!=0).sum(axis=0)
    salin=(degisim>=4)&(~kalici); dip=(~(b>=2).any(axis=0))&(b[-1]<=1)
    isk=1.0/(1.05)**(np.arange(T)/12.0)
    return dict(kalici=float(kalici.mean()),salinim=float(salin.mean()),dip=float(dip.mean()),yikim=float(r["iflas"].mean()),
      canli12=float(r["canli"][11].mean()),canli24=float(r["canli"][23].mean()),canli60=float(r["canli"][59].mean()),
      net_son=float(net[60:].mean()/ASGARI_NET),devlet_pv=float((r["devlet"]*isk[:,None]).sum(axis=0).mean()),gss_yillik=float(r["gss"].mean()/6.0))
VARSAYILAN=dict(b0=5500.0,L=0.45,b_ilk=0.5,duz_oran=0.105,kappa=0.10,talep_bolge=1.0,mal_pay=0.40,c_mal=0.50,c_hiz=0.15,
  faiz=0.015,sv=0.5,drag=0.0,aile_olcek=1.0,erisim_kd=0.55,kayip_kd=0.12,gss_ac=True,gss_esik_katsayi=1.0,hedef_canli12=0.75)
def kalibre(par,N,seed):
    P=nufus3(N,seed,par); S=sok3(N,72,seed+1)
    lo,hi=1500.0,15000.0
    for _ in range(14):
        m=(lo+hi)/2; p=dict(par); p["b0"]=m
        c=float(kos3(REJ["tarafsız"],P,S,N,p)["canli"][11].mean())
        if c<par["hedef_canli12"]: lo=m
        else: hi=m
    return (lo+hi)/2
def calistir(par,N=2000,seed=20261101,kal=True):
    p=dict(par)
    if kal: p["b0"]=kalibre(p,N,seed)
    P=nufus3(N,seed,p); S=sok3(N,72,seed+1)
    out={}
    for ad,rj in REJ.items(): out[ad]=olc3(kos3(rj,P,S,N,p))
    return p["b0"],out
if __name__=="__main__":
    par=dict(VARSAYILAN)
    print("== A) Kalibrasyon: ilk yıl canlılık hedefi %75 (TÜİK girişim demografisi 2024: 1 yıllık hayatta kalma ~%75-78, tüm girişimler) ==")
    print("   nüfus bileşimi (örneklem içi): ",end="")
    P=nufus3(20000,1,par);
    for i,t in enumerate(TIP_AD): print("%s %.3f; "%(t,(P["tip"]==i).mean()),end="")
    print(" ort.yaş %.1f"%P["yas"].mean())
    tum=[]
    for sd in range(8):
        b0,o=calistir(par,N=2000,seed=20261101+100*sd); tum.append((b0,o))
    print("b0 kalibre (8 tohum): ort %.0f std %.0f"%(np.mean([x[0] for x in tum]),np.std([x[0] for x in tum])))
    for ad in REJ:
        print("--",ad)
        for k in ["canli12","canli24","canli60","kalici","salinim","dip","yikim","net_son","devlet_pv","gss_yillik"]:
            v=np.array([x[1][ad][k] for x in tum]); print("   %-10s %.3f ± %.3f"%(k,v.mean(),1.96*v.std()/np.sqrt(len(v))))
