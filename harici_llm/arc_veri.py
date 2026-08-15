import json
import os
import random
from typing import Any, Dict, List, Optional, Tuple

Grid = List[List[int]]
Cift = Tuple[Grid, Grid]

KAGGLE_KOK = "/kaggle/input/competitions/arc-prize-2026-arc-agi-2"

YOLLAR = {
    "test_challenges": os.path.join(KAGGLE_KOK, "arc-agi_test_challenges.json"),
    "eval_challenges": os.path.join(KAGGLE_KOK, "arc-agi_evaluation_challenges.json"),
    "eval_solutions": os.path.join(KAGGLE_KOK, "arc-agi_evaluation_solutions.json"),
    "train_challenges": os.path.join(KAGGLE_KOK, "arc-agi_training_challenges.json"),
    "train_solutions": os.path.join(KAGGLE_KOK, "arc-agi_training_solutions.json"),
}


def json_oku(yol: str) -> Dict[str, Any]:
    with open(yol, "r", encoding="utf-8") as f:
        return json.load(f)


def gorev_yukle(task_id: str, yollar: Dict[str, str] = YOLLAR) -> Dict[str, Any]:

    for chal_key, sol_key in (("train_challenges", "train_solutions"), ("eval_challenges", "eval_solutions")):
        chal_yolu = yollar[chal_key]
        if not os.path.isfile(chal_yolu):
            continue
        challenges = json_oku(chal_yolu)
        if task_id not in challenges:
            continue
        gorev = dict(challenges[task_id])
        sol_yolu = yollar.get(sol_key)
        if sol_yolu and os.path.isfile(sol_yolu):
            solutions = json_oku(sol_yolu)
            if task_id in solutions:
                cozumler = solutions[task_id]
                for i, cikti in enumerate(cozumler):
                    if i < len(gorev.get("test", [])):
                        gorev["test"][i]["output"] = cikti
        return gorev

    chal_yolu = yollar["test_challenges"]
    challenges = json_oku(chal_yolu)
    if task_id in challenges:
        return dict(challenges[task_id])

    raise KeyError(f"Görev bulunamadı hiçbir dosyada: {task_id}")


def tum_test_gorevlerini_yukle(yollar: Dict[str, str] = YOLLAR) -> Dict[str, Any]:
    return json_oku(yollar["test_challenges"])


def izgarayi_metne_cevir(grid: Grid) -> str:
    return "\n".join(" ".join(str(hucre) for hucre in satir) for satir in grid)


def metni_izgaraya_cevir(metin: str) -> Optional[Grid]:

    satirlar = [s.strip() for s in metin.strip().splitlines() if s.strip()]
    if not satirlar:
        return None
    grid: Grid = []
    genislik = None
    for satir in satirlar:
        parcalar = satir.replace(",", " ").split()
        try:
            sayilar = [int(p) for p in parcalar]
        except ValueError:
            return None
        if not sayilar or any(s < 0 or s > 9 for s in sayilar):
            return None
        if genislik is None:
            genislik = len(sayilar)
        elif len(sayilar) != genislik:
            return None
        grid.append(sayilar)
    return grid if grid else None


def _dondur_90(grid: Grid) -> Grid:
    return [list(satir) for satir in zip(*grid[::-1])]


def _yatay_ayna(grid: Grid) -> Grid:
    return [list(reversed(satir)) for satir in grid]


def _renk_permutasyonu_uygula(grid: Grid, esleme: Dict[int, int]) -> Grid:
    return [[esleme.get(hucre, hucre) for hucre in satir] for satir in grid]


def _rastgele_renk_eslemesi(rng: random.Random) -> Dict[int, int]:
    renkler = list(range(10))
    karisik = renkler[1:]
    rng.shuffle(karisik)
    esleme = {0: 0}
    for orijinal, yeni in zip(renkler[1:], karisik):
        esleme[orijinal] = yeni
    return esleme


def gorev_ciftlerini_cikar(gorev: Dict[str, Any]) -> List[Cift]:
    return [(ornek["input"], ornek["output"]) for ornek in gorev.get("train", [])]


def veri_cogalt(ciftler: List[Cift], hedef_adet: int = 50, tohum: int = 42) -> List[Cift]:

    if not ciftler:
        return []

    rng = random.Random(tohum)
    donusumler = [
        lambda g: g,
        _dondur_90,
        lambda g: _dondur_90(_dondur_90(g)),
        lambda g: _dondur_90(_dondur_90(_dondur_90(g))),
        _yatay_ayna,
        lambda g: _yatay_ayna(_dondur_90(g)),
    ]

    sonuc: List[Cift] = []
    while len(sonuc) < hedef_adet:
        for girdi, cikti in ciftler:
            if len(sonuc) >= hedef_adet:
                break
            donusum = rng.choice(donusumler)
            g_donusmus = donusum(girdi)
            c_donusmus = donusum(cikti)
            if rng.random() < 0.5:
                esleme = _rastgele_renk_eslemesi(rng)
                g_donusmus = _renk_permutasyonu_uygula(g_donusmus, esleme)
                c_donusmus = _renk_permutasyonu_uygula(c_donusmus, esleme)
            sonuc.append((g_donusmus, c_donusmus))

    return sonuc[:hedef_adet]
