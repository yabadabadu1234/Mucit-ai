"""
Coz_yurutucu.py'nin cok-turlu arac-cagirma dongusu (varsayilan azami_tur=1,
ama arac-cagrisi/arac-yaniti ic ice devam ederse birden fazla "metin_isle+
uret" adimi ayni denemede yine olusabilir) icin: her adimda TUM konusma
metnini bastan tokenlestirip modelden GECIRME
-- rwkv_native.py'nin token-basina-forward duzeltmesinden (bkz. o dosyanin
basindaki not) SONRA bile hala var olan, AYRI bir performans acigi --
yerine RWKV'nin kendi RNN durumunu (state) TUR TUR TASIYARAK yalnizca o
turde YENI EKLENEN metni isler. Onceki turlerin tokenleri ASLA ikinci kez
islenmez.

Neden bu ayri bir aciktir: rwkv_native.py'deki duzeltme "T token'i T ayri
cagriyla isleme" sorununu cozdu, ama coz_yurutucu.py hala her turde
`mesajlar` listesinin TAMAMINI yeniden metne cevirip (mesajlari_metne_
donustur) SIFIRDAN besliyordu -- yani tur basina islenen token sayisi
tur ilerledikce (onceki turlerin + yeni turun toplami) KARELE buyuyordu.
6 turluk bir gorevde bu, gercekte gerekenden kat kat fazla token islemek
anlamina gelir. Bu modul, RWKV'nin dogal (RNN) avantajini -- durumu O(1)
tasiyabilmeyi -- kullanarak bunu DOGRUSAL maliyete indirir.

ONEMLI DOGRULUK NOKTASI: modelin KENDI urettigi (asistan) metni bir
sonraki turde TEKRAR tokenlestirip beslemeye GEREK YOKTUR -- uret_devam()
zaten her uretilen tokeni state'e isleyerek ilerler (rwkv_native.py:
uret_devam icindeki dongu, ureteceginden SONRAKI tahmini almak icin
sonraki_token'i da forward'a besliyor). Bu yuzden decode->re-encode
gidip-gelmesi (tokenizer'in tam tersine cevrilebilir olmama riski)
tamamen ELENIR -- eski yaklasimdan hem HIZLI hem de daha SADIK
(modelin GERCEKTEN urettigi tokenler, decode edilip sonra yeniden
tahmin edilen bir metin degil, dogrudan state'te kalir).
"""
from typing import Any, List, Optional


class RWKVSohbetOturumu:
    """Tek bir `_tek_deneme_uret` cagrisi (bir "attempt") boyunca RWKV
    RNN durumunu tasir. `metin_isle()` ile YENI eklenen metni (sistem/
    kullanici/arac-yaniti) besler, `uret()` ile modelin bir sonraki
    asistan donusunu urettirir (state otomatik ilerler, ayrica beslemeye
    gerek yoktur)."""

    def __init__(self, model: Any, tokenizer: Any):
        self.model = model
        self.tokenizer = tokenizer
        self.durum: Optional[List[Any]] = (
            model.baslangic_durumu_kopyala() if hasattr(model, "baslangic_durumu_kopyala") else None
        )
        self.son_logits: Any = None
        self._en_az_bir_kez_islendi = False

    def metin_isle(self, metin: str) -> None:
        token_ids = self.tokenizer.encode(metin)
        if not token_ids:
            return
        self.son_logits, self.durum = self.model.ileri_besle_tokenler(token_ids, self.durum)
        self._en_az_bir_kez_islendi = True

    def uret(self, azami_yeni_token: int, do_sample: bool = False,
             temperature: Optional[float] = None, top_p: Optional[float] = None,
             pad_token_id: Optional[int] = None, repetition_penalty: Optional[float] = None) -> str:
        if not self._en_az_bir_kez_islendi:
            raise RuntimeError(
                "RWKVSohbetOturumu.uret(): uret()'ten once en az bir kez metin_isle() cagrilmalidir "
                "(baslangic promptu hic islenmemis)."
            )
        uretilenler, self.son_logits, self.durum = self.model.uret_devam(
            self.son_logits, self.durum, azami_yeni_token,
            do_sample=do_sample, temperature=temperature, top_p=top_p, pad_token_id=pad_token_id,
            repetition_penalty=repetition_penalty,
        )
        return self.tokenizer.decode(uretilenler, skip_special_tokens=True)
