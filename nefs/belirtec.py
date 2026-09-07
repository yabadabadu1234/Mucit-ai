from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["Kodlama", "KODLAMALAR", "belirtec_kapisi", "belirtec_sozlugu",
           "basamak_sayisi", "tip_vektoru", "tipten", "belirtec_beyani",
           "BPE_DEPOSU", "onbellek_dizini"]

BPE_DEPOSU = "zurawiki/tiktoken-rs"
BPE_YOLU = "tiktoken-rs/assets"


@dataclass(frozen=True)
class Kodlama:

    ad: str
    blobpath: str
    ozet: str
    dosya: str


KODLAMALAR: Tuple[Kodlama, ...] = (
    Kodlama(ad="o200k_base",
            blobpath="https://openaipublic.blob.core.windows.net/"
                     "encodings/o200k_base.tiktoken",
            ozet="446a9538cb6c348e3516120d7c08b09f57c36495"
                 "e2acfffe59a5bf8b0cfb1a2d",
            dosya="o200k_base.tiktoken"),
    Kodlama(ad="cl100k_base",
            blobpath="https://openaipublic.blob.core.windows.net/"
                     "encodings/cl100k_base.tiktoken",
            ozet="223921b76ee99bde995b7ff738513eef100fb51d"
                 "18c93597a113bcffe865b2a7",
            dosya="cl100k_base.tiktoken"),
)

_KAPI: Dict[str, Any] = {}
_SAYAC: Dict[str, float] = {"kodlama": 0.0, "coz": 0.0, "belirtec": 0.0,
                            "yerlestirme": 0.0}


def onbellek_dizini() -> str:
    d = os.environ.get("TIKTOKEN_CACHE_DIR") \
        or os.environ.get("DATA_GYM_CACHE_DIR")
    if not d:
        d = os.path.join(os.environ.get("MUCIT_KULLIYAT", "depo/kulliyat"),
                         "tiktoken")
        os.environ["TIKTOKEN_CACHE_DIR"] = d
    os.makedirs(d, exist_ok=True)
    return d


def _kodlama(ad: str) -> Kodlama:
    for k in KODLAMALAR:
        if k.ad == ad:
            return k
    raise ValueError(
        "bilinmeyen kodlama %r; yoklanmışlar: %s"
        % (ad, ", ".join(k.ad for k in KODLAMALAR)))


def bpe_yerlestir(ad: str) -> Dict[str, Any]:
    k = _kodlama(ad)
    onb = onbellek_dizini()
    anahtar = hashlib.sha1(k.blobpath.encode()).hexdigest()
    hedef = os.path.join(onb, anahtar)
    if os.path.isfile(hedef) and os.path.getsize(hedef) > 0:
        return {"kodlama": ad, "yol": hedef, "yerleştirildi": False,
                "bayt": os.path.getsize(hedef)}
    kok = os.path.join(onb, "_bpe_deposu")
    if not os.path.isdir(os.path.join(kok, ".git")):
        shutil.rmtree(kok, ignore_errors=True)
        r = subprocess.run(
            ["git", "clone", "--depth", "1", "--filter=blob:none",
             "https://github.com/" + BPE_DEPOSU, kok],
            capture_output=True, text=True,
            env=dict(os.environ, GIT_LFS_SKIP_SMUDGE="1"), timeout=1800)
        assert r.returncode == 0, (
            "BPE tablosu alınamadı -- belirteçleyici olmadan tâlim "
            "başlayamaz.\n  depo : %s\n  sebep: %s\n"
            "  (tiktoken'in kendi adresi bu kapta kapalı: "
            "openaipublic.blob.core.windows.net → 000)"
            % (BPE_DEPOSU, (r.stderr or "").strip()[-300:]))
    kaynak = os.path.join(kok, BPE_YOLU, k.dosya)
    if not os.path.isfile(kaynak):
        r = subprocess.run(["git", "-C", kok, "checkout", "HEAD", "--",
                            os.path.join(BPE_YOLU, k.dosya)],
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0 and os.path.isfile(kaynak), (
            "BPE dosyası depoda bulunamadı: %s/%s/%s -- %s"
            % (BPE_DEPOSU, BPE_YOLU, k.dosya, (r.stderr or "").strip()[-200:]))
    with open(kaynak, "rb") as f:
        ham = f.read()
    olculen = hashlib.sha256(ham).hexdigest()
    assert olculen == k.ozet, (
        "BPE tablosunun özeti tutmuyor -- bu, tiktoken'in beklediği "
        "tablo DEĞİLDİR.\n  beklenen: %s\n  ölçülen : %s\n  dosya   : %s"
        % (k.ozet, olculen, kaynak))
    gecici = hedef + ".yaz"
    with open(gecici, "wb") as f:
        f.write(ham)
    os.replace(gecici, hedef)
    _SAYAC["yerlestirme"] += 1.0
    return {"kodlama": ad, "yol": hedef, "yerleştirildi": True,
            "bayt": len(ham), "sha256": olculen}


def belirtec_kapisi(ad: str = "o200k_base"):
    if ad in _KAPI:
        return _KAPI[ad]
    bpe_yerlestir(ad)
    import tiktoken

    kod = tiktoken.get_encoding(ad)
    _KAPI[ad] = kod
    return kod


def belirtec_sozlugu(ad: str = "o200k_base") -> int:
    return int(belirtec_kapisi(ad).n_vocab)


def basamak_sayisi(sozluk: int, taban: int) -> int:
    t, n, kap = max(2, int(taban)), 1, max(2, int(taban))
    while kap < int(sozluk):
        kap *= t
        n += 1
    return int(n)


def tip_vektoru(belirtecler: Sequence[int], taban: int, basamak: int
                ) -> np.ndarray:
    t = np.asarray(belirtecler, np.int64).reshape(-1)
    b, n = max(2, int(taban)), max(1, int(basamak))
    out = np.empty((t.size, n), np.int64)
    kalan = t.copy()
    for i in range(n):
        out[:, i] = kalan % b
        kalan //= b
    return out.reshape(-1)


def tipten(basamaklar: Sequence[int], taban: int, basamak: int
           ) -> np.ndarray:
    a = np.asarray(basamaklar, np.int64).reshape(-1, max(1, int(basamak)))
    b = max(2, int(taban))
    carp = b ** np.arange(a.shape[1], dtype=np.int64)
    return (a * carp[None, :]).sum(axis=1)


def belirtecle(metin, ad: str = "o200k_base") -> List[int]:
    kod = belirtec_kapisi(ad)
    if isinstance(metin, (bytes, bytearray)):
        metin = bytes(metin).decode("utf-8", "replace")
    t = kod.encode(str(metin), disallowed_special=())
    _SAYAC["kodlama"] += 1.0
    _SAYAC["belirtec"] += float(len(t))
    return list(t)


def coz(belirtecler: Sequence[int], ad: str = "o200k_base") -> str:
    _SAYAC["coz"] += 1.0
    return belirtec_kapisi(ad).decode(
        [int(x) % int(belirtec_sozlugu(ad)) for x in belirtecler])


def belirtec_beyani(ad: str = "o200k_base") -> Dict[str, Any]:
    acik = ad in _KAPI
    return {"kodlama": ad, "açık": acik,
            "sözlük": int(_KAPI[ad].n_vocab) if acik else 0,
            "kodlama_çağrısı": int(_SAYAC["kodlama"]),
            "çözme_çağrısı": int(_SAYAC["coz"]),
            "belirteç": int(_SAYAC["belirtec"]),
            "bpe_yerleştirme": int(_SAYAC["yerlestirme"]),
            "önbellek": onbellek_dizini()}
