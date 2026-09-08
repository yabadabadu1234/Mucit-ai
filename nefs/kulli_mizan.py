from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .ayna import AynaAyari, halka
from .hafiza import CERH, TASDIK, TEVAKKUF, Hafiza
from .tdd import esit_mi, kanonik_adres

__all__ = ["MizanAyari", "uhlmann", "givens", "holonomi",
           "holonomi_yigin", "engellenme", "kulli_mizan", "mizan_cetveli",
           "rapor"]


@dataclass
class MizanAyari:

    hal_kaynagi: str = "tutarlı"
    lam_cevrim: float = 1.0
    lam_monogami: float = 0.5
    lam_tip: float = 0.75
    lam_engel: float = 0.6
    ayna_tur: int = 24
    ayna_teta: float = 0.2617993877991494
    ayna_r: float = 0.35
    golge_ornegi: int = 0
    golge_haddi: float = 0.05
    qsvt: int = 16
    qudit_derece: int = 8
    qudit_yon: int = 8
    cevrim_boyu: int = 3
    cevrim_sayisi: int = 8
    rust_t0: float = 0.5
    rust_tau: float = 0.15
    sadakat_acik: int = 1
    parite_lifi: int = 2
    lam_tenakuz: float = 0.4
    tenakuz_eps: float = 1e-5
    dislama_tau: float = 8.0
    lam_kategori: float = 0.5
    lam_nokta: float = 0.25
    lam_meleke: float = 0.5
    lam_zirh: float = 0.5
    lam_kaide: float = 0.5
    lam_tasma: float = 0.5
    basamak: int = 0
    meleke_olcumu: int = 1
    usul_acik: int = 1
    usul_haddi: float = 0.0
    usul_seferi: int = 4
    suphe_acik: int = 1
    suphe_sonumu: float = 0.05
    rust_kapanis: float = 0.5
    rust_muayene: int = 1
    kenar: float = 0.0
    zeno_esigi: float = 0.35
    tdd_cekirdek: int = 16
    zeno_tepe: float = 0.9
    toplam_adim: int = 200
    tohum: int = 0

    def __post_init__(self) -> None:
        assert int(self.cevrim_boyu) >= 3, (
            "çevrim boyu en az 3 olmalı: iki adımlı çevrim daima U=I "
            "verir ve holonomi taşımaz (ölçüldü)")
        assert int(self.cevrim_sayisi) >= 1, "en az bir çevrim taranmalı"
        assert 0.0 <= float(self.kenar) < 0.5, "kenar [0, 0.5) olmalı"


def uhlmann(rho: np.ndarray, sigma: np.ndarray) -> float:
    R = np.asarray(rho, complex)
    S = np.asarray(sigma, complex)
    assert R.shape == S.shape and R.ndim == 2, (
        "sadakat için iki aynı boyda yoğunluk matrisi lâzım")
    w, V = np.linalg.eigh(0.5 * (R + R.conj().T))
    w = np.clip(w.real, 0.0, None)
    kok = (V * np.sqrt(w)) @ V.conj().T
    M = kok @ S @ kok
    e = np.linalg.eigvalsh(0.5 * (M + M.conj().T)).real
    F = float(np.sum(np.sqrt(np.clip(e, 0.0, None))) ** 2)
    return float(np.clip(F, 0.0, 1.0))


