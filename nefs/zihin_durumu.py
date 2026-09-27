from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from kuantum.qyazmac import KULLI_SEKTOR_TABANI, QuditAyar, QuditYazmac

__all__ = ["QAyar", "QIz", "QYazmac", "MAKAM_ADLARI",
           "kulli_sektor_adlari", "sektor_adresi", "donme",
           "donme_turevi", "donme_dilim", "donme_dilim_turevi",
           "tek_parite_donmesi", "tek_parite_donmesi_turevi",
           "faz_z", "degil_x",
           "makam_derecesi", "makam_merdiveni",
           "makam_kubit_manasi", "makam_mertebeleri", "makam_mertebesi"]


ALTIN_ACI: float = math.pi * (3.0 - math.sqrt(5.0))


def kulli_sektor_adlari() -> Tuple[str, ...]:
    return ("makam", "mizan", "tenakuz", "tasdik", "sukut",
            "nakz", "kelam", "kaide", "orak", "gaye", "tertip")


def sektor_adresi(ad: str, j: int,
                  taban: int = KULLI_SEKTOR_TABANI) -> int:
    adlar = kulli_sektor_adlari()
    if ad not in adlar:
        raise ValueError("bilinmeyen sektör: %r" % (ad,))
    return int(adlar.index(ad)) * int(taban) + int(j)


@dataclass
class QAyar:

    veri_lifi: int = 16
    yerel_yuva: int = 1
    kartan_acisi: float = 0.2617993877991494
    harman_kademesi: int = 3
    tohum: int = 0
    obek: int = 150000
    yigin: int = 1
    kulli_alanlar: Tuple[Tuple[str, int], ...] = (
        ("makam", 3), ("mizan", 4), ("tenakuz", 2), ("tasdik", 2),
        ("sukut", 1), ("nakz", 2), ("kelam", 4), ("kaide", 12),
        ("orak", 1), ("gaye", 2), ("tertip", 4),
    )
    parametre_genisligi: int = 1
    meleke_olcumu: int = 1
    kaide_basamak: int = 4
    bolge_ac: bool = True
    bolge_asgari: int = 1
    hukum_lifi: int = 256
    lif_yapisi: Optional[Tuple[int, ...]] = (16, 16, 16)
    motor: str = "sürekli"
    faz_mertebesi: int = 16
    hat: str = "c"
    hat_bandi: int = 0
    sadakat_acik: int = 1
    parite_lifi: int = 2
    tip: object = np.complex128

    @property
    def kulli_yuva(self) -> int:
        return len(self.kulli_alanlar) * int(KULLI_SEKTOR_TABANI)


class QIz:

    def __init__(self) -> None:
        self.kapi = 0
        self.kesme = 0.0
        self.defter: List[Tuple[str, str]] = []

    def not_dus(self, meleke: str, mesaj: str = "") -> None:
        self.defter.append((str(meleke), str(mesaj)))


