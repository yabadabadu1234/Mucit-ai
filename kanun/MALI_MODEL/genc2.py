import numpy as np, json, sys
from genc_model import tarife, W, ASGARI_NET, TAVAN, PRIM_AYLIK, SABIT_AYLIK, GIDER, REJIM
SMIN=ASGARI_NET/3
BANT2=np.array([1/3,1.0,2.0])
TIPLER=[("okuyor, lise",0.24,dict(okuyor=1,derece=0,vakit=0.35,erisim=0.20,beceri=1.0,aile=0.7,burs=0.4)),
 ("okuyor, üniversite",0.37,dict(okuyor=1,derece=0,vakit=0.45,erisim=0.50,beceri=1.2,aile=0.7,burs=0.4)),
 ("okumuyor, lise altı",0.15,dict(okuyor=0,derece=0,vakit=1.0,erisim=0.25,beceri=0.9,aile=0.35,burs=0.0)),
 ("okumuyor, lise",0.18,dict(okuyor=0,derece=1,vakit=1.0,erisim=0.45,beceri=1.0,aile=0.35,burs=0.0)),
 ("okumuyor, lisans+",0.06,dict(okuyor=0,derece=2,vakit=1.0,erisim=1.0,beceri=1.2,aile=0.35,burs=0.0))]
YOL_PAY={"okuyor, lise":(0.30,0.60,0.10),"okuyor, üniversite":(0.45,0.40,0.15),"okumuyor, lise altı":(0.10,0.75,0.15),"okumuyor, lise":(0.20,0.65,0.15),"okumuyor, lisans+":(0.65,0.20,0.15)}
YOLLAR=["serbest çalışan","bol rakipli iş","az rakipli iş"]
def nufus(N,seed):
    g=np.random.default_rng(seed); w=np.array([t[1] for t in TIPLER]); tip=g.choice(len(TIPLER),N,p=w/w.sum())
    yol=np.zeros(N,dtype=int)
    for i,t in enumerate(TIPLER):
        m=tip==i; yol[m]=g.choice(3,m.sum(),p=YOL_PAY[t[0]])
    P={k:np.array([TIPLER[i][2][k] for i in tip],dtype=float) for k in TIPLER[0][2]}
    P["aile"]=(g.random(N)<P["aile"]).astype(float); P["burs"]=(g.random(N)<P["burs"]).astype(float)
    P["tip"]=tip; P["yol"]=yol; P["yas"]=g.integers(16,30,N)
    return P
def sok2(N,T,seed):
    g=np.random.default_rng(seed); x=np.zeros(T)
    for t in range(1,T): x[t]=0.9*x[t-1]+g.normal(0,0.06)
    return dict(makro=np.exp(x),beceri=np.exp(g.normal(0,0.35,N)),yeni_u=g.random((T,N)),birim=np.exp(g.normal(0,0.3,(T,N))),
      kayip=g.normal(0,0.04,(T,N)),gurultu=np.exp(g.normal(0,0.15,(T,N))),olay=g.random((T,N))<0.015,denetim=g.random((T,N)),pazar=g.random((T,N))<0.04)
