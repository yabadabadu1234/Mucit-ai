import os, sys, json, math, hashlib, urllib.request
from pathlib import Path
import numpy as np
import networkx as nx
import kok_sayfasi as ks

CIKTI = Path(__file__).resolve().parent / "kaynak" / "lugat" / "pilot" / "kategori"
CIKTI.mkdir(parents=True, exist_ok=True)
ONBELLEK = Path(os.environ.get("EVREN_ONBELLEK", "/tmp/evren_gomme.json"))
KOKLER = ["صبر", "شكر", "رضو", "وكل", "خوف", "رجو", "حمد", "وقي", "كفر", "ظلم", "عدل", "هدي", "غفر"]
AD = {"صبر": "sabır", "شكر": "şükür", "رضو": "rızâ", "وكل": "tevekkül", "خوف": "havf", "رجو": "recâ",
      "حمد": "hamd", "وقي": "takvâ", "كفر": "küfür", "ظلم": "zulüm", "عدل": "adl", "هدي": "hidâyet", "غفر": "mağfiret"}
KOTA = 40


def ornekle(liste, n):
    if len(liste) <= n:
        return liste
    return [liste[int(i * len(liste) / n)] for i in range(n)]


def gom(metinler):
    onb = json.loads(ONBELLEK.read_text()) if ONBELLEK.exists() else {}
    eksik = [m for m in metinler if hashlib.md5(m.encode()).hexdigest() not in onb]
    anahtar = os.environ["EVREN_ANAHTAR"]
    for i in range(0, len(eksik), 32):
        grup = eksik[i:i + 32]
        istek = urllib.request.Request("https://evren-llmapi.ssyz.org.tr/v1/embeddings",
            data=json.dumps({"model": "qwen3-embedding-8b", "input": grup}).encode(),
            headers={"X-API-Key": anahtar, "Content-Type": "application/json"})
        with urllib.request.urlopen(istek, timeout=300) as y:
            d = json.load(y)["data"]
        for m, e in zip(grup, d):
            onb[hashlib.md5(m.encode()).hexdigest()] = e["embedding"]
        ONBELLEK.write_text(json.dumps(onb))
    return np.array([onb[hashlib.md5(m.encode()).hexdigest()] for m in metinler])


def bulutlar():
    onb, bul = {}, {}
    for k in KOKLER:
        _, gecis = ks.morfoloji_oku(k)
        sec = ornekle(gecis, KOTA)
        met = [ks.meal_oku(s, a, onb) for s, a in sec]
        bul[k] = [(s, a, t) for (s, a), t in zip(sec, met) if t]
    return bul


def yonlu_mesafe(A, B, ort):
    c = np.clip(A @ B.T, -1, 1)
    teta = np.arccos(c.max(axis=1))
    return float(teta.mean() if ort else teta.max())


def main():
    bul = bulutlar()
    tum = [t for k in KOKLER for _, _, t in bul[k]]
    E = gom(tum)
    E = E / np.linalg.norm(E, axis=1, keepdims=True)
    bulut, i = {}, 0
    for k in KOKLER:
        n = len(bul[k]); bulut[k] = E[i:i + n]; i += n
    n = len(KOKLER)
    D_ort = np.zeros((n, n)); D_max = np.zeros((n, n))
    for a, ka in enumerate(KOKLER):
        for b, kb in enumerate(KOKLER):
            D_ort[a, b] = yonlu_mesafe(bulut[ka], bulut[kb], True)
            D_max[a, b] = yonlu_mesafe(bulut[ka], bulut[kb], False)
    merkez = np.array([bulut[k].mean(axis=0) for k in KOKLER])
    merkez = merkez / np.linalg.norm(merkez, axis=1, keepdims=True)
    G = merkez @ merkez.T
    P = np.linalg.inv(G)
    d = np.sqrt(np.diag(P))
    kismi = -P / np.outer(d, d)
    np.fill_diagonal(kismi, 1.0)
    ihlal = 0; uc = 0
    for a in range(n):
        for b in range(n):
            for c in range(n):
                uc += 1
                if D_max[a, c] > D_max[a, b] + D_max[b, c] + 1e-9:
                    ihlal += 1
    ihlal_ort = 0
    for a in range(n):
        for b in range(n):
            for c in range(n):
                if D_ort[a, c] > D_ort[a, b] + D_ort[b, c] + 1e-9:
                    ihlal_ort += 1
    profil = D_ort.T
    en_yakin_profil = [int(np.argmin([np.linalg.norm(profil[a] - profil[b]) if a != b else 9e9 for b in range(n)])) for a in range(n)]
    asimetri = float(np.abs(D_ort - D_ort.T).mean() / D_ort.mean())
    G_nx = nx.Graph()
    for a in range(n):
        for b in range(a + 1, n):
            G_nx.add_edge(a, b, weight=abs(kismi[a, b]))
    agac = sorted(tuple(sorted(e)) for e in nx.maximum_spanning_tree(G_nx).edges())
    dot = ["digraph K {", ' graph [rankdir=LR, fontname="Amiri", bgcolor="transparent", splines=true, overlap=false];',
           ' node [shape=box, style="rounded,filled", fillcolor="#f4efe3", fontname="Amiri", fontsize=14];',
           ' edge [fontname="Amiri", fontsize=10];']
    for a, k in enumerate(KOKLER):
        dot.append(f' n{a} [label="{k}\\n{AD[k]}"];')
    okla = []
    for a in range(n):
        s = sorted([b for b in range(n) if b != a], key=lambda b: D_ort[a, b])
        b = s[0]
        okla.append((a, b))
        dot.append(f' n{a} -> n{b} [label="{math.degrees(D_ort[a,b]):.1f}°", color="#7a3b1d"];')
    for a, b in agac:
        dot.append(f' n{a} -> n{b} [dir=none, style=dashed, color="#2a5d7a", label="ρ={kismi[a,b]:.2f}"];')
    dot.append("}")
    (CIKTI / "kategori.dot").write_text("\n".join(dot), encoding="utf-8")
    sonuc = {"kokler": KOKLER, "ad": AD, "adet": {k: len(bul[k]) for k in KOKLER}, "model": "qwen3-embedding-8b", "boyut": int(E.shape[1]),
             "D_ort_derece": np.degrees(D_ort).round(2).tolist(), "D_max_derece": np.degrees(D_max).round(2).tolist(),
             "kismi_korelasyon": kismi.round(3).tolist(), "gram_cond": float(np.linalg.cond(G)),
             "ucgen_ihlal_max": [ihlal, uc], "ucgen_ihlal_ort": [ihlal_ort, uc], "asimetri_orani": asimetri,
             "en_yakin_ok": [[KOKLER[a], KOKLER[b]] for a, b in okla], "chow_liu": [[KOKLER[a], KOKLER[b]] for a, b in agac],
             "yoneda_en_yakin_profil": [[KOKLER[a], KOKLER[b]] for a, b in enumerate(en_yakin_profil)]}
    (CIKTI / "kategori.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: sonuc[k] for k in ["adet", "gram_cond", "ucgen_ihlal_max", "ucgen_ihlal_ort", "asimetri_orani", "en_yakin_ok", "chow_liu"]}, ensure_ascii=False))


main()
