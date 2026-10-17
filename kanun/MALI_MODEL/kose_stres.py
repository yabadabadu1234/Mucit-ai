# Birlikte en kötü ve en iyi uç: her girdi, senaryonun kendi (en düşük, en yüksek) aralığının aleyhte/lehte ucunda.
# Aralıklar mc_uc.py'deki DAG ile aynıdır. n_toplam için: en kötü = 2021 düzeyi 255 bin, en iyi = 2025 eğiliminin 5 yıl uzatılması 462 bin (veriye dayalı).
import json
from model import *
ALEYHE={'s_kayitli':'lo','phi':'hi','onlem':'lo','ort_H_W':'lo','prim_odeme':'lo','u_ucretli':'hi','duz_oran':'lo','kgf_temerrut':'hi','kgf_alim':'hi',
        'kdv_donanim_pay':'hi','marj':'lo','bes_vazgecme':'hi','myo_uygun':'hi','prim_toplama':'lo','sigma':'hi','prim_k':'hi'}
DAG={
 'Kötümser':dict(s_kayitli=(0.0,0.0,0.489), prim_toplama=(0.6,0.9,1.0), u_ucretli=(0.15,0.25,0.35), ort_H_W=(30,43,85), sigma=(1.5,2.0,2.0), prim_odeme=(0.5,0.8,1.0), phi=(0.01,0.02,0.03), onlem=(0.2,0.3,0.5), myo_uygun=(0.3,0.5,0.6), bes_vazgecme=(0.2,0.35,0.5), kdv_donanim_pay=(0.4,0.5,0.6), kgf_alim=(0.05,0.08,0.10), kgf_temerrut=(0.10,0.15,0.20), marj=(0.4,0.5,0.6), prim_k=(3,6,12)),
 'Orta':dict(s_kayitli=(0.0,0.489,0.489), prim_toplama=(0.6,0.9,1.0), u_ucretli=(0.05,0.20,0.35), ort_H_W=(30,43,85), sigma=(1.25,1.75,2.0), prim_odeme=(0.4,0.8,1.0), phi=(0,0.01,0.03), onlem=(0.2,0.5,0.8), myo_uygun=(0.1,0.35,0.6), bes_vazgecme=(0.1,0.35,0.6), kdv_donanim_pay=(0.2,0.4,0.6), kgf_alim=(0.02,0.05,0.10), kgf_temerrut=(0.05,0.10,0.20), marj=(0.35,0.5,0.65), prim_k=(3,6,12)),
 'İyimser':dict(s_kayitli=(0.489,0.489,0.489), prim_toplama=(0.8,1.0,1.0), u_ucretli=(0.05,0.15,0.25), ort_H_W=(30,43,85), sigma=(1.25,1.5,1.75), prim_odeme=(0.5,0.9,1.0), phi=(0,0.005,0.01), onlem=(0.5,0.7,0.8), myo_uygun=(0.1,0.2,0.4), bes_vazgecme=(0.3,0.5,0.6), kdv_donanim_pay=(0.2,0.3,0.4), kgf_alim=(0.01,0.03,0.05), kgf_temerrut=(0.03,0.06,0.10), marj=(0.4,0.5,0.6), prim_k=(3,6,12)),
}
def uc(p): 
    p['n_yeni_pay']=1-p['s_kayitli']-p['u_ucretli']; return npv(p)[1][3]['net']/1e9
res={}
for ad,spec in DAG.items():
    base=sc(ad); w=dict(base); b=dict(base)
    for k,(lo,m,hi) in spec.items():
        if ALEYHE.get(k)=='hi': w[k],b[k]=hi,lo
        else: w[k],b[k]=lo,hi
    w['n_toplam']=255000; b['n_toplam']=462000
    res[ad]=dict(taban=uc(dict(base)),en_kotu=uc(w),en_iyi=uc(b))
    print(ad,{k:round(v,2) for k,v in res[ad].items()})
json.dump(res,open('kose_stres.json','w'),indent=1,ensure_ascii=False)
