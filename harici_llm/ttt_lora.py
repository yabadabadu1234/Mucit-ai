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


def _repo_id_dogrulama_hatasi_mi(hata: Exception) -> bool:
    return "repo id must be in the form" in str(hata).lower()


def temel_model_yukle(model_ailesi: str, veri_tipi: torch.dtype = torch.bfloat16) -> Any:
    """Model DAIMA yerel dosya yolundan yuklenir; internet erisimi kapali
    oldugundan `local_files_only=True` her zaman zorunludur.

    Ucuncu bir kademe uyguluyor:
      1) trust_remote_code=False (mimari transformers'a yerlesikse yeter)
      2) yerlesik degilse: ozel_kod_kaydi ile Config/Model siniflarini
         DOGRUDAN dosyadan importlib ile yukleyip Auto* kayit defterine
         ekle, sonra YINE trust_remote_code=False ile dene -- artik hicbir
         hub-tarzi dinamik modul cozumlemesi devreye girmez.
      3) yalnizca 1 ve 2 de basarisiz olursa, son care olarak
         trust_remote_code=True denenir (bazi transformers surumlerinde
         yerel yol + repo_id dogrulama hatasi hic olusmayabilir)."""
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

    from ozel_kod_kaydi import ozel_kodu_manuel_kaydet

    try:
        ozel_kodu_manuel_kaydet(yol)
        return AutoModelForCausalLM.from_pretrained(
            yol, torch_dtype=veri_tipi, device_map="cuda",
            trust_remote_code=False, local_files_only=True,
        )
    except Exception as ikinci_hata:
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

        from ozel_kod_kaydi import ozel_kodu_manuel_kaydet
        try:
            ozel_kodu_manuel_kaydet(yol)
            tok = AutoTokenizer.from_pretrained(yol, trust_remote_code=False, local_files_only=True)
        except Exception:
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


_TAMAMLAMA_ISARETLERI = {
    RWKV: ("Assistant:", "\n\n"),
    "mamba": ("Output:\n", "\n\n"),
    "falcon_mamba": ("Output:\n", "\n\n"),
}


def _tamamlama_araliklarini_bul(metin: str, baslangic_isareti: str, bitis_isareti: str) -> List[Any]:
    araliklar = []
    idx = 0
    while True:
        b = metin.find(baslangic_isareti, idx)
        if b == -1:
            break
        b_icerik = b + len(baslangic_isareti)
        e = metin.find(bitis_isareti, b_icerik)
        e = e if e != -1 else len(metin)
        araliklar.append((b_icerik, e))
        idx = e
    return araliklar


def _tamamlama_sadece_etiketleri_olustur(
    tokenizer: Any, metin: str, model_ailesi: str, input_ids: List[int], offsetler: Optional[List[Any]]
) -> Optional[List[int]]:
    """arc_solver.py'deki QwenDataCollatorForCompletionOnlyLM'in genel
    hali: USER_TOKEN_ID/ASSISTANT_TOKEN_ID gibi TEK bir tokenizer'a
    (Qwen) sabitlenmis token ID'leri yerine, metindeki 'Assistant:'/
    'Output:\\n' gibi donus isaretlerinin KARAKTER araliklarini bulup,
    hizli tokenizer'in offset_mapping'i ile bu araliklarin disinda kalan
    (yani kullanicinin/girdinin oldugu) tum tokenlari -100 ile maskeler.
    Yalnizca modelin URETMESI gereken asistan/cikti kismindan gradyan
    alinir. offset_mapping desteklenmeyen (yavas) bir tokenizer icin
    None doner; cagiran taraf bu durumda tam-dizi kaybina duser."""
    if offsetler is None:
        return None

    isaretler = _TAMAMLAMA_ISARETLERI.get(model_ailesi)
    if isaretler is None:
        return None

    tamamlama_araliklari = _tamamlama_araliklarini_bul(metin, *isaretler)
    if not tamamlama_araliklari:
        return None

    etiketler: List[int] = []
    for i, (tok_b, tok_e) in enumerate(offsetler):
        icinde_mi = any(a_b <= tok_b < a_e for a_b, a_e in tamamlama_araliklari)
        etiketler.append(input_ids[i] if icinde_mi else -100)

    if all(e == -100 for e in etiketler):
        return None
    return etiketler


def gorev_ozelinde_ince_ayar(
    lora_model: Any,
    tokenizer: Any,
    egitim_metinleri: List[str],
    model_ailesi: Optional[str] = None,
    ogrenme_orani: float = 2e-4,
    adim_sayisi: int = 20,
    azami_token: int = 1024,
    tamamlama_sadece: bool = True,
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

        etiketler_tensoru = None
        if tamamlama_sadece and model_ailesi is not None:
            try:
                kodlama = tokenizer(
                    metin, return_tensors=None, truncation=True, max_length=azami_token,
                    return_offsets_mapping=True,
                )
                etiketler = _tamamlama_sadece_etiketleri_olustur(
                    tokenizer, metin, model_ailesi, kodlama["input_ids"], kodlama.get("offset_mapping")
                )
                if etiketler is not None:
                    girdiler = {"input_ids": torch.tensor([kodlama["input_ids"]], dtype=torch.long, device=cihaz)}
                    etiketler_tensoru = torch.tensor([etiketler], dtype=torch.long, device=cihaz)
            except TypeError:
                pass  # tokenizer offset_mapping desteklemiyor -> tam-dizi kaybina duselim

        if etiketler_tensoru is None:
            girdiler = tokenizer(
                metin, return_tensors="pt", truncation=True, max_length=azami_token
            ).to(cihaz)
            etiketler_tensoru = girdiler["input_ids"]

        ciktilar = lora_model(**girdiler, labels=etiketler_tensoru)
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
