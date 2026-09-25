from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
from typing import Any, Dict, List, Optional, Sequence

__all__ = ["DERLEME_DIZINI", "ORTAK_BAYRAK", "ozet", "derle"]

DERLEME_DIZINI = os.environ.get(
    "MUCIT_DERLEME", os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "depo", "derleme"))

ORTAK_BAYRAK: List[str] = ["-O3", "-fPIC"]

_ONBELLEK: Dict[str, Dict[str, Any]] = {}


def ozet(kaynak: str, bayrak: Sequence[str], ek: str = "") -> str:
    h = hashlib.sha256()
    h.update(kaynak.encode("utf-8"))
    h.update(" ".join(bayrak).encode("utf-8"))
    if ek:
        h.update(ek.encode("utf-8"))
    return h.hexdigest()[:16]


def derle(ad: str, kaynak: str, bayrak: Sequence[str],
          yoklama_kaynagi: Optional[str] = None) -> Dict[str, Any]:
    anahtar = ad
    c = _ONBELLEK.get(anahtar)
    if c is not None:
        return c
    os.makedirs(DERLEME_DIZINI, exist_ok=True)
    oz = ozet(kaynak, bayrak, yoklama_kaynagi or "")
    so = os.path.join(DERLEME_DIZINI, "%s_%s.so" % (ad, oz))
    prob = (os.path.join(DERLEME_DIZINI, "%s_%s.yokla" % (ad, oz))
            if yoklama_kaynagi else "")
    cc = os.environ.get("CC", "cc")
    o: Dict[str, Any] = {"ad": ad, "kaynak_özeti": oz, "so": so,
                         "yoklama_ikilisi": prob, "derleyici": cc,
                         "bayrak": " ".join(bayrak)}
    hazir = os.path.exists(so) and (not prob or os.path.exists(prob))
    if hazir:
        o["derlendi"] = True
        o["önbellekten"] = True
        _ONBELLEK[anahtar] = o
        return o
    ciktilar: List[str] = []
    kod = 0
    with tempfile.TemporaryDirectory() as td:
        kay = os.path.join(td, "%s.c" % ad)
        with open(kay, "w", encoding="utf-8") as f:
            f.write(kaynak)
        r = subprocess.run([cc] + list(bayrak) + ["-shared", "-o", so, kay],
                           capture_output=True, text=True)
        ciktilar.append(r.stderr or "")
        kod |= r.returncode
        if yoklama_kaynagi:
            yok = os.path.join(td, "yokla.c")
            with open(yok, "w", encoding="utf-8") as f:
                f.write(yoklama_kaynagi)
            r2 = subprocess.run([cc] + list(bayrak) + ["-o", prob, yok, kay],
                                capture_output=True, text=True)
            ciktilar.append(r2.stderr or "")
            kod |= r2.returncode
    o["derlendi"] = bool(kod == 0)
    o["derleyici_çıktısı"] = "".join(ciktilar)
    o["önbellekten"] = False
    _ONBELLEK[anahtar] = o
    return o
