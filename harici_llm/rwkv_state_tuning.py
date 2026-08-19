"""
RWKV state-tuning (başlangıç durumu ince ayarı): LoRA'nın native `rwkv`
pip paketiyle ÇALIŞMAMASI üstüne (ağırlıklar nn.Linear alt-modül değil,
düz tensör sözlüğü) devreye giren, RWKV topluluğunun kendi PEFT yöntemi.

Fikir: modelin ağırlıklarına hiç dokunmadan, yalnızca modelin RNN/SSM
durumunun (state) BAŞLANGIÇ değerini öğrenilebilir bir parametre haline
getirip eğitiyoruz. Eğitim, "görevin örnekleri hafızaya önceden işlenmiş
gibi" davranan bir başlangıç durumu bulmaya çalışır -- LoRA'nın ağırlık-
uzayında yaptığını, state-uzayında yapar. Çok daha ucuzdur (katman sayısı
x state-boyutu kadar parametre, milyonlarca değil binlerce), ve `rwkv`
paketinin ağırlıklarına hiç dokunmadığı için nn.Linear alt-modül
gereksinimi yok.

KISIT (açıkça bildiriliyor): Bu, `rwkv` pip paketinin forward()
kernellerinin state üzerinden geri yayılıma (autograd) izin verdiğini
varsayar. Eğer belirli bir strateji (özellikle int8/custom CUDA
hızlandırmalı) autograd'i kırarsa, ilk adımda RuntimeError ile açıkça
bildirilir -- sessizce sıfır gradyanla "başarılı" gibi görünmez.
"""
from typing import Any, List, Optional

import torch
import torch.nn as nn


def baslangic_durumunu_al(native_rwkv: Any, ornek_token: int = 0) -> List[torch.Tensor]:
    """Modelin kendi ilk-durum şeklini/dtype'ını/cihazını öğrenmek için tek
    bir token ile sıfır durumdan bir adım çalıştırır, dönen durumla AYNI
    biçimde SIFIRLARLA doldurulmuş yeni bir durum üretir (bu adımın
    kendisinin etkisini geri almış oluruz)."""
    with torch.no_grad():
        _, durum = native_rwkv.forward([ornek_token], None)
    return [torch.zeros_like(t) for t in durum]


