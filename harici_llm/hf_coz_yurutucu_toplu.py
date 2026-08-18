"""
RWKV DIŞI (standart `transformers` uyumlu) model aileleri -- Granite 4.0,
LFM2.5, ve gelecekte eklenecek her HF-uyumlu aile -- için ÇOKLU-GÖREV
toplu (batched) çözücü.

coz_yurutucu_toplu.py'de RWKV için rwkv_batch.py'nin kendi ÖZEL maskeli-adım
mekanizmasını yazmamızın TEK sebebi, kurulu `rwkv` pip paketinin GERÇEK bir
batched forward SUNMAMASIYDI (o paket B=1'e kilitli). Standart `transformers`
modelleri (Granite 4.0/LFM2.5 dahil) ise kendi RESMİ model.generate()'inde
padding + attention_mask ile GERÇEK batched üretimi zaten DESTEKLER -- bu
yüzden burada RWKV'deki gibi elle yazılmış bir maskeli-adım çekirdeğine HİÇ
GEREK YOK, doğrudan standart HF API'si kullanılır.

DÜRÜSTLÜK NOTU (bu dosya YAZILDIĞI haliyle hiçbir GPU'da ÇALIŞTIRILMADI --
bu ortamda ne CUDA ne de bu iki modelin ağırlıkları var): aşağıdaki mantık
BİLEREK basit ve doğruluk-öncelikli tutuldu -- her kontrol aralığında TÜM
aktif diziler için TEK bir model.generate() çağrısı yapılır, KV-cache
turlar arası TAŞINMAZ (her turda prompt+o ana kadar üretilen metin YENİDEN
işlenir). Bu, RWKV'nin sürekli-admisyon/slot-geri-dönüştürme mekanizması
kadar hızlı DEĞİLDİR -- ama gerçek bir GPU'da hiç doğrulanmamış bir
KV-cache-taşıma/sürekli-admisyon mantığını körlemesine yazıp kırılgan bir
yarışma koşusuna göndermektense, önce BASİT VE DOĞRU bir temel hat kurup
(RWKV'de yaptığımız gibi) gerçek Kaggle loglarına bakarak hızlandırmak
tercih edildi. İlk pilot koşudan sonra gerçek zamanlama loglarıyla buraya
dönülüp coz_yurutucu_toplu.py'deki admisyon/geri-dönüştürme deseni
uyarlanabilir.
"""
import time
from typing import Any, Dict, List, Optional

import torch

from arc import Task
from araclar import CevapDefteri, arac_cagrilarini_ayikla, arac_cagrisini_yurut, train_examples_sandbox_bicimine_donustur
from coz_yurutucu import BOS_TAHMIN, _ilk_mesajlar
from rwkv_native import _tekrara_kilitlenme_periyodu
from transkript import transkript_satiri_yaz
from ttt_lora import mesajlari_metne_donustur, uretim_ayarlarini_al

_ONEK = "[hf_coz_yurutucu_toplu]"


