import numpy as np, json, math
W=33030.0
TAVAN=24*W
ESIKLER=[190000.0,400000.0,1000000.0,5300000.0]
ORANLAR=[0.15,0.20,0.27,0.35,0.40]
def tarife(S):
    S=np.asarray(S,dtype=float); t=0*S; lo=0.0
    for e,r in zip(ESIKLER,ORANLAR[:4]):
        t=t+r*np.clip(S-lo,0,e-lo); lo=e
    return t+ORANLAR[4]*np.clip(S-lo,0,None)
def tevkifat(H,gider=0.30): return tarife((1-gider)*np.asarray(H,dtype=float))
BAZ=dict(medyan_W=5.0,sigma=0.9,gider=0.30,bes=0.03,devlet_katki=0.20,bes_vazgecme=0.35,
 myo_oran=0.21,myo_gun_ay=3,myo_uygun=0.35,kdv_donanim_pay=0.4,kdv_donanim_kdv=5000.0,kdv_mahsup_tavan=0.5,
 n_toplam=350000,s_kayitli=0.15,u_ucretli=0.20,marj=0.5,prim_eski=141699.0,prim_odeme=0.8,r_marj_ucretli=0.27,uyum_ucretli=0.5,
 kurumsal_pay=0.70,kv=0.25,phi=0.01,onlem=0.5,
 kgf_alim=0.05,kgf_temerrut=0.10,kgf_kurtarma=0.30,kgf_pay=0.5,
 prim_devam=1.0,duz_oran=None,ptt_birim=50.0,ptt_pay=0.8,bt_tek=250e6,bt_yillik=50e6,itiraz_oran=0.04,itiraz_maliyet=2000.0,denetim=0.01,
 ramp=[0.25,0.55,0.8,1.0,1.0],iskonto=0.05)
SENARYO={
 "Kötümser":dict(medyan_W=4.0,n_toplam=150000,s_kayitli=0.30,u_ucretli=0.25,phi=0.02,onlem=0.3,myo_uygun=0.5,bes_vazgecme=0.2,kgf_alim=0.08,kgf_temerrut=0.15,kdv_donanim_pay=0.5),
 "Orta":dict(),
 "İyimser":dict(medyan_W=6.0,n_toplam=700000,s_kayitli=0.05,u_ucretli=0.15,phi=0.005,onlem=0.7,myo_uygun=0.2,bes_vazgecme=0.5,kgf_alim=0.03,kgf_temerrut=0.06,kdv_donanim_pay=0.3)}
def agirliklar(p,k=60):
    lo,hi=0.1*W,TAVAN
    edges=np.geomspace(lo,hi,k+1); mid=np.sqrt(edges[:-1]*edges[1:])
    mu=math.log(p['medyan_W']*W); sg=p['sigma']
    cdf=lambda x:0.5*(1+np.vectorize(math.erf)((np.log(x)-mu)/(sg*math.sqrt(2))))
    w=cdf(edges[1:])-cdf(edges[:-1]); return mid,w/w.sum()
def kisi_basi(H,p):
    T=tevkifat(H,p['gider'])
    if p.get('duz_oran') is not None: T=p['duz_oran']*H
    bes=p['bes']*T*(1-p['bes_vazgecme']); dk=bes*p['devlet_katki']
    myo=np.where(H>=0.5*TAVAN,p['myo_uygun']*p['myo_gun_ay']*W*p['myo_oran'],0.0)
    kdv=p['kdv_donanim_pay']*np.minimum(p['kdv_mahsup_tavan']*T,p['kdv_donanim_kdv'])
    yeni_net=T-bes-dk-myo-kdv
    eski_vergi=tarife(p['marj']*H)
    eski_prim=p['prim_odeme']*p['prim_eski']*(1-p['prim_devam'])
    eski_kayitli=eski_vergi+eski_prim
    eski_ucretli=p['uyum_ucretli']*p['r_marj_ucretli']*p['marj']*H
    return dict(T=T,bes=bes,dk=dk,myo=myo,kdv=kdv,yeni_net=yeni_net,eski_kayitli=eski_kayitli,eski_ucretli=eski_ucretli,eski_vergi=eski_vergi,eski_prim=eski_prim)
def yil(p,carpan=1.0,ilk=False):
    H,w=agirliklar(p); k=kisi_basi(H,p); N=p['n_toplam']*carpan
    n_yeni=1-p['s_kayitli']-p['u_ucretli']
    E=lambda x:float((w*x).sum())
    ET,EH=E(k['T']),E(H)
    brut=N*ET
    bes_k=N*E(k['bes']+k['dk']); myo=N*E(k['myo']); kdv=N*E(k['kdv'])
    y_vergi=N*(p['s_kayitli']*E(k['eski_vergi'])+p['u_ucretli']*E(k['eski_ucretli']))
    y_prim=N*p['s_kayitli']*E(k['eski_prim'])
    eski=y_vergi+y_prim
    reff=ET/EH
    F=p['phi']*(1-p['onlem'])*p['kurumsal_pay']*N*EH
    sahte=F*max(p['kv']-reff,0)
    kgf=N*p['kgf_alim']*E(p['kgf_pay']*H)*p['kgf_temerrut']*(1-p['kgf_kurtarma'])
    ptt=N*p['ptt_pay']*p['ptt_birim']*(1.0 if ilk else 0.0)
    it=(p['bt_tek'] if ilk else 0.0)+p['bt_yillik']
    itiraz=N*p['itiraz_oran']*p['itiraz_maliyet']
    den=p['denetim']*brut
    net=brut-bes_k-myo-kdv-eski-sahte-kgf-ptt-it-itiraz-den
    return dict(N=N,ort_H=EH,ort_T=ET,etkin_oran=reff,brut_tevkifat=brut,bes_ve_devlet_katkisi=bes_k,myo_primi=myo,kdv_mahsubu=kdv,
      yutulma_kaybi=eski,yutulma_vergi=y_vergi,yutulma_prim=y_prim,sahte_fatura_kaybi=sahte,kgf_maliyeti=kgf,ptt=ptt,bt=it,itiraz=itiraz,denetim=den,net=net)
def bes_yil(p):
    return [yil(p,r,ilk=(i==0)) for i,r in enumerate(p['ramp'])]
def npv(p):
    ys=bes_yil(p); return sum(y['net']/(1+p['iskonto'])**(i+1) for i,y in enumerate(ys)),ys
def sc(ad):
    p=dict(BAZ); p.update(SENARYO[ad]); return p
if __name__=="__main__":
    for ad in SENARYO:
        p=sc(ad); v,ys=npv(p); s=ys[3]
        print(ad,"N=%d etkin=%.3f brut=%.2f mlr net=%.2f mlr npv5=%.2f mlr"%(s['N'],s['etkin_oran'],s['brut_tevkifat']/1e9,s['net']/1e9,v/1e9))
        for k in ['bes_ve_devlet_katkisi','myo_primi','kdv_mahsubu','yutulma_kaybi','sahte_fatura_kaybi','kgf_maliyeti','denetim','itiraz']: print("   ",k,"%.2f"%(s[k]/1e9))
    H=np.array([2,6,12,24])*W; print(tevkifat(H),tevkifat(H)/H)
