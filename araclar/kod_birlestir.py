from __future__ import annotations

import os
import sys
from typing import List

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

CIKTI = os.path.join(KOK, "TUM_KOD_BIRLESIK.py")

HARIC_DIZINLER = {
    "idrak", ".git", ".github", "__pycache__", ".venv", "venv",
}

HARIC_DOSYALAR = {
    os.path.basename(__file__),
    os.path.basename(CIKTI),
}


def toplanacak_dosyalar() -> List[str]:
    bulunanlar: List[str] = []
    for kok, dizinler, dosyalar in os.walk(KOK):
        goreli_kok = os.path.relpath(kok, KOK)
        parcalar = set(goreli_kok.split(os.sep))
        if parcalar & HARIC_DIZINLER:
            dizinler[:] = []
            continue
        dizinler[:] = [d for d in dizinler if d not in HARIC_DIZINLER]
        for ad in dosyalar:
            if not ad.endswith(".py"):
                continue
            if ad in HARIC_DOSYALAR:
                continue
            bulunanlar.append(os.path.join(kok, ad))
    return sorted(bulunanlar, key=lambda p: os.path.relpath(p, KOK))


def birlestir() -> str:
    dosyalar = toplanacak_dosyalar()
    parcalar: List[str] = []
    for tam_yol in dosyalar:
        goreli = os.path.relpath(tam_yol, KOK)
        with open(tam_yol, "r", encoding="utf-8", errors="replace") as f:
            icerik = f.read()
        parcalar.append("# ==== BAŞLIYOR: %s ====" % goreli)
        parcalar.append(icerik.rstrip("\n"))
        parcalar.append("# ==== BİTTİ: %s ====" % goreli)
        parcalar.append("")
    return "\n".join(parcalar) + "\n"


def yaz() -> str:
    metin = birlestir()
    with open(CIKTI, "w", encoding="utf-8") as f:
        f.write(metin)
    return CIKTI


if __name__ == "__main__":
    yol = yaz()
    sys.stdout.write("%s yazıldı\n" % yol)