def givens(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = np.asarray(a, complex).reshape(-1)
    b = np.asarray(b, complex).reshape(-1)
    assert a.size == b.size and a.size >= 2, "Givens için aynı boyda iki hâl"
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    assert na > 0 and nb > 0, "sıfır hâl arasında morfizm kurulamaz"
    a = a / na
    b = b / nb
    c = complex(np.vdot(a, b))
    dik = b - c * a
    s = float(np.linalg.norm(dik))
    n = a.size
    if s < 1e-12:
        faz = c / abs(c) if abs(c) > 0 else 1.0 + 0j
        return np.eye(n, dtype=complex) * faz
    e2 = dik / s
    U = np.eye(n, dtype=complex)
    P = np.stack([a, e2], axis=1)
    R = np.array([[c, -np.conj(s)], [s, np.conj(c)]], dtype=complex)
    U = U - P @ P.conj().T + P @ R @ P.conj().T
    return U


def holonomi(hal: Sequence[np.ndarray]) -> Tuple[np.ndarray, float, float]:
    H = [np.asarray(h, complex).reshape(-1) for h in hal]
    assert len(H) >= 3, (
        "kapalı çevrim en az üç köşe ister; iki köşe daima U=I verir")
    n = H[0].size
    U = np.eye(n, dtype=complex)
    for i in range(len(H)):
        U = givens(H[i], H[(i + 1) % len(H)]) @ U
    omega = float(np.real(np.trace(U)) / n)
    yol = 0.0
    for i in range(len(H)):
        a = H[i] / (np.linalg.norm(H[i]) or 1.0)
        b = H[(i + 1) % len(H)]
        b = b / (np.linalg.norm(b) or 1.0)
        yol += float(math.acos(float(np.clip(abs(np.vdot(a, b)), 0.0, 1.0))))
    return U, float(np.clip(omega, -1.0, 1.0)), float(yol)


def holonomi_yigin(H: np.ndarray, idx: np.ndarray
                   ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    H = np.asarray(H, complex)
    idx = np.asarray(idx, int)
    C, boy = idx.shape
    n = H.shape[1]
    assert boy >= 3, "kapalı çevrim en az üç köşe ister"
    K = H[idx]
    K = K / np.maximum(np.linalg.norm(K, axis=-1, keepdims=True), 1e-300)
    U = np.broadcast_to(np.eye(n, dtype=complex), (C, n, n)).copy()
    yol = np.zeros(C, float)
    for t in range(boy):
        A = K[:, t, :]
        Bv = K[:, (t + 1) % boy, :]
        c = np.einsum('ci,ci->c', A.conj(), Bv)
        yol += np.arccos(np.clip(np.abs(c), 0.0, 1.0))
        dik = Bv - c[:, None] * A
        sn = np.linalg.norm(dik, axis=-1)
        e2 = dik / np.maximum(sn, 1e-300)[:, None]
        P0 = np.einsum('ci,cj->cij', A, A.conj())
        P1 = np.einsum('ci,cj->cij', e2, e2.conj())
        X01 = np.einsum('ci,cj->cij', A, e2.conj())
        X10 = np.einsum('ci,cj->cij', e2, A.conj())
        G = (c[:, None, None] * P0 - sn[:, None, None] * X01
             + sn[:, None, None] * X10
             + np.conj(c)[:, None, None] * P1)
        birim = np.broadcast_to(np.eye(n, dtype=complex), (C, n, n))
        Gt = birim - P0 - P1 + G
        ayni = sn < 1e-12
        if np.any(ayni):
            faz = np.where(np.abs(c) > 0, c / np.maximum(np.abs(c), 1e-300),
                           1.0 + 0j)
            Gt = np.where(ayni[:, None, None],
                          birim + (faz[:, None, None] - 1.0) * P0, Gt)
        U = np.einsum('cij,cjk->cik', Gt, U)
    Kq = np.transpose(K, (0, 2, 1))
    Q, R = np.linalg.qr(Kq)
    kose = np.abs(np.diagonal(R, axis1=1, axis2=2))
    var = kose > 1e-9
    r_etkin = np.maximum(var.sum(axis=1), 1)
    Qc = Q * var[:, None, :]
    om = np.real(np.einsum('cni,cnm,cmi->c', Qc.conj(), U, Qc)) / r_etkin
    return U, np.clip(om, -1.0, 1.0), yol


def _cevrimleri_tara(haller: Sequence[np.ndarray], ayar: MizanAyari,
                     baglamlar: Optional[Sequence[Sequence[int]]] = None,
                     hedefler: Optional[Sequence[int]] = None,
                     n_v: int = 0) -> Dict[str, Any]:
    m = len(haller)
    a = ayar
    if m < int(a.cevrim_boyu):
        return {"ceza": 0.0, "meşru": 0, "kısır": 0, "tenakuz": 0,
                "engel": 0, "çevrim": [], "ω": [], "indis": [],
                "bariyer": {"ceza": 0.0, "azamî": 0.0, "ham_azamî": 0.0,
                            "tavan": 0.0, "dışlama_ortalama": 0.0,
                            "çevrim": 0}}
    r = np.random.default_rng(int(a.tohum))
    ceza = 0.0
    say = {"meşru": 0, "kısır": 0, "tenakuz": 0, "engel": 0}
    kayit: List[Tuple[float, float, float]] = []
    omegalar: List[float] = []
    idx_hepsi = np.stack([
        r.choice(m, size=int(a.cevrim_boyu), replace=False)
        for _ in range(int(a.cevrim_sayisi))])
    H = np.stack([np.asarray(h, complex).reshape(-1) for h in haller])
    U_hepsi, om_hepsi, yol_hepsi = holonomi_yigin(H, idx_hepsi)
    A0 = H[idx_hepsi[:, 0]]
    A0 = A0 / np.maximum(np.linalg.norm(A0, axis=-1, keepdims=True), 1e-300)
    A1 = np.einsum('cij,cj->ci', U_hepsi, A0)
    cek = int(a.tdd_cekirdek)
    kapali = [esit_mi(kanonik_adres(A0[c], cekirdek=cek),
                      kanonik_adres(A1[c], cekirdek=cek))
              for c in range(idx_hepsi.shape[0])]
    tdd_kimlik = bool(all(kapali))
    _eps = float(np.finfo(H.dtype).eps)
    _cz = float(np.arccos(np.clip(1.0 - np.sqrt(_eps), -1.0, 1.0)))
    yol_haddi = float(a.kenar) if float(a.kenar) > 0.0 else \
        _cz * float(int(a.cevrim_boyu))
    kenar_haddi = float(a.kenar) if float(a.kenar) > 0.0 else _cz
    for c_no in range(int(a.cevrim_sayisi)):
        idx = [int(i) for i in idx_hepsi[c_no]]
        koseler = [haller[i] for i in idx]
        om = float(om_hepsi[c_no])
        yol = float(yol_hepsi[c_no])
        omegalar.append(om)
        c = float(max(0.0, -om) ** 2)
        ceza += c
        ort = []
        for i in range(len(koseler)):
            for j in range(i + 1, len(koseler)):
                u = koseler[i] / (np.linalg.norm(koseler[i]) or 1.0)
                v = koseler[j] / (np.linalg.norm(koseler[j]) or 1.0)
                ort.append(float(abs(np.vdot(u, v))))
        engelli = bool(ort) and max(ort) < 0.5
        if om < -1.0 + kenar_haddi:
            say["tenakuz"] += 1
        elif yol <= yol_haddi:
            say["kısır"] += 1
        elif engelli:
            say["engel"] += 1
        else:
            say["meşru"] += 1
        kayit.append((om, yol, c))
    n_c = max(1, int(a.cevrim_sayisi))
    from .tenakuz import TenakuzAyari, dislama_dizeyi, log_bariyer
    ta = TenakuzAyari(lam=float(a.lam_tenakuz), eps=float(a.tenakuz_eps),
                      tau=float(a.dislama_tau))
    if baglamlar is not None and hedefler is not None and int(n_v) > 0:
        S = dislama_dizeyi(baglamlar, int(n_v), ta)
        h = np.asarray(list(hedefler), np.int64) % int(n_v)
        cift = np.empty(idx_hepsi.shape[0], float)
        for c_no in range(idx_hepsi.shape[0]):
            t = h[idx_hepsi[c_no]]
            alt = [float(S[int(t[i]), int(t[j])])
                   for i in range(t.size) for j in range(i + 1, t.size)]
            cift[c_no] = float(np.mean(alt)) if alt else 1.0
    else:
        cift = np.ones(idx_hepsi.shape[0], float)
    bariyer = log_bariyer(U_hepsi, cift, ta)
    return {"ceza": ceza / n_c, "çevrim": kayit, "ω": omegalar,
            "indis": [[int(i) for i in r] for r in idx_hepsi],
            "bariyer": bariyer, "tdd_kimlik": tdd_kimlik, **say}


def _monogami(M3: np.ndarray, sektorler: Sequence[Tuple[int, int]]
              ) -> Tuple[float, float, float]:
    M = np.asarray(M3, complex)
    assert M.ndim == 3 and M.size > 0, "lifli yığın (S, n_v, n_h) olmalı"
    S, n_v, n_h = M.shape
    d = n_v * n_h
    top = np.sum(np.abs(M) ** 2, axis=(1, 2))
    assert float(np.min(top)) > 0.0, "durum BOŞ -- monogami ölçülemez"
    M = M / np.sqrt(top)[:, None, None]

    Mc = M.conj()

    def _saflik(X: np.ndarray, Xc: np.ndarray) -> np.ndarray:
        g = np.matmul(X, Xc.swapaxes(1, 2))
        return np.real(np.einsum('svw,swv->s', g, g))

    C2_hepsi = np.maximum(0.0, 2.0 * (1.0 - _saflik(M, Mc)))

    F = M.reshape(S, d)
    Fc = Mc.reshape(S, d)
    g2 = np.abs(F) ** 2
    A = np.zeros((S, d), complex)
    Ac = np.zeros((S, d), complex)
    Av = A.reshape(S, n_v, n_h)
    Avc = Ac.reshape(S, n_v, n_h)
    toplam = np.zeros(S, float)
    for (i, j) in sektorler:
        assert 0 <= i < j <= d, (
            "sektör düz indisin dışında: (%d,%d) ∉ [0,%d]" % (i, j, d))
        w = np.sum(g2[:, i:j], axis=1)
        var = w > 1e-15
        if not np.any(var):
            continue
        A[:, i:j] = F[:, i:j]
        Ac[:, i:j] = Fc[:, i:j]
        v0, v1 = i // n_h, (j - 1) // n_h
        saf = (_saflik(Av[:, v0:v1 + 1], Avc[:, v0:v1 + 1])
               / np.maximum(w, 1e-300) ** 2)
        A[:, i:j] = 0.0
        Ac[:, i:j] = 0.0
        toplam += np.where(var, w * np.maximum(0.0, 2.0 * (1.0 - saf)), 0.0)
    return (float(np.sum(np.maximum(0.0, toplam - C2_hepsi))),
            float(np.sum(toplam)), float(np.sum(C2_hepsi)))


def engellenme(H: np.ndarray, ayar: Optional[MizanAyari] = None
               ) -> Dict[str, Any]:
    a = ayar or MizanAyari()
    H = np.asarray(H, complex)
    m = H.shape[0]
    if m < 3:
        return {"ceza": 0.0, "bağ": 0, "toplam": 0, "spin": None,
                "doyum": 0.0}
    Hn = H / np.maximum(np.linalg.norm(H, axis=-1, keepdims=True), 1e-300)
    J = np.real(Hn @ Hn.conj().T)
    np.fill_diagonal(J, 0.0)
    olcek = float(np.sum(np.abs(J)))
    if olcek <= 0.0:
        return {"ceza": 0.0, "bağ": 0, "toplam": 0, "spin": None,
                "doyum": 0.0}
    h = halka(J, AynaAyari(teta=float(a.ayna_teta), r=float(a.ayna_r),
                           tur=int(a.ayna_tur), tohum=int(a.tohum)),
              ne="döküm")
    s = np.asarray(h["spin"], int)
    tatmin = J * np.outer(s, s)
    kazanc = float(np.sum(np.maximum(tatmin, 0.0)))
    ceza = float(np.clip(1.0 - kazanc / olcek, 0.0, 1.0))
    bag = int(np.count_nonzero(tatmin < 0) // 2)
    top = int(np.count_nonzero(J) // 2)
    return {"ceza": ceza, "bağ": bag, "toplam": top, "spin": s,
            "doyum": float(h.get("bedel", 0.0)),
            "öbek": int(h.get("öbek", 0)),
            "şahit_nispeti": float(h.get("şahit_nispeti", 0.0)),
            "kilitlendi": bool(h.get("kilitlendi", False))}


def _laplasyen(baglamlar: Sequence[Sequence[int]], n: int) -> np.ndarray:
    W = np.zeros((n, n), float)
    for bag in baglamlar:
        t = sorted({int(x) % n for x in bag})
        for a in range(len(t)):
            for b in range(a + 1, len(t)):
                W[t[a], t[b]] += 1.0
                W[t[b], t[a]] += 1.0
    m = float(W.max())
    if m > 0:
        W /= m
    D = np.diag(W.sum(axis=1))
    return D - W


def _ileri(nefs, veri, sozluk: int, ayar=None) -> Dict[str, Any]:
    from .qegitim import belirtecleri_kodla, ornek_bol
    haller: List[np.ndarray] = []
    lifliler: List[np.ndarray] = []
    hedefler: List[int] = []
    cinsler: List[str] = []
    makamlar: List[int] = []
    baglamlar: List[Sequence[int]] = []
    sektor: List[Tuple[int, int]] = []
    veri = list(veri)
    B = max(1, int(getattr(nefs.ayar, "yigin", 1)))
    kubit = int(nefs.ayar.veri_lifi)
    okumalar: Dict[int, Dict[str, float]] = {}
    dS: Dict[int, float] = {}
    alan_okumasi: Dict[str, float] = {}
    kesme_kesri = 1.0
    for bas in range(0, len(veri), B):
        dilim = veri[bas:bas + B]
        _bag = [ornek_bol(o) for o in dilim]
        _boy = {len(b) for b, _h, _c, _m in _bag}
        assert len(_boy) == 1, (
            "bağlam boyu tek olmalı, %s bulundu -- cins başına boy: %s. "
            "İki cins iki boy demek, ferman 1-R'nin yasakladığı iki "
            "motordur."
            % (sorted(_boy),
               sorted({(c, len(b)) for b, _h, c, _m in _bag})))
        E = np.stack([belirtecleri_kodla(list(bag), kubit, kubit)
                      for bag, _h, _c, _m in _bag])
        if E.shape[0] < B:
            E = np.concatenate(
                [E, np.repeat(E[-1:], B - E.shape[0], axis=0)], axis=0)
        q = nefs.idrak_et(E)
        assert q.y.B == B, (
            "yazmaç yığını %d, istenen %d -- ayar ile veri uyuşmuyor"
            % (q.y.B, B))
        n_v = int(q.y.ayar.lif[0])
        M_hepsi = np.asarray(q.y.psi, complex).reshape(B, n_v, -1)
        assert M_hepsi.size > 0, "ileri geçiş BOŞ durum verdi"
        _hk = str(getattr(ayar, "hal_kaynagi", "tutarlı"))
        if _hk == "tutarlı":
            _H = M_hepsi.sum(axis=-1)
            _H = _H / np.maximum(
                np.linalg.norm(_H, axis=-1, keepdims=True), 1e-300)
        elif _hk == "özvektör":
            rho = np.einsum('bvh,bwh->bvw', M_hepsi, M_hepsi.conj())
            rho = 0.5 * (rho + np.conj(np.swapaxes(rho, -1, -2)))
            _w, V = np.linalg.eigh(rho)
            _H = V[:, :, -1]
        else:
            raise ValueError("hal_kaynagi bilinmiyor: %r" % (_hk,))
        for t, (bag, hedef, cins, makam) in enumerate(_bag):
            lifliler.append(M_hepsi[t])
            haller.append(np.asarray(_H[t], complex))
            hb = int(hedef)
            assert 0 <= hb < int(kubit), (
                "hedef basamak taşıyıcının dışında: %d ∉ [0,%d) -- veri "
                "katmanı tip vektörüne çevirmemiş olabilir (ferman 1-N)"
                % (hb, kubit))
            hedefler.append(hb)
            cinsler.append(str(cins))
            makamlar.append(int(makam))
            baglamlar.append(list(bag))
        if not sektor:
            sektor = [q.y.sektor(ad) for ad, _ in q.ayar.kulli_alanlar]
        for no, d in (getattr(q, "okumalar", None) or {}).items():
            eski = okumalar.get(int(no))
            okumalar[int(no)] = dict(d) if eski is None else {
                k: min(v, eski.get(k, v)) for k, v in d.items()}
        for no, v in (getattr(q, "dS", None) or {}).items():
            dS[int(no)] = dS.get(int(no), 0.0) + float(v)
        from .kulli_kayip import UZAYLAR, zayif_halka
        _alan = q.olcumler()
        for ad, _kac in q.ayar.kulli_alanlar:
            if ad in _alan and ad in UZAYLAR:
                v = float(zayif_halka(_alan[ad]))
                alan_okumasi[ad] = min(alan_okumasi.get(ad, v), v)
        kesme_kesri = min(
            kesme_kesri,
            float(q.y.sadakat_kapi_basina(max(int(q.iz.kapi), 1))))
    assert haller, "BOŞ veriyle mizan kurulamaz"
    assert len(haller) == len(veri), (
        "ileri geçiş %d örnek aldı, %d netice verdi -- örnek kayboldu"
        % (len(veri), len(haller)))
    return {"hal": haller, "lifli": lifliler, "hedef": hedefler,
            "cins": cinsler, "makam": makamlar, "bağlam": baglamlar, "sektör": sektor,
            "okumalar": okumalar, "ΔS": dS, "alan": alan_okumasi,
            "kesme": float(kesme_kesri)}


def kulli_mizan(nefs, veri, p=None, sozluk: int = 16,
                ayar: Optional[MizanAyari] = None,
                hafiza: Optional[Hafiza] = None, adim: int = 0,
                kademe_gorevleri=None, ne: str = "toplam"
                ) -> Dict[str, Any]:
    a = ayar or MizanAyari()
    if p is not None:
        nefs.yukle(np.asarray(p, float))
    veri = list(veri)
    assert veri, "BOŞ veriyle mizan kurulamaz"
    ileri = _ileri(nefs, veri, sozluk, ayar)

    n_v = ileri["lifli"][0].shape[0]
    rho_model = np.zeros((n_v, n_v), complex)
    for M in ileri["lifli"]:
        w = float(np.sum(np.abs(M) ** 2)) or 1.0
        rho_model += (M @ M.conj().T) / w
    rho_model /= len(ileri["lifli"])
    say = np.zeros(n_v, float)
    for t in ileri["hedef"]:
        say[int(t) % n_v] += 1.0
    say /= say.sum()
    rho_veri = np.diag(say).astype(complex)
    F = uhlmann(rho_veri, rho_model)
    L_rez = float(1.0 - F)

    cv = _cevrimleri_tara(ileri["hal"], a, ileri["bağlam"],
                          ileri["hedef"], n_v)
    L_cev = float(cv["ceza"])
    L_ten = float(cv["bariyer"]["ceza"])

    mono, mono_sol, mono_sag = _monogami(
        np.stack(ileri["lifli"]), ileri["sektör"])
    n_o = len(ileri["lifli"])
    L_mon = float(mono / n_o)

    eng = engellenme(np.stack([np.asarray(h, complex).reshape(-1)
                               for h in ileri["hal"]]), a)
    L_eng = float(eng["ceza"])

    D = _laplasyen(ileri["bağlam"], n_v)
    psi = np.zeros(n_v, complex)
    for h in ileri["hal"]:
        psi += h
    nrm = float(np.linalg.norm(psi))
    assert nrm > 0.0, "yığın hâli sıfıra çöktü -- Hodge ölçülemez"
    psi /= nrm
    L_ham = float(np.real(np.vdot(psi, D @ psi)))
    if int(a.qsvt) > 0 and psi.size >= 4:
        from .qudit import QuditAyari, suz
        qa = QuditAyari(d=int(psi.size), qsvt=int(a.qsvt),
                        derece=int(a.qudit_derece), yon=int(a.qudit_yon))
        harmonik = np.asarray(suz(D, psi, qa), complex).reshape(-1)
        artik = psi - harmonik
        nrm_a = float(np.linalg.norm(artik))
        L_hod = (float(np.real(np.vdot(artik, D @ artik))) / (nrm_a ** 2)
                 if nrm_a > 1e-12 else 0.0)
    else:
        L_hod = L_ham
    assert L_hod >= -1e-9, (
        "Hodge enerjisi NEGATİF çıktı (%.6f) -- Laplasyen PSD değil, "
        "ceza ödüle dönmüş demektir" % L_hod)
    L_hod = max(0.0, L_hod)

    from .tabakali_mizan import kategori_kaybi, nokta_kaybi, tasma_kaybi
    kat = kategori_kaybi(ileri["hal"], azami=int(a.cevrim_sayisi) * 4,
                         tohum=int(a.tohum))
    nok = nokta_kaybi(ileri["lifli"], ileri["hedef"], n_v,
                      cinsler=ileri.get("cins"))
    tas = tasma_kaybi(ileri["lifli"], ileri.get("makam") or [], n_v,
                      int(sozluk), int(a.basamak))
    L_tas = float(tas["kayıp"])
    L_kat = float(kat["kayıp"])
    L_nok = float(nok["kayıp"])

    from .kulli_kayip import (UZAYLAR, Olcum, kademeleri_kos,
                              meleke_olcumleri)
    _okumalar = ileri.get("okumalar") or {}
    _bilesen: List[Tuple[str, float, float]] = []
    _mel_lam = float(a.lam_meleke)
    if int(a.meleke_olcumu) and _okumalar:
        _grup: Dict[str, List[Olcum]] = {}
        for o in meleke_olcumleri(_okumalar):
            _grup.setdefault(str(o.kaynak).split(".")[0], []).append(o)
        for ad, v in sorted((ileri.get("alan") or {}).items()):
            if ad in UZAYLAR:
                _grup["alan.%s" % ad] = [
                    Olcum("alan.%s" % ad, float(v), UZAYLAR[ad])]
        if kademe_gorevleri:
            for g in kademe_gorevleri:
                for o in kademeleri_kos(g, p=nefs.p)["ölçümler"]:
                    _grup.setdefault(str(o.kaynak), []).append(o)
        _pay = _mel_lam / max(1, len(_grup))
        for ad, olculer in sorted(_grup.items()):
            hata = sum(float(o.eksik()) for o in olculer) / len(olculer)
            _bilesen.append((ad, float(hata), _pay))
    L_mel = float(sum(h * l for _ad, h, l in _bilesen))
    _en_kotu = (max(_bilesen, key=lambda x: x[1])[:2] if _bilesen
                else ("ÖLÇÜM KAPALI", 0.0))

    from .zirh import ZirhAyari, taahhude_yuzlestir, zirh_kaybi
    from .melekeler import qsicil
    _dS = ileri.get("ΔS") or {}
    if int(a.meleke_olcumu) and _dS:
        _sic = qsicil()
        _ih = [float(taahhude_yuzlestir(sinif=_sic[int(no)].SINIF,
                                        dS=float(v)))
               for no, v in sorted(_dS.items()) if int(no) in _sic]
        L_nizam = float(max(_ih)) if _ih else 0.0
    else:
        L_nizam = 0.0
    from .mukayese import (spektrum as _spektrum, vecih_kur as _vecih_kur,
                           hipotez_halkasi as _hipotez_halkasi)
    _vec = _vecih_kur([(ad, sk) for (ad, _n), sk
                       in zip(nefs.ayar.kulli_alanlar,
                              ileri["sektör"])]) if ileri.get("sektör") \
        else None
    _hal = list(ileri["hal"])[:max(3, int(a.cevrim_boyu) + 1)]
    spek = (_spektrum(_hal, _vec, azami_n=int(a.cevrim_boyu),
                      tohum=int(a.tohum)) if len(_hal) >= 2 else None)
    dk = _hipotez_halkasi(ileri["hal"], ileri.get("cins"),
                          (_vec[0] if _vec else None))
    _bilesen.append(("kaide_halkası", float(dk["Δ_K"]), float(a.lam_kaide)))
    _bilesen.append(("taşma", L_tas, float(a.lam_tasma)))
    from .zirh import zirhla
    _H_zirh = np.real(rho_model).astype(float)
    _z_ham, _z = zirhla(_H_zirh, ZirhAyari())
    _zirh = zirh_kaybi(sheaf=float(_z["sheaf_ceza"]),
                       betti=float(_z["betti_ceza"]),
                       koho=float(_z["koho_ceza"]),
                       homotopi=float(_z["homotopi_ceza"]),
                       nizam=L_nizam, ayar=ZirhAyari())
    _z_bes = (("zırh.sheaf", float(_z["sheaf_ceza"])),
              ("zırh.betti", float(_z["betti_ceza"])),
              ("zırh.koho", float(_z["koho_ceza"])),
              ("zırh.homotopi", float(_z["homotopi_ceza"])),
              ("zırh.nizam", float(L_nizam)))
    _zpay = float(a.lam_zirh) / len(_z_bes)
    for _ad, _v in _z_bes:
        _bilesen.append((_ad, _v, _zpay))
    L_zirh = float(sum(_v * _zpay for _ad, _v in _z_bes))
    L_zirh_softmax = float(_zirh["kayıp"])

    from .suphe import SupheAyari, suphe_manifoldu
    sup = suphe_manifoldu(
        ileri["hal"], cv["ω"],
        ayar=SupheAyari(acik=int(a.suphe_acik), sonum=float(a.suphe_sonumu),
                        kip_kenari=float(a.kenar) * 5.0,
                        parite_lifi=int(a.parite_lifi)))

    from .usul import UsulAyari, usul_kos
    usl = usul_kos(ileri["hal"], cv["indis"], cv["ω"],
                   UsulAyari(acik=int(a.usul_acik), had=float(a.usul_haddi),
                             sefer=int(a.usul_seferi)))

    from .rust import RustAyari, rust_kilidi, topolojik_yirtik
    ra = RustAyari(t0=float(a.rust_t0), tau=float(a.rust_tau),
                   kapanis=float(a.rust_kapanis),
                   muayene=int(a.rust_muayene),
                   toplam_adim=int(a.toplam_adim))
    yirtik = topolojik_yirtik(ileri["bağlam"], n_v)
    kilit = rust_kilidi(int(adim), float(yirtik["dF_dec"]),
                        int(yirtik["h1"]), ra)
    alfa = float(kilit["α"])
    fitrata = (1.0 - alfa) * L_cev
    hafizaya = alfa * L_cev
    if hafiza is not None and cv["çevrim"]:
        for (om, ds, _c), hidx in zip(
                cv["çevrim"], range(len(cv["çevrim"]))):
            hukum = (CERH if om < -1.0 + a.kenar else
                     TEVAKKUF if om > 1.0 - a.kenar else TASDIK)
            j = hidx % len(ileri["hal"])
            mu = sup.get("μ")
            if (hukum == TASDIK and mu is not None and len(mu) > j
                    and float(mu[j]) < 0.35):
                hukum = TEVAKKUF
            if hukum == TEVAKKUF:
                hafiza.taban_degistir(ileri["hal"][j],
                                      yaprak="ω%+.2f" % float(om),
                                      omega=float(om))
            hafiza.yaz(ileri["hal"][j], omega=om, hukum=hukum)
    if hafiza is not None:
        for _j, _netice in usl.get("netice", ()):
            hafiza.yaz(_netice, omega=1.0, hukum=TASDIK)

    L_gedik = float(a.lam_cevrim) * float(usl["borç"])
    _bilesen = [("nokta", L_nok, float(a.lam_nokta)),
                ("uzay", L_rez, 1.0),
                ("kategori", L_kat, float(a.lam_kategori)),
                ("tip", L_hod, float(a.lam_tip)),
                ("çevrim", fitrata, float(a.lam_cevrim)),
                ("tenakuz", L_ten, float(a.lam_tenakuz)),
                ("gedik", float(usl["borç"]), float(a.lam_cevrim)),
                ("monogami", L_mon, float(a.lam_monogami)),
                ("engel", L_eng, float(a.lam_engel))] + _bilesen
    artik = np.array([float(h) * float(l) for _ad, h, l in _bilesen],
                     float)
    ham_artik = np.array([float(h) for _ad, h, _l in _bilesen], float)
    artik_adlari = tuple(str(ad) for ad, _h, _l in _bilesen)
    assert np.all(np.isfinite(artik)), (
        "hata vektöründe NaN/Inf var: %s"
        % [artik_adlari[i] for i in np.flatnonzero(~np.isfinite(artik))])
    kayip = float(artik.sum())
    assert np.isfinite(kayip), "mizan sonlu değil"

    kayip_ham = float(ham_artik.sum())
    if ne == "toplam":
        return {"kayıp": float(kayip), "kayıp_ham": kayip_ham,
                "artık": artik, "ham_artık": ham_artik,
                "artık_adı": artik_adlari}
    if ne != "döküm":
        raise ValueError("mizan kipi bilinmiyor: %r" % (ne,))
    return {"kayıp": float(kayip), "kayıp_ham": kayip_ham,
            "ham_artık": ham_artik, "rezonans": L_rez, "sadakat": F,
            "taşma": L_tas, "taşma_dökümü": tas,
            "nokta": L_nok, "nokta_isabet": float(nok["isabet"]),
            "nokta_cins": nok.get("cins", {}),
            "kategori": L_kat, "kategori_ihlâl": int(kat["ihlâl"]),
            "kategori_deneme": int(kat["deneme"]),
            "artık": artik, "artık_adı": artik_adlari,
            "bileşen": int(artik.size), "spektrum": spek,
            "meleke": L_mel, "meleke_en_zayıf": _en_kotu[0],
            "meleke_en_kötü_hata": float(_en_kotu[1]),
            "meleke_sayısı": sum(1 for ad in artik_adlari
                                 if ad.startswith("𝒪")),
            "kesme_yapısal": float(ileri.get("kesme", 0.0)),
            "zırh": L_zirh, "zırh_softmax": L_zirh_softmax,
            "zırh_sheaf": float(_z["sheaf_ceza"]),
            "zırh_betti": float(_z["betti_ceza"]),
            "zırh_koho": float(_z["koho_ceza"]),
            "zırh_homotopi": float(_z["homotopi_ceza"]),
            "zırh_nizam": float(L_nizam),
            "tenakuz_bariyer": L_ten,
            "tenakuz_azamî": float(cv["bariyer"]["azamî"]),
            "tenakuz_tavan": float(cv["bariyer"]["tavan"]),
            "dışlama_ortalama": float(cv["bariyer"]["dışlama_ortalama"]),
            "rüşt_takvim": float(kilit["takvim"]),
            "rüşt_muayene": float(kilit["muayene"]),
            "dF_dec": float(yirtik["dF_dec"]), "h1": int(yirtik["h1"]),
            "sefer": int(usl["sefer"]), "gedik": int(usl["gedik"]),
            "sefer_kapanan": int(usl["kapanan"]),
            "gedik_borcu": float(usl["borç"]), "L_gedik": float(L_gedik),
            "tevakkuf": int(sup["tevakkuf"]),
            "çevrim": L_cev, "çevrim_fıtrata": float(fitrata),
            "çevrim_hafızaya": float(hafizaya),
            "monogami": L_mon, "monogami_sol": float(mono_sol / n_o),
            "monogami_sağ": float(mono_sag / n_o),
            "hodge": L_hod, "hodge_ham": L_ham, "engel": L_eng,
            "engel_bağ": int(eng["bağ"]), "engel_toplam": int(eng["toplam"]),
            "engel_öbek": int(eng.get("öbek", 0)),
            "engel_şahidi": float(eng.get("şahit_nispeti", 0.0)),
            "α_rüşt": float(alfa),
            "meşru": int(cv["meşru"]), "kısır": int(cv["kısır"]),
            "tenakuz": int(cv["tenakuz"]), "engel": int(cv["engel"]),
            "ihlâl": int(mono_sol > mono_sag),
            "ω_ortalama": float(np.mean(cv["ω"])) if cv["ω"] else 0.0,
            "örnek": len(veri)}


def mizan_cetveli(nefs, veri, p=None, sozluk: int = 16,
                  ayar: Optional[MizanAyari] = None) -> Dict[str, int]:
    a = ayar or MizanAyari()
    if p is not None:
        nefs.yukle(np.asarray(p, float))
    veri = list(veri)
    assert veri, "BOŞ veri tasnif edilemez"
    ileri = _ileri(nefs, veri, sozluk, ayar)
    n_v = ileri["lifli"][0].shape[0]
    D = _laplasyen(ileri["bağlam"], n_v)

    rez: List[float] = []
    hod: List[float] = []
    cev: List[float] = []
    m = len(ileri["hal"])
    for i, (M, h, t) in enumerate(zip(ileri["lifli"], ileri["hal"],
                                      ileri["hedef"])):
        w = float(np.sum(np.abs(M) ** 2)) or 1.0
        rho = (M @ M.conj().T) / w
        hedef = np.zeros((n_v, n_v), complex)
        hedef[int(t) % n_v, int(t) % n_v] = 1.0
        rez.append(1.0 - uhlmann(hedef, rho))
        hh = h / (np.linalg.norm(h) or 1.0)
        hod.append(float(np.real(np.vdot(hh, D @ hh))))
        if m >= int(a.cevrim_boyu):
            idx = [(i + k) % m for k in range(int(a.cevrim_boyu))]
            _, om, _yol = holonomi([ileri["hal"][j] for j in idx])
            cev.append(float(max(0.0, -om)))
        else:
            cev.append(0.0)

    r_esik = float(np.median(rez))
    h_esik = float(np.median(hod))
    c_esik = float(a.kenar)
    out = {"hakikat": 0, "tenakuz": 0, "şüpheli": 0, "gürültü": 0}
    for r_, c_, h_ in zip(rez, cev, hod):
        if c_ > c_esik:
            out["tenakuz"] += 1
        elif r_ > r_esik and h_ <= h_esik:
            out["gürültü"] += 1
        elif r_ <= r_esik and h_ > h_esik:
            out["şüpheli"] += 1
        else:
            out["hakikat"] += 1
    assert sum(out.values()) == len(veri), "tasnif toplamı tutmuyor"
    return out


def rapor(profil: str = "kısa") -> str:
    import time

    from main.egitim import PROFILLER
    from nefs.melekeler import QNefs
    from nefs.musahede import gorevleri_getir
    from nefs.qegitim import ornekler

    ayar = PROFILLER.get(profil, PROFILLER["kısa"])
    a = MizanAyari(tohum=ayar.tohum, cevrim_sayisi=12)
    g = list(gorevleri_getir("training"))[:12]
    veri = ornekler(g, azami=int(ayar.ornek_sayisi), pencere=ayar.pencere,
                    sozluk=ayar.sozluk, tohum=ayar.tohum,
                    taban=int(ayar.veri_lifi),
                    basamak=int(getattr(ayar, "belirtec_basamak", 0)))
    nefs = QNefs(ayar.tohum, ayar.qayar())
    nefs.idrak_et(np.zeros((2, ayar.veri_lifi)))
    haf = Hafiza(kapasite=64)

    t0 = time.perf_counter()
    d = kulli_mizan(nefs, veri, nefs.vektor(), ayar.sozluk, ayar=a,
                    hafiza=haf, adim=0, ne="döküm")
    sure = time.perf_counter() - t0
    cet = mizan_cetveli(nefs, veri, nefs.vektor(), ayar.sozluk, ayar=a)

    n = 8
    r = np.random.default_rng(0)
    e = np.eye(n, dtype=complex)
    _, om_dik, yol_dik = holonomi([e[0], e[1], e[2]])
    _, om_kisir, yol_kisir = holonomi([e[0], e[0], e[0]])
    _ac = [0.0, 0.25 * math.pi, 0.5 * math.pi]
    _egri = []
    for _th in _ac:
        _c, _s = math.cos(_th), math.sin(_th)
        _b = _c * e[0] + _s * e[1]
        _d = math.cos(2 * _th) * e[0] + math.sin(2 * _th) * e[1]
        _egri.append(float(holonomi([e[0], _b, _d])[1]))
    U_par, om_par, yol_par = holonomi([e[0], e[1], -e[0]])
    from .tenakuz import TenakuzAyari, log_bariyer
    from .tabakali_mizan import kategori_kaybi
    from .rust import RustAyari, rust_kilidi
    _ta = TenakuzAyari(eps=float(a.tenakuz_eps), tau=float(a.dislama_tau))
    _bar_par = log_bariyer(U_par[None, :, :], np.ones(1), _ta)
    _bar_bir = log_bariyer(np.eye(U_par.shape[0], dtype=complex)[None],
                           np.ones(1), _ta)
    _rk = np.random.default_rng(7)
    _dik = np.linalg.qr(_rk.normal(size=(8, 8))
                        + 1j * _rk.normal(size=(8, 8)))[0]
    _kat_kirmizi = kategori_kaybi([_dik[:, 0], _dik[:, 1], _dik[:, 2]],
                                  azami=1, tohum=0)
    _kat_yesil = kategori_kaybi([_dik[:, 0], _dik[:, 0], _dik[:, 0]],
                                azami=1, tohum=0)
    _ra = RustAyari(t0=float(a.rust_t0), tau=float(a.rust_tau),
                    kapanis=float(a.rust_kapanis), muayene=1,
                    toplam_adim=int(a.toplam_adim))
    _rust_saglam = rust_kilidi(a.toplam_adim, 0.0, 0, _ra)
    _rust_yirtik = rust_kilidi(a.toplam_adim, 0.0, 2, _ra)
    from .usul import UsulAyari, usul_beyani, usul_kos, usul_sifirla
    _u_once = usul_beyani()["sefer"]
    _ua = UsulAyari(acik=1, had=0.0, sefer=2)
    _gedikli = usul_kos([_dik[:, i] for i in range(4)],
                        [[0, 1, 2], [1, 2, 3]], [-0.9, +0.9], _ua)
    _kapali = usul_kos([_dik[:, i] for i in range(4)],
                       [[0, 1, 2]], [-0.9], UsulAyari(acik=0))
    from .sadakat import SadakatAyari, sadakat_uygula
    _yirtik_hal = np.ones(64, complex) / 8.0
    _sa = SadakatAyari(parite_lifi=1, lif_yapisi=(8, 8))
    _sad_acik = sadakat_uygula(_yirtik_hal.copy(),
                               SadakatAyari(acik=1, parite_lifi=1,
                                            lif_yapisi=(8, 8)))
    _sad_kapali = sadakat_uygula(_yirtik_hal.copy(),
                                 SadakatAyari(acik=0, parite_lifi=1,
                                              lif_yapisi=(8, 8)))

    s = ["=== MÎZÂN-I KÜLLÎ (nefs/kulli_mizan.py) ===", "",
         "  TABAKALI MİZAN (zabıt): L = L_nokta + α·L_uzay + β·L_kategori + γ·L_tip",
         "  L_uzay ≡ ℒ_Rezonans (Uhlmann), L_tip ≡ ℒ_Hodge -- terkip, tabela değil.",
         "  Yanına mizanın kendi kefeleri: λ₁ℒ_Çevrim + λ_t ℒ_Tenakuz + λ₂ℒ_Monogami + λ₄ℒ_Engel",
         "", "  --- KEFELER (%d örnek, %.2f sn) ---" % (d["örnek"], sure),
         "    ℒ_Rezonans (Uhlmann)  : %.6f   (sadakat F = %.6f)"
         % (d["rezonans"], d["sadakat"]),
         "    ℒ_Çevrim   (Wilson)   : %.6f   ω̄ = %+.4f"
         % (d["çevrim"], d["ω_ortalama"]),
         "        meşru %d | kısır %d | tenakuz %d | engel %d"
         % (d["meşru"], d["kısır"], d["tenakuz"], d["engel"]),
         "    ℒ_Monogami (CKW ⊕)    : %.6f   (Σ_A %.4f vs hepsi %.4f)"
         % (d["monogami"], d["monogami_sol"], d["monogami_sağ"]),
         "    ℒ_Hodge    (Δ|Ψ⟩=0)   : %.6f" % d["hodge"],
         "    ℒ_Tenakuz  (log bar.) : %.6f   azamî %.4f / tavan %.4f"
         % (d["tenakuz_bariyer"], d["tenakuz_azamî"], d["tenakuz_tavan"]),
         "        S_dışlama ortalaması %.4f" % d["dışlama_ortalama"],
         "    ℒ_Kategori (funktör)  : %.6f   ihlâl %d/%d"
         % (d["kategori"], d["kategori_ihlâl"], d["kategori_deneme"]),
         "    ℒ_Nokta    (kısmî Born): %.6f   tepe isabeti %.4f"
         % (d["nokta"], d["nokta_isabet"]),
         "    ─────────────────────────────────────",
         "    ℒ_Küllî               : %.6f" % d["kayıp"],
         "",
         "  --- RÜŞT KİLİDİ: TAKVİM **VE** MUAYENE (nefs/rust.py) ---",
         "    ölçülen ‖dF‖² = %.6f   ‖H¹‖ = %d  (kapanmamış delik)"
         % (d["dF_dec"], d["h1"]),
         "    takvim σ(·) = %.4f   muayene exp(·) = %.4f   α = %.4f"
         % (d["rüşt_takvim"], d["rüşt_muayene"], d["α_rüşt"]),
         "    → tenakuzun %%%.1f'i FITRATA, %%%.1f'i HAFIZAYA"
         % (100 * (1 - d["α_rüşt"]), 100 * d["α_rüşt"]),
         "    kör takvim olsaydı α = %.4f olurdu (fark: muayene kapısı)"
         % d["rüşt_takvim"],
         "",
         "  --- ÖLÇÜ KIRMIZI YANABİLİYOR MU? (elle kurulan üç hal) ---",
         "    üç dik hâl (engellenme): ω = %+.6f  yol = %.4f   %s"
         % (om_dik, yol_dik,
            "yol katedildi" if yol_dik > 1e-9 else "⚠ YOL SIFIR"),
         "    aynı hâl üç kere       : ω = %+.6f  yol = %.4f   %s"
         % (om_kisir, yol_kisir,
            "KISIR (doğru)" if yol_kisir < 1e-9 else "⚠ KISIR GÖRÜLMEDİ"),
         "    ω LİF BOYUNDAN BAĞIMSIZ MI (evvelce ω ≥ 1−4/n idi):",
         "      çevrim açıldıkça ω: θ=0 → %+.4f | θ=π/4 → %+.4f | "
         "θ=π/2 → %+.4f   %s"
         % (_egri[0], _egri[1], _egri[2],
            "CEVAP VERİYOR" if (_egri[0] > _egri[1] > _egri[2])
            else "⚠ CEVAPSIZ"),
         "      (eski 'parite taklası a→b→−a' sınaması KALDIRILDI: "
         "|−a⟩ ile |a⟩ aynı fizikî hâldir, o bir küme fazıydı; ω = %+.4f)"
         % om_par,
         "    L_Tenakuz bariyeri     : U=I → %.6f | U≈−I → %.6f  "
         "(tavan %.4f)   %s"
         % (_bar_bir["ceza"], _bar_par["ceza"], _bar_par["tavan"],
            "YANDI" if _bar_par["ceza"] > 10 * _bar_bir["ceza"] + 1e-6
            else "⚠ YANMADI"),
         "    L_Kategori             : eş hâl → %.3e | dik üçlü → %.6f   %s"
         % (_kat_yesil["kayıp"], _kat_kirmizi["kayıp"],
            "YANDI" if _kat_kirmizi["kayıp"] > 1e-6
            and _kat_yesil["kayıp"] < 1e-9 else "⚠ YANMADI"),
         "    Rüşt kilidi (t=T)      : yırtıksız α = %.4f | ‖H¹‖=2 iken "
         "α = %.4f   %s"
         % (_rust_saglam["α"], _rust_yirtik["α"],
            "KİLİTLENDİ" if _rust_yirtik["α"] < 0.01 * _rust_saglam["α"]
            else "⚠ KİLİTLENMEDİ"),
         "    Sefer (nefs/usul.py)   : gedikli → %d sefer | kapı kapalı "
         "→ %d sefer   %s"
         % (_gedikli["sefer"], _kapali["sefer"],
            "AÇILDI" if _gedikli["sefer"] > 0 and _kapali["sefer"] == 0
            else "⚠ AÇILMADI"),
         "    Sadakat (nefs/sadakat.py): açık → alarm %d→%d | kapalı → "
         "alarm %d→%d   %s"
         % (_sad_acik["alarm_önce"], _sad_acik["alarm_sonra"],
            _sad_kapali["alarm_önce"], _sad_kapali["alarm_sonra"],
            "SÖNDÜRDÜ" if _sad_acik["alarm_sonra"] == 0
            and _sad_kapali["alarm_sonra"] == 1 else "⚠ SÖNDÜREMEDİ"),
         "",
         "  --- VERİ KENDİNİ DÖRDE AYIRDI MI? (etiketsiz) ---",
         "    hakikat %d | tenakuz %d | şüpheli %d | gürültü %d"
         % (cet["hakikat"], cet["tenakuz"], cet["şüpheli"], cet["gürültü"]),
         "",
         "  --- HAFIZA (ağırlık değil, hadise) ---",
         "    %r" % (haf.beyan(),)]
    return "\n".join(s)


if __name__ == "__main__":
    import sys
    print(rapor(sys.argv[1] if len(sys.argv) > 1 else "kısa"))
