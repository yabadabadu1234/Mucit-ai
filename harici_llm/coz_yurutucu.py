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
from model_yapilandirmalari import RWKV
from transkript import transkript_satiri_yaz
from ttt_lora import gorev_ozelinde_ince_ayar, mesajlari_metne_donustur, rwkv_tek_mesaji_sar, uret_sohbet, uretim_ayarlarini_al

BOS_TAHMIN = [[0, 0], [0, 0]]

_ARAC_CAGRISI_YOK_UYARISI = "You must call a tool (execute_python or submit_answer) as a JSON function call."


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


def _ilk_mesajlar(task: Task) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": sistem_promptu_olustur()},
        {"role": "user", "content": gorev_kullanici_promptu_olustur(task)},
    ]


def _tek_deneme_uret_artimli(
    lora_model: Any,
    tokenizer: Any,
    model_ailesi: str,
    task: Task,
    azami_tur: int,
    azami_yeni_token: int,
    deneme_etiketi: str = "?",
) -> Optional[List[List[int]]]:
    """RWKV native/state-tuning yolu için: `_tek_deneme_uret`in HER turde
    tüm konuşma metnini baştan işleyen versiyonuna göre performans
    düzeltmesi -- rwkv_oturum.RWKVSohbetOturumu ile RNN durumu tur-tur
    TAŞINIR, önceki turların tokenleri ASLA ikinci kez işlenmez (bkz.
    rwkv_oturum.py başındaki not). Ürettiği metin/karar dizisi, eski
    `_tek_deneme_uret` ile AYNIDIR (aynı `rwkv_tek_mesaji_sar` sarma
    mantığı kullanılır) -- yalnızca YENİDEN-İŞLEME elenmiştir."""
    from rwkv_oturum import RWKVSohbetOturumu

    defter = CevapDefteri()
    mesajlar = _ilk_mesajlar(task)

    oturum = RWKVSohbetOturumu(lora_model, tokenizer)
    oturum.metin_isle(mesajlari_metne_donustur(tokenizer, model_ailesi, mesajlar))

    uretim_ayarlari = uretim_ayarlarini_al(model_ailesi, tokenizer)

    for _tur in range(azami_tur):
        print(f"[coz_yurutucu] {task.name}: tur {_tur + 1}/{azami_tur} başlıyor (artımlı oturum)...")
        model_ciktisi = oturum.uret(azami_yeni_token, **uretim_ayarlari)
        mesajlar.append({"role": "assistant", "content": model_ciktisi})
        print(f"[coz_yurutucu]   model çıktısı ({len(model_ciktisi)} karakter): {model_ciktisi[:500]!r}")
        transkript_satiri_yaz({
            "gorev": task.name, "deneme": deneme_etiketi, "tur": _tur + 1,
            "rol": "assistant", "icerik": model_ciktisi,
        })
        # NOT: assistan'in kendi urettigi metni tekrar tokenlestirip
        # oturum.metin_isle() ile BESLEMIYORUZ -- uret() zaten state'i bu
        # tokenlerle ilerletti (bkz. rwkv_native.uret_devam).

        cagrilar = arac_cagrilarini_ayikla(model_ciktisi)
        if not cagrilar:
            mesaj = {"role": "user", "content": _ARAC_CAGRISI_YOK_UYARISI}
            mesajlar.append(mesaj)
            oturum.metin_isle(rwkv_tek_mesaji_sar(mesaj))
            transkript_satiri_yaz({
                "gorev": task.name, "deneme": deneme_etiketi, "tur": _tur + 1,
                "rol": "sistem-uyari", "icerik": _ARAC_CAGRISI_YOK_UYARISI,
            })
            continue

        for cagri in cagrilar:
            sonuc = arac_cagrisini_yurut(cagri, defter)
            mesaj = {"role": "user", "content": tool_response_mesaji_olustur(sonuc)}
            mesajlar.append(mesaj)
            oturum.metin_isle(rwkv_tek_mesaji_sar(mesaj))
            transkript_satiri_yaz({
                "gorev": task.name, "deneme": deneme_etiketi, "tur": _tur + 1,
                "rol": "arac-sonucu", "arac": cagri.get("name"), "icerik": sonuc,
            })

            if cagri.get("name") == "submit_answer" and sonuc.get("basarili"):
                return defter.kaydedilen_cevap

    return defter.kaydedilen_cevap


def _tek_deneme_uret(
    lora_model: Any,
    tokenizer: Any,
    model_ailesi: str,
    task: Task,
    azami_tur: int,
    azami_yeni_token: int,
    deneme_etiketi: str = "?",
) -> Optional[List[List[int]]]:

    if model_ailesi == RWKV and hasattr(lora_model, "ileri_besle_tokenler"):
        # native RWKV (bare RWKVUyumluModel ya da RWKVDurumAyarlayici):
        # her turde tum gecmisi yeniden isleyen genel yol yerine, RNN
        # durumunu tasiyan artimli/performansli yolu kullan.
        return _tek_deneme_uret_artimli(
            lora_model, tokenizer, model_ailesi, task, azami_tur, azami_yeni_token, deneme_etiketi
        )

    defter = CevapDefteri()
    mesajlar = _ilk_mesajlar(task)

    for _tur in range(azami_tur):
        print(f"[coz_yurutucu] {task.name}: tur {_tur + 1}/{azami_tur} başlıyor...")
        model_ciktisi = uret_sohbet(
            lora_model, tokenizer, model_ailesi, mesajlar, azami_yeni_token=azami_yeni_token
        )
        mesajlar.append({"role": "assistant", "content": model_ciktisi})
        print(f"[coz_yurutucu]   model çıktısı ({len(model_ciktisi)} karakter): {model_ciktisi[:500]!r}")
        transkript_satiri_yaz({
            "gorev": task.name, "deneme": deneme_etiketi, "tur": _tur + 1,
            "rol": "assistant", "icerik": model_ciktisi,
        })

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
            transkript_satiri_yaz({
                "gorev": task.name, "deneme": deneme_etiketi, "tur": _tur + 1,
                "rol": "arac-sonucu", "arac": cagri.get("name"), "icerik": sonuc,
            })

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

    attempt_1 = _tek_deneme_uret(lora_model, tokenizer, model_ailesi, task, azami_tur, azami_yeni_token, "attempt_1")
    attempt_2 = _tek_deneme_uret(lora_model, tokenizer, model_ailesi, task, azami_tur, azami_yeni_token, "attempt_2")

    return {
        "attempt_1": attempt_1 if attempt_1 is not None else BOS_TAHMIN,
        "attempt_2": attempt_2 if attempt_2 is not None else (attempt_1 or BOS_TAHMIN),
    }
