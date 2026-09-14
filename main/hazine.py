from __future__ import annotations

import hashlib
import json
import os
import struct
import time
from typing import Any, Dict, List, Mapping, Optional, Tuple

import numpy as np

__all__ = ["ust_coz", "UZANTI", "BICIM", "muhurle", "koy", "al", "listele", "beyan", "rapor"]

UZANTI = ".safetensors"

BICIM = "safetensors/1.0"

_TIP: Dict[str, str] = {
    "float64": "F64", "float32": "F32", "float16": "F16",
    "int64": "I64", "int32": "I32", "int16": "I16", "int8": "I8",
    "uint64": "U64", "uint32": "U32", "uint16": "U16", "uint8": "U8",
    "bool": "BOOL",
}
_TERS: Dict[str, str] = {v: k for k, v in _TIP.items()}


def _ayir(agirliklar: Mapping[str, Any]) -> Tuple[Dict[str, np.ndarray],
                                                  List[str]]:
    duz: Dict[str, np.ndarray] = {}
    karmasik: List[str] = []
    for ad, a in agirliklar.items():
        assert isinstance(ad, str) and ad, "tensör adı boş olamaz"
        assert "$" not in ad, (
            "tensör adında '$' kullanılamaz -- karmaşık ayrımına ayrıldı: %r"
            % ad)
        v = np.ascontiguousarray(np.asarray(a))
        assert v.size > 0, "BOŞ tensör kaydedilemez: %r" % ad
        if np.iscomplexobj(v):
            karmasik.append(ad)
            duz[ad + "$re"] = np.ascontiguousarray(v.real)
            duz[ad + "$im"] = np.ascontiguousarray(v.imag)
            continue
        assert str(v.dtype) in _TIP, (
            "safetensors bu tipi tanımaz: %s (tensör %r)" % (v.dtype, ad))
        duz[ad] = v
    assert duz, "hazineye BOŞ sözlük konulamaz"
    return duz, karmasik


def _birlestir(duz: Mapping[str, np.ndarray], karmasik: List[str]
               ) -> Dict[str, np.ndarray]:
    out: Dict[str, np.ndarray] = {}
    for ad in karmasik:
        re, im = ad + "$re", ad + "$im"
        assert re in duz and im in duz, (
            "karmaşık tensörün yarısı eksik: %r" % ad)
        out[ad] = np.asarray(duz[re]) + 1j * np.asarray(duz[im])
    for k, v in duz.items():
        if "$" in k and k.rsplit("$", 1)[0] in out:
            continue
        out[k] = v
    return out


def _yol(yol: str) -> str:
    return yol if yol.endswith(UZANTI) else yol + UZANTI


def muhurle(kapanan: int, *arg, **kw):
    if int(kapanan) <= 0:
        return {"yazıldı": False, "kapanan_küme": 0,
                "sebep": "hiçbir küme kapanmadı -- yarıda kesilen koşu "
                         "hazineye yazmaz (ferman 1-Y)"}
    o = koy(*arg, **kw)
    o = dict(o) if isinstance(o, dict) else {"netice": o}
    o["yazıldı"] = True
    o["kapanan_küme"] = int(kapanan)
    return o


def koy(yol: str, agirliklar: Mapping[str, Any],
        ust_veri: Optional[Mapping[str, Any]] = None) -> Dict[str, object]:
    duz, karmasik = _ayir(agirliklar)
    yol = _yol(yol)
    dizin = os.path.dirname(os.path.abspath(yol))
    if dizin:
        os.makedirs(dizin, exist_ok=True)

    govde = bytearray()
    basi: Dict[str, Any] = {}
    for ad in sorted(duz):
        v = duz[ad]
        ham = v.tobytes(order="C")
        bas = len(govde)
        govde += ham
        basi[ad] = {"dtype": _TIP[str(v.dtype)], "shape": list(v.shape),
                    "data_offsets": [bas, len(govde)]}
    ozet = hashlib.sha256(bytes(govde)).hexdigest()

    meta: Dict[str, str] = {"biçim": BICIM, "sha256": ozet,
                            "zaman": time.strftime("%Y-%m-%dT%H:%M:%S"),
                            "tensör": str(len(basi))}
    if karmasik:
        meta["karmaşık"] = json.dumps(sorted(karmasik), ensure_ascii=False)
    for k, v in dict(ust_veri or {}).items():
        meta[str(k)] = v if isinstance(v, str) else json.dumps(
            v, ensure_ascii=False, default=str)
    basi["__metadata__"] = meta

    ham_bas = json.dumps(basi, ensure_ascii=False,
                         separators=(",", ":")).encode("utf-8")
    dolgu = (-len(ham_bas)) % 8
    ham_bas += b" " * dolgu

    gecici = yol + ".yazılıyor"
    with open(gecici, "wb") as f:
        f.write(struct.pack("<Q", len(ham_bas)))
        f.write(ham_bas)
        f.write(bytes(govde))
    os.replace(gecici, yol)

    boy = os.path.getsize(yol)
    assert boy == 8 + len(ham_bas) + len(govde), "yazılan boy tutmadı"
    return {"yol": yol, "bayt": int(boy), "tensör": len(duz),
            "karmaşık": karmasik, "sha256": ozet,
            "başlık_bayt": len(ham_bas)}


