GSMH_2025 = 62_288_195_804_000
ISV_PAYI = 7844.6
SGK_TOPLAM = 7844.6 + 4954.5
SGK_YILLIK = SGK_TOPLAM * 12

ISGUCU = 35533
ISSIZ = 2966
POTANSIYEL = 2608 + 2348 + 173
ATIL_ORAN = 29.7
PAYDA = ISGUCU + POTANSIYEL
ATIL = ATIL_ORAN / 100 * PAYDA
EKSIK = ATIL - ISSIZ - POTANSIYEL
KAYITDISI_TOPLAM = 8344
KAYITDISI_UCRETLI = 2843
KAYITDISI_TARIM = 3735
KAYITDISI_TARIM_DISI = KAYITDISI_TOPLAM - KAYITDISI_TARIM

print("A. ATIL ISGUCU 2025 (bin kisi; TUIK t15,t26,t27,t05)")
print("isgucu %d | potansiyel isgucu %d (umitsiz 2608, aramayan 2348, arayip baslayamayan 173) | payda %d" % (ISGUCU, POTANSIYEL, PAYDA))
print("atil = %.1f%% x payda = %.0f bin | issiz %d | zamana bagli eksik istihdam (turetilen) %.0f | potansiyel %d" % (ATIL_ORAN, ATIL, ISSIZ, EKSIK, POTANSIYEL))
print("kontrol: (eksik+issiz)/isgucu = %.1f%% (TUIK 19.6) ; (issiz+potansiyel)/payda = %.1f%% (TUIK 19.9)" % ((EKSIK + ISSIZ) / ISGUCU * 100, (ISSIZ + POTANSIYEL) / PAYDA * 100))
print("kadin atil 39.1 / erkek 24.0 ; 15-29 NEET 4711 (kadin 3233 = %.0f%%) ; uzun sureli issiz 537 ; Iskur basvuran issiz 1096 (%.0f%%)" % (3233 / 4711 * 100, 1096 / 2966 * 100))
print("kayit disi calisan %d (tarim disi %d) ; kayit disi ucretli %d" % (KAYITDISI_TOPLAM, KAYITDISI_TARIM_DISI, KAYITDISI_UCRETLI))
print()
print("B. BUTCESIZ TEDBIRLER - tavan aritmetigi (SGK getirisi %.1f TL/ay, %.0f bin TL/yil/kisi)" % (SGK_TOPLAM, SGK_YILLIK / 1000))
hedefler = [
    ("B1 potansiyel isgucu eslestirme (ilan yayini, Iskur disi kanallar)", POTANSIYEL),
    ("B2 zamana bagli eksik istihdam: tam zamana gecis hakki/esnek vardiya", EKSIK),
    ("B3 kayit disi ucretli: kayda gecis", KAYITDISI_UCRETLI),
    ("B4 kayit disi tarim disi toplam", KAYITDISI_TARIM_DISI),
    ("B5 15-29 NEET kadin: kismi sureli/ev eksenli is hakki", 3233),
]
for ad, n in hedefler:
    print(ad, "hedef %.0f bin" % n)
    for p in (0.01, 0.03, 0.05, 0.10):
        k = n * p
        print("   donusum %%%d: %.1f bin kisi; atil orani etkisi -%.2f puan; SGK geliri(asgari ucretle tavan) %.1f milyar TL/yil"
              % (p * 100, k, k / PAYDA * 100, k * 1000 * SGK_YILLIK / 1e9))
print()
print("C. PRIM DESTEGI KIRILMA TABLOSU: ek is basina net = (1-d)*SGK*(T+H) - s*ISV*T")
print("d* = 1 - s*ISV*T / (SGK*(T+H))  (T destek ayi, H destek sonrasi ayri istihdam ayi, iskonto 0)")
print("s    T   H=0   H=12  H=24  H=36")
for s in (0.5, 1.0):
    for T in (6, 12, 24):
        row = []
        for H in (0, 12, 24, 36):
            d = 1 - s * ISV_PAYI * T / (SGK_TOPLAM * (T + H))
            row.append("%5.1f%%" % (d * 100))
        print("%.1f %3d  %s" % (s, T, " ".join(row)))
print("(deadweight bu orani asarsa program zarar eder; negatif = H ne olursa olsun zarar)")
print()
CAP_ORAN = 0.001
cap = GSMH_2025 * CAP_ORAN
print("D. ANI YUK SINIRI (varsayim: yillik net cikis <= GSMH'nin %%%.1f'i = %.1f milyar TL)" % (CAP_ORAN * 100, cap / 1e9))
for s, T in ((1.0, 12), (0.5, 12), (1.0, 6)):
    print("   s=%.1f T=%d: yillik en fazla %.0f bin hirasyon (brut maliyet)" % (s, T, cap / (s * ISV_PAYI * T) / 1000))
print()
print("E. 10 YILLIK SIMULASYON (sabit 2026 TL; varsayim: ise alis yili 1-3 pilot 50/100/200 bin sonra 200 bin; s=1,T=12; yillik elde kalma ro)")
def sim(d, ro, sched, s=1.0, T=12, iskonto=0.0, yil=10):
    cum = 0.0
    peak = 0.0
    pay = None
    rows = []
    for y in range(yil):
        cost = 0.0
        gain = 0.0
        for k in range(y + 1):
            hire = sched[min(k, len(sched) - 1)] * 1000
            if k == y:
                cost += hire * s * ISV_PAYI * T
            age = y - k
            if age == 0:
                gain += hire * (1 - d) * SGK_YILLIK
            else:
                gain += hire * (1 - d) * (ro ** age) * SGK_YILLIK
        net = (gain - cost) / (1 + iskonto) ** y
        cum += net
        peak = min(peak, cum)
        if pay is None and cum >= 0:
            pay = y + 1
        rows.append((y + 1, cost / 1e9, gain / 1e9, cum / 1e9))
    return rows, peak, pay
sched = [50, 100, 200]
print("d     ro   iskonto  10y kumulatif(mlr TL)  dip(mlr TL)  dip/GSMH  basabas yili  max yillik cikis/GSMH")
for d in (0.3, 0.5, 0.7, 0.8):
    for ro in (0.6, 0.8):
        for isk in (0.0, 0.2):
            rows, peak, pay = sim(d, ro, sched, iskonto=isk)
            mx = max(r[1] for r in rows) * 1e9 / GSMH_2025 * 100
            print("%.1f  %.1f  %.1f   %10.1f   %10.1f   %.4f%%   %s   %.3f%%" % (d, ro, isk, rows[-1][3], peak / 1e9, abs(peak) / GSMH_2025 * 100, pay, mx))
print()
print("F. ESLESTIRME/DANISMANLIK (kisi basi maliyet c): kirilma c* = p*(1-d)*SGK_ayi*H ; p yerlesme olasiligi")
for p in (0.02, 0.05, 0.10):
    for d in (0.5, 0.8):
        for H in (12, 36):
            print("   p=%.2f d=%.1f H=%d ay: c* = %.0f TL/kisi" % (p, d, H, p * (1 - d) * SGK_TOPLAM * H))
