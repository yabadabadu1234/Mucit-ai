from __future__ import annotations

import os
import sys
from typing import List

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

CIKTI = os.path.join(KOK, "TUM_MD_BIRLESIK.md")

DOSYA_ADLARI = (
    "CLAUDE.md", "FORMUL.md", "KARARLAR.md", "MUNASEBET_YURUYUSU.md",
    "SERH.md", "ZABIT_TARAMASI.md",
)


def toplanacak_dosyalar() -> List[str]:
    bulunanlar: List[str] = []
    for ad in DOSYA_ADLARI:
        tam_yol = os.path.join(KOK, ad)
        if os.path.isfile(tam_yol):
            bulunanlar.append(tam_yol)
    return bulunanlar


def birlestir() -> str:
    dosyalar = toplanacak_dosyalar()
    parcalar: List[str] = []
    for tam_yol in dosyalar:
        goreli = os.path.relpath(tam_yol, KOK)
        with open(tam_yol, "r", encoding="utf-8", errors="replace") as f:
            icerik = f.read()
        parcalar.append("==== BAŞLIYOR: %s ====" % goreli)
        parcalar.append(icerik.rstrip("\n"))
        parcalar.append("==== BİTTİ: %s ====" % goreli)
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
