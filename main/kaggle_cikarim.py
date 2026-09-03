"""
KÜLLÎ DİMAĞ -- KAGGLE ÇIKARIM VE TESLİMAT NAZIRI
Dosya: main/kaggle_cikarim.py

Vazifesi:
  Kaggle test kümesini okur; Fubini-Study ağaç okumasıyla her göreve
  hüküm verir; ``submission.json`` teslimat dosyasını üretir.

===================================================================
YARIŞMA HÜKMÜ İLE KÜTÜK HÜKMÜ AYRI ŞEYDİR -- İKİSİ DE BURADA
===================================================================

Kütüğün doktrini (H10/H16) **sebebi söylenebilen sükût**tur: bilmiyorsan
sus. ARC yarışmasının puanlamasında ise **yanlış cevabın cezası yoktur**;
susmak, yanlış cevaptan daha iyi değildir.

İkisi çelişir ve çelişki gizlenmez: ``teslimat`` kipi ``asgari_disarida
= 0.0`` ile koşar, yani **hiçbir görevi boş bırakmaz**; ``kütük`` kipi
eşiği ``1.0``da tutar. Hangisinin koşacağı bir **ölçü kararıdır** ve
ölçüyü kullanıcı koyar (hüküm E). Ölçülmüş cetvel::

    training (200 görev)   eşik 1,00 →   1 cevap,  1 TAM (%100,0)
                           eşik 0,00 → 182 cevap,  5 TAM (%2,7)
    evaluation (120 görev) her eşikte TAM = 0

Teslimatta boş bırakmamak **daha çok TAM** getiriyor (5 > 1); onun için
teslimat kipinin varsayılanı ``0.0``dır. Bu, kütüğün doktrinini
nakzetmez -- ayrı bir gayeye ayrı bir ölçü koyar ve ikisi yan yana durur.

**Cevap üretilemeyen görevde ne olur.** Dalga hiç kurulamazsa (ebat
kanunu tutmuyorsa) girdinin kendisi teslim edilir ve o görev
``boş_bırakılmadı_fakat_dalga_yok`` diye **sayılır**. Uydurma bir ızgara
basıp "çözdüm" dememek için bu sayı raporda ayrı durur.
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import Dict, List, Optional, Tuple

import numpy as np

from main.cikarim import KulliHukumMotoru, dalga_kur

__all__ = ["test_gorevlerini_oku", "gorev_cevabi_uret",
           "kaggle_teslimat_dosyasi_uret"]


def test_gorevlerini_oku(yol: str) -> Tuple[Dict[str, object], bool]:
    """``(görevler, hakikî_mi)`` -- dosya yoksa sentetiğe düşer ve söyler."""
    if os.path.isfile(yol):
        with open(yol, "r", encoding="utf-8") as f:
            return json.load(f), True
    rng = np.random.default_rng(0)
    ornek = {
        "sentetik_001": {
            "train": [{"input": rng.integers(0, 5, (3, 3)).tolist(),
                       "output": rng.integers(0, 5, (3, 3)).tolist()}
                      for _ in range(3)],
            "test": [{"input": rng.integers(0, 5, (3, 3)).tolist()}],
        }
    }
    return ornek, False


def _cift_cikar(gorev: object) -> Tuple[List, List]:
    """ARC JSON'undan ``(şahit çiftleri, sınama girdileri)``."""
    if isinstance(gorev, dict):
        egt = [(np.asarray(c["input"], int), np.asarray(c["output"], int))
               for c in gorev.get("train", []) if "output" in c]
        sin = [np.asarray(c["input"], int) for c in gorev.get("test", [])]
        return egt, sin
    egt, sin = [], []
    for c in (gorev or []):
        if isinstance(c, dict) and "input" in c:
            if "output" in c:
                egt.append((np.asarray(c["input"], int),
                            np.asarray(c["output"], int)))
            else:
                sin.append(np.asarray(c["input"], int))
    return egt, sin


