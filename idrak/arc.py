"""
idrak/arc.py - ARC-AGI-2 Veri Yükleyici ve Geometrik Dönüşümler
"""

import os
import json
import glob
from typing import List, Dict, Any, Tuple, Optional


def arc_gorev_yukle(gorev_id: str, set_adi: str = "training") -> Optional[Dict[str, Any]]:
    yol = f"idrak/veri/arc_agi_2/{set_adi}/{gorev_id}.json"
    if not os.path.exists(yol):
        return None
    with open(yol, "r", encoding="utf-8") as f:
        return json.load(f)


def d4_donusumleri(izgara: List[List[int]]) -> Dict[str, List[List[int]]]:
    """D4 Dihedral Grubu: 8 Simetri Dönüşümü"""
    R = len(izgara)
    C = len(izgara[0]) if R > 0 else 0

    # 1. Özdeşlik
    I = [row[:] for row in izgara]

    # 2. Döndür 90 derece saat yönü
    rot90 = [[izgara[R - 1 - r][c] for r in range(R)] for c in range(C)]

    # 3. Döndür 180 derece
    rot180 = [[izgara[R - 1 - r][C - 1 - c] for c in range(C)] for r in range(R)]

    # 4. Döndür 270 derece
    rot270 = [[izgara[r][C - 1 - c] for r in range(R)] for c in range(C)]

    # 5. Yatay Ayna
    yatay_ayna = [row[::-1] for row in izgara]

    # 6. Dikey Ayna
    dikey_ayna = izgara[::-1]

    # 7. Esas Köşegen Devrik (Transpose)
    devrik = [[izgara[r][c] for r in range(R)] for c in range(C)]

    # 8. Yan Köşegen Devrik
    yan_devrik = [[izgara[R - 1 - r][C - 1 - c] for r in range(R)] for c in range(C)]

    return {
        "D4:ozdeslik": I,
        "D4:don90": rot90,
        "D4:don180": rot180,
        "D4:don270": rot270,
        "D4:yatay_ayna": yatay_ayna,
        "D4:dikey_ayna": dikey_ayna,
        "D4:devrik": devrik,
        "D4:yan_devrik": yan_devrik
    }


def izgara_esit_mi(g1: List[List[int]], g2: List[List[int]]) -> bool:
    if len(g1) != len(g2):
        return False
    for r1, r2 in zip(g1, g2):
        if r1 != r2:
            return False
    return True


if __name__ == "__main__":
    ornek = [[1, 2], [3, 4]]
    donusumler = d4_donusumleri(ornek)
    print(f"[idrak.arc] D4 Simetri Sayısı: {len(donusumler)}")
    print(f"  Özdeşlik: {donusumler['D4:ozdeslik']}")
    print(f"  Dön 90:   {donusumler['D4:don90']}")
    print(f"  Yatay Ayna: {donusumler['D4:yatay_ayna']}")
