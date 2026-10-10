import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from model import *
plt.rcParams['font.family']='DejaVu Sans'
S=json.load(open('sonuc.json'))
NOT="Varsayımsal model çıktısı (sabit 2026 TL, 2026 asgari ücret). Girdilerin çoğu ölçülmemiştir; MALI_MODEL.md'ye bakınız."
O=S['senaryo']['Orta']['yil4']
M=1e9
# 1 şelale
adim=[("Brüt tevkifat",O['brut_tevkifat']),("BES + Devlet katkısı",-O['bes_ve_devlet_katkisi']),("90 gün prim",-O['myo_primi']),("Donanım KDV",-O['kdv_mahsubu']),
 ("Yutulma: vergi",-O['yutulma_vergi']),("Yutulma: prim",-O['yutulma_prim']),("Sahte fatura",-O['sahte_fatura_kaybi']),("KGF",-O['kgf_maliyeti']),("İşletme ve itiraz",-(O['bt']+O['itiraz']+O['denetim']+O['ptt']))]
fig,ax=plt.subplots(figsize=(12,6.2)); cum=0
for i,(a,v) in enumerate(adim):
    if i==0: ax.bar(i,v/M,color='#2d6aa8'); cum=v
    else: ax.bar(i,v/M,bottom=cum/M,color='#a11d1d'); cum+=v
    ax.text(i,(cum-v/2 if i else v/2)/M if False else (cum/M + (0.3 if v<0 else 0.3)),"%.2f"%(v/M),ha='center',fontsize=9)
net=O['net']; ax.bar(len(adim),net/M,color='#14662b' if net>0 else '#7a1f1f'); ax.text(len(adim),net/M-0.9 if net<0 else net/M+0.3,"%.2f"%(net/M),ha='center',fontsize=10,fontweight='bold')
ax.axhline(0,color='#333',lw=1); ax.set_xticks(range(len(adim)+1)); ax.set_xticklabels([a for a,_ in adim]+["NET"],rotation=25,ha='right',fontsize=9)
ax.set_ylabel("milyar TL / yıl"); ax.set_title("Orta senaryo, 4. yıl (kararlı durum): Hazine net etkisi",fontsize=13,fontweight='bold',color='#1f3a5f'); ax.spines[['top','right']].set_visible(False)
fig.text(0.01,-0.10,NOT,fontsize=8,color='#555'); fig.savefig('../GORSELLER/model_01_selale.png',dpi=110,bbox_inches='tight'); plt.close()
# 2 tornado
T=S['tornado'][:10]; T=T[::-1]
ad={'s_kayitli':'Halen kayıtlı oranı (s)','n_toplam':'Katılımcı sayısı (N)','prim_odeme':'Eski 4/b prim ödeme oranı','medyan_W':'Medyan hasılat (asgari ücret)','marj':'Kâr marjı (eski rejim)','uyum_ucretli':'Ücretlilerin eski uyumu','u_ucretli':'Ücretli ek gelir payı (u)','sigma':'Hasılat dağılımı yayılımı','phi':'Sahte fatura payı','kgf_alim':'KGF kullanım oranı','myo_uygun':'90 gün prim hak edenler','bes_vazgecme':'BES vazgeçme','kdv_donanim_pay':'Donanım alan payı','kgf_temerrut':'KGF temerrüt','onlem':'Önlem etkinliği','r_marj_ucretli':'Ücretli marjinal oran'}
fig,ax=plt.subplots(figsize=(11,6)); 
for i,t in enumerate(T):
    ax.barh(i,t[3]/M,color='#2d6aa8'); ax.barh(i,t[4]/M,color='#c98b00')
