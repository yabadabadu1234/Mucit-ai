# Üç senaryo için birleşik belirsizlik Monte Carlo + duyarlılık (Spearman) + birlikte kötü uç.
# Her senaryo kendi tabanı etrafında üçgen dağılımlarla örneklenir; tüm girdiler birlikte değişir.
import numpy as np, json, time
from scipy.stats import spearmanr
from model import *
NS=6000
rng=np.random.default_rng(20261017)
# (ad, en düşük, mod, en yüksek) -- senaryoya göre; Orta ve İyimser/Kötümser birbirinden farklı
DAG={
 'Kötümser':dict(n_toplam=('lnorm',255000,0.106), s_kayitli=(0.15,0.30,0.45), prim_toplama=(0.6,0.9,1.0), u_ucretli=(0.15,0.25,0.35),
   medyan_W=(3,4,6), sigma=(0.7,0.9,1.2), prim_odeme=(0.5,0.8,1.0), phi=(0.01,0.02,0.03), onlem=(0.2,0.3,0.5),
   myo_uygun=(0.3,0.5,0.6), bes_vazgecme=(0.2,0.35,0.5), kdv_donanim_pay=(0.4,0.5,0.6), kgf_alim=(0.05,0.08,0.10), kgf_temerrut=(0.10,0.15,0.20), marj=(0.4,0.5,0.6), duz_oran=(0.135,0.135,0.27)),
 'Orta':dict(n_toplam=('lnorm',332000,0.106), s_kayitli=(0.05,0.15,0.30), prim_toplama=(0.6,0.9,1.0), u_ucretli=(0.05,0.20,0.35),
   medyan_W=(3,5,8), sigma=(0.6,0.9,1.2), prim_odeme=(0.4,0.8,1.0), phi=(0,0.01,0.03), onlem=(0.2,0.5,0.8),
   myo_uygun=(0.1,0.35,0.6), bes_vazgecme=(0.1,0.35,0.6), kdv_donanim_pay=(0.2,0.4,0.6), kgf_alim=(0.02,0.05,0.10), kgf_temerrut=(0.05,0.10,0.20), marj=(0.35,0.5,0.65), duz_oran=(0.135,0.135,0.27)),
 'İyimser':dict(n_toplam=('lnorm',462000,0.106), s_kayitli=(0.02,0.05,0.10), prim_toplama=(0.8,1.0,1.0), u_ucretli=(0.05,0.15,0.25),
   medyan_W=(4,6,8), sigma=(0.6,0.9,1.1), prim_odeme=(0.5,0.9,1.0), phi=(0,0.005,0.01), onlem=(0.5,0.7,0.8),
   myo_uygun=(0.1,0.2,0.4), bes_vazgecme=(0.3,0.5,0.6), kdv_donanim_pay=(0.2,0.3,0.4), kgf_alim=(0.01,0.03,0.05), kgf_temerrut=(0.03,0.06,0.10), marj=(0.4,0.5,0.6), duz_oran=(0.135,0.135,0.27)),
}
def draw(spec,n):
    out={}
    for k,v in spec.items():
        if v[0]=='lnorm': out[k]=np.exp(rng.normal(np.log(v[1]),v[2],n))
        else: out[k]=rng.triangular(v[0],v[1],v[2],n)
    return out
RES={}
t0=time.time()
for ad,spec in DAG.items():
    S=draw(spec,NS)
    net=np.zeros(NS); npvv=np.zeros(NS)
    for i in range(NS):
        p=sc(ad)
        for k in S: p[k]=float(S[k][i])
        p['n_yeni_pay']=1-p['s_kayitli']-p['u_ucretli']
        v,ys=npv(p); net[i]=ys[3]['net']; npvv[i]=v
    q=lambda a:{k:float(np.percentile(a,k)) for k in (1,5,10,25,50,75,90,95,99)}
    rho={k:float(spearmanr(S[k],net).correlation) for k in S}
    RES[ad]=dict(net_q=q(net/1e9),npv_q=q(npvv/1e9),p_net_pozitif=float((net>0).mean()),p_npv_pozitif=float((npvv>0).mean()),
                 spearman=dict(sorted(rho.items(),key=lambda x:-abs(x[1]))))
    print(ad,"net P5/P50/P95 = %.2f / %.2f / %.2f  P(net>0)=%.3f  NPV P50=%.2f"%(q(net/1e9)[5],q(net/1e9)[50],q(net/1e9)[95],(net>0).mean(),q(npvv/1e9)[50]))
    for k,r in list(RES[ad]['spearman'].items())[:6]: print("   rho %-16s %+.2f"%(k,r))
RES['_sure_sn']=time.time()-t0
json.dump(RES,open('mc_uc_sonuc.json','w'),ensure_ascii=False,indent=1)
print("süre %.0f sn"%RES['_sure_sn'])
