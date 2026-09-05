"""VERİ -- belirteçleri diske dizen ve Kaggle'a gönderen tek kapı.

Padişahın zabıtı: ``docs/zabit/kudret/Kaggle_Veri_Donusturucu_ve_Gonderici.py``.
İhtiyaç orada yazılıdır; burada **hem Kaggle'ı hem burayı** destekleyen
hâli kurulur.

===================================================================
ZABITTAN NE ALINDI, NE DEĞİŞTİRİLDİ -- ve niçin
===================================================================

**Alınanlar (aynen):**

* mmap'lenebilir ham ikili (``.bin`` + ``.idx``), GPUDirect'e uygun,
  64 baytlık hizalama ile.
* **500 MB parça haddi.** Kaggle'ın dosya haddi budur ve aşılmaz.
* Safetensors (sıfır kopyalı ağırlık) ve Zarr v3 (bloklu tensör)
  yolları.
* Umuma açık veri kümesi olarak gönderme.

**Değiştirilenler -- her biri ölçülmüş bir sebeple:**

1. **Anahtar adları.** Zabıt ``KAGGLE_USERNAME``/``KAGGLE_KEY`` diyor;
   padişahın fermanı ``kaggle_username`` ve ``key``dir. İkisi de
   denenir (kasa adları büyük/küçük harfe duyarlıdır), fakat **asıl
   olan fermandaki ikisidir**.

2. **Dizinler koda gömülü değildir.** Zabıt ``/kaggle/input`` ve
   ``/kaggle/working``ı sabit yazıyor; o hâlde modül burada hiç
   koşmaz. ``kok()`` nerede olduğunu **ölçer**: Kaggle varsa oradan,
   yoksa deponun kendi ``idrak/veri``sinden okur.

3. **Belirteçleme naif değildir.** Zabıt metni ham UTF-8 baytına
   çeviriyor (``np.frombuffer(metin.encode())``). Bu proje için
   yanlıştır: ARC verisi metin değil **ızgaradır** ve bu deponun
   kendi belirteçlemesi ``nefs/musahede.py:gorev_dizisi``dedir --
   ``girdi₁ 12 çıktı₁ 14 … girdi* 12`` nizamı. Ham bayta çevirmek o
   nizamı yok eder ve model hiçbir şey öğrenemez. O hâlde
   belirteçleme deponun kendi uzvuna havale edilir.

4. **torch/safetensors/zarr mecburî değildir.** Bu makinede üçü de
   **kurulu değil** (ölçüldü). Zabıt onları doğrudan ithal ediyor;
   öyle olsa modül burada hiç yüklenmezdi. Üçü de isteğe bağlıdır ve
   yoklukları ``rapor()``da **sayılır**, gizlenmez. ``.bin``/``.idx``
   yolu saf numpy'dır ve her yerde çalışır.

5. **Okuma yolu da vardır.** Zabıtta yalnız yazma var; yazılan şey
   okunamıyorsa dönüştürücü değil çöp üreticisidir. ``oku()``
   ``mmap`` ile açar -- bellek kopyası yoktur, GPUDirect'in istediği
   budur.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["kok", "belirtecle", "yaz", "oku", "yetki", "gonder", "rapor",
           "PARCA_HADDI", "HIZA"]

#: Kaggle'ın dosya haddi. Aşılmaz.
PARCA_HADDI: int = 500 * 1024 * 1024
#: GPUDirect/tensör çekirdeği hizalaması (bayt).
HIZA: int = 64
#: Belirteç tipi. ARC sözlüğü küçüktür; ``uint16`` 65 535'e kadar yeter
#: ve ``uint32``nin yarısı yer tutar. Sözlük büyürse ``yaz`` kendisi
#: ``uint32``ye geçer ve bunu ``.meta``ya yazar -- sessizce taşmaz.
TIP_KUCUK = np.uint16
TIP_BUYUK = np.uint32


# ══════════════════════════════════════════════════════════════════
#  1. NEREDEYİZ
# ══════════════════════════════════════════════════════════════════

def kok(ne: str = "veri") -> Path:
    """Verinin **ölçülen** yeri -- koda gömülü değil.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``veri``        okunacak kök (Kaggle girdisi yahut deponun kendisi)
    ``cikti``       yazılacak kök (Kaggle çalışma dizini yahut ``depo/``)
    ``kaggle_mi``   ``Path`` değil ``bool``: Kaggle'da mıyız
    ==============  ==================================================
    """
    kaggle = Path("/kaggle/input")
    calisma = Path("/kaggle/working")
    icerde = kaggle.exists() and calisma.exists()
    if ne == "kaggle_mi":
        return icerde                                    # type: ignore[return-value]
    if ne == "veri":
        if icerde:
            return kaggle
        return Path(__file__).resolve().parent.parent / "idrak" / "veri"
    if ne == "cikti":
        if icerde:
            return calisma / "veri_kumesi"
        return Path(__file__).resolve().parent.parent / "depo" / "veri_kumesi"
    raise ValueError("kök kipi bilinmiyor: %r" % (ne,))


# ══════════════════════════════════════════════════════════════════
#  2. BELİRTEÇLEME -- deponun kendi nizamıyla
# ══════════════════════════════════════════════════════════════════

def belirtecle(gorevler: Optional[Sequence] = None, kume: str = "training",
               sozluk: int = 16) -> Tuple[np.ndarray, np.ndarray]:
    """Görevleri **tek bir belirteç akışına** ve sınır tablosuna çevir.

    Döner: ``(akis, sinir)``.

    * ``akis``  -- bütün görevlerin belirteçleri ardı ardına.
    * ``sinir`` -- ``(görev, 3)``: ``(başlangıç, bağlam_uzunluğu,
      hedef_uzunluğu)``. Yâni her görevin nerede başladığı ve nerede
      bağlamın bitip hedefin başladığı.

    **Belirteçleme uydurulmaz**, ``nefs/musahede.py:gorev_dizisi``ye
    havale edilir: ``girdi₁ 12 çıktı₁ 14 … girdi* 12`` nizamı ve hedef
    ızgaranın bağlamda **hiç geçmemesi** kaidesi oradadır. Burada o
    kaideyi tekrar yazmak, iki yerde iki farklı nizam demek olurdu.
    """
    from nefs.musahede import gorevleri_getir, gorev_dizisi

    if gorevler is None:
        gorevler = gorevleri_getir(kume)
    akis: List[int] = []
    sinir: List[Tuple[int, int, int]] = []
    for g in gorevler:
        try:
            bag, hedef = gorev_dizisi(g)
        except Exception:                                # noqa: BLE001
            continue
        b = [int(x) % int(sozluk) for x in bag]
        h = [int(x) % int(sozluk) for x in hedef]
        sinir.append((len(akis), len(b), len(h)))
        akis.extend(b)
        akis.extend(h)
    tip = TIP_KUCUK if int(sozluk) <= np.iinfo(TIP_KUCUK).max else TIP_BUYUK
    return (np.asarray(akis, dtype=tip),
            np.asarray(sinir, dtype=np.uint64).reshape(-1, 3))


# ══════════════════════════════════════════════════════════════════
#  3. YAZMA -- 500 MB parçalar, hizalı
# ══════════════════════════════════════════════════════════════════

def yaz(akis: np.ndarray, sinir: np.ndarray, cikti: Optional[Path] = None,
        onek: str = "belirtec", ne: str = "bin") -> Dict[str, object]:
    """Belirteç akışını diske diz. ``ne``: ``bin`` | ``safetensors`` | ``zarr``.

    ``bin`` yolu **saf numpy**dır ve her yerde çalışır; ötekiler
    kütüphane ister ve yoksa **açıkça** düşerler (sessizce atlamazlar).

    Her parça ``PARCA_HADDI``i aşmaz ve ``HIZA`` baytına hizalanır.
    Yanına ``.meta.json`` yazılır: tip, sözlük, parça listesi. Meta
    olmadan ``.bin`` bir bayt yığınıdır; onunla veridir.
    """
    cikti = Path(cikti) if cikti is not None else kok("cikti")
    cikti.mkdir(parents=True, exist_ok=True)
    akis = np.ascontiguousarray(akis)

    if ne == "bin":
        return _bin_yaz(akis, sinir, cikti, onek)
    if ne == "safetensors":
        return _safetensors_yaz(akis, sinir, cikti, onek)
    if ne == "zarr":
        return _zarr_yaz(akis, sinir, cikti, onek)
    raise ValueError("yazma kipi bilinmiyor: %r" % (ne,))


def _bin_yaz(akis, sinir, cikti: Path, onek: str) -> Dict[str, object]:
    eleman = int(akis.dtype.itemsize)
    # Parça başına kaç belirteç sığar: had / eleman, HIZA'ya yuvarlanmış.
    parca_eleman = (PARCA_HADDI // eleman) // HIZA * HIZA
    parcalar: List[Dict[str, object]] = []
    for i, bas in enumerate(range(0, akis.size, parca_eleman)):
        dilim = akis[bas:bas + parca_eleman]
        yol = cikti / ("%s_%04d.bin" % (onek, i))
        with open(yol, "wb") as f:
            f.write(dilim.tobytes())
            # Hizalama dolgusu: GPUDirect sektör hizası ister.
            art = (dilim.nbytes % HIZA)
            if art:
                f.write(b"\x00" * (HIZA - art))
        parcalar.append({"dosya": yol.name, "belirtec": int(dilim.size),
                         "bayt": int(yol.stat().st_size),
                         "ilk_belirtec": int(bas)})
    idx = cikti / ("%s.idx" % onek)
    np.asarray(sinir, np.uint64).tofile(idx)
    meta = {"tip": str(akis.dtype), "belirtec": int(akis.size),
            "gorev": int(np.asarray(sinir).shape[0]),
            "hiza": HIZA, "parca_haddi": PARCA_HADDI,
            "parca": parcalar, "idx": idx.name,
            "idx_sutun": ["baslangic", "baglam", "hedef"]}
    (cikti / ("%s.meta.json" % onek)).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def _safetensors_yaz(akis, sinir, cikti: Path, onek: str) -> Dict[str, object]:
    try:
        import torch
        from safetensors.torch import save_file
    except Exception as exc:                             # noqa: BLE001
        raise RuntimeError(
            "safetensors yolu torch+safetensors ister; bu makinede yok "
            "(%s). `.bin` yolu saf numpy'dır ve her yerde çalışır."
            % type(exc).__name__) from exc
    yol = cikti / ("%s.safetensors" % onek)
    save_file({"akis": torch.from_numpy(akis.astype(np.int32)),
               "sinir": torch.from_numpy(np.asarray(sinir, np.int64))},
              str(yol))
    return {"dosya": yol.name, "bayt": int(yol.stat().st_size)}


def _zarr_yaz(akis, sinir, cikti: Path, onek: str) -> Dict[str, object]:
    try:
        import zarr
    except Exception as exc:                             # noqa: BLE001
        raise RuntimeError(
            "zarr yolu zarr ister; bu makinede yok (%s)."
            % type(exc).__name__) from exc
    yol = cikti / ("%s.zarr" % onek)
    kok_g = zarr.open_group(str(yol), mode="w")
    blok = max(1, (PARCA_HADDI // int(akis.dtype.itemsize)) // 2)
    kok_g.create_dataset("akis", data=akis, chunks=(min(akis.size, blok),))
    kok_g.create_dataset("sinir", data=np.asarray(sinir, np.uint64))
    return {"dizin": yol.name}


# ══════════════════════════════════════════════════════════════════
#  4. OKUMA -- mmap, kopyasız
# ══════════════════════════════════════════════════════════════════

def oku(cikti: Optional[Path] = None, onek: str = "belirtec"
        ) -> Tuple[np.ndarray, np.ndarray, Dict[str, object]]:
    """Yazılanı **belleğe kopyalamadan** aç: ``(akis, sinir, meta)``.

    Parçalar ``np.memmap`` ile açılıp ``concatenate`` edilmeden
    okunur; her parça kendi mmap'idir ve yalnız dokunulan sayfa
    belleğe gelir. GPUDirect'in istediği budur ve 500 MB haddi de
    bunun için vardır.
    """
    cikti = Path(cikti) if cikti is not None else kok("cikti")
    meta = json.loads((cikti / ("%s.meta.json" % onek)).read_text("utf-8"))
    tip = np.dtype(meta["tip"])
    parcalar = []
    for p in meta["parca"]:
        m = np.memmap(cikti / p["dosya"], dtype=tip, mode="r")
        parcalar.append(m[: int(p["belirtec"])])         # dolguyu kes
    akis = (parcalar[0] if len(parcalar) == 1
            else np.concatenate([np.asarray(x) for x in parcalar]))
    sinir = np.fromfile(cikti / meta["idx"], dtype=np.uint64).reshape(-1, 3)
    return akis, sinir, meta


# ══════════════════════════════════════════════════════════════════
#  5. KAGGLE
# ══════════════════════════════════════════════════════════════════

def yetki() -> Tuple[str, str]:
    """Kaggle anahtarları. **Ferman: ``kaggle_username`` ve ``key``.**

    Zabıt ``KAGGLE_USERNAME``/``KAGGLE_KEY`` diyordu; padişahın koyduğu
    adlar bunlar değil. Kasa adları harfe duyarlı olduğu için fermandaki
    ikisi **evvela** denenir, sonra eski adlar; hiçbiri yoksa açıkça
    patlar. Anahtar burada **basılmaz** ve kütüğe yazılmaz.
    """
    adaylar = (("kaggle_username", "key"),
               ("KAGGLE_USERNAME", "KAGGLE_KEY"))
    try:
        from kaggle_secrets import UserSecretsClient     # type: ignore
        kasa = UserSecretsClient()
        for ka, kk in adaylar:
            try:
                k, a = kasa.get_secret(ka), kasa.get_secret(kk)
                if k and a:
                    os.environ["KAGGLE_USERNAME"] = k
                    os.environ["KAGGLE_KEY"] = a
                    return k, a
            except Exception:                            # noqa: BLE001
                continue
    except Exception:                                    # noqa: BLE001
        pass
    for ka, kk in adaylar:
        k, a = os.environ.get(ka), os.environ.get(kk)
        if k and a:
            os.environ["KAGGLE_USERNAME"] = k
            os.environ["KAGGLE_KEY"] = a
            return k, a
    raise RuntimeError(
        "Kaggle anahtarı yok. Add-ons → Secrets'e 'kaggle_username' ve "
        "'key' ekleyin (yahut aynı adlı ortam değişkenleri).")


def gonder(veri_dizini: Optional[Path] = None, etiket: str = "mucit-ai-belirtec",
           baslik: str = "Mucit-AI belirtec akisi (mmap .bin + .idx)",
           umumi: bool = True) -> Dict[str, object]:
    """İşlenmiş dosyaları Kaggle'a **umuma açık** veri kümesi yap.

    Evvela yeni sürüm denenir (küme zaten varsa); olmazsa sıfırdan
    kurulur. Hangisinin olduğu döner -- "yüklendi" deyip geçilmez.
    """
    veri_dizini = Path(veri_dizini) if veri_dizini else kok("cikti")
    kullanici, _ = yetki()
    from kaggle.api.kaggle_api_extended import KaggleApi  # type: ignore
    api = KaggleApi()
    api.authenticate()
    (veri_dizini / "dataset-metadata.json").write_text(json.dumps(
        {"title": baslik, "id": "%s/%s" % (kullanici, etiket),
         "licenses": [{"name": "CC0-1.0"}]},
        ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        api.dataset_create_version(str(veri_dizini),
                                   version_notes="yeni sürüm",
                                   dir_mode="zip")
        return {"usul": "yeni sürüm", "id": "%s/%s" % (kullanici, etiket)}
    except Exception as exc:                             # noqa: BLE001
        api.dataset_create_new(str(veri_dizini), public=bool(umumi),
                               dir_mode="zip", quiet=False)
        return {"usul": "sıfırdan kuruldu", "id": "%s/%s" % (kullanici, etiket),
                "evvelki_hata": type(exc).__name__}


# ══════════════════════════════════════════════════════════════════
#  6. ÖLÇÜ
# ══════════════════════════════════════════════════════════════════

def rapor(kume: str = "training") -> str:                # pragma: no cover
    """Dönüştür, geri oku, **birebir tuttuğunu ölç**."""
    import tempfile
    import time

    s = ["=== VERİ -- dönüştürücü ===", ""]
    s.append("  yer          : %s" % ("KAGGLE" if kok("kaggle_mi") else "yerel"))
    s.append("  okuma kökü   : %s" % kok("veri"))
    t0 = time.perf_counter()
    akis, sinir = belirtecle(kume=kume)
    s.append("  belirteçleme : %d görev, %d belirteç, %.2f sn"
             % (sinir.shape[0], akis.size, time.perf_counter() - t0))
    s.append("  tip          : %s" % akis.dtype)
    with tempfile.TemporaryDirectory() as d:
        m = yaz(akis, sinir, Path(d), ne="bin")
        a2, s2, m2 = oku(Path(d))
        ayni = bool(np.array_equal(np.asarray(a2), akis)
                    and np.array_equal(np.asarray(s2), sinir))
        s += ["", "  YAZ → OKU",
              "    parça        : %d" % len(m["parca"]),
              "    azamî parça  : %.2f MB"
              % (max(p["bayt"] for p in m["parca"]) / 1024 / 1024),
              "    had (500 MB) : %s"
              % ("AŞILMADI" if all(p["bayt"] <= PARCA_HADDI
                                   for p in m["parca"]) else "AŞILDI"),
              "    hizalama     : %s"
              % ("%d bayt" % HIZA if all(p["bayt"] % HIZA == 0
                                         for p in m["parca"]) else "BOZUK"),
              "    BİREBİR      : %s" % ("EVET" if ayni else "HAYIR")]
    s += ["", "  İSTEĞE BAĞLI YOLLAR"]
    for ad, mod in (("safetensors", "safetensors"), ("zarr", "zarr"),
                    ("torch", "torch"), ("kaggle", "kaggle")):
        try:
            __import__(mod)
            s.append("    %-12s var" % ad)
        except Exception:                                # noqa: BLE001
            s.append("    %-12s YOK -- o yol düşer, .bin yolu çalışır" % ad)
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())
