"""Yarışma eğitim setinden doğrulanmış görev kayıtlarını üretir (Kaggle CPU kernel'inde koşar).

Her görev: F2P/P2P türetilir (swe_dogrula.f2p_p2p_turet; altın yama ve test yaması koşar).
Başarılı görevler verified.jsonl'e yazılır; başarısızlar sebebiyle hatalar.jsonl'e yazılır.
Hiçbir görev sessizce atlanmaz: çıktı sayıları (doğrulanan + hata = toplam) raporlanır.

Ortam değişkenleri:
  YARISMA_TASKS      tasks.jsonl yolu
  SWE_SNAPSHOTS      snapshots klasörü (<instance_id>.tgz)
  YARISMA_WHEELS     wheels klasörü
  YARISMA_DOCKER     imp.py / telnetlib.py klasörü
  YARISMA_OUT        çıktı klasörü (varsayılan /kaggle/working/uretim)
  YARISMA_LIMIT      (isteğe bağlı) ilk N görev; sınama için
"""
import json
import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swe_dogrula as S  # noqa: E402
from swe_dogrula import EnvHatasi  # noqa: E402


def main():
    tasks_yol = os.environ["YARISMA_TASKS"]
    cikti = os.environ.get("YARISMA_OUT", "/kaggle/working/uretim")
    limit = int(os.environ.get("YARISMA_LIMIT", "0"))
    os.makedirs(cikti, exist_ok=True)
    with open(tasks_yol, encoding="utf-8") as f:
        gorevler = [json.loads(s) for s in f if s.strip()]
    if limit:
        gorevler = gorevler[:limit]

    dogrulanan, hatalar = [], []
    yol_dogrulanan = os.path.join(cikti, "verified.jsonl")
    yol_hata = os.path.join(cikti, "hatalar.jsonl")
    t0 = time.time()
    with open(yol_dogrulanan, "w", encoding="utf-8") as fd, open(yol_hata, "w", encoding="utf-8") as fh:
        for i, g in enumerate(gorevler, 1):
            kimlik = g["instance_id"]
            t = time.time()
            try:
                sonuc = S.f2p_p2p_turet(g, None, 900)
                satir = {
                    "instance_id": kimlik,
                    "repo": g["repo"],
                    "base_commit": g["base_commit"],
                    "prompt": g["problem_statement"],
                    "hints_text": g.get("hints_text") or "",
                    "patch": g["patch"],
                    "test_patch": g["test_patch"],
                    "FAIL_TO_PASS": sonuc["FAIL_TO_PASS"],
                    "PASS_TO_PASS": sonuc["PASS_TO_PASS"],
                    "ortam": sonuc["ortam"],
                    "verified": True,
                }
                fd.write(json.dumps(satir, ensure_ascii=False) + "\n")
                fd.flush()
                dogrulanan.append(kimlik)
                durum = "tamam"
            except Exception as e:  # noqa: BLE001 -- her hata kayda geçer; sessiz ikame yok
                tur = "EnvHatasi" if isinstance(e, EnvHatasi) else type(e).__name__
                hata = {"instance_id": kimlik, "repo": g["repo"], "tur": tur,
                        "ileti": str(e)[:600], "iz": traceback.format_exc(limit=3)[-900:]}
                fh.write(json.dumps(hata, ensure_ascii=False) + "\n")
                fh.flush()
                hatalar.append(kimlik)
                durum = tur
            print(f"[{i}/{len(gorevler)}] {kimlik}: {durum} ({time.time() - t:.0f}s)", flush=True)

    ozet = {
        "toplam": len(gorevler),
        "dogrulanan": len(dogrulanan),
        "hata": len(hatalar),
        "sure_saniye": round(time.time() - t0),
    }
    if ozet["dogrulanan"] + ozet["hata"] != ozet["toplam"]:
        raise RuntimeError(f"sayım tutmuyor: {ozet}")
    with open(os.path.join(cikti, "ozet.json"), "w", encoding="utf-8") as f:
        json.dump(ozet, f, ensure_ascii=False, indent=2)
    print("ÖZET", json.dumps(ozet, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
