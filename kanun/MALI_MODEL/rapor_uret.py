# MALI_SIMULASYON_SONUCLARI.md'yi JSON çıktılarından yeniden üretir (elle rakam girilmez).
import json
from model import *
B=json.load(open('baz_sonuc.json')); MC=json.load(open('mc_uc_sonuc.json')); KR=json.load(open('kirilma_izgara.json'))
KS=json.load(open('kose_stres.json')); SZ=json.load(open('sizinti_analiz.json')); TO=json.load(open('tornado_senaryo.json'))
L=["# MALİ MODEL: VERİYE BAĞLI SENARYOLAR, BELİRSİZLİK VE KIRILMA ANALİZİ (Ekim 2026)","",
"Üretici: `rapor_uret.py` (tüm rakamlar JSON çıktılarından alınır). Net ve NPV milyar TL, 4. yıl ve 5 yıl reel %5.","",
"## 0. Senaryo girdileri (veriye bağlı)","",
"N (katılımcı) TÜİK 2025 tablolarından: Kötümser = 2021 düzeyi (255 bin, kendi işyeri kurmak niyetli işsiz); Orta = 2025 (332 bin); İyimser = 2025'in 2021–2025 büyüme hızıyla (%6,8/yıl) 5 yıl uzatılması (462 bin). Dağılım σ(log) = 0,106 (aynı seriden). Brezilya MEI analogu (havuzun %20'si ≈ 1.047 bin) yalnızca dış sınır olarak kırılma ızgarasında ve tornado'da kullanıldı.","",
"| Senaryo | N | Baz net | NPV5 | Brüt tevkifat |","|:--|--:|--:|--:|--:|"]
for ad in ['Kötümser','Orta','İyimser']:
    b=B[ad]; L.append("| %s | %s | %.2f | %.2f | %.2f |"%(ad,f"{int(b['N']):,}".replace(',','.'),b['net'],b['npv'],b['brut']))
L+=["","## 1. Birleşik Monte Carlo (6000 çekim, tüm girdiler birlikte)","","| Senaryo | P1 | P5 | P50 | P95 | P99 | P(net>0) | NPV P50 |","|:--|--:|--:|--:|--:|--:|--:|--:|"]
for ad in ['Kötümser','Orta','İyimser']:
    q=MC[ad]['net_q']; L.append("| %s | %.2f | %.2f | %.2f | %.2f | %.2f | %.3f | %.2f |"%(ad,q['1'],q['5'],q['50'],q['95'],q['99'],MC[ad]['p_net_pozitif'],MC[ad]['npv_q']['50']))
L+=["","## 2. Spearman duyarlılığı (ilk 6)",""]
for ad in ['Kötümser','Orta','İyimser']:
    L.append("- **%s:** "%ad+", ".join("%s %+.2f"%(k,v) for k,v in list(MC[ad]['spearman'].items())[:6]))
L+=["","## 3. Tek parametre tornado (17 parametre; düşük / yüksek uç)",""]
for ad in ['Kötümser','Orta','İyimser']:
    L.append("**%s** (taban %.2f)"%(ad,TO[ad]['taban'])); L.append("")
    L.append("| parametre | düşük uç değeri | yüksek uç değeri | Δ düşük | Δ yüksek |"); L.append("|:--|--:|--:|--:|--:|")
    for k,a,b,lo,hi in TO[ad]['tornado']: L.append("| %s | %g | %g | %.2f | %.2f |"%(k,a,b,lo,hi))
    L.append("")
L+=["## 4. Kırılma ızgarası (net): s × φ (sahte fatura)",""]
for ad in ['Kötümser','Orta','İyimser']:
    g=KR[ad]; L.append("**%s** (satır φ, sütun s)"%ad); L.append("")
    L.append("| φ \\ s | "+" | ".join("%.1f"%s for s in g['grid_s'])+" |"); L.append("|:--|"+"--:|"*len(g['grid_s']))
    for ph,row in zip(g['grid_phi'],g['net']): L.append("| %.2f | "%ph+" | ".join("%.1f"%x for x in row)+" |")
    L.append("")
L+=["## 5. Sızıntı (sizinti) × kimlik kiralama (kiralama)",""]
for ad in ['Kötümser','Orta','İyimser']:
    g=SZ[ad]; L.append("**%s** (satır kiralama, sütun sızıntı)"%ad); L.append("")
    L.append("| kiralama \\ sızıntı | "+" | ".join("%.2f"%z for z in g['grid_sizinti'])+" |"); L.append("|:--|"+"--:|"*len(g['grid_sizinti']))
    for k,row in zip(g['grid_kiralama'],g['net']): L.append("| %.2f | "%k+" | ".join("%.2f"%x for x in row)+" |")
    L.append("")
L+=["## 6. Birlikte en kötü / en iyi uç","","| Senaryo | Taban | En kötü | En iyi |","|:--|--:|--:|--:|"]
for ad in ['Kötümser','Orta','İyimser']:
    r=KS[ad]; L.append("| %s | %.2f | %.2f | %.2f |"%(ad,r['taban'],r['en_kotu'],r['en_iyi']))
L+=["","## 7. Sınırlılıklar","",
"- N aralığı 2021–2025 niyet serisinden türetildi; yalnızca iki sayı noktası (2021, 2025) ve beş yıl var. Niyet ≠ katılım: kendi işyeri kurmak isteyen işsiz sayısı, mikro mükellefiyete geçecek kişi sayısının bir vekilidir. Serbest çalışanların geçişi bu sayıya dahil değil.",
"- Brezilya analogu (%19–20) yalnızca dış sınır; Türkiye'de bu oran verilerle doğrulanmadı.",
"- s, φ, sızıntı, kiralama, π, KGF, BES: veri yok, varsayım. Sonuçların bunlara duyarlılığı §3–§5'te.",
"- Model yalnızca 4. yıl ve 5 yıllık NPV verir; ilk yıl etkisi ve genç seyri bu raporda yok.",""]
open('MALI_SIMULASYON_SONUCLARI.md','w').write("\n".join(L)+"\n")
print("rapor yazıldı")