def hf_toplu_gorevleri_coz(
    model: Any,
    tokenizer: Any,
    model_ailesi: str,
    tasks: List[Task],
    azami_yeni_token: int = 8000,
    kontrol_araligi: int = 300,
    deneme_etiketi: str = "toplu",
    bitis_zamani: Optional[float] = None,
) -> Dict[str, Dict[str, Any]]:
    """B = len(tasks) görevin HEPSİNİ, standart `transformers` batched
    generate() ile eşzamanlı çözer. Döner: coz_yurutucu_toplu.
    toplu_gorevleri_coz ile AYNI şema: {task.name: {"attempt_1": grid,
    "attempt_1_gonderildi_mi": bool}}."""
    B = len(tasks)
    cihaz = next(model.parameters()).device
    uretim_ayarlari = uretim_ayarlarini_al(model_ailesi, tokenizer)

    # Batched NEDENSEL-LM üretiminde SOL dolgu (left padding) ŞARTTIR --
    # sağ dolgu olsaydı her dizinin "bir sonraki token"i, dizinin gerçek
    # sonundan DEĞİL, dolgu tokenlerinden sonra üretilirdi.
    onceki_dolgu_yonu = tokenizer.padding_side
    tokenizer.padding_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    metinler = [mesajlari_metne_donustur(tokenizer, model_ailesi, _ilk_mesajlar(t)) for t in tasks]
    defterler = [CevapDefteri() for _ in tasks]
    for _defter, _task in zip(defterler, tasks):
        _defter.train_examples = train_examples_sandbox_bicimine_donustur(_task.train_examples)
    uretilen_metin = [""] * B
    uretilen_tokenler: List[List[int]] = [[] for _ in range(B)]
    bitti = [False] * B
    sonuclar: List[Optional[List[List[int]]]] = [None] * B

    baslangic = time.time()
    adim = 0
    try:
        while adim < azami_yeni_token and not all(bitti):
            aktif_idx = [b for b in range(B) if not bitti[b]]
            aktif_metinler = [metinler[b] + uretilen_metin[b] for b in aktif_idx]

            kodlama = tokenizer(aktif_metinler, return_tensors="pt", padding=True).to(cihaz)
            adim_boyutu = min(kontrol_araligi, azami_yeni_token - adim)

            with torch.no_grad():
                uretim_kwargs: Dict[str, Any] = dict(
                    **kodlama, max_new_tokens=adim_boyutu, pad_token_id=tokenizer.pad_token_id,
                    do_sample=uretim_ayarlari.get("do_sample", True),
                )
                if "temperature" in uretim_ayarlari:
                    uretim_kwargs["temperature"] = uretim_ayarlari["temperature"]
                if "top_p" in uretim_ayarlari:
                    uretim_kwargs["top_p"] = uretim_ayarlari["top_p"]
                if "repetition_penalty" in uretim_ayarlari:
                    uretim_kwargs["repetition_penalty"] = uretim_ayarlari["repetition_penalty"]
                cikti_idler = model.generate(**uretim_kwargs)

            girdi_uzunlugu = kodlama["input_ids"].shape[1]
            for i, b in enumerate(aktif_idx):
                yeni_tok_tensoru = cikti_idler[i][girdi_uzunlugu:]
                uretilen_tokenler[b].extend(int(t) for t in yeni_tok_tensoru.tolist())
                uretilen_metin[b] += tokenizer.decode(yeni_tok_tensoru, skip_special_tokens=True)

            adim += adim_boyutu
            print(
                f"{_ONEK} ({deneme_etiketi})   üretim: {adim}/{azami_yeni_token} adım, "
                f"{sum(1 for x in bitti if not x)}/{B} görev hâlâ aktif ({time.time() - baslangic:.1f} sn)."
            )

            if bitis_zamani is not None and time.time() > bitis_zamani and not all(bitti):
                print(f"{_ONEK} ({deneme_etiketi})   SÜRE BÜTÇESİ TÜKENDİ: {adim} adımda, hâlâ bitmemiş görevler boş tahminle işaretlenecek.")
                for b in range(B):
                    bitti[b] = True
                break

            for b in aktif_idx:
                cagrilar = arac_cagrilarini_ayikla(uretilen_metin[b])
                for cagri in cagrilar:
                    sonuc = arac_cagrisini_yurut(cagri, defterler[b])
                    transkript_satiri_yaz({
                        "gorev": tasks[b].name, "deneme": deneme_etiketi, "tur": 1,
                        "rol": "arac-sonucu", "arac": cagri.get("name"), "icerik": sonuc,
                    })
                    if cagri.get("name") == "submit_answer" and sonuc.get("success"):
                        sonuclar[b] = defterler[b].kaydedilen_cevap
                        bitti[b] = True
                if bitti[b]:
                    transkript_satiri_yaz({
                        "gorev": tasks[b].name, "deneme": deneme_etiketi, "tur": 1,
                        "rol": "assistant", "icerik": uretilen_metin[b],
                    })
                    continue

                # Yozlaşmış döngü kontrolü -- coz_yurutucu_toplu.py'deki AYNI
                # mantık (bkz. o dosyadaki gerekçe): RWKV'de gördüğümüz
                # sorunun bu modellerde de olup olmadığını GERÇEKTEN ÖLÇMEK
                # için buraya da eklendi (varsayılan olarak "olmaz" diye
                # KABUL EDİLMEDİ). İLK SÜRÜM: yalnızca tespit + bitirme;
                # RWKV'deki "aynı promptla yeniden dene" admisyon mantığı
                # bu temel hat gerçek bir GPU'da doğrulandıktan SONRA
                # buraya taşınmalı (bkz. dosya başındaki dürüstlük notu).
                periyot = _tekrara_kilitlenme_periyodu(uretilen_tokenler[b])
                if periyot is not None:
                    print(
                        f"{_ONEK} ({deneme_etiketi})   {tasks[b].name}: YOZLAŞMIŞ DÖNGÜ tespit edildi "
                        f"({periyot} token'lık alt-dizi 3 kez tekrarlandı) -- bu dizi ERKEN durduruldu."
                    )
                    transkript_satiri_yaz({
                        "gorev": tasks[b].name, "deneme": deneme_etiketi, "tur": 1,
                        "rol": "sistem-uyari", "icerik": f"yozlaşmış döngü tespit edildi (periyot={periyot})",
                    })
                    bitti[b] = True
    finally:
        tokenizer.padding_side = onceki_dolgu_yonu

    tamamlanan = sum(1 for s in sonuclar if s is not None)
    print(
        f"{_ONEK} ({deneme_etiketi}) BİTTİ: B={B} görevden {tamamlanan} tanesi GERÇEKTEN submit_answer ile "
        f"sonuçlandı, toplam {adim} adım, {time.time() - baslangic:.1f} sn."
    )

    return {
        tasks[b].name: {
            "attempt_1": sonuclar[b] if sonuclar[b] is not None else BOS_TAHMIN,
            "attempt_1_gonderildi_mi": sonuclar[b] is not None,
        }
        for b in range(B)
    }
