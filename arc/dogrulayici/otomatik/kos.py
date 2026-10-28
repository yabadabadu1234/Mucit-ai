import json
import sys
from pathlib import Path

import torch

BURA = Path(__file__).resolve().parent
sys.path.insert(0, str(BURA))

import cozucu
import onkayit


def muhur_tutar_mi(kayit, arsiv):
    simdi = {
        "cozucu.py": onkayit.ozet(BURA / "cozucu.py"),
        "kos.py": onkayit.ozet(BURA / "kos.py"),
        "onkayit.py": onkayit.ozet(BURA / "onkayit.py"),
        "veri_arsivi": onkayit.ozet(arsiv),
    }
    return [k for k, v in simdi.items() if kayit[k] != v]


def dosyalar(dizin, kisim):
    return {int(p.name.split("_")[0][2:]): p for p in sorted(Path(dizin).glob("qa*_%s.txt" % kisim))}


if __name__ == "__main__":
    arsiv, dizin, kosu = sys.argv[1], sys.argv[2], sys.argv[3]
    torch.set_num_threads(1)
    kayit = json.loads((BURA / "ONKAYIT.json").read_text())
    bozuk = muhur_tutar_mi(kayit, arsiv)
    if bozuk:
        print("MÜHÜR BOZUK, PUAN VERİLMEZ:", bozuk)
        sys.exit(2)
    sema = kayit["kosular"][kosu]
    tren = [o for p in dosyalar(dizin, "train").values() for o in cozucu.ayristir(p)]
    gunluk = lambda s: print(kosu, s, flush=True)
    model, sz, uzun = cozucu.egit(tren, sema, gunluk)
    netice = {}
    for no, p in dosyalar(dizin, "test").items():
        test = cozucu.ayristir(p)
        tahmin = cozucu.cevapla(model, sz, uzun, test)
        dogru = sum(1 for t, (_, _, a) in zip(tahmin, test) if t == a)
        netice[no] = dogru / len(test)
    gecme = kayit["dis_olcu"]["gecme"]
    dusen = sorted(no for no, d in netice.items() if d < gecme)
    beklenen = set(kayit["tahmin_dusen"][kosu])
    cikti = {
        "kosu": kosu,
        "dogruluk": netice,
        "gecen": 20 - len(dusen),
        "dusen": dusen,
        "tahmin_isabet": sorted(beklenen & set(dusen)),
        "tahmin_kacan": sorted(beklenen - set(dusen)),
        "tahminsiz_dusen": sorted(set(dusen) - beklenen),
    }
    (BURA / ("NETICE_%s.json" % kosu)).write_text(json.dumps(cikti, ensure_ascii=False, indent=1))
    print(json.dumps(cikti, ensure_ascii=False))
