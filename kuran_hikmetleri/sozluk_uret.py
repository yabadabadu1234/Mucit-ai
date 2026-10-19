#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kur'ân metninden sözlük: sırayla karşılaşılan farklı kelimeler; kök, kelime türü, fiil babı ve zaman.

Kaynak: veri_harici/eyupipler/quran-morphology.txt (kelime çözümleme etiketleri).
Anlam (lugat) bu betikte üretilmez; hazır sözlük kopyalanmaz.
"""
import json
import re
from collections import OrderedDict
from pathlib import Path

BASE = Path(__file__).resolve().parent
MORFOLOJI = BASE / "veri_harici" / "eyupipler" / "quran-morphology.txt"
CIKTI = BASE / "kaynak" / "sozluk" / "kelimeler.json"
ROMEN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def yukle():
    kelimeler = OrderedDict()  # (sure, ayet, kelime_no) -> parçalar (sırayla)
    with open(MORFOLOJI, encoding="utf-8") as f:
        for satir in f:
            p = satir.rstrip("\n").split("\t")
            if len(p) < 4:
                continue
            sure, ayet, kelime, parca = p[0].split(":")
            kelimeler.setdefault((int(sure), int(ayet), int(kelime)), []).append((p[1], p[2], p[3]))
    return kelimeler


def tek_kelime(parcalar):
    yuzey = "".join(form for form, _, _ in parcalar)
    kok = next((re.search(r"ROOT:([^|]+)", etiket).group(1) for _, _, etiket in parcalar if "ROOT:" in etiket), "")
    lem = ""
    for _, _, etiket in reversed(parcalar):
        m = re.search(r"LEM:([^|]+)", etiket)
        if m and "PREF" not in etiket:
            lem = m.group(1)
            break
    vf = next((int(re.search(r"VF:(\d+)", etiket).group(1)) for _, _, etiket in parcalar if "VF:" in etiket), 0)
    zaman = next((z for _, _, etiket in parcalar for z in ("PERF", "IMPF", "IMPV") if z in etiket.split("|")), "")
    tur = parcalar[-1][1]
    return {"kelime": yuzey, "kok": kok, "lem": lem, "tur": tur,
            "bab": ROMEN[vf] if 0 < vf < len(ROMEN) else "", "zaman": zaman}


def main():
    kelimeler = yukle()
    sozluk = OrderedDict()  # yüzey -> kayıt (ilk geçtiği yerle)
    for (sure, ayet, no), parcalar in kelimeler.items():
        k = tek_kelime(parcalar)
        if k["kelime"] not in sozluk:
            k["ilk"] = f"{sure}:{ayet}"
            k["adet"] = 0
            sozluk[k["kelime"]] = k
        sozluk[k["kelime"]]["adet"] += 1
    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    CIKTI.write_text(json.dumps(list(sozluk.values()), ensure_ascii=False, indent=0), encoding="utf-8")
    toplam = sum(v["adet"] for v in sozluk.values())
    kokler = {v["kok"] for v in sozluk.values() if v["kok"]}
    print("kelime (toplam):", toplam, "| farklı yüzey:", len(sozluk), "| farklı kök:", len(kokler))
    print("kök etiketi olmayan farklı kelime:", sum(1 for v in sozluk.values() if not v["kok"]))
    print("bab dağılımı:", {b: sum(1 for v in sozluk.values() if v["bab"] == b) for b in ROMEN[1:]})


if __name__ == "__main__":
    main()
