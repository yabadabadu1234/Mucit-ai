import collections
from pathlib import Path

KOK = Path(__file__).resolve().parents[2]
MORFOLOJI = KOK / "veri_harici" / "eyupipler" / "quran-morphology.txt"


def ayetler():
    sonuc = collections.OrderedDict()
    for satir in open(MORFOLOJI, encoding="utf-8"):
        p = satir.rstrip("\n").split("\t")
        if len(p) < 2:
            continue
        s, a, k, _ = p[0].split(":")
        sonuc.setdefault((int(s), int(a)), collections.OrderedDict()).setdefault(int(k), []).append(p[1])
    return collections.OrderedDict((ref, ["".join(v) for v in kel.values()]) for ref, kel in sonuc.items())


def sureler():
    d = collections.OrderedDict()
    for (s, a), kel in ayetler().items():
        d.setdefault(s, []).append((a, kel))
    return d
