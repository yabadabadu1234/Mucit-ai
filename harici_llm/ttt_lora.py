from typing import Any, List, Optional

import torch

MODEL_AILE_HEDEF_MODULLERI = {
    "rwkv": ["key", "value", "receptance", "output", "gate"],
    "mamba": ["in_proj", "out_proj", "x_proj", "dt_proj"],
    "falcon_mamba": ["in_proj", "out_proj", "x_proj", "dt_proj"],
}

DESTEKLENEN_MODELLER = {
    "BlinkDL/rwkv7-g1": "rwkv",
    "mistralai/Mamba-Codestral-7B-v0.1": "mamba",
    "tiiuae/falcon-mamba-7b-instruct": "falcon_mamba",
}


def model_ailesini_belirle(model_id: str) -> str:
    if model_id in DESTEKLENEN_MODELLER:
        return DESTEKLENEN_MODELLER[model_id]
    kucuk = model_id.lower()
    if "rwkv" in kucuk:
        return "rwkv"
    if "falcon" in kucuk and "mamba" in kucuk:
        return "falcon_mamba"
    if "mamba" in kucuk:
        return "mamba"
    raise ValueError(
        f"Bilinmeyen model ailesi: {model_id}. Desteklenen: {sorted(DESTEKLENEN_MODELLER)} "
        f"veya adında 'rwkv'/'mamba' geçen bir model_id."
    )


def temel_model_yukle(model_id: str, cihaz: str = "cuda", veri_tipi: torch.dtype = torch.bfloat16) -> Any:
    from transformers import AutoModelForCausalLM

    return AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=veri_tipi, device_map=cihaz, trust_remote_code=True
    )


def tokenizer_yukle(model_id: str) -> Any:
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return tok


def lora_adaptoru_kur(base_model: Any, model_id: str, r: int = 8, alpha: int = 16, dropout: float = 0.05) -> Any:
    from peft import LoraConfig, get_peft_model

    aile = model_ailesini_belirle(model_id)
    hedef_moduller = MODEL_AILE_HEDEF_MODULLERI[aile]

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


def uret(
    lora_model: Any,
    tokenizer: Any,
    sistem_promptu: str,
    kullanici_promptu: str,
    azami_yeni_token: int = 768,
    sicaklik: float = 0.7,
    ornekleme: bool = True,
) -> str:
    cihaz = next(lora_model.parameters()).device

    if hasattr(tokenizer, "apply_chat_template"):
        mesajlar = [
            {"role": "system", "content": sistem_promptu},
            {"role": "user", "content": kullanici_promptu},
        ]
        girdi_metni = tokenizer.apply_chat_template(mesajlar, tokenize=False, add_generation_prompt=True)
    else:
        girdi_metni = f"{sistem_promptu}\n\n{kullanici_promptu}\n\nAssistant:"

    girdiler = tokenizer(girdi_metni, return_tensors="pt").to(cihaz)

    with torch.no_grad():
        cikti_idler = lora_model.generate(
            **girdiler,
            max_new_tokens=azami_yeni_token,
            do_sample=ornekleme,
            temperature=sicaklik if ornekleme else None,
            top_p=0.9 if ornekleme else None,
            pad_token_id=tokenizer.pad_token_id,
        )

    uretilen = cikti_idler[0][girdiler["input_ids"].shape[1]:]
    return tokenizer.decode(uretilen, skip_special_tokens=True)
