"""Altı kuvvetli gradyan birleştirici (LoRA, düz kayıp; DoRA yok).

Kuvvetler (her biri bir gradyan akışıdır):
  K1  bağımsız veri yolları: 4 güzergâh (route 0..3), her birinin derleyici skoru ağırlıktır
  K2  teste verilen cevap: doğruluğa olan uzaklık d_i ile ağırlıklı akış
  K3  pusula: akışlar arası çatışma önleme (PCGrad, sabit sıra, zar yok)
  K4  kademeli tesir: w_i = w_taban + (1 - w_taban) * (1 - d_i), w_taban > 0
  K5  CLM: tüm token'lar üzerinden kayıp (maskesiz)
  K6  SFT: yalnız asistan token'ları üzerinden kayıp
  K7  politika: REINFORCE terimi; üretimin log-olasılığı, avantajla ağırlıklı (altın cevap yok)

Akışlar: 0..3 güzergâh, 4 uzaklık, 5 CLM, 6 SFT, 7 politika. Her örnek için yalnız iki geri yayılım
gerekir (CLM ve SFT kayıpları); akışlar bu iki gradyanın katsayılı toplamıdır.
Veri eksik alan içeriyorsa reddedilir; uydurma değer yoktur.
"""
ROUTES = 4
STREAMS = ROUTES + 4  # 4 güzergâh + uzaklık + CLM + SFT + politika (REINFORCE)
STREAM_DIST = ROUTES
STREAM_CLM = ROUTES + 1
STREAM_SFT = ROUTES + 2
STREAM_POL = ROUTES + 3  # K7: -A * ∇log p(üretim); A = (1 − mesafe) − taban


def validate_row(row, where=""):
    """Her satır üç alan taşımalı: route (0..3), compiler_score ∈ [0,1], distance ∈ [0,1]."""
    r = row.get("route")
    c = row.get("compiler_score")
    d = row.get("distance")
    if r not in range(ROUTES):
        raise ValueError(f"{where} route eksik ya da 0..3 dışında: {r!r}")
    for name, v in (("compiler_score", c), ("distance", d)):
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not (0.0 <= float(v) <= 1.0):
            raise ValueError(f"{where} {name} eksik ya da [0,1] dışında: {v!r}")
    return int(r), float(c), float(d)


def ezber_orani(uretilen, altin, n=8):
    """Altın cevabın kelime n-gramlarının üretilen metinde geçme oranı, [0,1].

    Yüksekse model altın cevabı kelimesi kelimesine üretiyor (ezber). Bu oran yalnızca ÖLÇÜLÜR;
    eğitim sinyali olarak kullanılmaz. Altın kısa ise (n'den az kelime) 0 döner.
    """
    a = altin.split()
    if len(a) < n:
        return 0.0
    u = uretilen.split()
    altin_ng = {tuple(a[i:i + n]) for i in range(len(a) - n + 1)}
    uretilen_ng = {tuple(u[i:i + n]) for i in range(len(u) - n + 1)}
    return len(altin_ng & uretilen_ng) / len(altin_ng)


def guzergah_skorlari(onceki, uretilen, taban=0.1):
    """K1 derleyici skoru: her güzergâh için 1 − ortalama mesafe (güzergâha özgü denetçiyle ölçülür).

    uretilen: model çıktıları [{"route", "distance"}]. Bu partide o güzergâhtan çıktı yoksa önceki
    değer kalır. taban > 0: skor 0'a inmez, güzergâh K1'den tamamen düşmez.
    """
    if not (0.0 < taban <= 1.0):
        raise ValueError("taban (0, 1] aralığında olmalı")
    yeni = list(onceki)
    for r in range(ROUTES):
        ds = [float(g["distance"]) for g in uretilen if g["route"] == r]
        if ds:
            yeni[r] = max(taban, 1.0 - sum(ds) / len(ds))
    return yeni


def taban_agirlik(distance, w_taban):
    """K4: uzaklık 0 (doğru) iken 1, uzaklık 1 iken w_taban. Her zaman w_taban > 0."""
    if not (0.0 < w_taban <= 1.0):
        raise ValueError("w_taban (0, 1] aralığında olmalı")
    d = min(max(float(distance), 0.0), 1.0)
    return w_taban + (1.0 - w_taban) * (1.0 - d)


def katsayilar(rows, w_taban):
    """Her örnek için iki katsayı vektörü: A (CLM) ve B (SFT), her biri STREAMS uzunluğunda.

    Akış k = Σ_i (A[i][k] * g_clm_i + B[i][k] * g_sft_i). Normalizasyon: n = örnek sayısı,
    n_r = güzergâh r'deki örnek sayısı (0 ise o akış sıfır).
    """
    n = len(rows)
    if n == 0:
        raise ValueError("boş küme")
    n_route = [0] * ROUTES
    parsed = []
    for i, row in enumerate(rows):
        r, c, d = validate_row(row, where=f"satır {i}:")
        if c > 0.0:
            n_route[r] += 1  # yalnız derleyici skoru olan (doğrulanmış) örnekler K1'e girer
        parsed.append((r, c, d))
    A, B = [], []
    for r, c, d in parsed:
        w = taban_agirlik(d, w_taban)
        a = [0.0] * STREAMS
        b = [0.0] * STREAMS
        if c > 0.0:
            a[r] = c * w / n_route[r]  # K1 + K4
        a[STREAM_DIST] = d * w / n  # K2 + K4
        a[STREAM_CLM] = 1.0 / n  # K5
        b[STREAM_SFT] = 1.0 / n  # K6
        A.append(a)
        B.append(b)
    return A, B


def pcgrad(flat_streams):
    """K3: Yu & Kumar (2020) PCGrad. flat_streams: STREAMS adet düz vektör (liste).

    Her akış, diğer AKIŞIN ORİJİNAL gradyanıyla negatif iç çarpımı varsa, o gradyanın normal
    bileşeni çıkarılarak projekte edilir. Sıra sabittir (indeks sırası). Dönüş: toplam vektör.
    """
    k = len(flat_streams)
    dim = len(flat_streams[0])
    proj = [list(g) for g in flat_streams]
    for i in range(k):
        for j in range(k):
            if i == j:
                continue
            gi, gj = proj[i], flat_streams[j]
            dot = sum(x * y for x, y in zip(gi, gj))
            if dot < 0.0:
                nj = sum(y * y for y in gj)
                if nj > 0.0:
                    coef = dot / nj
                    proj[i] = [x - coef * y for x, y in zip(gi, gj)]
    total = [0.0] * dim
    for g in proj:
        for t in range(dim):
            total[t] += g[t]
    return total


def pcgrad_t(stream_tensors):
    """Torch sürümü (aynı kural). stream_tensors: STREAMS adet 1-D tensor listesi."""
    import torch

    proj = [g.clone() for g in stream_tensors]
    for i in range(len(stream_tensors)):
        for j in range(len(stream_tensors)):
            if i == j:
                continue
            gj = stream_tensors[j]
            dot = torch.dot(proj[i], gj)
            if dot < 0:
                nj = torch.dot(gj, gj)
                if nj > 0:
                    proj[i] = proj[i] - (dot / nj) * gj
    return torch.stack(proj).sum(dim=0)
