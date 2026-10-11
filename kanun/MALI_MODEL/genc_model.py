import numpy as np, json
W=33030.0
ASGARI_NET=28075.0
GEC=15000.0
ESIK=np.array([190000.0,400000.0,1000000.0,5300000.0])
ORAN=np.array([0.15,0.20,0.27,0.35,0.40])
TAVAN=24*W
PRIM_AYLIK=141699.0/12
SABIT_AYLIK=2000.0
BANT=np.array([0.6,1.2,2.5])
GIDER=0.30
BU0=0.004
BU1=0.008
YAN_GELIR=0.35*ASGARI_NET
def tarife(S):
    S=np.asarray(S,dtype=float); t=np.zeros_like(S); lo=0.0
    for e,r in zip(ESIK,ORAN[:4]):
        t=t+r*np.clip(S-lo,0,e-lo); lo=e
    return t+ORAN[4]*np.clip(S-lo,0,None)
def sok(N,T,seed):
    g=np.random.default_rng(seed); x=np.zeros(T)
    for t in range(1,T): x[t]=0.9*x[t-1]+g.normal(0,0.06)
    return dict(makro=np.exp(x),beceri=np.exp(g.normal(0,0.35,N)),yeni_u=g.random((T,N)),birim=np.exp(g.normal(0,0.3,(T,N))),
      kayip=g.normal(0,0.04,(T,N)),gurultu=np.exp(g.normal(0,0.15,(T,N))),olay=g.random((T,N))<0.015,denetim=g.random((T,N)))
REJIM={
 "Tarafsız ölçü (kanunsuz)":dict(erisim=1.0,kayip=0.08,vergi="yok",prim="yok",sabit=False,tavan=False,istisna=False,denetim=0.0),
 "Mevcut kanun, kayıtlı":dict(erisim=1.0,kayip=0.08,vergi="kar",prim="sabit",sabit=True,tavan=False,istisna=True,denetim=0.0),
 "Mevcut kanun, kayıt dışı":dict(erisim=0.55,kayip=0.12,vergi="yok",prim="yok",sabit=False,tavan=False,istisna=False,denetim=0.004),
 "Teklif S":dict(erisim=1.0,kayip=0.08,vergi="tevk",prim="yok",sabit=False,tavan=True,istisna=True,denetim=0.0),
 "Model G (tavanda genel hükümler)":dict(erisim=1.0,kayip=0.08,vergi="tevk",prim="gelir",sabit=False,tavan=True,istisna=True,denetim=0.0),
 "Model G2 (tavanda uçurum yok)":dict(erisim=1.0,kayip=0.08,vergi="tevk",prim="gelir",sabit=False,tavan=False,istisna=True,denetim=0.0),
 "Model G3 (G2 + yuvarlanan tevkifat)":dict(erisim=1.0,kayip=0.08,vergi="tevk_yuv",prim="gelir",sabit=False,tavan=False,istisna=True,denetim=0.0)}
