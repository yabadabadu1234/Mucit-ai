"""
Gorev basina cozum dongusu: verilen kodun worker() fonksiyonundaki TTT
deseni (LoRA agirliklarini varsayilana sifirla -> augment -> ince ayar ->
degerlendir) BIREBIR korunarak, Unsloth yerine duz transformers+peft ve
Qwen-e ozgu QwenFormatter yerine model-ailesine gore genel sohbet
sablonuyla calisir. Nihai cevap, kaidesi ajan tarafindan bulunan
`submit_answer` arac cagrisiyla kaydedilir; boyut tutarsizligi varsa
kendimiz duzeltmeyiz, hatayi ajana geri donduren `araclar.py` bunu saglar.
"""
import time
from typing import Any, Dict, List, Optional

from arc import Example, Task
from arc_loader import ArcDataset, GenelSohbetBicimlendirici
from araclar import (
    CevapDefteri,
    arac_cagrilarini_ayikla,
    arac_cagrisini_yurut,
    tool_response_mesaji_olustur,
)
from arc_prompt import gorev_kullanici_promptu_olustur, sistem_promptu_olustur, ttt_egitim_metni_olustur
from ttt_lora import gorev_ozelinde_ince_ayar, uret_sohbet

BOS_TAHMIN = [[0, 0], [0, 0]]


def _task_dict_al(task: Task) -> Dict[str, Any]:
    veri = task.serialize()
    return {"train": veri["train"], "test": veri["test"]}


def _ttt_uygula(
    lora_model: Any,
    tokenizer: Any,
    model_ailesi: str,
    task: Task,
    varsayilan_lora_agirliklari: Optional[Dict[str, Any]],
    cogaltma_n: int,
    ttt_adim_sayisi: int,
    azami_token: int,
) -> None:
    if not (hasattr(lora_model, "peft_config") or hasattr(lora_model, "durum_ayari")):
        # Ne LoRA (peft) ne de state-tuning uygulanabilen bir modelde TTT
        # atlanır -- ilgili adaptoru_kur() zaten bunun uyarısını basmıştı.
        return

    if varsayilan_lora_agirliklari is not None:
        if hasattr(lora_model, "durum_ayari"):
            lora_model.durum_anlik_goruntusunu_yukle(varsayilan_lora_agirliklari)
        else:
            from peft import set_peft_model_state_dict
            set_peft_model_state_dict(lora_model, varsayilan_lora_agirliklari.copy(), adapter_name="default")

    if not task.train_examples:
        return

    formatter = GenelSohbetBicimlendirici(tokenizer, model_ailesi)

    ds = ArcDataset(queries={task.name: _task_dict_al(task)}, is_orig=False)
    ds = ds.augment(n=cogaltma_n, shfl_keys=True, seed=1)
    ds = ds.cut_to_len(formatter=formatter, name="text", max_len=azami_token)

    egitim_metinleri = [ornek["text"] for ornek in ds.as_list(formatter)]
    gorev_ozelinde_ince_ayar(
        lora_model, tokenizer, egitim_metinleri, model_ailesi=model_ailesi,
        adim_sayisi=ttt_adim_sayisi, azami_token=azami_token,
    )


def _tek_deneme_uret(
    lora_model: Any,
    tokenizer: Any,
    model_ailesi: str,
    task: Task,
    azami_tur: int,
    azami_yeni_token: int,
) -> Optional[List[List[int]]]:

    defter = CevapDefteri()
    mesajlar: List[Dict[str, str]] = [
        {"role": "system", "content": sistem_promptu_olustur()},
        {"role": "user", "content": gorev_kullanici_promptu_olustur(task)},
    ]

    for _tur in range(azami_tur):
        model_ciktisi = uret_sohbet(
            lora_model, tokenizer, model_ailesi, mesajlar, azami_yeni_token=azami_yeni_token
        )
        mesajlar.append({"role": "assistant", "content": model_ciktisi})

        cagrilar = arac_cagrilarini_ayikla(model_ciktisi)
        if not cagrilar:

            mesajlar.append({
                "role": "user",
                "content": "You must call a tool (execute_python or submit_answer) as a JSON function call.",
            })
            continue

        for cagri in cagrilar:
            sonuc = arac_cagrisini_yurut(cagri, defter)
            mesajlar.append({"role": "user", "content": tool_response_mesaji_olustur(sonuc)})

            if cagri.get("name") == "submit_answer" and sonuc.get("basarili"):
                return defter.kaydedilen_cevap

    return defter.kaydedilen_cevap


def gorevi_coz(
    lora_model: Any,
    tokenizer: Any,
    model_ailesi: str,
    task: Task,
    varsayilan_lora_agirliklari: Optional[Dict[str, Any]] = None,
    cogaltma_n: int = 16,
    ttt_adim_sayisi: int = 20,
    azami_token: int = 4096,
    azami_yeni_token: int = 900,
    azami_tur: int = 6,
) -> Dict[str, List[List[int]]]:

    _ttt_uygula(
        lora_model, tokenizer, model_ailesi, task, varsayilan_lora_agirliklari,
        cogaltma_n, ttt_adim_sayisi, azami_token,
    )

    attempt_1 = _tek_deneme_uret(lora_model, tokenizer, model_ailesi, task, azami_tur, azami_yeni_token)
    attempt_2 = _tek_deneme_uret(lora_model, tokenizer, model_ailesi, task, azami_tur, azami_yeni_token)

    return {
        "attempt_1": attempt_1 if attempt_1 is not None else BOS_TAHMIN,
        "attempt_2": attempt_2 if attempt_2 is not None else (attempt_1 or BOS_TAHMIN),
    }