def beyan(yol: str) -> Dict[str, Any]:
    yol = _yol(yol)
    assert os.path.exists(yol), "hazine yok: %s" % yol
    with open(yol, "rb") as f:
        (n,) = struct.unpack("<Q", f.read(8))
        assert 0 < n < 100_000_000, "başlık uzunluğu makul değil: %d" % n
        basi = json.loads(f.read(n).decode("utf-8"))
    assert isinstance(basi, dict) and basi, "başlık boş yahut bozuk"
    return basi


def ust_coz(meta: Mapping[str, str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in dict(meta or {}).items():
        if not isinstance(v, str):
            out[k] = v
            continue
        try:
            out[k] = json.loads(v)
        except (ValueError, TypeError):
            out[k] = v
    return out


def al(yol: str, mmap: bool = True, tahkik: bool = True
       ) -> Tuple[Dict[str, np.ndarray], Dict[str, str]]:
    yol = _yol(yol)
    basi = beyan(yol)
    meta: Dict[str, str] = dict(basi.pop("__metadata__", {}) or {})
    assert basi, "hazinede hiç tensör yok -- boş bir şey dönemez"
    with open(yol, "rb") as f:
        (n,) = struct.unpack("<Q", f.read(8))
    bas_sonu = 8 + n
    boy = os.path.getsize(yol)
    govde_boy = boy - bas_sonu

    if tahkik and "sha256" in meta:
        with open(yol, "rb") as f:
            f.seek(bas_sonu)
            h = hashlib.sha256()
            while True:
                p = f.read(1 << 20)
                if not p:
                    break
                h.update(p)
        assert h.hexdigest() == meta["sha256"], (
            "HAZİNE BOZUK: sha256 tutmuyor (%s ≠ %s). Bozuk ağırlıkla "
            "çıkarım yapmak sessizce yanlış cevap vermektir."
            % (h.hexdigest()[:16], meta["sha256"][:16]))

    if mmap:
        ham = np.memmap(yol, dtype=np.uint8, mode="r",
                        offset=bas_sonu, shape=(govde_boy,))
    else:
        with open(yol, "rb") as f:
            f.seek(bas_sonu)
            ham = np.frombuffer(f.read(), dtype=np.uint8)

    duz: Dict[str, np.ndarray] = {}
    for ad, t in basi.items():
        a, b = int(t["data_offsets"][0]), int(t["data_offsets"][1])
        assert 0 <= a <= b <= govde_boy, (
            "ofset gövdenin dışında: %r %r" % (ad, t["data_offsets"]))
        dt = _TERS.get(str(t["dtype"]))
        assert dt is not None, "bilinmeyen dtype: %r" % t["dtype"]
        v = ham[a:b].view(np.dtype(dt)).reshape(tuple(t["shape"]))
        assert v.size > 0, "BOŞ tensör okundu: %r" % ad
        duz[ad] = v

    karmasik: List[str] = json.loads(meta.get("karmaşık", "[]"))
    out = _birlestir(duz, karmasik)
    assert out, "hazineden BOŞ sözlük çıktı"
    return out, meta


def listele(dizin: str = "depo") -> List[Dict[str, object]]:
    if not os.path.isdir(dizin):
        return []
    out: List[Dict[str, object]] = []
    for ad in sorted(os.listdir(dizin)):
        if not ad.endswith(UZANTI):
            continue
        y = os.path.join(dizin, ad)
        b = beyan(y)
        m = b.get("__metadata__", {}) or {}
        out.append({"ad": ad, "bayt": os.path.getsize(y),
                    "tensör": len([k for k in b if k != "__metadata__"]),
                    "zaman": m.get("zaman", ""), "biçim": m.get("biçim", "")})
    return out


def rapor(yol: Optional[str] = None) -> str:
    import tempfile
    r = np.random.default_rng(0)
    ornek = {"p": r.normal(size=(3, 5)),
             "psi": (r.normal(size=64) + 1j * r.normal(size=64)),
             "sayaç": np.arange(7, dtype=np.int64)}
    with tempfile.TemporaryDirectory() as td:
        y = os.path.join(td, "deneme")
        k = koy(y, ornek, {"ayar": "deneme", "kayıp": 0.5})
        g, m = al(y)
        fark = max(float(np.max(np.abs(np.asarray(g[a]) - ornek[a])))
                   for a in ornek)
        ham = sum(np.asarray(v).nbytes for v in ornek.values())
        s = ["=== HAZİNE -- safetensors (elde yazıldı, kütüphane yok) ===",
             "",
             "  yazılan          : %d bayt (%d tensör, başlık %d bayt)"
             % (k["bayt"], k["tensör"], k["başlık_bayt"]),
             "  ham tensör toplamı: %d bayt  (üstyük %%%.2f)"
             % (ham, 100.0 * (k["bayt"] - ham) / max(ham, 1)),
             "  karmaşık ayrılan  : %s" % (k["karmaşık"] or "yok"),
             "  sha256            : %s…" % k["sha256"][:24],
             "",
             "  YUVARLAK DÖNÜŞ (yazıp geri okuyunca en büyük fark)",
             "    %.3e   %s" % (fark, "KAYIPSIZ" if fark == 0.0 else "KAYIPLI"),
             "  üst veri geri geldi mi: %s"
             % ("evet" if m.get("ayar") == "deneme" else "HAYIR")]
    if yol:
        s += ["", "  DEPODAKİLER:"]
        for h in listele(os.path.dirname(_yol(yol)) or "depo"):
            s.append("    %-40s %10d bayt  %s"
                     % (h["ad"], h["bayt"], h["zaman"]))
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor("depo/x"))
