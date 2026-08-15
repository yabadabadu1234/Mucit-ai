from typing import Any, Dict, List, Optional

import torch

from model_yapilandirmalari import (
    DECODING_ONERILERI,
    LORA_HEDEF_MODULLERI,
    RWKV,
    asistan_donusu_sar,
    kullanici_donusu_sar,
    model_ailesini_belirle,
    rwkv_fonksiyon_cagirma_sistem_promptu,
    yerel_model_yolu,
)


def _guven_kodu_gerekli_mi(hata: Exception) -> bool:
    metin = str(hata).lower()
    return "trust_remote_code" in metin or "does not recognize this architecture" in metin


def temel_model_yukle(model_ailesi: str, veri_tipi: torch.dtype = torch.bfloat16) -> Any:
    """Model DAIMA yerel dosya yolundan yuklenir; internet erisimi kapali
    oldugundan `local_files_only=True` her zaman zorunludur.

    `trust_remote_code=True`, dinamik modul cozumlemesinde yerel yolu bile
    once bir "repo_id" gibi regex ile dogrulamaya calisip cok-slash'li
    yerel yollarda hataya dusebiliyor (huggingface_hub validate_repo_id).
    Bu yuzden ONCE trust_remote_code=False ile denenir (mimari transformers
    icinde yerlesikse -- RWKV ve Mamba genelde oyledir); yalnizca gercekten
    ozel kod gerektiren bir hata alinirsa trust_remote_code=True ile tekrar
    denenir."""
    from transformers import AutoModelForCausalLM

    yol = yerel_model_yolu(model_ailesi)
    try:
        return AutoModelForCausalLM.from_pretrained(
            yol, torch_dtype=veri_tipi, device_map="cuda",
            trust_remote_code=False, local_files_only=True,
        )
    except Exception as ilk_hata:
        if not _guven_kodu_gerekli_mi(ilk_hata):
            raise
        return AutoModelForCausalLM.from_pretrained(
            yol, torch_dtype=veri_tipi, device_map="cuda",
            trust_remote_code=True, local_files_only=True,
        )


def tokenizer_yukle(model_ailesi: str) -> Any:
    from transformers import AutoTokenizer

    yol = yerel_model_yolu(model_ailesi)
    try:
        tok = AutoTokenizer.from_pretrained(yol, trust_remote_code=False, local_files_only=True)
    except Exception as ilk_hata:
        if not _guven_kodu_gerekli_mi(ilk_hata):
            raise
        tok = AutoTokenizer.from_pretrained(yol, trust_remote_code=True, local_files_only=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return tok


def lora_adaptoru_kur(base_model: Any, model_ailesi: str, r: int = 8, alpha: int = 16, dropout: float = 0.05) -> Any:
    from peft import LoraConfig, get_peft_model

    hedef_moduller = LORA_HEDEF_MODULLERI[model_ailesi]

    peft_config = LoraConfig(
        r=r,
        lora_alpha=alpha,
        target_modules=hedef_moduller,
        lora_dropout=dropout,
        bias="none",
        task_type="CAUSAL_LM",
    )
    return get_peft_model(base_model, peft_config)


def adaptoru_sifirla(lora_model: Any) -> None:
    with torch.no_grad():
        for isim, parametre in lora_model.named_parameters():
            if "lora_A" in isim:
                torch.nn.init.kaiming_uniform_(parametre, a=5 ** 0.5)
            elif "lora_B" in isim:
                torch.nn.init.zeros_(parametre)


def gorev_ozelinde_ince_ayar(
    lora_model: Any,
    tokenizer: Any,
    egitim_metinleri: List[str],
    ogrenme_orani: float = 2e-4,
    adim_sayisi: int = 20,
    azami_token: int = 1024,
) -> List[float]:

    if not egitim_metinleri:
        return []

    cihaz = next(lora_model.parameters()).device
    optimizer = torch.optim.AdamW(
        (p for p in lora_model.parameters() if p.requires_grad), lr=ogrenme_orani
    )

    lora_model.train()
    kayip_gecmisi: List[float] = []
    n = len(egitim_metinleri)
    for adim in range(adim_sayisi):
        metin = egitim_metinleri[adim % n]
        girdiler = tokenizer(
            metin, return_tensors="pt", truncation=True, max_length=azami_token
        ).to(cihaz)

        ciktilar = lora_model(**girdiler, labels=girdiler["input_ids"])
        kayip = ciktilar.loss

        optimizer.zero_grad(set_to_none=True)
        kayip.backward()
        torch.nn.utils.clip_grad_norm_(
            (p for p in lora_model.parameters() if p.requires_grad), max_norm=1.0
        )
        optimizer.step()

        kayip_gecmisi.append(float(kayip.detach().item()))

    lora_model.eval()
    return kayip_gecmisi


def _rwkv_mesajlari_metne_sar(mesajlar: List[Dict[str, str]]) -> str:
    parcalar = []
    for mesaj in mesajlar:
        rol, icerik = mesaj["role"], mesaj["content"]
        if rol == "system":
            parcalar.append(icerik if icerik.startswith("System:") else f"System: {icerik}")
        elif rol == "user" or rol == "tool":
            parcalar.append(kullanici_donusu_sar(icerik, RWKV))
        elif rol == "assistant":
            parcalar.append(asistan_donusu_sar(icerik, RWKV))
    return "".join(parcalar)


def mesajlari_metne_donustur(tokenizer: Any, model_ailesi: str, mesajlar: List[Dict[str, str]]) -> str:
    if model_ailesi == RWKV:
        return _rwkv_mesajlari_metne_sar(mesajlar)
    if hasattr(tokenizer, "apply_chat_template"):
        return tokenizer.apply_chat_template(mesajlar, tokenize=False, add_generation_prompt=True)
    return "\n".join(f"{m['role']}: {m['content']}" for m in mesajlar) + "\nassistant:"


def uret_sohbet(
    lora_model: Any,
    tokenizer: Any,
    model_ailesi: str,
    mesajlar: List[Dict[str, str]],
    azami_yeni_token: int = 768,
    preset: str = "fonksiyon_cagirma",
) -> str:
    cihaz = next(lora_model.parameters()).device
    ayar = DECODING_ONERILERI[model_ailesi][preset]

    girdi_metni = mesajlari_metne_donustur(tokenizer, model_ailesi, mesajlar)
    girdiler = tokenizer(girdi_metni, return_tensors="pt").to(cihaz)

    ornekleme = ayar["temp"] > 0.0

    with torch.no_grad():
        uretim_kwargs: Dict[str, Any] = dict(
            **girdiler,
            max_new_tokens=azami_yeni_token,
            do_sample=ornekleme,
            pad_token_id=tokenizer.pad_token_id,
        )
        if ornekleme:
            uretim_kwargs["temperature"] = ayar["temp"]
            if ayar.get("top_p", 0.0) > 0.0:
                uretim_kwargs["top_p"] = ayar["top_p"]
        if ayar.get("alpha_presence"):
            uretim_kwargs["repetition_penalty"] = 1.0 + ayar["alpha_presence"] / 10.0

        cikti_idler = lora_model.generate(**uretim_kwargs)

    uretilen = cikti_idler[0][girdiler["input_ids"].shape[1]:]
    return tokenizer.decode(uretilen, skip_special_tokens=True)