class RWKVDurumAyarlayici(nn.Module):
    """Öğrenilebilir başlangıç durumunu tutan, sarmalı RWKVUyumluModel
    üzerinden forward/generate çağırırken bu durumu enjekte eden ince
    katman. peft.LoraConfig'in yerini alır: `hasattr(model, 'durum_ayari')`
    ile geri kalan kod (gonderim_uret.py/coz_yurutucu.py) bu modeli
    tanıyıp uygun snapshot/reset akışını uygular."""

    durum_ayari = True

    def __init__(self, sarmali_model: Any, ornek_token: int = 0):
        super().__init__()
        self.model = sarmali_model

        # GUVENLIK: self.model = sarmali_model, nn.Module oldugu icin
        # otomatik alt-modul olarak kaydedilir; bu da .parameters()'in
        # 7.2B'lik ham agirliklari da (RWKVUyumluModel.parameters() bunlari
        # dondurur) dolasima sokmasi riskini dogurur. requires_grad'i acikca
        # False yaparak, optimizer'in bunlari YANLISLIKLA yakalamasini
        # -- requires_grad filtresine guvenmek yerine -- kesin olarak
        # engelliyoruz.
        for p in self.model.parameters():
            if isinstance(p, torch.Tensor):
                p.requires_grad_(False)

        varsayilan_durum = baslangic_durumunu_al(sarmali_model._rwkv, ornek_token)
        self.durum_parametreleri = nn.ParameterList(
            [nn.Parameter(t.clone()) for t in varsayilan_durum]
        )
        self._varsayilan_durum_yedegi = [t.clone().detach() for t in varsayilan_durum]

    @property
    def device(self) -> torch.device:
        return self.model.device

    def sifirla(self) -> None:
        with torch.no_grad():
            for p, yedek in zip(self.durum_parametreleri, self._varsayilan_durum_yedegi):
                p.copy_(yedek)

    def durum_anlik_goruntusu_al(self) -> List[torch.Tensor]:
        return [p.clone().detach() for p in self.durum_parametreleri]

    def durum_anlik_goruntusunu_yukle(self, anlik_goruntu: List[torch.Tensor]) -> None:
        with torch.no_grad():
            for p, deger in zip(self.durum_parametreleri, anlik_goruntu):
                p.copy_(deger)

    def _yayilmis_durum(self, batch_boyutu: int) -> List[List[torch.Tensor]]:
        return [[p.clone() for p in self.durum_parametreleri] for _ in range(batch_boyutu)]

    def forward(self, input_ids: torch.Tensor, **kwargs) -> Any:
        B = input_ids.shape[0]
        baslangic = self._yayilmis_durum(B)
        return self.model.forward(input_ids, past_key_values=baslangic, **kwargs)

    def generate(self, input_ids: torch.Tensor, **kwargs) -> torch.Tensor:
        baslangic = [p.clone().detach() for p in self.durum_parametreleri]
        return self.model.generate(input_ids, baslangic_durumu=baslangic, **kwargs)

    def baslangic_durumu_kopyala(self) -> List[torch.Tensor]:
        """rwkv_oturum.py'nin çok-turlu, TEK-KEZ-İŞLE oturumu için: öğrenilmiş
        (ya da state-tuning atlanmışsa sıfır) başlangıç durumunun bağımsız bir
        kopyasını verir."""
        return [p.clone().detach() for p in self.durum_parametreleri]

    def ileri_besle_tokenler(self, token_ids: List[int], durum: Optional[List[torch.Tensor]]) -> Any:
        return self.model.ileri_besle_tokenler(token_ids, durum)

    def uret_devam(self, son_logits: Any, durum: Optional[List[torch.Tensor]], max_new_tokens: int, **kwargs: Any) -> Any:
        return self.model.uret_devam(son_logits, durum, max_new_tokens, **kwargs)


def state_egitimi_calisir_mi_dogrula(durum_ayarlayici: RWKVDurumAyarlayici) -> None:
    """State-tuning'in gercekten gradyan uretip uretmedigini KANITLAR;
    sessizce sifir-gradyanli 'sozde basari' vermez. Kucuk, tek adimlik bir
    dogrulama: rastgele bir token dizisi uzerinden forward+backward
    calistirip durum parametrelerinden en az birinin .grad'inin None
    OLMADIGINI ve sifirdan FARKLI oldugunu kontrol eder."""
    cihaz = durum_ayarlayici.device
    sahte_girdi = torch.randint(1, 50, (1, 4), device=cihaz)
    sahte_etiket = torch.randint(1, 50, (1, 4), device=cihaz)

    cikti = durum_ayarlayici.forward(sahte_girdi, labels=sahte_etiket)
    if cikti.loss is None:
        raise RuntimeError(
            "State-tuning doğrulaması başarısız: forward() loss üretmedi."
        )
    cikti.loss.backward()

    herhangi_bir_gradyan_var = any(
        p.grad is not None and torch.any(p.grad != 0) for p in durum_ayarlayici.durum_parametreleri
    )
    for p in durum_ayarlayici.durum_parametreleri:
        p.grad = None

    if not herhangi_bir_gradyan_var:
        raise RuntimeError(
            "State-tuning doğrulaması başarısız: `rwkv` pip paketinin forward() kernelleri "
            "state üzerinden geri yayılıma (autograd) izin vermiyor gibi görünüyor -- "
            "durum parametrelerinin HİÇBİRİNDE sıfırdan farklı gradyan oluşmadı. Bu strateji "
            "(özellikle int8/custom CUDA hızlandırmalı) autograd'i kırıyor olabilir; "
            "'cuda fp16' gibi tam-hassasiyetli bir stratejiyle tekrar deneyin."
        )