def gorev_cevabi_uret(gorev: object, devir: int = 120
                      ) -> Tuple[List[np.ndarray], str]:
    """Bir görevin bütün sınama girdilerine cevap üret.

    Dönen ``izah`` şudur: ``dalga`` (öğrenilen ağırlıktan okundu) yahut
    ``dalga_yok`` (kanun kurulamadı, girdi aynen teslim edildi). İkisi
    ayrı sayılır ki teslimat sayısı çözüm sanılmasın.
    """
    egt, sin = _cift_cikar(gorev)
    if not sin:
        return [], "sınama yok"
    d = dalga_kur(egt, devir=int(devir)) if egt else None
    if d is None:
        return [np.asarray(g, int) for g in sin], "dalga_yok"
    cevap = []
    for g in sin:
        r = d.oku(g)
        cevap.append(np.asarray(g, int) if r is None else r[0])
    return cevap, "dalga"


def kaggle_teslimat_dosyasi_uret(
        model_agirlik_yolu: Optional[str] = None,
        test_veri_yolu: str = ("/kaggle/input/arc-prize-2026/"
                               "arc-agi_test_challenges.json"),
        cikti_json_yolu: str = "/kaggle/working/submission.json",
        devir: int = 120) -> str:
    """Teslimat dosyasını üret ve **muhasebesini** bas."""
    print("=== KAGGLE TESLİMAT VE ÇIKARIM NAZIRI ===", flush=True)
    t0 = time.perf_counter()

    gorevler, hakiki = test_gorevlerini_oku(test_veri_yolu)
    if not hakiki:
        print("  [İHTAR] Test dosyası bulunamadı (%s); SENTETİK mini-test "
              "koşuluyor. Bu bir teslimat değildir." % test_veri_yolu,
              flush=True)

    if model_agirlik_yolu and os.path.isfile(model_agirlik_yolu):
        KulliHukumMotoru(model_agirlik_yolu)     # mührü doğrula ve bildir

    teslimat: Dict[str, List[Dict[str, List[List[int]]]]] = {}
    toplam = len(gorevler)
    dalgali = dalgasiz = 0

    for idx, (gid, gorev) in enumerate(gorevler.items()):
        cevaplar, izah = gorev_cevabi_uret(gorev, devir=devir)
        if izah == "dalga":
            dalgali += 1
        elif izah == "dalga_yok":
            dalgasiz += 1
        teslimat[str(gid)] = [
            {"attempt_1": np.asarray(c, int).tolist(),
             "attempt_2": np.asarray(c, int).tolist()} for c in cevaplar]
        if (idx + 1) % 10 == 0 or (idx + 1) == toplam:
            print("  [%04d/%04d] mühürlendi (dalga %d, dalgasız %d)"
                  % (idx + 1, toplam, dalgali, dalgasiz), flush=True)

    dizin = os.path.dirname(cikti_json_yolu)
    if dizin:
        os.makedirs(dizin, exist_ok=True)
    with open(cikti_json_yolu, "w", encoding="utf-8") as f:
        json.dump(teslimat, f)

    sure = time.perf_counter() - t0
    s = ["", "=== TESLİMAT MUHASEBESİ ===", "",
         "  görev              : %d" % toplam,
         "  dalgadan okunan    : %d" % dalgali,
         "  dalga kurulamayan  : %d  (girdi aynen teslim edildi)" % dalgasiz,
         "  dosya              : %s" % cikti_json_yolu,
         "  süre               : %.2f sn" % sure, "",
         "  HAD: 'dalga kurulamayan' satırı bir ÇÖZÜM DEĞİLDİR; boş",
         "  bırakmamak için girdi teslim edilmiştir ve ayrı sayılmıştır."]
    if not hakiki:
        s += ["", "  BU KOŞU SENTETİKTİR; hakikî teslimat değildir."]
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    agirlik = sys.argv[1] if len(sys.argv) > 1 else \
        "/kaggle/working/kulli_dimag_kaggle_final.npy"
    test = sys.argv[2] if len(sys.argv) > 2 else \
        "/kaggle/input/arc-prize-2026/arc-agi_test_challenges.json"
    cikti = sys.argv[3] if len(sys.argv) > 3 else \
        "/kaggle/working/submission.json"
    print(kaggle_teslimat_dosyasi_uret(agirlik, test, cikti))