def kos(rj,S,N,T=72,istisna_tutar=400000.0,b0=7000.0,lam0=0.7,prim_oran=0.10,ruin_ay=6):
    K=np.zeros(N); s=S['beceri'].copy(); B=0.5*b0*s; aktif=np.zeros(N); harap=np.zeros(N,dtype=int)
    yil=np.zeros(N); onceki_yil=np.zeros(N); genel=np.zeros(N,dtype=bool)
    net=np.zeros((T,N)); devlet=np.zeros((T,N)); iflas=np.zeros(N,dtype=bool); iflas_ay=np.zeros(N); genel_ay=np.zeros(N)
    gecmis=np.zeros((T,N))
    for t in range(T):
        ay=t%12
        if ay==0:
            genel=(yil>TAVAN) if (t>0 and rj['tavan']) else np.zeros(N,dtype=bool)
            yil=np.zeros(N)
        buf=np.clip(K/(6*GEC),0,1)
        lam=lam0*rj['erisim']*(1+0.5*buf)*(1+0.02*np.minimum(aktif,36))
        yeni=(S['yeni_u'][t]<np.minimum(lam,0.95)).astype(float)
        kay=np.clip(rj['kayip']-0.03*buf+S['kayip'][t],0.0,0.6)
        B=np.where(harap>0,0.0,B*(1-kay)+yeni*b0*s*S['birim'][t])
        aktif=np.where(harap>0,0,aktif+1)
        s=s*(1+BU0+BU1*buf)
        R=B*S['makro'][t]*S['gurultu'][t]
        gig=np.where(harap>0,0.5*ASGARI_NET,YAN_GELIR*(t<12))
        yil=yil+R
        genel=genel|(yil>TAVAN) if rj['tavan'] else genel
        ist=(t<36) if rj['istisna'] else False
        kar_modu=(rj['vergi']=="kar")|genel
        vergi=np.zeros(N); prim=np.zeros(N); sabit=np.zeros(N)
        if rj['vergi']=="tevk":
            vergi=np.where(genel,0.0,tarife((1-GIDER)*yil)-tarife((1-GIDER)*(yil-R)))
        if rj['vergi']=="tevk_yuv":
            gecmis[t]=R
            son12=gecmis[max(0,t-11):t+1].sum(axis=0)
            e=tarife((1-GIDER)*son12)/np.maximum((1-GIDER)*son12,1.0)
            vergi=np.where(genel,0.0,e*(1-GIDER)*R)
        pm=PRIM_AYLIK+SABIT_AYLIK
        kar_ytd=np.maximum((1-GIDER)*yil-pm*(ay+1)-(istisna_tutar if ist else 0),0)
        kar_prev=np.maximum((1-GIDER)*(yil-R)-pm*ay-(istisna_tutar if ist else 0),0)
        vergi=np.where(kar_modu,tarife(kar_ytd)-tarife(kar_prev),vergi)
        if rj['prim']=="sabit": prim=np.full(N,PRIM_AYLIK)
        elif rj['prim']=="gelir":
            yillik=12*(1-GIDER)*np.maximum(R,0)
            oran=np.where(yillik>=2*W,np.where(yillik>=10*W,2*prim_oran,prim_oran),0.0)
            prim=np.where(genel,PRIM_AYLIK,oran*(1-GIDER)*R)
        if rj['sabit']: sabit=np.full(N,SABIT_AYLIK)
        prim=np.where(genel&(rj['prim']!="sabit"),PRIM_AYLIK,prim)
        sabit=np.where(genel,SABIT_AYLIK,sabit)
        ceza=np.zeros(N)
        if rj['denetim']>0: ceza=np.where((S['denetim'][t]<rj['denetim'])&(R>0),3*R,0.0)
        odeme=(harap==0)
        prim=np.where(odeme,prim,0.0); sabit=np.where(odeme,sabit,0.0); vergi=np.where(odeme,vergi,0.0)
        gel=(1-GIDER)*R-vergi-prim-sabit-ceza+gig
        olay=np.where(S['olay'][t],2*GEC,0.0)
        fazla=np.maximum(gel-GEC,0)
        K=K+np.where(gel>=GEC,0.5*fazla,gel-GEC)-olay
        yeni_iflas=(K<-6*GEC)&(harap==0)
        iflas=iflas|yeni_iflas
        harap=np.where(yeni_iflas,ruin_ay,np.maximum(harap-1,0))
        K=np.where(yeni_iflas,-2*GEC,K)
        iflas_ay=iflas_ay+(harap>0); genel_ay=genel_ay+genel
        net[t]=gel; devlet[t]=vergi+prim
    return dict(net=net,devlet=devlet,iflas=iflas,iflas_ay=iflas_ay,genel_ay=genel_ay)
def bant_serisi(net,pen=3):
    T=net.shape[0]; ort=np.zeros_like(net)
    for t in range(T):
        a=max(0,t-pen+1); ort[t]=net[a:t+1].mean(axis=0)/ASGARI_NET
    return np.digitize(ort,BANT)
