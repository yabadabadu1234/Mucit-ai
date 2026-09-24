"""
idrak/cozucu.py - Doğrulanabilir ARC Çözücüsü ("Ya İspat Ya Sükût")
Nefs-i Müdrike Mimarîsi
"""

import os
import glob
from typing import List, Dict, Any, Optional, Tuple
from idrak.arc import d4_donusumleri, izgara_esit_mi, arc_gorev_yukle
from nefs.mukayese import MukayeseMotoru, OntoMertebe
from matematik.temel import KuantumDurum


class DogrulanabilirCozucu:
    """
    ARC-AGI-2 Çözücü:
    Bir aday, görevin bütün gösterim çiftlerini tam tutmadıkça kullanılmaz;
    tutan aday yoksa CEVAP VERİLMEZ (Sükût edilir).
    """
    def __init__(self, d: int = 16):
        self.mukayese = MukayeseMotoru(d=d)

    def coz_gorev(self, gorev: Dict[str, Any]) -> Dict[str, Any]:
        train_pairs = gorev.get("train", [])
        test_pairs = gorev.get("test", [])

        if not train_pairs or not test_pairs:
            return {"cozuldu": False, "sebep": "Girdi eksik", "cevap": None}

        # Kural Adayları: D4 Dihedral Simetrileri
        kural_adaylari = [
            "D4:ozdeslik", "D4:don90", "D4:don180", "D4:don270",
            "D4:yatay_ayna", "D4:dikey_ayna", "D4:devrik", "D4:yan_devrik"
        ]

        tutan_kural = None
        for kural_adi in kural_adaylari:
            hepsi_tuttu = True
            for pair in train_pairs:
                inp = pair["input"]
                out = pair["output"]
                donusmus = d4_donusumleri(inp).get(kural_adi)
                if not donusmus or not izgara_esit_mi(donusmus, out):
                    hepsi_tuttu = False
                    break

            if hepsi_tuttu:
                tutan_kural = kural_adi
                break

        if tutan_kural:
            # Test çıktısını üret
            test_inp = test_pairs[0]["input"]
            tahmin = d4_donusumleri(test_inp)[tutan_kural]
            return {
                "cozuldu": True,
                "kural": tutan_kural,
                "tahmin": tahmin,
                "sukut": False,
                "aciklama": f"Kural '{tutan_kural}' bütün {len(train_pairs)} eğitim çiftinde %100 doğrulandı."
            }
        else:
            return {
                "cozuldu": False,
                "kural": None,
                "tahmin": None,
                "sukut": True,
                "aciklama": "Bütün çiftleri sağlayan kat'î kural bulunamadı; sükût edildi (Fermân 1-T: Ya İspat Ya Sükût)."
            }


if __name__ == "__main__":
    cozucu = DogrulanabilirCozucu()
    test_gorev = {
        "train": [
            {"input": [[1, 2], [3, 4]], "output": [[2, 1], [4, 3]]},
            {"input": [[5, 6], [7, 8]], "output": [[6, 5], [8, 7]]}
        ],
        "test": [
            {"input": [[9, 0], [1, 2]]}
        ]
    }
    sonuc = cozucu.coz_gorev(test_gorev)
    print(f"[idrak.cozucu] Çözüldü mü: {sonuc['cozuldu']}")
    print(f"  Kural: {sonuc['kural']}")
    print(f"  Tahmin: {sonuc['tahmin']}")
    print(f"  Açıklama: {sonuc['aciklama']}")
