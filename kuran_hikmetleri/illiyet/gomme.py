import os, sys, json, re, pathlib, time, urllib.request
import numpy as np
B = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(os.environ["EVREN_GOMME_DIZIN"])
OUT.mkdir(parents=True, exist_ok=True)
def gom(metin):
    istek = urllib.request.Request("https://evren-llmapi.ssyz.org.tr/v1/embeddings",
        data=json.dumps({"model": "qwen3-embedding-8b", "input": metin}).encode(),
        headers={"X-API-Key": os.environ["EVREN_ANAHTAR"], "Content-Type": "application/json"})
    for den in range(6):
        try:
            with urllib.request.urlopen(istek, timeout=300) as y:
                return [e["embedding"] for e in json.load(y)["data"]]
        except Exception:
            time.sleep(10 * (den + 1))
    raise RuntimeError("gömme alınamadı")
def toplu(ad, metinler, parca=32):
    yol = OUT / f"{ad}.npy"
    if yol.exists():
        return np.load(yol)
    M = []
    for i in range(0, len(metinler), parca):
        M += gom(metinler[i:i + parca])
        if (i // parca) % 20 == 0:
            print(ad, i, len(metinler), flush=True)
    M = np.array(M, dtype=np.float32)
    M /= np.linalg.norm(M, axis=1, keepdims=True)
    np.save(yol, M)
    return M
if __name__ == "__main__":
    kok = json.load(open(B / "kaynak/lugat/kok_anlamlari.json", encoding="utf-8"))
    kmet = [f"{x['kok']}: {x['turkce']}" for x in kok]
    json.dump([x["kok"] for x in kok], open(OUT / "kokler.json", "w", encoding="utf-8"), ensure_ascii=False)
    toplu("kok", kmet)
    ay, anahtar = [], []
    for s in range(1, 115):
        d = json.load(open(B / f"kaynak/sure/{s}.json", encoding="utf-8"))
        for v in d["verses"]:
            t = v["turkish"]
            if isinstance(t, str):
                t = eval(t) if t.startswith("{") else {"x": t}
            m = re.sub(r"<[^>]+>", "", t.get("diyanet_vakfi") or next(iter(t.values())) or "")
            ay.append(m); anahtar.append(f"{s}:{v['verseNumber']}")
    json.dump(anahtar, open(OUT / "ayet_anahtar.json", "w"))
    toplu("ayet", ay)
    print("bitti")