def olc(res,pen=12):
    b=bant_serisi(res['net'],pen); T=b.shape[0]
    kalici=(b[48:]>=2).all(axis=0)
    degisim=(np.diff(b[24:],axis=0)!=0).sum(axis=0)
    salin=(degisim>=4)&(~kalici)
    dip=(~(b>=2).any(axis=0))&(b[-1]<=1)
    bol=lambda t:[float((b[t]==k).mean()) for k in range(4)]
    iskonto=1.0/(1+0.05)**(np.arange(T)/12.0)
    return dict(kalici_ust=float(kalici.mean()),salinim=float(salin.mean()),dip=float(dip.mean()),yikim=float(res['iflas'].mean()),
      yikim_ay=float(res['iflas_ay'].mean()),bant12=bol(11),bant36=bol(35),bant72=bol(71),
      devlet_pv=float((res['devlet']*iskonto[:,None]).sum(axis=0).mean()),devlet_yil5=float(res['devlet'][48:].mean()*12),
      net_ay_son=float(res['net'][60:].mean()),degisim_ort=float(degisim.mean()),genel_ay=float(res['genel_ay'].mean()),
      ort_net_pv=float((res['net']*iskonto[:,None]).sum(axis=0).mean()))
def yillik_net(Ra,rj):
    R=np.asarray(Ra,dtype=float)
    pm=12*(PRIM_AYLIK+SABIT_AYLIK)
    cep=(1-GIDER)*R
    if rj['vergi']=="yok": return cep
    if rj['vergi']=="tevk_yuv":
        s=cep-tarife(cep); oran=np.where(cep>=2*W,np.where(cep>=10*W,0.2,0.1),0.0); return s-oran*cep
    genel=(R>TAVAN)&rj['tavan']
    kar=np.maximum(cep-pm,0); mevcut=cep-tarife(kar)-pm
    if rj['vergi']=="kar": return mevcut
    s=cep-tarife(cep)
    if rj['prim']=="gelir":
        oran=np.where(cep>=2*W,np.where(cep>=10*W,0.2,0.1),0.0); s=s-oran*cep
    return np.where(genel,mevcut,s)
KAL={"zor":dict(b0=4500.0,lam0=0.30),"orta":dict(b0=5500.0,lam0=0.45),"kolay":dict(b0=7000.0,lam0=0.60)}
def tum(N=4000,seed=20261014,**kw):
    S=sok(N,72,seed); out={}
    for ad,rj in REJIM.items():
        r=kos(rj,S,N,**kw); out[ad]=dict(m12=olc(r,12),m3=olc(r,3))
    return out
def aylik_oran(rj,S,N):
    r=kos(rj,S,N); return r
if __name__=="__main__":
    N=3000; R={}
    for kad,kw in KAL.items():
        R[kad]=tum(N,**kw)
        print("==",kad)
        for ad,v in R[kad].items():
            m=v['m12']; print("%-34s kalıcı %.3f salınım %.3f dip %.3f yıkım %.3f devletPV %8.0f net/ay %7.0f genel_ay %.1f | 3ay salınım %.3f"%(ad,m['kalici_ust'],m['salinim'],m['dip'],m['yikim'],m['devlet_pv'],m['net_ay_son'],m['genel_ay'],v['m3']['salinim']))
    H=dict(istisna0=tum(N,istisna_tutar=0.0,**KAL["orta"]))
    print("== istisna yok (orta)")
    for ad,v in H['istisna0'].items():
        m=v['m12']; print("%-34s kalıcı %.3f salınım %.3f dip %.3f yıkım %.3f devletPV %8.0f"%(ad,m['kalici_ust'],m['salinim'],m['dip'],m['yikim'],m['devlet_pv']))
    Rg=np.array([100000,300000,600000,792720,800000,1000000,1500000.0])
    C={ad:[float(x) for x in yillik_net(Rg,rj)] for ad,rj in REJIM.items()}
    json.dump(dict(sonuc=R,hassasiyet=H,cenik=C,gelir=[float(x) for x in Rg]),open('sonuc_genc.json','w'),ensure_ascii=False,indent=1)
