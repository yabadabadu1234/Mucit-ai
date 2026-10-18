#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kelime mealli veri: her âyetin kelimelerini, Türkçe karşılıklarıyla birlikte üretir.

Kaynak: veri_harici/eyupipler (morfoloji + Arabça→Türkçe sözlük).
Sözlükte karşılığı olmayan kelimelerin anlamı boş bırakılır; bu sayı derleme sırasında raporlanır.
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MORFOLOJI = BASE_DIR / "veri_harici" / "eyupipler" / "quran-morphology.txt"
SOZLUK = BASE_DIR / "veri_harici" / "eyupipler" / "word-translations-tr.json"


def yukle():
    """(sure, ayet) -> [{'ar': kelime, 'tr': karşılık, 'lem': sözlük formu}, ...] döndürür."""
    sozluk = json.load(open(SOZLUK, encoding="utf-8"))["translations"]
    parcalar = {}
    with open(MORFOLOJI, encoding="utf-8") as f:
        for satir in f:
            p = satir.rstrip("\n").split("\t")
            if len(p) < 4:
                continue
            sure, ayet, kelime, _ = p[0].split(":")
            lem = re.search(r"LEM:([^|]+)", p[3])
            parcalar.setdefault((int(sure), int(ayet), int(kelime)), []).append(
                (p[1], lem.group(1) if lem else "")
            )

    kelimeler = {}
    for (sure, ayet, _), kisimlar in parcalar.items():
        ar = "".join(form for form, _ in kisimlar)
        lemmalar = [lem for _, lem in kisimlar if lem]
        tr = ""
        for lem in reversed(lemmalar):
            if lem in sozluk:
                tr = sozluk[lem]
                break
        kelimeler.setdefault((sure, ayet), []).append(
            {"ar": ar, "tr": tr, "lem": lemmalar[-1] if lemmalar else ""}
        )
    return kelimeler


def kapsam(kelimeler):
    """Anlamı bulunan kelime oranını döndürür: (bulunan, toplam)."""
    toplam = sum(len(v) for v in kelimeler.values())
    bulunan = sum(1 for v in kelimeler.values() for k in v if k["tr"])
    return bulunan, toplam