ax.set_yticks(range(len(T))); ax.set_yticklabels([ad.get(t[0],t[0]) for t in T],fontsize=9); ax.axvline(0,color='#333')
ax.set_xlabel("Net etkideki değişim (milyar TL / yıl); mavi: alt uç, sarı: üst uç değeri"); ax.set_title("Duyarlılık (tornado): hangi girdi sonucu en çok değiştirir?",fontsize=13,fontweight='bold',color='#1f3a5f'); ax.spines[['top','right']].set_visible(False)
fig.text(0.01,-0.02,NOT,fontsize=8,color='#555'); fig.savefig('../GORSELLER/model_02_tornado.png',dpi=110,bbox_inches='tight'); plt.close()
# 3 Monte Carlo
net=np.array(S['mc']['net'])/M; fig,ax=plt.subplots(figsize=(11,5.6))
ax.hist(np.clip(net,-40,15),bins=60,color='#2d6aa8'); ax.axvline(0,color='#a11d1d',lw=2)
q=S['mc']['net_q']
for k,c in ((5,'#777'),(50,'#14662b'),(95,'#777')): ax.axvline(q[str(k)]/M,color=c,ls='--'); ax.text(q[str(k)]/M,ax.get_ylim()[1]*0.93,"P%d: %.1f"%(k,q[str(k)]/M),fontsize=9,ha='center')
ax.set_xlabel("4. yıl net Hazine etkisi (milyar TL; −40 altı kırpıldı)"); ax.set_ylabel("deneme sayısı")
ax.set_title("Monte Carlo (%d deneme): net etkinin dağılımı; net > 0 olasılığı %%%.0f"%(S['mc']['n'],100*S['mc']['p_net_pozitif']),fontsize=12,fontweight='bold',color='#1f3a5f'); ax.spines[['top','right']].set_visible(False)
fig.text(0.01,-0.02,NOT,fontsize=8,color='#555'); fig.savefig('../GORSELLER/model_03_montecarlo.png',dpi=110,bbox_inches='tight'); plt.close()
# 4 varyantlar
V=S['varyant']; ks=list(V.keys()); vs=[V[k]/M for k in ks]
fig,ax=plt.subplots(figsize=(12,5.8)); ax.barh(range(len(ks)),vs,color=['#14662b' if v>0 else '#a11d1d' for v in vs]); ax.set_yticks(range(len(ks))); ax.set_yticklabels(ks,fontsize=9); ax.invert_yaxis(); ax.axvline(0,color='#333')
for i,v in enumerate(vs): ax.text(v+(0.15 if v>0 else -0.15),i,"%.1f"%v,va='center',ha='left' if v>0 else 'right',fontsize=9)
ax.set_xlabel("4. yıl net etki, Orta senaryo (milyar TL)"); ax.set_title("Politika varyantları: hangi hüküm Hazine dengesini nasıl değiştirir?",fontsize=13,fontweight='bold',color='#1f3a5f'); ax.spines[['top','right']].set_visible(False)
fig.text(0.01,-0.02,NOT,fontsize=8,color='#555'); fig.savefig('../GORSELLER/model_04_varyantlar.png',dpi=110,bbox_inches='tight'); plt.close()
# 5 beş yıl
fig,ax=plt.subplots(figsize=(10,5.4))
for ad_,c in (('Kötümser','#a11d1d'),('Orta','#c98b00'),('İyimser','#14662b')): ax.plot(range(1,6),[x/M for x in S['senaryo'][ad_]['yillar']],marker='o',color=c,label=ad_)
ax.axhline(0,color='#333'); ax.set_xlabel("yıl"); ax.set_ylabel("net etki (milyar TL)"); ax.legend(frameon=False); ax.set_xticks(range(1,6))
ax.set_title("Beş yıllık net etki (1. yılda tek seferlik BT ve PTT gideri dâhil)",fontsize=12,fontweight='bold',color='#1f3a5f'); ax.spines[['top','right']].set_visible(False)
fig.text(0.01,-0.02,NOT,fontsize=8,color='#555'); fig.savefig('../GORSELLER/model_05_bes_yil.png',dpi=110,bbox_inches='tight'); plt.close()
print('ok')
