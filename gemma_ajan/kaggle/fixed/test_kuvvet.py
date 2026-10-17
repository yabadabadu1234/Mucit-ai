"""kuvvet.py birim testleri (CPU). Çalıştırma: PYTHONPATH=/tmp/cputorch python3 test_kuvvet.py"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch  # noqa: E402

import kuvvet as K  # noqa: E402

random.seed(7)


def rows(n):
    out = []
    for _ in range(n):
        out.append({"route": random.randrange(4), "compiler_score": random.random(), "distance": random.random()})
    return out


def test_taban():
    w = 0.1
    assert abs(K.taban_agirlik(0.0, w) - 1.0) < 1e-12
    assert abs(K.taban_agirlik(1.0, w) - w) < 1e-12
    xs = [K.taban_agirlik(i / 10, w) for i in range(11)]
    assert all(xs[i] >= xs[i + 1] for i in range(10)), "uzaklık arttıkça ağırlık azalmalı"
    assert min(xs) > 0.0, "w_taban > 0 kuralı"
    try:
        K.taban_agirlik(0.5, 0.0)
        raise AssertionError("w_taban = 0 reddedilmeli")
    except ValueError:
        pass


def test_validate():
    for bad in ({"route": 4, "compiler_score": 0.5, "distance": 0.5},
                {"route": 0, "compiler_score": 1.5, "distance": 0.5},
                {"route": 0, "compiler_score": 0.5},
                {"route": 0, "compiler_score": True, "distance": 0.5}):
        try:
            K.validate_row(bad)
            raise AssertionError(f"reddedilmedi: {bad}")
        except ValueError:
            pass
    assert K.validate_row({"route": 2, "compiler_score": 0.0, "distance": 1.0}) == (2, 0.0, 1.0)


def test_katsayi_toplamlari():
    rs = rows(20)
    A, B = K.katsayilar(rs, 0.1)
    # CLM akışı: her örnek 1/n, toplam 1
    assert abs(sum(a[K.STREAM_CLM] for a in A) - 1.0) < 1e-12
    # SFT akışı: her örnek 1/n, toplam 1
    assert abs(sum(b[K.STREAM_SFT] for b in B) - 1.0) < 1e-12
    # Güzergâh r: katsayı ortalaması, c*w ortalamasına eşit
    for r in range(4):
        idx = [i for i, row in enumerate(rs) if row["route"] == r]
        if not idx:
            continue
        lhs = sum(A[i][r] for i in idx)
        rhs = sum(rs[i]["compiler_score"] * K.taban_agirlik(rs[i]["distance"], 0.1) for i in idx) / len(idx)
        assert abs(lhs - rhs) < 1e-12, (r, lhs, rhs)


def test_uretilmis_ornek_k1_seyreltmez():
    """compiler_score = 0 (üretilmiş) örnek K1 paydasını değiştirmemeli, yalnız K2'ye girer."""
    dogrulanmis = [{"route": 0, "compiler_score": 1.0, "distance": 0.0},
                   {"route": 0, "compiler_score": 1.0, "distance": 0.0}]
    uretilmis = {"route": 0, "compiler_score": 0.0, "distance": 0.5}
    A1, _ = K.katsayilar(dogrulanmis, 0.1)
    A2, _ = K.katsayilar(dogrulanmis + [uretilmis], 0.1)
    assert abs(A2[0][0] - A1[0][0]) < 1e-12 and abs(A2[1][0] - A1[1][0]) < 1e-12, "K1 seyrelmemeli"
    assert A2[2][0] == 0.0 and A2[2][K.STREAM_CLM] > 0.0
    _, B2 = K.katsayilar([uretilmis], 0.1)
    assert B2[0][K.STREAM_SFT] == 1.0, "SFT akışı her örneğe 1/n"
    assert abs(K.katsayilar([uretilmis], 0.1)[0][0][K.STREAM_DIST] - 0.5 * K.taban_agirlik(0.5, 0.1)) < 1e-12