def kos2(rj,P,S,N,T=72,b0=5500.0,L=0.45,istisna_tutar=1737500.0,prim_oran=0.10,yol_zorla=None,burs_miktar=0.25*ASGARI_NET,k0=0.0,b_ilk=0.5,kar_payi=0.0,pay_tavan=None,duz_oran=None):
    yol=P["yol"] if yol_zorla is None else np.full(N,yol_zorla)
    s=S["beceri"]*P["beceri"]
    lam_yol=np.where(yol==0,P["erisim"],np.where(yol==1,0.9,0.3))
    b_yol=np.where(yol==0,1.0,np.where(yol==1,0.6,1.8))
    K=np.full(N,float(k0)); B=b_ilk*b0*b_yol*s*(lam_yol>0.3); aktif=np.zeros(N); harap=np.zeros(N,dtype=int); yil=np.zeros(N); genel=np.zeros(N,dtype=bool)
    pay_toplam=np.zeros(N)
    gecmis=np.zeros((T,N)); net=np.zeros((T,N)); devlet=np.zeros((T,N)); gel_hepsi=np.zeros((T,N)); iflas=np.zeros(N,dtype=bool); iflas_ay=np.zeros(N); ac_ay=np.zeros(N); genel_ay=np.zeros(N)
    for t in range(T):
        ay=t%12
        if ay==0:
            genel=(yil>TAVAN) if (t>0 and rj['tavan']) else np.zeros(N,dtype=bool); yil=np.zeros(N)
        buf=np.clip(K/(6*SMIN),0,1)
        zor=np.where(yol==2,1/(1+np.exp(-(s-1.15)/0.2)),1.0)
        lam=L*rj['erisim']*lam_yol*P["vakit"]*zor*(1+0.5*buf)*(1+0.02*np.minimum(aktif,36))
        yeni=(S['yeni_u'][t]<np.minimum(lam,0.95)).astype(float)
        kay=np.clip(rj['kayip']-0.03*buf+S['kayip'][t],0.0,0.6)
        B=np.where(harap>0,0.0,B*(1-kay)+yeni*b0*b_yol*s*S['birim'][t])
        B=np.where((yol>0)&S['pazar'][t],B*0.5,B)
        aktif=np.where(harap>0,0,aktif+1)
        s=s*(1+0.003+0.006*buf)
        R=B*S['makro'][t]*S['gurultu'][t]*np.where(yol==0,P["vakit"],1.0)**0
        gig=np.where(harap>0,0.5*ASGARI_NET*P["vakit"]**0.5,0.0)
        destek=SMIN*P["aile"]*(t<(36 if True else 12))*np.where(P["okuyor"]>0,1.0,(t<12)*1.0)
        yil=yil+R
        genel=genel|(yil>TAVAN) if rj['tavan'] else genel
        ist=(t<36) if rj['istisna'] else False
        kar_modu=(rj['vergi']=="kar")|genel
        vergi=np.zeros(N); prim=np.zeros(N); sabit=np.zeros(N)
        if rj['vergi']=="tevk": vergi=np.where(genel,0.0,tarife((1-GIDER)*yil)-tarife((1-GIDER)*(yil-R)))
        if rj['vergi']=="tevk" and duz_oran is not None: vergi=np.where(genel,0.0,duz_oran*R)
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
        prim=np.where(genel&(rj['prim']!="sabit"),PRIM_AYLIK,prim); sabit=np.where(genel,SABIT_AYLIK,sabit)
        ceza=np.zeros(N)
        if rj['denetim']>0: ceza=np.where((S['denetim'][t]<rj['denetim'])&(R>0),3*R,0.0)
        kayitli_mevcut=(rj['vergi']=="kar")
        burs_kaybi=burs_miktar*P["burs"]*kayitli_mevcut*(R>0)
        odeme=(harap==0)
        prim=np.where(odeme,prim,0.0); sabit=np.where(odeme,sabit,0.0); vergi=np.where(odeme,vergi,0.0)
        gel=(1-GIDER)*R-vergi-prim-sabit-ceza+gig
        pay=kar_payi*np.maximum((1-GIDER)*R-vergi-prim-sabit,0)*(harap==0)
        if pay_tavan is not None: pay=np.minimum(pay,np.maximum(pay_tavan-pay_toplam,0))
        gel=gel-pay; pay_toplam=pay_toplam+pay
        eldeki=gel+destek-burs_kaybi
        olay=np.where(S['olay'][t],2*SMIN,0.0)
        K=K+np.where(eldeki>=SMIN,0.5*(eldeki-SMIN),eldeki-SMIN)-olay
        ac_ay=ac_ay+((eldeki<SMIN)&(K<0))
        yeni_iflas=(K<-6*SMIN)&(harap==0)
        iflas=iflas|yeni_iflas
        harap=np.where(yeni_iflas,6,np.maximum(harap-1,0)); K=np.where(yeni_iflas,-2*SMIN,K); B=np.where(yeni_iflas,0.0,B)
        iflas_ay=iflas_ay+(harap>0); genel_ay=genel_ay+genel
        net[t]=gel; devlet[t]=vergi+prim; gel_hepsi[t]=R
    return dict(pay_toplam=pay_toplam,net=net,devlet=devlet,iflas=iflas,iflas_ay=iflas_ay,ac_ay=ac_ay,genel_ay=genel_ay,R=gel_hepsi)
def bant2(net,pen=12):
    T=net.shape[0]; o=np.zeros_like(net)
    for t in range(T):
        a=max(0,t-pen+1); o[t]=net[a:t+1].mean(axis=0)/ASGARI_NET
    return np.digitize(o,BANT2)
def olc2(r,idx=None):
    net=r['net'] if idx is None else r['net'][:,idx]
    devlet=r['devlet'] if idx is None else r['devlet'][:,idx]
    sel=(lambda a:a) if idx is None else (lambda a:a[idx])
    b=bant2(net,12); T=b.shape[0]
    kalici=(b[48:]>=2).all(axis=0); degisim=(np.diff(b[24:],axis=0)!=0).sum(axis=0)
    salin=(degisim>=4)&(~kalici); dip=(~(b>=2).any(axis=0))&(b[-1]<=1)
    isk=1.0/(1+0.05)**(np.arange(T)/12.0)
    bol=lambda t:[float((b[t]==k).mean()) for k in range(4)]
    return dict(kalici_ust=float(kalici.mean()),salinim=float(salin.mean()),dip=float(dip.mean()),yikim=float(sel(r['iflas']).mean()),
      ac_ay=float(sel(r['ac_ay']).mean()),aclik_alti_ay_orani=float(sel(r['ac_ay']).mean()/T),bant12=bol(11),bant36=bol(35),bant72=bol(71),
      devlet_pv=float((devlet*isk[:,None]).sum(axis=0).mean()),net_ay_son=float(net[60:].mean()),genel_ay=float(sel(r['genel_ay']).mean()))
KAL={"zor":dict(b0=4500.0,L=0.30),"orta":dict(b0=5500.0,L=0.45),"kolay":dict(b0=7000.0,L=0.60)}
if __name__=="__main__":
    N=3000; P=nufus(N,20261015); S=sok2(N,72,20261016); out={}
    for kad,kw in KAL.items():
        out[kad]={}
        for ad,rj in REJIM.items():
            if ad.startswith("Model G3"): continue
            r=kos2(rj,P,S,N,**kw); o=dict(genel=olc2(r))
            o["tip"]={TIPLER[i][0]:olc2(r,np.where(P["tip"]==i)[0]) for i in range(len(TIPLER))}
            o["yol"]={}
            for y in range(3):
                ry=kos2(rj,P,S,N,yol_zorla=y,**kw); o["yol"][YOLLAR[y]]=olc2(ry)
            out[kad][ad]=o
            g=o["genel"]; print(kad,"%-36s kalıcı %.3f dip %.3f yıkım %.3f aç-ay %.1f devletPV %8.0f"%(ad,g['kalici_ust'],g['dip'],g['yikim'],g['ac_ay'],g['devlet_pv']),flush=True)
    json.dump(out,open("sonuc_genc2.json","w"),ensure_ascii=False,indent=1)
