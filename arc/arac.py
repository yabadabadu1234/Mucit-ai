import json
import os
import resource
import subprocess
import sys
import tempfile

SURE_SANIYE = 10
BELLEK_BAYT = 2 * 1024 ** 3

KUMBARA = """
import json, sys
import numpy as np
girdi = json.load(open(sys.argv[1]))
ad = {}
exec(compile(girdi["kod"], "program", "exec"), ad)
f = ad["solve"]
sonuc = []
for g in girdi["gridler"]:
    try:
        o = f(np.array(g))
        sonuc.append({"ok": True, "grid": np.asarray(o).astype(int).tolist()})
    except Exception as e:
        sonuc.append({"ok": False, "hata": type(e).__name__ + ": " + str(e)[:200]})
json.dump(sonuc, open(sys.argv[2], "w"))
"""


def _sinirla():
    resource.setrlimit(resource.RLIMIT_AS, (BELLEK_BAYT, BELLEK_BAYT))
    resource.setrlimit(resource.RLIMIT_CPU, (SURE_SANIYE, SURE_SANIYE + 2))


def calistir(kod, gridler, sure=SURE_SANIYE):
    with tempfile.TemporaryDirectory() as d:
        gi, go, gk = (os.path.join(d, x) for x in ("girdi.json", "cikti.json", "kumbara.py"))
        json.dump({"kod": kod, "gridler": gridler}, open(gi, "w"))
        open(gk, "w").write(KUMBARA)
        try:
            p = subprocess.run([sys.executable, "-I", gk, gi, go], capture_output=True, text=True, timeout=sure * max(1, len(gridler)), preexec_fn=_sinirla, cwd=d)
        except subprocess.TimeoutExpired:
            return [{"ok": False, "hata": "zaman_asimi"} for _ in gridler]
        if not os.path.exists(go):
            hata = (p.stderr or "")[-300:] or "cikti_yok"
            return [{"ok": False, "hata": hata} for _ in gridler]
        return json.load(open(go))


def sinama(kod, gorev):
    sonuc = calistir(kod, [p["input"] for p in gorev["train"]])
    rapor = []
    for p, s in zip(gorev["train"], sonuc):
        if not s["ok"]:
            rapor.append({"durum": "hata", "ayrinti": s["hata"]})
            continue
        beklenen, gelen = p["output"], s["grid"]
        if beklenen == gelen:
            rapor.append({"durum": "dogru"})
        elif len(beklenen) != len(gelen) or len(beklenen[0]) != len(gelen[0]):
            rapor.append({"durum": "boyut", "ayrinti": "beklenen %dx%d, gelen %dx%d" % (len(beklenen), len(beklenen[0]), len(gelen), len(gelen[0]))})
        else:
            yanlis = sum(a != b for ra, rb in zip(beklenen, gelen) for a, b in zip(ra, rb))
            rapor.append({"durum": "yanlis", "ayrinti": "%d hucre farkli" % yanlis})
    return {"hepsi_dogru": all(r["durum"] == "dogru" for r in rapor), "ornekler": rapor}


def test_uygula(kod, gorev):
    return calistir(kod, [t["input"] for t in gorev["test"]])