def test_guzergah_skoru():
    onceki = [1.0, 0.8, 0.6, 0.4]
    uretilen = [{"route": 0, "distance": 0.25}, {"route": 0, "distance": 0.75},
                {"route": 2, "distance": 1.0}]
    yeni = K.guzergah_skorlari(onceki, uretilen, taban=0.1)
    assert abs(yeni[0] - 0.5) < 1e-12, "1 - ortalama(0.25, 0.75)"
    assert yeni[1] == 0.8, "çıktısı olmayan güzergâh önceki değerini korur"
    assert abs(yeni[2] - 0.1) < 1e-12, "taban: skor 0'a inmez"
    assert yeni[3] == 0.4
    # Skorlar değişken: güzergâhlar birbirinden farklı olabilir
    assert len({round(x, 6) for x in yeni}) > 1
    try:
        K.guzergah_skorlari(onceki, uretilen, taban=0.0)
        raise AssertionError("taban = 0 reddedilmeli")
    except ValueError:
        pass


def test_pcgrad_ozellikleri():
    g1 = [1.0, 0.0]
    g2 = [-1.0, 0.5]  # g1 ile negatif iç çarpım
    out = K.pcgrad([g1, g2] + [[0.0, 0.0]] * (K.STREAMS - 2))
    assert len(out) == 2
    # Ortogonal akışlarda PCGrad toplama eşittir
    h = K.pcgrad([[1.0, 0.0], [0.0, 2.0]])
    assert h == [1.0, 2.0]
    # Python ve torch sürümleri aynı sonucu verir
    rnd = [[random.gauss(0, 1) for _ in range(6)] for _ in range(K.STREAMS)]
    a = K.pcgrad(rnd)
    b = K.pcgrad_t([torch.tensor(v, dtype=torch.float64) for v in rnd]).tolist()
    assert max(abs(x - y) for x, y in zip(a, b)) < 1e-9


def test_pcgrad_cakisma_giderilir():
    # Tek çatışma: projeksiyondan sonra g1' · g2 = 0
    g1 = torch.tensor([1.0, 1.0])
    g2 = torch.tensor([-1.0, 0.0])
    p = K.pcgrad_t([g1, g2])
    # g1' = g1 - (g1·g2/|g2|²) g2 = [1,1] - (-1)[-1,0] = [0,1]
    # g2' = g2 - (g2·g1/|g1|²) g1 = [-1,0] - (-1/2)[1,1] = [-0.5,0.5]
    # toplam = [-0.5, 1.5]
    assert torch.allclose(p, torch.tensor([-0.5, 1.5]), atol=1e-6), p.tolist()


def test_akis_toplami_otomatik_turev():
    """Akışların katsayılı toplamı, doğrudan kayıp toplamının gradyanına eşit olmalı."""
    torch.manual_seed(0)
    d_in, d_out, n = 5, 3, 6
    W = torch.randn(d_out, d_in, requires_grad=True)
    xs = [torch.randn(d_in) for _ in range(n)]
    ys = [torch.randint(0, d_out, (1,)).item() for _ in range(n)]
    rs = []
    for i in range(n):
        rs.append({"route": i % 4, "compiler_score": 0.2 + 0.1 * i, "distance": 0.05 * i})
    A, B = K.katsayilar(rs, 0.1)

    def per_sample(i):
        logits = W @ xs[i]
        nll = torch.nn.functional.cross_entropy(logits.unsqueeze(0), torch.tensor([ys[i]]))
        return nll, nll  # tek token: CLM = SFT = nll (maske tümü açık)

    # Akış yolu
    streams = [torch.zeros(W.numel()) for _ in range(K.STREAMS)]
    for i in range(n):
        clm, sft = per_sample(i)
        gc = torch.autograd.grad(clm, W, retain_graph=True)[0].reshape(-1)
        gs = torch.autograd.grad(sft, W)[0].reshape(-1)
        for k in range(K.STREAMS):
            streams[k] += A[i][k] * gc + B[i][k] * gs
    via_streams = sum(streams)

    # Doğrudan yol: katsayılı kayıp toplamı
    total = 0.0
    for i in range(n):
        clm, sft = per_sample(i)
        coef_clm = sum(A[i])
        coef_sft = sum(B[i])
        total = total + coef_clm * clm + coef_sft * sft
    direct = torch.autograd.grad(total, W)[0].reshape(-1)
    assert torch.allclose(via_streams, direct, atol=1e-5), (via_streams[:4], direct[:4])


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for t in tests:
        t()
        print("GEÇTİ", t.__name__)
    print(f"TÜMÜ GEÇTİ ({len(tests)})")
