#!/usr/bin/env python3
import csv
import glob
import os
import re
import sys

MUHURLER = {"kadîm", "teklif", "şüpheli"}
SUTUNLAR = ["kimlik", "ingilizce", "osmanlica", "muhur", "delil", "izah"]
YASAK_PARCALAR = ["itis", "ozis", "ektomi", "skopi", "grafi", "loji", "terapi", "plazi", "trofi",
                  "fobi", "emi ", "algi", "nöro", "kardiyo", "gastro", "hepato", "dermato", "onko",
                  "hemato", "artro", "osteo", "pnömo", "nefro", "bakteri", "virüs", "hormon", "enzim",
                  "protein", "gen ", "kromozom", "hücre zarı"]


def yari_latince_mi(metin):
    m = " " + (metin or "").casefold() + " "
    return [p.strip() for p in YASAK_PARCALAR if p in m]


def karsiliklari_oku(klasor, uyarilar=None):
    satirlar = []
    hatalar = []
    for yol in sorted(glob.glob(os.path.join(klasor, "*.tsv"))):
        ad = os.path.basename(yol)
        with open(yol, encoding="utf-8", newline="") as f:
            for no, s in enumerate(csv.reader(f, delimiter="\t"), 1):
                if not s or not "".join(s).strip() or s[0].startswith("#"):
                    continue
                if s[:len(SUTUNLAR)] == SUTUNLAR:
                    continue
                if len(s) < 4:
                    hatalar.append(f"{ad}:{no}: sütun eksik")
                    continue
                s = (s + [""] * len(SUTUNLAR))[:len(SUTUNLAR)]
                k = dict(zip(SUTUNLAR, [x.strip() for x in s]))
                k["dosya"], k["satir"] = ad, no
                if k["muhur"] not in MUHURLER:
                    hatalar.append(f"{ad}:{no}: mühür tanınmadı: {k['muhur']!r}")
                if k["muhur"] == "kadîm" and not k["delil"]:
                    hatalar.append(f"{ad}:{no}: kadîm mühürlü karşılığın delili yok")
                if not k["osmanlica"]:
                    hatalar.append(f"{ad}:{no}: Osmanlıca karşılık boş")
                bulunan = yari_latince_mi(k["osmanlica"])
                if bulunan and uyarilar is not None:
                    uyarilar.append(f"{ad}:{no}: {k['osmanlica']!r} içinde yarı Latince şüphesi: {', '.join(bulunan)}")
                satirlar.append(k)
    if hatalar:
        raise SystemExit("Karşılık dosyalarında hata:\n" + "\n".join(hatalar))
    return satirlar


if __name__ == "__main__":
    klasor = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "karsiliklar")
    u = []
    s = karsiliklari_oku(klasor, u)
    print(f"{len(s)} karşılık okundu.")
    for x in u:
        print("UYARI:", x)