class QYazmac:

    def __init__(self, n_satir: int, ayar: Optional[QAyar] = None) -> None:
        self.ayar = ayar or QAyar()
        a = self.ayar
        assert int(n_satir) >= 1, (
            "bağlam uzunluğu en az bir belirteç olmalı: %r" % (n_satir,))
        sozluk = int(a.veri_lifi)
        assert sozluk >= 2, (
            "veri lifi en az iki seviyeli olmalı: veri_lifi=%d" % sozluk)
        azami = tuple(int(x) for x in (a.lif_yapisi
                                       or (sozluk, a.hukum_lifi)))
        assert int(azami[0]) == sozluk, (
            "ilk lif veri lifidir, sözlükle bir olmalı: %d ≠ %d"
            % (azami[0], sozluk))
        yer_azami = int(np.prod(azami[1:]))
        assert int(n_satir) <= yer_azami, (
            "bağlam azamî hududu aşıyor: %d basamak, basamak başına hadd "
            "%d yer (ferman 2-O)" % (int(n_satir), yer_azami))
        yuva = int(a.kulli_yuva)
        K = 2
        while K * K < int(n_satir) or K * K < yuva:
            K *= 2
        K = min(K, int(math.isqrt(yer_azami)))
        lif = (sozluk, K, K)
        d = int(np.prod(lif))
        assert K * K >= int(n_satir), (
            "yazmaç bağlamı taşımıyor: basamak başına %d yer < bağlam=%d "
            "-- her basamak kendi seviyesini ister (ferman 2-M)"
            % (K * K, int(n_satir)))
        self.y = QuditYazmac(
            QuditAyar(d=d, lif=lif, yigin=int(a.yigin),
                      kulli_alanlar=a.kulli_alanlar,
                      yerel_yuva=int(a.yerel_yuva), tohum=int(a.tohum),
                      tip=a.tip, motor=str(a.motor),
                      faz_mertebesi=int(a.faz_mertebesi),
                      hat=str(a.hat), hat_bandi=int(a.hat_bandi)),
            veri_lifi=int(a.veri_lifi))
        self.iz = self.y.iz
        self.veri = self.y.veri
        self.yerel = self.y.yerel
        self.kulli = self.y.kulli
        self.tek = self.y.tek
        self.cift = self.y.cift
        self.uzak_cift = self.y.uzak_cift
        self.sektor_faz_vur = self.y.sektor_faz_vur
        self.sektor_donmesi = self.y.sektor_donmesi
        self.sektor_cifti = self.y.sektor_cifti
        self.satir_donmesi_m = self.y.satir_donmesi
        self.satir_donmesi_coklu_m = self.y.satir_donmesi_coklu
        self.satir_cifti_m = self.y.satir_cifti
        self.sektor_oruntusu = self.y.sektor_oruntusu
        self.sektor_kenetleri = self.y.sektor_kenetleri
        self.sektor_faz_bagi = self.y.sektor_faz_bagi
        self._alan: Dict[str, Tuple[int, int]] = {
            ad: (self.y.kulli(ad, 0), int(kac))
            for ad, kac in a.kulli_alanlar}

    @property
    def n_satir(self) -> int:
        return int(self.y.n_satir)

    @property
    def veri_yuvasi(self) -> int:
        return int(self.y.veri_yuvasi)

    def yereller(self) -> List[int]:
        return self.y.yereller()

    def not_dus(self, meleke: str, mesaj: str = "") -> None:
        self.y.not_dus(meleke, mesaj)

    @property
    def n(self) -> int:
        return self.y.n

    @property
    def kubit_sayisi(self) -> int:
        return self.y.n

    def kulli_bas(self) -> int:
        return self.y.kulli(self.ayar.kulli_alanlar[0][0], 0)

    def bolge_var(self, ad: str) -> bool:
        return ad in ("veri", "yerel") or self.y.bolge_var(ad)

    @property
    def veri_kubiti(self) -> int:
        return self.n_satir * self.veri_yuvasi

    @property
    def kulli_yuva(self) -> int:
        return self.ayar.kulli_yuva

    @property
    def meleke_kubiti(self) -> int:
        return self.kulli_yuva

    @property
    def ancilla(self) -> int:
        return 0

    def mpo_esigi(self) -> int:
        return 0

    def bolge_olculeri(self) -> Dict[str, int]:
        return {ad: (j - i) for ad, (i, j) in self.y._sektor.items()}

    def tek_yigin(self, yuvalar, G, baglar=None) -> None:
        self.y.tek_yigin(yuvalar, G, baglar=baglar)

    def kontrollu_tek(self, yuva: int, G_dilim) -> None:
        self.y.kontrollu_tek(yuva, G_dilim)

    def veri_izgara(self, sutun=None, satir=None):
        return self.y.veri_izgara(sutun, satir)

    def cift_yigin(self, sol_yuvalar, G, baglar=None) -> None:
        G = np.asarray(G)
        yuvalar = [int(y) for y in sol_yuvalar]
        m = len(yuvalar)
        if G.ndim == 2:
            G = np.broadcast_to(G, (m,) + G.shape)
        yv = np.asarray(yuvalar, np.int64)
        gec = self.y.gecerli_toplu(yv) & self.y.gecerli_toplu(yv + 1)
        self.y._dusen_kapi += int((~gec).sum())
        cift = self.y.cift
        tekil = (baglar is not None and len(baglar) == m
                 and not isinstance(baglar[0], tuple))
        for idx in np.flatnonzero(gec):
            cift(int(yv[idx]), G[int(idx)],
                 baglar=(baglar[int(idx)] if tekil else baglar))

    def mpo_topla(self, alan: str, acilar=None, duraklar=None, j: int = 0,
                  par=None, olcek: float = 1.0, egim=None, bag=None):
        return self.y.mpo_topla(alan, acilar, duraklar, j, par, olcek,
                                egim, bag)

    def mpo_dagit(self, alan: str, acilar=None, duraklar=None, j: int = 0,
                  par=None, olcek: float = 1.0, egim=None, bag=None):
        return self.y.mpo_dagit(alan, acilar, duraklar, j, par, olcek,
                                egim, bag)

    def kodla(self, E) -> None:
        E = np.asarray(E, float)
        if E.ndim == 2:
            E = E[None]
        sozluk = int(self.ayar.veri_lifi)
        B = self.y.B
        d = int(self.y.d)
        n_sat = int(E.shape[1])
        if E.shape[0] != B:
            E = E[np.arange(B) % E.shape[0]]
        assert sozluk == int(self.y.ayar.lif[0]), (
            "bağlam basamak eksenine yazılır: veri_lifi %d, lif[0] %d -- "
            "ikisi aynı eksen olmalı (ferman 1-M)"
            % (sozluk, int(self.y.ayar.lif[0])))
        Ez = E.reshape(B, n_sat, -1)
        bas = np.argmax(Ez, axis=-1) % sozluk
        dolu = Ez.max(axis=-1) > 0.0
        assert n_sat <= int(self.mahalli.qudit), (
            "bağlam mahallî zırha sığmıyor: %d basamak, zırh %d qudit "
            "(ferman 2-Ĝ: bağlam mahallî yazmacın qudit indisindedir)"
            % (n_sat, int(self.mahalli.qudit)))
        genlik = np.zeros((B, d), float)
        yigin = np.repeat(np.arange(B), n_sat)
        sec = dolu.reshape(-1)
        sut = np.mod(bas.reshape(-1), d)
        np.add.at(genlik, (yigin[sec], sut[sec]), 1.0)
        assert bool(dolu.any()), (
            "bağlamın hiçbir basamağı dolu değil -- yazmaca yazacak şey "
            "yok, norm sıfır çıkardı (ferman 5)")
        pq = getattr(self, "pq", None)
        bas_duz = bas.reshape(-1)
        faz = np.zeros((B, d), float)
        if pq is None:
            faz[yigin[sec], sut[sec]] = (
                (-2.0 * math.pi / float(sozluk))
                * (bas_duz[sec].astype(float) + 1.0))
        self.mahalli.hazirla(n_sat, B)
        self.mahalli.yerlestir(bas, dolu)
        if pq is not None:
            kontrol, bag = pq.temas_kapilari()
            self.mahalli.kapilari_vur(
                kontrol,
                pq.rezonans(self.mahalli.koordinat(), int(kontrol.size)),
                bag)
            if int(np.asarray(kontrol).size):
                teta = np.asarray(pq.faz, float)[
                    np.asarray(kontrol, np.int64)]
                agir = np.asarray(bag, float).reshape(-1)
                pay = float(np.sum(np.abs(agir)))
                assert pay > 0.0, (
                    "TEMAS KAPILARININ AĞIRLIĞI TAMAMEN SÖNDÜ -- "
                    "parametre sürekli kanala giremez (ferman 2-Â, 5)")
                self.mahalli.cartan_ekle(
                    "parametre.temas",
                    float(np.sum(teta * np.abs(agir)) / pay))
            self._temas_kontrol_asli = np.asarray(
                kontrol, np.int64).copy()
        izd = getattr(self, "izdusum", None)
        if izd is not None:
            self.mahalli.modlari_vur(izd[0], izd[1])
        self._tohum = (bas, sec, yigin, sut, B, n_sat, d)
        self.y.psi = genlik.astype(self.y.ayar.tip)
        self.y.normalize()
        n_gomme = 0
        if pq is None:
            self.y.faz(faz)
        else:
            degerler = np.unique(bas_duz[sec])
            tam_carpan = np.empty(degerler.size, complex)
            faz_carpan = np.empty(degerler.size, complex)
            adr_faz = np.empty(degerler.size, np.int64)
            adr_agirlik = np.empty(degerler.size, np.int64)
            for k, v in enumerate(degerler):
                anahtar = "gömme/%d" % int(v)
                teta = float(pq.aci(anahtar, 1, 1.0)[0])
                agirlik = float(pq.buyukluk(anahtar, 1)[0])
                adr_faz[k] = int(pq.aci_adresi(anahtar, 1)[0])
                adr_agirlik[k] = int(pq.adres(anahtar, 1)[0])
                faz_carpan[k] = complex(math.cos(teta), -math.sin(teta))
                tam_carpan[k] = agirlik * faz_carpan[k]
            no = (self.y.iz.kapi_yaz("gömme", degerler, tam_carpan)
                  if self.y.iz.senet_acik else -1)
            self.y.psi[:, degerler] *= tam_carpan[None, :]
            if no >= 0:
                for k, v in enumerate(degerler):
                    self.y.iz.bag_yaz(
                        no, int(adr_faz[k]), 1.0,
                        ("köşegen", np.array([int(v)], np.int64),
                         np.array([-1j * tam_carpan[k]], complex)))
                    self.y.iz.bag_yaz(
                        no, int(adr_agirlik[k]), 1.0,
                        ("köşegen", np.array([int(v)], np.int64),
                         np.array([faz_carpan[k]], complex)))
            n_gomme = int(degerler.size)
            self.y.normalize()
        self.y.iz.not_dus("kodla", "dolu %d / %d seviye  gömme %d/%d hane"
                          % (int(dolu.sum() // max(B, 1)), d,
                             n_gomme, sozluk))

    def intac(self) -> float:
        kan = getattr(self, "kan", None)
        pq = getattr(self, "pq", None)
        tohum = getattr(self, "_tohum", None)
        assert kan is not None, (
            "intâc KAN'sız çağrıldı -- genlik fonksiyoneli yoksa "
            "üretilecek bir hâl de yoktur (ferman 2-T, 2-A)")
        assert tohum is not None, (
            "intâc tohumsuz çağrıldı -- `kodla` mahallî yazmaca tohum "
            "ekmeden intâca geçilemez (ferman 2-A)")
        bas, sec, yigin, sut, B, n_sat, d = tohum
        m = self.mahalli
        kuresel = m.kuresel_faz()
        taban = int(self.ayar.veri_lifi)
        seviye_fazi = m.seviye_fazi(taban)
        cephe = max(0, int(n_sat) - 1)
        aday = np.concatenate(
            [np.repeat(bas, taban, axis=0),
             np.tile(np.arange(taban, dtype=bas.dtype), B)[:, None]],
            axis=1)
        kulli_aday, T_kan, U_kan, kenet_bilgisi = kan.genlik_ve_katkilar(
            aday, parametre=pq, yerel_faz=np.tile(seviye_fazi, B))
        kulli_aday = kulli_aday.reshape(B, taban)
        kulli = kulli_aday.sum(axis=1)
        bas_sev = np.mod(np.asarray(bas, np.int64), taban)
        kendi = kulli_aday[np.arange(B)[:, None], bas_sev]
        assert kendi.shape == (B, n_sat), (
            "KAN genliği basamak başına düşmedi: %r ≠ %r -- satır başına "
            "tek skaler, sütun normalizasyonunda sadeleşir ve kaybı "
            "parametreye kör bırakır (ferman 2-Ā-D)"
            % (kendi.shape, (B, n_sat)))
        agirlik = (m.genlik[:B, :n_sat] * kendi).reshape(-1)
        G = np.zeros((B, d), complex)
        V = G.reshape(B, taban, -1)
        n_yer = int(V.shape[-1])
        m_sat = int(min(int(n_sat), n_yer))
        assert m_sat >= 1, (
            "yazmaçta tek mevki bile yok: taban %d, d %d (ferman 1-N-B)"
            % (taban, d))
        V[:, :, :m_sat] = (kulli_aday[:, :, None]
                           * m.genlik[:B, :m_sat][:, None, :])
        np.add.at(G, (yigin[sec], sut[sec]), agirlik[sec])
        self.y.cephe = int(cephe)
        self.y._cephe_genligi = np.asarray(kulli_aday, complex).copy()
        self.y.psi = G.astype(self.y.ayar.tip)
        no_ham = self.y.iz.son_senet if self.y.iz.senet_acik else -1
        if no_ham >= 0 and pq is not None:
            self._kan_blokla_bagla(no_ham, kan, pq, kulli_aday, T_kan,
                                   U_kan, kenet_bilgisi, m, bas, yigin,
                                   sut, sec, taban, n_yer, m_sat, B, d)
        self.y.normalize()
        self._tur_genligi = np.asarray(self.y.psi, complex).copy()
        m.uzunluk_katmani(int(n_sat))
        if self.y.iz.senet_acik:
            self.y.iz.kapi_yaz(
                "durum", (), np.asarray(self.y.psi, complex).copy())
        return float(kuresel)

    def _kan_blokla_bagla(self, no_ham, kan, pq, kulli_aday, T_kan, U_kan,
                          kenet_bilgisi, m, bas, yigin, sut, sec, taban,
                          n_yer, m_sat, B, d) -> None:
        # pq'nun temas-kapıları (θ=faz, ağırlık=genlik) İKİ yoldan A'ya
        # karışır: (1) kenet()'in enerji/faz terimleri (kan.genlik_ve_
        # katkilar içinde doğrudan reel/sanal'a eklenir; kenet_ve_katkilar
        # içindeki kontrol kümesi İNTÂC ânında, gömme kayıtlarından SONRA
        # okunur ve pq._yer o âna dek büyümüş olabilir); (2) kodla()'nın
        # cartan_ekle("parametre.temas", Δ) çağrısı -- Δ = Σθ·bag/Σbag,
        # kontrolü kodla ânında, gömme kaydından ÖNCE, DAHA DAR bir
        # kümeden hesaplanmıştır -- m.seviye_fazi() üzerinden yerel_faz'a,
        # yâni AYNI sanal kanalına, yalnız belirli bir "col" sütununda
        # (n mod taban == col) girer. İki yol İKİ AYRI kontrol kümesi
        # görür; karıştırılırsa (2)'nin payda ve Δ'sı yanlış hesaplanır.
        C_boy = int(kan.C.size)
        S_boy = int(kan.S.size)
        kan_bas = 2 * int(pq.d)
        kontrol = kenet_bilgisi["kontrol"] if kenet_bilgisi else np.zeros(
            0, np.int64)
        bag = kenet_bilgisi["bag"] if kenet_bilgisi else np.zeros(0, float)
        teta = kenet_bilgisi["teta"] if kenet_bilgisi else np.zeros(0, float)
        w_t = (kenet_bilgisi["w_t"] if kenet_bilgisi
              else np.zeros((0, 0), float))
        col = m._kok.get("parametre.temas")
        N = int(kulli_aday.size)
        col_mod = (int(col) % int(taban)) if col is not None else -1
        mask = ((np.arange(N) % int(taban)) == col_mod
                if col_mod >= 0 else np.zeros(N, bool))
        kontrol_asli = np.asarray(
            getattr(self, "_temas_kontrol_asli", np.zeros(0, np.int64)),
            np.int64)
        if kontrol_asli.size:
            teta_asli = np.asarray(pq.faz, float)[kontrol_asli]
            bag_asli = np.abs(np.asarray(pq.genlik, float)[kontrol_asli])
            pay_asli = float(np.sum(bag_asli))
            delta_asli = (float(np.sum(teta_asli * bag_asli) / pay_asli)
                         if pay_asli > 0.0 else 0.0)
        else:
            teta_asli = np.zeros(0, float)
            bag_asli = np.zeros(0, float)
            pay_asli = 0.0
            delta_asli = 0.0

        def hesapla(lam, onceki):
            Lam = np.asarray(lam, complex).reshape(B, d)
            Vr = Lam.reshape(B, taban, n_yer)
            genlik_msat = m.genlik[:B, :m_sat]
            pay = np.zeros((B, taban), float)
            agirlik_katsayi = m.genlik[:B, :int(bas.shape[-1])].reshape(-1)
            np.add.at(pay, (yigin[sec], sut[sec]), agirlik_katsayi[sec])
            lam_A = (np.einsum("btp,bp->bt", Vr[:, :, :m_sat], genlik_msat)
                    + Lam[:, :taban] * pay).reshape(-1)
            Aflat = kulli_aday.reshape(-1)
            W = np.conj(lam_A) * Aflat
            Aabs2 = np.abs(Aflat) ** 2
            Ebar = np.einsum("jnk,n->kj", T_kan, Aabs2)
            terim1_C = np.einsum("jnk,n->kj", T_kan, W)
            w0 = float(np.real(np.sum(W)))
            g_C = 2.0 * np.real(terim1_C) - 2.0 * w0 * Ebar
            terim1_S = np.einsum("jnk,n->kj", U_kan, W)
            g_S = -2.0 * np.imag(terim1_S)
            idx = [kan_bas + np.arange(C_boy + S_boy, dtype=np.int64)]
            val = [np.concatenate([g_C.reshape(-1), g_S.reshape(-1)])]
            if kontrol.size:
                Kc = W @ w_t
                Sc = Aabs2 @ w_t
                temel = np.real(Kc) - Sc * w0
                g_teta = 2.0 * bag * temel - 2.0 * np.imag(Kc)
                g_bag = 2.0 * teta * temel
                idx.append((pq.d + kontrol).astype(np.int64))
                idx.append(kontrol.astype(np.int64))
                val.append(g_teta)
                val.append(g_bag)
            if kontrol_asli.size and col_mod >= 0 and pay_asli > 0.0:
                M = complex(np.sum(W[mask]))
                g_teta_c = -2.0 * (bag_asli / pay_asli) * np.imag(M)
                g_bag_c = -2.0 * ((teta_asli - delta_asli) / pay_asli
                                 ) * np.imag(M)
                idx.append((pq.d + kontrol_asli).astype(np.int64))
                idx.append(kontrol_asli.astype(np.int64))
                val.append(g_teta_c)
                val.append(g_bag_c)
            return np.concatenate(idx), np.concatenate(val)

        self.y.iz.kan_blok_yaz(int(no_ham), hesapla)

    def superpozisyon(self, yalniz_veri: bool = False) -> None:
        h = int(np.prod(self.y.ayar.lif[1:]))
        T = self.y.psi.reshape(self.y.B, -1, h).copy()
        T[...] = T.sum(axis=-1, keepdims=True) / np.sqrt(h)
        self.y.psi = T.reshape(self.y.B, self.y.d)
        self.y.normalize()

    def harman(self, kademe: Optional[int] = None, teta=None,
             kulli_dahil: bool = True, par_bas: int = -1,
             olcek: float = 1.0) -> None:
        k = int(kademe if kademe is not None else self.ayar.harman_kademesi)
        acilar = (None if teta is None
                  else np.asarray(teta, float).reshape(-1))
        s = 0
        _kok_sayaci = 0
        for _ in range(max(1, k)):
            for f, n in enumerate(self.y.ayar.lif):
                if not kulli_dahil and f == len(self.y.ayar.lif) - 1:
                    continue
                for alt in range(max(1, int(n).bit_length() - 1)):
                    if acilar is None:
                        a = 0.1 * math.cos(float(_kok_sayaci) * ALTIN_ACI)
                        _kok_sayaci += 1
                    else:
                        a = float(acilar[s % acilar.size])
                        s += 1
                    c, sn = np.cos(a), np.sin(a)
                    bag = None
                    if acilar is not None and int(par_bas) >= 0:
                        bag = [(int(par_bas) + ((s - 1) % acilar.size),
                                float(olcek),
                                np.array([[-sn, -c], [c, -sn]], complex))]
                    self.y.bit_kapisi(
                        f, alt, np.array([[c, -sn], [sn, c]], complex),
                        bag=bag)

    def alan_degeri(self, ad: str):
        return self.y.alan_degeri(ad)

    def olcumler(self) -> Dict[str, float]:
        return self.y.olcumler()

    def olcumler_yigin(self) -> Dict[str, np.ndarray]:
        return self.y.olcumler_yigin()

    def makam_dagilimi(self) -> np.ndarray:
        return self.y.makam_dagilimi()

    def makam_derece_vektoru(self) -> np.ndarray:
        return self.y.makam_derece_vektoru()

    def makam_mertebe_dagilimi(self, P=None) -> Dict[str, np.ndarray]:
        P = self.makam_dagilimi() if P is None else np.atleast_2d(P)
        n = P.shape[1]
        k = max(1, n // 5)
        return {"m%d" % i: P[:, i * k:(i + 1) * k].sum(axis=1)
                for i in range(min(5, n // max(k, 1)))}

    def blok_dagilimi(self, bas: int, kac: int) -> np.ndarray:
        return self.y.blok_dagilimi(bas, kac)

    def povm(self, yuvalar) -> np.ndarray:
        R = self.y.tekil_yogunluklar(yuvalar)
        return np.stack([np.real(R[..., 1, 1]), np.real(R[..., 0, 1])],
                        axis=-1)

    def beyan(self, sozluk: int = 0, satir: int = 0) -> np.ndarray:
        return self.y.beyan(sozluk)

    def beyan_vecihle(self, sozluk: int, vecihler) -> np.ndarray:
        return self.y.beyan_vecihle(sozluk, vecihler)

    def durma_hukmu(self, adim: int) -> bool:
        m = getattr(self, "mahalli", None)
        assert m is not None, (
            "yazmaca mahallî zırh bağlanmadı -- durma hükmü veremeyiz "
            "ve üretim susmazdı (ferman 2-Ğ, 2-Ó-B)")
        return bool(m.durma_hukmu(int(adim)))


MAKAM_ADLARI: Tuple[str, ...] = ("Vehim", "Şek", "Zan", "Zann-ı gālib",
                                 "Yakîn")

def makam_merdiveni(kac: int) -> Tuple[int, ...]:
    n = 1 << int(kac)
    return tuple(k ^ (k >> 1) for k in range(n))

def makam_derecesi(kac: int) -> np.ndarray:
    merd = makam_merdiveni(kac)
    n = len(merd)
    derece = np.zeros(n, dtype=float)
    for i, idx in enumerate(merd):
        derece[idx] = float(i) / max(n - 1, 1)
    return derece

def makam_mertebesi(derece: float) -> str:
    L = len(MAKAM_ADLARI)
    x = float(min(max(float(derece), 0.0), 1.0))
    return MAKAM_ADLARI[min(int(x * L), L - 1)]


def makam_mertebeleri(kac: int) -> Tuple[str, ...]:
    return tuple(makam_mertebesi(x) for x in makam_derecesi(kac))

def makam_kubit_manasi(kac: int) -> Dict[int, Tuple[int, ...]]:
    merd = makam_merdiveni(kac)
    out: Dict[int, Tuple[int, ...]] = {}
    for b in range(int(kac)):
        vurgu = 1 << (int(kac) - 1 - b)
        out[b] = tuple(k for k, idx in enumerate(merd) if idx & vurgu)
    return out

def donme(teta: float) -> np.ndarray:
    c, s = math.cos(float(teta)), math.sin(float(teta))
    return np.array([[c, -s], [s, c]], dtype=np.float64)

def faz_z() -> np.ndarray:
    return np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.float64)

def degil_x() -> np.ndarray:
    return np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.float64)

def donme_dilim(teta) -> np.ndarray:
    t = np.asarray(teta, float).reshape(-1)
    c, s = np.cos(t), np.sin(t)
    G = np.empty((t.size, 2, 2), dtype=np.float64)
    G[:, 0, 0] = c; G[:, 0, 1] = -s
    G[:, 1, 0] = s; G[:, 1, 1] = c
    return G


def donme_dilim_turevi(teta) -> np.ndarray:
    t = np.asarray(teta, float).reshape(-1)
    c, s = np.cos(t), np.sin(t)
    G = np.empty((t.size, 2, 2), dtype=np.float64)
    G[:, 0, 0] = -s; G[:, 0, 1] = -c
    G[:, 1, 0] = c; G[:, 1, 1] = -s
    return G


def donme_turevi(teta: float) -> np.ndarray:
    c, s = math.cos(float(teta)), math.sin(float(teta))
    return np.array([[-s, -c], [c, -s]], dtype=np.float64)


def tek_parite_donmesi(teta: float) -> np.ndarray:
    R = donme(teta)
    G = np.eye(4, dtype=np.float64)
    G[1, 1], G[1, 2] = R[0, 0], R[0, 1]
    G[2, 1], G[2, 2] = R[1, 0], R[1, 1]
    return G


def tek_parite_donmesi_turevi(teta: float) -> np.ndarray:
    dR = donme_turevi(teta)
    G = np.zeros((4, 4), dtype=np.float64)
    G[1, 1], G[1, 2] = dR[0, 0], dR[0, 1]
    G[2, 1], G[2, 2] = dR[1, 0], dR[1, 1]
    return G
