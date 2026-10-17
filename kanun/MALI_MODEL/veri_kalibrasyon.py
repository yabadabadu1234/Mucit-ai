import re, math, json
import numpy as np
from math import erf, log, exp, sqrt
ASGARI_2024_BRUT=20002.50
YOUNG_CIRO=13.5276596335813
YOUNG_FIRMA=33.4949753549253
DOGAN_2024={'G':203028,'H':106630,'F':64021,'I':59544,'C':59454,'M':39718,'S':26956,'L':14435,'J':12894,'Q':12769,'N':12554,'R':6352,'P':5625,'D':1184,'B':839,'E':792}
def val(x):
    try: return float(x)
    except: return None
def oku(dosya):
    toplam={}; mikro={}; son=None
    for line in open(dosya):
        p=[x.strip() for x in line.rstrip('\n').split(' | ')]
        if len(p)<3: continue
        m=re.match(r'^\d+ (.*)$',p[0])
        if not m: continue
        ad=m.group(1)
        k=re.match(r'^Kısım ([A-Z])$',ad)
        if k:
            son=k.group(1); toplam[son]=val(p[-1]); continue
        s=re.match(r'^Section ([A-Z])$',ad)
        if s and 'Mikro' in p[1]:
            mikro[s.group(1)]=val(p[-1])
    return toplam,mikro
def phi(z): return 0.5*(1+erf(z/sqrt(2)))
tg,mg=oku('veri/boyut_girisim_sayisi.txt')
tc,mc=oku('veri/boyut_ciro.txt')
sek={}
for h in sorted(mg):
    if mg[h] and mc.get(h): sek[h]=(mg[h],mc[h],mc[h]/mg[h])
w=np.array([DOGAN_2024[h] for h in sek if h in DOGAN_2024]); hs=[h for h in sek if h in DOGAN_2024]
ort_sektor=np.array([sek[h][2] for h in hs])
agirlikli=float((w*ort_sektor).sum()/w.sum())
mikro_firma=np.array([sek[h][0] for h in hs])
lg=np.log(ort_sektor)
mu_b=float((mikro_firma*lg).sum()/mikro_firma.sum())
sig_b=float(sqrt((mikro_firma*(lg-mu_b)**2).sum()/mikro_firma.sum()))
genc_katsayi=YOUNG_CIRO/YOUNG_FIRMA
mean_tl=genc_katsayi*agirlikli
mean_W=mean_tl/ASGARI_2024_BRUT
sonuc=dict(sektorler={h:dict(mikro_firma=sek[h][0],mikro_ciro=sek[h][1],ciro_firma_tl=sek[h][2]) for h in hs},
  doğum_agirlikli_mikro_ciro_firma_tl=agirlikli,genc_katsayi=genc_katsayi,genc_ortalama_ciro_tl=mean_tl,genc_ortalama_ciro_W=mean_W,sigma_sektorlerarasi=sig_b)
izgara=[]
for sg in [sig_b,1.0,1.25,1.5,1.75,2.0]:
    med=mean_W*exp(-sg*sg/2)
    p_alti=phi((log(24)-log(med))/sg)
    izgara.append(dict(sigma=round(sg,3),medyan_W=round(med,2),p_tavan_alti=round(p_alti,3)))
sonuc['izgara']=izgara
json.dump(sonuc,open('veri_kalibrasyon.json','w'),ensure_ascii=False,indent=1)
print('sektör mikro ciro/firma (TL, 2024):')
for h in hs: print(' ',h,'firma',int(sek[h][0]),'ciro/firma %.2f mn'%(sek[h][2]/1e6))
print('doğum ağırlıklı mikro ciro/firma: %.3f mn TL'%(agirlikli/1e6))
print('genç katsayısı (2021+ ciro payı/firma payı): %.4f'%genc_katsayi)
print('genç ort ciro: %.3f mn TL = %.1f asgari (2024 brüt %.2f)'%(mean_tl/1e6,mean_W,ASGARI_2024_BRUT))
print('sektörler arası sigma (log): %.3f'%sig_b)
for r in izgara: print(r)
