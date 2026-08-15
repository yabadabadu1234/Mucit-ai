from typing import Any, Callable, Dict, List, Optional, Tuple

from arc_prompt import SISTEM_PROMPTU, gorev_kullanici_promptu_olustur, ttt_egitim_metni_olustur
from arc_veri import Cift, Grid, gorev_ciftlerini_cikar, veri_cogalt
from kod_ajani import kodu_egitim_ornekleriyle_dogrula, kodu_guvenle_calistir, kodu_metinden_cikar

BOS_TAHMIN: Grid = [[0, 0], [0, 0]]

UretFn = Callable[[Any, Any, str, str, float, bool], str]
IneAyarFn = Callable[[Any, Any, List[str]], List[float]]


def _tahminleri_uret_ve_dogrula(
    lora_model: Any,
    tokenizer: Any,
    task_id: str,
    train_ciftleri: List[Cift],
    test_girdisi: Grid,
    uret_fn: UretFn,
    azami_deneme: int = 6,
) -> List[Grid]:

    kullanici_promptu = gorev_kullanici_promptu_olustur(task_id, train_ciftleri, test_girdisi)

    dogrulanmis_tahminler: List[Grid] = []
    denenmis_kodlar: set = set()

    for deneme_no in range(azami_deneme):
        if len(dogrulanmis_tahminler) >= 2:
            break

        model_ciktisi = uret_fn(
            lora_model, tokenizer, SISTEM_PROMPTU, kullanici_promptu,
            0.2 if deneme_no == 0 else 0.8, deneme_no > 0,
        )
        kod = kodu_metinden_cikar(model_ciktisi)
        if kod is None or kod in denenmis_kodlar:
            continue
        denenmis_kodlar.add(kod)

        if not kodu_egitim_ornekleriyle_dogrula(kod, train_ciftleri):
            continue

        basarili, sonuc = kodu_guvenle_calistir(kod, test_girdisi)
        if basarili and isinstance(sonuc, list):
            dogrulanmis_tahminler.append(sonuc)

    return dogrulanmis_tahminler


def gorevi_coz(
    lora_model: Any,
    tokenizer: Any,
    task_id: str,
    gorev: Dict[str, Any],
    uret_fn: UretFn,
    ince_ayar_fn: Optional[IneAyarFn] = None,
    cogaltma_hedefi: int = 50,
    ttt_adim_sayisi: int = 20,
) -> List[Dict[str, Grid]]:

    train_ciftleri = gorev_ciftlerini_cikar(gorev)

    if ince_ayar_fn is not None and train_ciftleri:
        cogaltilmis = veri_cogalt(train_ciftleri, hedef_adet=cogaltma_hedefi)
        egitim_metinleri = [
            ttt_egitim_metni_olustur(task_id, girdi, cikti) for girdi, cikti in cogaltilmis
        ]
        ince_ayar_fn(lora_model, tokenizer, egitim_metinleri)

    sonuclar: List[Dict[str, Grid]] = []
    for test_ornegi in gorev.get("test", []):
        test_girdisi = test_ornegi["input"]

        tahminler = _tahminleri_uret_ve_dogrula(
            lora_model, tokenizer, task_id, train_ciftleri, test_girdisi, uret_fn
        )

        attempt_1 = tahminler[0] if len(tahminler) >= 1 else BOS_TAHMIN
        attempt_2 = tahminler[1] if len(tahminler) >= 2 else attempt_1

        sonuclar.append({"attempt_1": attempt_1, "attempt_2": attempt_2})

    return sonuclar
