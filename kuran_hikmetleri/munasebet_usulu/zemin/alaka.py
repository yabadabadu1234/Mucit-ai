import json
import sys
from pathlib import Path

import numpy as np

from korpus import ayetler
from vektor import Zemin

MP = Path(__file__).resolve().parents[1]

OLUMSUZ = {
    "I1d": "Muhatabın adı bilinmesin.",
    "I1a": "Muhatabın bütün âlemleri terbiye edip yönettiği bilinmesin.",
    "I1b": "Muhatabın merhameti bilinmesin.",
    "I1c": "Yolun karşılığının ve hesabın muhatapta olduğu bilinmesin.",
    "H1": "Takdir ve şükran duygusu yaşanmasın.",
    "H2": "Merhamete güven ve ümit duyulmasın.",
    "H3": "Hesaba karşı haşyet ve ciddiyet duyulmasın.",
    "I2": "Muhatabın övgüye lâyık olduğunu kabul etmesin.",
    "I3a": "Yalnız muhataba yönelme ikrarı yapılmasın.",
    "I3b": "Kendi aczini, yalnız muhataptan yardım istemekle beyan etmesin.",
    "I5": "Hidayet talebini açıkça ifade etmesin.",
    "I4a": "Yolun olumlu tarifi nimet verilenlerin yolu olmasın.",
    "I4b": "Gazaba uğrayanlar yolu kaçırmış olmasın.",
    "I4c": "Sapanlar yolu kaçırmış olmasın.",
    "I6": "Talebin karşılığının ne ve nereden geleceği bilinmesin.",
}


def hedefler(d):
    sonuc = {}
    for k in d["kararlar"]:
        ay = {tuple(int(x) for x in r.split(":")[0:1] + [r.split(":")[1].rstrip("abc")]) for r in k["karsilik"]}
        for i in k["ihtiyac"]:
            sonuc.setdefault(i, set()).update(ay)
    return sonuc


def sual(metin):
    return "Sual: " + metin + "\nCevap: "


def main():
    d = json.load(open(MP / "FATIHA_KARARLAR.json", encoding="utf-8"))
    ihtiyac = {i["id"]: i for i in d["ihtiyaclar"]}
    hed = hedefler(d)
    ay = ayetler()
    aday = [(1, a) for a in range(1, 8)] + [(2, 2)]
    metin = {r: " ".join(ay[r]) for r in aday}
    z = Zemin()
    taban = {r: z.loglik("Cevap: ", metin[r]) for r in aday}
    pmi = {}
    pmi_olumsuz = {}
    for i in hed:
        for r in aday:
            pmi[(i, r)] = z.loglik(sual(ihtiyac[i]["icerik"]), metin[r]) - taban[r]
            pmi_olumsuz[(i, r)] = z.loglik(sual(OLUMSUZ[i]), metin[r]) - taban[r]
    isabet = 0
    sira_toplam = 0.0
    beklenen = 0.0
    ihlal = 0
    farklar = []
    for i, A in hed.items():
        puan = sorted(aday, key=lambda r: -pmi[(i, r)])
        ilk = puan[0]
        sira = min(puan.index(r) + 1 for r in A)
        isabet += ilk in A
        sira_toplam += 1 / sira
        beklenen += len(A) / len(aday)
        for r in A:
            farklar.append(pmi[(i, r)] - pmi_olumsuz[(i, r)])
        ihlal += sum(pmi[(i, r)] <= pmi_olumsuz[(i, r)] for r in A)
        print(i, "hedef", sorted(A), "ilk", ilk, "sira", sira, "pmi_hedef", [round(pmi[(i, r)], 1) for r in sorted(A)])
    n = len(hed)
    print("ihtiyac", n, "aday", len(aday))
    print("top1", isabet, "/", n, "tesadüf beklentisi", round(beklenen, 2))
    print("MRR", round(sira_toplam / n, 3))
    print("olumsuzlama: PMI(ihtiyac) > PMI(olumsuz) olmayan (ihtiyac,ayet) cifti", ihlal, "/", len(farklar), "ortalama fark", round(float(np.mean(farklar)), 2))
    np.save(MP / "zemin" / ".pmi_fatiha.npy", np.array([[pmi[(i, r)] for r in aday] for i in hed]))


if __name__ == "__main__":
    main()
