import numpy as np, json, model
from model import *
_orj=model.kisi_basi
def _yama(H,p):
    k=_orj(H,p); d=p.get('dolasma',0.0)
    if d>0:
        yarim=_orj(H/2,p); m=(H>=0.5*TAVAN)
        for x in ['T','bes','dk','myo','kdv']: k[x]=np.where(m,(1-d)*k[x]+d*2*yarim[x],k[x])
        k['yeni_net']=k['T']-k['bes']-k['dk']-k['myo']-k['kdv']
    return k
model.kisi_basi=_yama
TAM=141699.0
M0=dict(cap_e=None,r_e=None,floor_e=0.0,r_y=0.0,e0=0.0,kulucka=3,levy=0.0,prog=1.0,prog_esik=10.0,
 kp_maliyet_pay=0.6,eps_pp=0.0,dolasma=0.0,pej=0.0,pej_onlem=0.0,pej_sgk=0.30,pej_vergi=0.15,
 ghost=0.0,ghost_onlem=0.0,uyum_bireysel=1.0,c_e=1.0,cyc=0.0,cyc_onlem=0.0,prim_devam=1.0,levy_kacis=3.0)
def pm(ad,**kw):
    p=sc(ad); p.update(M0); p.update(kw); return p
def prim_y(p,H):
    gelir=(1-p['gider'])*H/W
    r=np.where(gelir>p['prog_esik'],p['r_y']*p['prog'],p['r_y'])
    return np.where(gelir>=p['e0'],r*(1-p['gider'])*H,0.0)
def prim_e(p,H):
    full=p['prim_odeme']*TAM
    if p['r_e'] is None:
        v=np.full_like(H,full)*p['prim_devam']
        return v if p['cap_e'] is None else np.minimum(v,p['cap_e']*(1-p['gider'])*H)
    return np.clip(p['r_e']*(1-p['gider'])*H,p['floor_e'],full)
def kos(p,detay=False):
    H,w=agirliklar(p); ys=[]; top=0.0
    pe=prim_e(p,H); full=p['prim_odeme']*TAM
    for i in range(5):
        f=1.0
        if i>=p['kulucka'] and p['r_y']>0: f=1-p['eps_pp']*100*p['r_y']
        r=p['ramp'][i]*f; q=dict(p); q['prim_devam']=1.0
        y=yil(q,r,ilk=(i==0)); n=y['net']; N=p['n_toplam']*r
        nyeni=1-p['s_kayitli']-p['u_ucretli']
        n-=N*p['s_kayitli']*float((w*(full-pe)).sum())
        if p['r_e'] is not None: n-=N*p['s_kayitli']*(1-p['c_e'])*float((w*pe).sum())
        n-=N*(1-p['uyum_bireysel'])*(1-p['kurumsal_pay'])*y['ort_T']
        if p['r_y']>0:
            if i>=p['kulucka']:
                g=N*nyeni*float((w*prim_y(p,H)).sum())*(1-p['cyc']*(1-p['cyc_onlem']))
                n+=g*(1-p['kp_maliyet_pay'])
        if p['levy']>0:
            x=min(1.0,p['levy_kacis']*p['levy']); bz=N*p['kurumsal_pay']*float((w*H).sum())
            n+=p['levy']*bz*(1-x)-x*N*p['kurumsal_pay']*y['ort_T']
        if p['pej']>0:
            k=model.kisi_basi(H,p); kisi=p['pej']*(1-p['pej_onlem'])*N
            n+=kisi*(float((w*k['yeni_net']).sum())-(p['pej_sgk']+p['pej_vergi'])*float((w*(1-p['gider'])*H).sum()))
        if p['ghost']>0:
            Hg=np.array([0.55*TAVAN]); k=model.kisi_basi(Hg,p)
            n+=p['ghost']*(1-p['ghost_onlem'])*N*float(k['yeni_net'][0]-p['kv']*Hg[0])
        ys.append(n); top+=n/(1+p['iskonto'])**(i+1)
    return (ys[3],top,ys) if detay else (ys[3],top)
