"""
BlinkDL/rwkv7-g1 deposundan indirilen HAM .pth kontrol noktasi (transformers
config.json TASIMIYOR) icin native yukleme yolu.

`rwkv` pip paketinin kendi RWKV sinifi, HF'nin batched
forward(input_ids=...)/generate() arayuzunden FARKLI bir arayuz sunar:
tek bir token dizisini, kendi tasidigi (state) ile TEK TEK isler. Bu dosya,
geri kalan tum boru hattinin (mcts_dallanma.py'deki turbo_dfs BATCHED
cagrisi dahil) HICBIR SATIRI degismeden calismaya devam etmesi icin, native
RWKV'yi HF-uyumlu bir sarmalayiciya (adapter) gizler: batch'teki her satiri
kendi bagimsiz state'iyle TEK TEK isleyip sonuclari yigin (tensor) halinde
geri dondurur.

ONEMLI KISIT: `rwkv` pip paketinin agirliklari (`self.w`) standart
nn.Linear alt-moduller olarak DEGIL, duz bir tensor sozlugu olarak
saklanir. Bu yuzden `peft.get_peft_model()` bu modele dogrudan LoRA
uygulayamaz -- target_modules eslesmesi nn.Module agac gezintisine
dayanir. lora_adaptoru_kur() bu durumu tespit edip LoRA'yi ATLAR ve
acik bir uyari basar; test-time-training bu native yolda su an icin
devre disi kalir (inference/degerlendirme calisir, TTT calismaz). Bu,
kaide/hile ile ortulmez -- kullaniciya acikca bildirilir.
"""
import os
import time
from typing import Any, List, Optional, Tuple

import torch

_ILERLEME_ADIMI = 5000  # her N tokende bir ilerleme satırı bas (sessiz kalıp "donmuş gibi" görünmesin diye)

# Kullanıcının GERÇEK Kaggle transkriptinde doğrudan gözlemlendi: küçük/az
# eğitilmiş model bazen aynı token dizisini (ör. kendi orijinal promptunun
# kuyruğunu) ONLARCA kez ARDIŞIK olarak birebir tekrarlayan yozlaşmış bir
# döngüye kilitleniyor -- bu durumda 55000/60000 tokenlik BÜTÜN bütçe
# anlamsız tekrara harcanıyor. Token-seviyesinde ucuz bir tekrar
# denetimiyle bu döngü ERKEN yakalanıp üretim durdurulur (harcanan zaman/
# token boşa gitmez, İKAZ/yeniden-deneme mantığı daha erken devreye girer).
_TEKRAR_KONTROL_ADIMI = 500
# NOT (kullanıcının açık talebi): eski eşik (asgari periyot 4 token) ARC-AGI
# ızgaralarının KENDİ DOĞASINDA zaten var olan kısa tekrarları (ör. bir
# ızgarada "0, 0, 0, 0, ..." gibi aynı sayının art arda geçmesi -- YOZLAŞMIŞ
# bir döngü DEĞİL, tamamen GEÇERLİ bulmaca içeriği) yanlışlıkla yakalıyordu
# ("6 token'lık alt-dizi 3 kez tekrarlandı" gibi false-positive'ler).
# Eşik artık çok daha yükseğe (binlerce token) çekildi -- BEDELİ: gerçekten
# yozlaşmış bir döngü de artık en az 3 × _TEKRAR_ASGARI_PERIYOT (yaklaşık
# 12.000) token üretilmeden YAKALANAMAZ; kısa (13-48 token'lık) döngüleri
# yakaladığımız ÖNCEKİ gerçek Kaggle vakası artık bu eşiğin ALTINDA kalır.
# Bu BİLİNÇLİ bir ödünleşim: ARC'de sürekli ve MEŞRU sayı tekrarı, kısa
# döngü tespitinden çok daha sık/yaygın bir durum olduğu için tercih edildi.
_TEKRAR_AZAMI_PERIYOT = 6000
_TEKRAR_ASGARI_PERIYOT = 4000


def _tekrar_cezasi_uygula(logits: torch.Tensor, gecmis_tokenler: List[int], ceza: float) -> torch.Tensor:
    """HF'nin standart `repetition_penalty`siyle AYNI mantık: `gecmis_
    tokenler`de (bu ana kadar ÜRETİLEN tokenler) daha önce görülmüş her
    token'ın logit'i cezalandırılır (pozitifse cezaya BÖLÜNÜR, negatifse
    cezaYLA ÇARPILIR -- işareti koruyup büyüklüğü küçültür), böylece aynı
    token'ı TEKRAR seçme olasılığı düşer. `ceza<=1.0` iken hiçbir etkisi
    yoktur (no-op) -- kullanıcının fark ettiği yozlaşmış döngü olgusuna
    karşı `_tekrara_kilitlenme_periyodu`nun (kesin/geç kalan bir "zaten
    kilitlendi" tespiti) TAMAMLAYICISIdır: bu fonksiyon döngüye GİRMEYİ
    baştan ZORLAŞTIRIR, öteki ise girildiyse ERKEN çıkışı garanti eder."""
    if ceza is None or ceza <= 1.0 or not gecmis_tokenler:
        return logits
    benzersiz = torch.as_tensor(sorted(set(gecmis_tokenler)), dtype=torch.long, device=logits.device)
    degerler = logits[benzersiz]
    cezali = torch.where(degerler > 0, degerler / ceza, degerler * ceza)
    logits = logits.clone()
    logits[benzersiz] = cezali
    return logits


# HIZ (kullanıcının açık talebi -- "seyrekleştirmek yetmez, makalelerden
# mülhem, matematiksel olarak gerçekten hızlı bir usul kullan"): eski
# uygulama p'yi _TEKRAR_ASGARI_PERIYOT..._TEKRAR_AZAMI_PERIYOT (4000..6000)
# arasında TARIYOR, HER p adayı için tokenler[-p:] gibi p-uzunluklu YENİ
# Python listeleri DİLİMLEYİP karşılaştırıyordu -- bu O((azami-asgari) * p)
# demekti; azami_p=6000 civarında bu, TEK bir kontrolde onlarca milyon
# eleman karşılaştırmasına çıkabiliyordu. Burada Rabin-Karp'ın (Karp &
# Rabin, "Efficient randomized pattern-matching algorithms", 1987)
# POLİNOM ÖZ-İMZA (rolling hash) fikri kullanılıyor: kuyruktaki EN FAZLA
# 3*azami_p'lik pencerenin ÖN-EK hash'leri TEK GEÇİŞTE (O(pencere))
# hesaplanır; ardından HER p adayı için üç alt-dizinin (son p, ondan
# önceki p, ondan önceki p) hash'i O(1)'de karşılaştırılır -- p'ye göre
# DOĞRUSAL değil SABİT maliyetli. Hash eşleşmesi (ÇOK NADİR bir çakışma
# hariç) GERÇEK bir eşleşmenin KANITIdır; olası bir hash ÇAKIŞMASINA karşı
# (yanlış-pozitif YOZLAŞMIŞ-DÖNGÜ tespiti riskini SIFIRLAMAK için) hash
# eşleştiğinde YİNE DE gerçek dilim karşılaştırmasıyla DOĞRULANIR -- bu
# doğrulama yalnızca hash eşleştiğinde (pratikte hemen hiç) çalıştığından
# ortalama karmaşıklığı ETKİLEMEZ, sonucun eski uygulamayla BİREBİR AYNI
# (asla yanlış-pozitif/yanlış-negatif üretmeyen) olmasını GARANTİ eder.
_HASH_TABAN = 1_000_003
_HASH_MODULUS = (1 << 61) - 1  # Mersenne asalı -- Rabin-Karp icin standart secim


def _tekrara_kilitlenme_periyodu(tokenler: List[int]) -> Optional[int]:
    """`tokenler`in KUYRUĞU, uzunluğu p olan bir alt-dizinin ARDIŞIK EN AZ
    3 kez BİREBİR tekrarından mı oluşuyor (p, _TEKRAR_ASGARI_PERIYOT..
    _TEKRAR_AZAMI_PERIYOT arasında)? Öyleyse o p'yi döndürür (yozlaşmış
    döngü kanıtı), yoksa None. Semantik ESKİ O(p^2) uygulamayla BİREBİR
    AYNIDIR (bkz. yukarıdaki not) -- yalnızca ASİMPTOTİK olarak çok daha
    hızlıdır."""
    n = len(tokenler)
    azami_p = min(_TEKRAR_AZAMI_PERIYOT, n // 3)
    if azami_p < _TEKRAR_ASGARI_PERIYOT:
        return None

    pencere_uzunlugu = min(n, 3 * azami_p)
    pencere = tokenler[-pencere_uzunlugu:]
    L = len(pencere)

    on_hash = [0] * (L + 1)
    guc = [1] * (L + 1)
    for i, tok in enumerate(pencere):
        on_hash[i + 1] = (on_hash[i] * _HASH_TABAN + (tok + 1)) % _HASH_MODULUS
        guc[i + 1] = (guc[i] * _HASH_TABAN) % _HASH_MODULUS

    def _dilim_hash(basi: int, bitis: int) -> int:
        return (on_hash[bitis] - on_hash[basi] * guc[bitis - basi]) % _HASH_MODULUS

    for p in range(_TEKRAR_ASGARI_PERIYOT, azami_p + 1):
        if 3 * p > L:
            break
        h1 = _dilim_hash(L - p, L)
        h2 = _dilim_hash(L - 2 * p, L - p)
        h3 = _dilim_hash(L - 3 * p, L - 2 * p)
        if h1 == h2 == h3 and pencere[-p:] == pencere[-2 * p:-p] == pencere[-3 * p:-2 * p]:
            return p
    return None


def rwkv_ham_pth_mi(yol: str) -> bool:
    """Yol bir .pth DOSYASI ise (transformers dizini degil), native
    yukleme gerektigini soyler."""
    if os.path.isfile(yol):
        return True
    if os.path.isdir(yol) and not os.path.isfile(os.path.join(yol, "config.json")):
        return any(f.endswith(".pth") for f in os.listdir(yol))
    return False


class _RWKVCiktisi:
    __slots__ = ("logits", "past_key_values", "loss", "state")


class RWKVUyumluModel(torch.nn.Module):
    """rwkv pip paketindeki modeli, geri kalan boru hattinin (uret_sohbet,
    turbo_dfs, gorev_ozelinde_ince_ayar) beklediği HF-benzeri arayuze
    (forward(input_ids, past_key_values, use_cache, return_dict),
    .generate(), .device, .parameters()) sarmalar."""

    def __init__(self, rwkv_model: Any, strateji: str):
        super().__init__()
        self._rwkv = rwkv_model
        self._strateji = strateji
        self._cihaz = torch.device("cuda" if "cuda" in strateji else "cpu")

    @property
    def device(self) -> torch.device:
        return self._cihaz

    @property
    def ham_model(self) -> Any:
        """rwkv_batch.py'nin (toplu/batched çok-görev çözümü) ihtiyaç
        duyduğu ham `.z`/`.n_layer`/`.n_embd`/`.n_head`/`.head_size`
        özniteliklerini taşıyan, `rwkv` pip paketinin GERÇEK model
        nesnesi -- dışarıya `_rwkv` private alanına doğrudan erişmek
        yerine temiz bir kapı."""
        return self._rwkv

    def baslangic_durumu_kopyala(self) -> None:
        """rwkv_oturum.py için: TTT devre dışıysa (bkz. ttt_lora.lora_adaptoru_kur)
        öğrenilmiş bir durum yok -- `rwkv` paketi zaten `durum=None`'ı sıfır
        durum olarak yorumluyor, o yüzden burada da None döndürülür."""
        return None

    def _agirlik_sozlugu(self) -> Any:
        """RWKV-7 (RWKV_x070) ağırlıklarını `self.z` sözlüğünde tutar;
        eski (v4/5/6) `RWKV` sınıfı `self.w` kullanır. RWKV_V7_ON=1 ile
        artık daima RWKV_x070 kullanıldığından `z` önce denenir, ama
        eski sınıfla da (örn. test/gelecek uyumluluk) çalışmaya devam
        etsin diye `w`'ye geri düşülür. Gerçek kurulu `rwkv==0.8.32`
        kaynağı doğrudan okunarak doğrulandı (RWKV_x070.__init__ içinde
        `self.z = {}`, `self.w` YOK)."""
        sozluk = getattr(self._rwkv, "z", None)
        if sozluk is None:
            sozluk = getattr(self._rwkv, "w", None)
        if sozluk is None:
            raise AttributeError(
                "native rwkv modelinde ne 'z' (RWKV-7) ne de 'w' (eski sürüm) "
                "ağırlık sözlüğü bulundu; `rwkv` paketinin sürümü/mimarisi değişmiş olabilir."
            )
        return sozluk

    def parameters(self, recurse: bool = True):
        for tensor in self._agirlik_sozlugu().values():
            if isinstance(tensor, torch.Tensor):
                yield tensor

    def named_parameters(self, prefix: str = "", recurse: bool = True):
        for isim, tensor in self._agirlik_sozlugu().items():
            if isinstance(tensor, torch.Tensor):
                yield isim, tensor

    def forward(self, input_ids: torch.Tensor, position_ids: Any = None,
                past_key_values: Optional[List[Any]] = None, use_cache: bool = True,
                return_dict: bool = True, labels: Optional[torch.Tensor] = None) -> _RWKVCiktisi:
        """Batch'teki HER satiri kendi bagimsiz (state) ile tek tek isler
        (native RWKV RNN state'i satirlar arasinda paylasilamaz), sonuclari
        yigin haline getirir. past_key_values burada aslinda per-satir
        RWKV state listesidir (isim, geri kalan koddaki genel 'onbellek'
        kavramiyla uyumlu kalsin diye korunuyor).

        HER T konumundaki logit toplanir (yalnizca sonuncusu degil) --
        state-tuning'in ogrenilebilir baslangic durumu ile HEDEF cikti
        dizisinin TUM pozisyonlarindan ogrenmesi icin sart; mcts_dallanma.
        py'nin `outputs.logits[:, -1]` kullanimi da bu bicimle (B,T,V)
        sorunsuz calisir.

        ONEMLI PERFORMANS NOTU: `rwkv` paketinin KENDI forward() metodu,
        TEK bir cagriya BIRDEN FAZLA token listesi verilince (`len(idx)>1`)
        otomatik olarak `forward_seq`'e yonlenir -- bu, katman basina TEK
        Python/JIT cagrisiyla tum diziyi isler. Onceden burada her token
        icin AYRI bir `forward([token], state)` cagrisi yapiliyordu; bu,
        7.2B/32-katmanlik modelde katman-basi kurulum/JIT dispatch
        maliyetini T KERE tekrarlatip devasa bir yavaslamaya yol aciyordu.
        Simdi satir basina TEK cagri (`forward(tum_token_listesi, state,
        full_output=True)`) yapiliyor."""
        B, T = input_ids.shape
        durumlar = list(past_key_values) if past_key_values is not None else [None] * B

        baslangic = time.time()
        if B > _ILERLEME_ADIMI:
            print(f"[rwkv_native] ({self._cihaz}) forward(): {B} satır x {T} token, her satır TEK forward_seq çağrısıyla işleniyor...")
        tum_logitler = []
        yeni_durumlar = []
        for b in range(B):
            durum = durumlar[b]
            token_listesi = input_ids[b].tolist()
            if len(token_listesi) > 1:
                logitler, durum = self._rwkv.forward(token_listesi, durum, full_output=True)
                satir_logitleri = torch.as_tensor(logitler, device=self._cihaz)
            else:
                logit, durum = self._rwkv.forward(token_listesi, durum)
                satir_logitleri = torch.as_tensor(logit, device=self._cihaz).unsqueeze(0)
            tum_logitler.append(satir_logitleri)
            yeni_durumlar.append(durum)
            if (b + 1) % _ILERLEME_ADIMI == 0 or (b + 1) == B:
                gecen = time.time() - baslangic
                print(f"[rwkv_native] ({self._cihaz})   forward(): {b + 1}/{B} satır işlendi ({gecen:.1f} sn)")

        cikti = _RWKVCiktisi()
        cikti.logits = torch.stack(tum_logitler, dim=0)
        cikti.past_key_values = yeni_durumlar
        cikti.state = yeni_durumlar
        cikti.loss = None
        if labels is not None:
            kaydirilmis_logits = cikti.logits[:, :-1, :].reshape(-1, cikti.logits.shape[-1])
            kaydirilmis_hedefler = labels[:, 1:].reshape(-1)
            cikti.loss = torch.nn.functional.cross_entropy(
                kaydirilmis_logits, kaydirilmis_hedefler, ignore_index=-100,
            )
        return cikti

    def ileri_besle_tokenler(self, token_ids: List[int], durum: Optional[List[torch.Tensor]]) -> Tuple[Any, List[torch.Tensor]]:
        """Verilen token dizisini TEK bir forward çağrısıyla besler, (son_logit,
        güncellenmiş_durum) döndürür. ÇAĞIRAN TARAF durumu SAKLAYIP bir sonraki
        adımda buradan devam edebilir -- coz_yurutucu.py'nin çok-turlu araç
        döngüsünde (bkz. rwkv_oturum.py) AYNI tokenlerin İKİNCİ kez asla
        işlenmemesi tam olarak bu metotla sağlanır."""
        if not token_ids:
            raise ValueError("ileri_besle_tokenler: boş token listesi verildi")
        baslangic = time.time()
        if len(token_ids) > 1:
            son_logits, durum = self._rwkv.forward(token_ids, durum, full_output=False)
        else:
            son_logits, durum = self._rwkv.forward(token_ids, durum)
        if len(token_ids) > 1:
            gecen = time.time() - baslangic
            print(f"[rwkv_native] ({self._cihaz}) {len(token_ids)} token TEK çağrıyla işlendi ({gecen:.1f} sn, {len(token_ids) / max(gecen, 1e-6):.2f} token/sn).")
        return son_logits, durum

    def uret_devam(self, son_logits: Any, durum: Optional[List[torch.Tensor]], max_new_tokens: int,
                    do_sample: bool = True, temperature: Optional[float] = None,
                    top_p: Optional[float] = None, pad_token_id: Optional[int] = None,
                    repetition_penalty: Optional[float] = None,
                    ) -> Tuple[List[int], Any, List[torch.Tensor]]:
        """generate()'in oto-regresif kısmı: HAZIR bir (son_logits, durum)
        çiftinden devam eder, prefill'i TEKRARLAMAZ. Dönen `durum`, üretilen
        TÜM tokenleri de kapsar (RNN'in doğası gereği state zaten bu tokenleri
        "görmüş" haldedir) -- bir sonraki turde bu tokenleri TEKRAR beslemeye
        gerek yoktur.

        `repetition_penalty` (>1.0): daha önce üretilmiş tokenlerin
        olasılığını düşürür (bkz. _tekrar_cezasi_uygula) -- ÖZELLİKLE
        `do_sample=False` (greedy/argmax) iken kritik, çünkü greedy
        kararlar rastgelelik içermez: bir kez döngüye girerse hiçbir
        şansa dayalı kaçış yolu yoktur, ceza YOKSA sonsuza dek aynı
        döngüde kalır (kullanıcının gerçek transkriptinde gözlemlenen
        davranış tam olarak budur -- ajan preset'i `temp=0.0` kullanır)."""
        uretim_baslangici = time.time()
        uretilenler: List[int] = []
        for _adim in range(max_new_tokens):
            logit_bu_adim = torch.as_tensor(son_logits)
            if repetition_penalty and repetition_penalty > 1.0 and uretilenler:
                logit_bu_adim = _tekrar_cezasi_uygula(logit_bu_adim, uretilenler, repetition_penalty)
            olasiliklar = torch.softmax(
                logit_bu_adim / max(temperature or 1.0, 1e-4), dim=-1
            )
            if do_sample:
                sonraki_token = int(torch.multinomial(olasiliklar, 1).item())
            else:
                sonraki_token = int(torch.argmax(olasiliklar).item())

            uretilenler.append(sonraki_token)
            if (_adim + 1) % _ILERLEME_ADIMI == 0:
                gecen = time.time() - uretim_baslangici
                print(f"[rwkv_native] ({self._cihaz})   üretim: {_adim + 1}/{max_new_tokens} token üretildi ({gecen:.1f} sn, {(_adim + 1) / max(gecen, 1e-6):.2f} token/sn)")
            if pad_token_id is not None and sonraki_token == pad_token_id:
                break
            if (_adim + 1) % _TEKRAR_KONTROL_ADIMI == 0:
                periyot = _tekrara_kilitlenme_periyodu(uretilenler)
                if periyot is not None:
                    print(
                        f"[rwkv_native] ({self._cihaz})   YOZLAŞMIŞ DÖNGÜ tespit edildi: son "
                        f"{3 * periyot} token, {periyot} token'lık bir alt-diziyi ARDIŞIK 3 kez "
                        f"birebir tekrarlıyor -- {_adim + 1}. tokende üretim ERKEN durduruluyor "
                        f"(kalan {max_new_tokens - _adim - 1} token boşa harcanmayacak)."
                    )
                    break

            son_logits, durum = self._rwkv.forward([sonraki_token], durum)

        gecen_toplam = time.time() - uretim_baslangici
        print(f"[rwkv_native] ({self._cihaz}) üretim tamamlandı: {len(uretilenler)} token, {gecen_toplam:.1f} sn.")
        return uretilenler, son_logits, durum

    @torch.no_grad()
    def generate(self, input_ids: torch.Tensor, max_new_tokens: int = 768,
                 do_sample: bool = True, temperature: Optional[float] = None,
                 top_p: Optional[float] = None, pad_token_id: Optional[int] = None,
                 baslangic_durumu: Optional[List[torch.Tensor]] = None,
                 repetition_penalty: Optional[float] = None,
                 **_yoksayilan: Any) -> torch.Tensor:
        B, T = input_ids.shape
        assert B == 1, "native RWKV generate() şu an tek örnek (B=1) destekliyor"

        durum = [t.clone() for t in baslangic_durumu] if baslangic_durumu is not None else None
        prompt_token_listesi = input_ids[0].tolist()
        # PERFORMANS: onceden burada T ayrı forward([token], state) cagrisi
        # yapiliyordu (bkz. forward()'daki not) -- tum prompt'u TEK
        # forward_seq cagrisiyla isleyip yalnizca son pozisyonun logitini
        # istiyoruz (full_output=False, kutuphanenin varsayilani).
        son_logits, durum = self.ileri_besle_tokenler(prompt_token_listesi, durum)

        uretilenler, _son_logits, _durum = self.uret_devam(
            son_logits, durum, max_new_tokens,
            do_sample=do_sample, temperature=temperature, top_p=top_p, pad_token_id=pad_token_id,
            repetition_penalty=repetition_penalty,
        )
        tam_dizi = input_ids[0].tolist() + uretilenler
        return torch.tensor([tam_dizi], device=self._cihaz, dtype=torch.long)


class RWKVUyumluTokenizer:
    """rwkv.utils.PIPELINE'i, geri kalan kodun bekledigi tokenizer
    arayuzune (encode/decode/__call__/pad_token_id/eos_token_id) sarmalar.
    "rwkv_vocab_v20230424" pip paketiyle birlikte gelir; internet gerekmez."""

    def __init__(self, pipeline: Any):
        self._pipeline = pipeline
        self.pad_token_id = 0
        self.eos_token_id = 0

    def encode(self, metin: str, add_special_tokens: bool = True) -> List[int]:
        return self._pipeline.encode(metin)

    def decode(self, token_idler: Any, skip_special_tokens: bool = True) -> str:
        """KRİTİK: `rwkv` pip paketinin KENDİ `TRIE_TOKENIZER.decode()`'u
        (site-packages/rwkv_tokenizer.py) TÜM diziyi TEK bir `bytes.decode
        ('utf-8')` çağrısına sokuyor ve ETRAFINA ÇIPLAK bir `except:`
        koyuyor -- dizide TEK bir sorunlu id olsa bile (ör. bizim
        pad_token_id=0 -- ki bu id'nin idx2token'da HİÇ karşılığı yok,
        `decodeBytes` KeyError fırlatıyor -- ya da üretim tam bir çok-
        baytlı UTF-8 karakterin ORTASINDA kesildiyse) TÜM çıktıyı TEK bir
        '\\ufffd' karakterine indirger, geri kalan (belki binlerce
        karakterlik) GEÇERLİ metni de birlikte YOK EDER. Kullanıcının
        gerçek Kaggle transkriptinde "model çıktısı (2 karakter): '��'"
        olarak gördüğü şeyin GERÇEK kök nedeni -- muhtemelen modelin
        ürettiği asıl (belki tutarlı) metnin çoğu kaybolmuştu.

        Burada `decodeBytes` DOĞRUDAN kullanılır: (a) vocab'da karşılığı
        OLMAYAN id'ler (pad/eos sentinel'i dahil) SESSİZCE atlanır --
        çökmeye/tüm-diziyi-bozmaya değil, (b) `errors='replace'` ile
        yalnızca GERÇEKTEN geçersiz olan bayt aralığı '\\ufffd' olur,
        ETRAFINDAKİ geçerli metin KORUNUR."""
        if hasattr(token_idler, "tolist"):
            token_idler = token_idler.tolist()
        ham_tokenizer = self._pipeline.tokenizer
        idx2token = ham_tokenizer.idx2token
        parcalar = []
        for tok in token_idler:
            if skip_special_tokens and tok == self.pad_token_id:
                continue
            parca = idx2token.get(tok) if isinstance(idx2token, dict) else None
            if parca is None:
                continue  # vocab'da olmayan/özel id -- SESSİZCE atla, tüm diziyi bozmasın
            parcalar.append(parca)
        return b"".join(parcalar).decode("utf-8", errors="replace")

    def __call__(self, metin: str, return_tensors: Optional[str] = None, truncation: bool = True,
                 max_length: int = 4096, return_offsets_mapping: bool = False) -> Any:
        idler = self.encode(metin)[:max_length]
        if not idler:
            idler = [self.pad_token_id]
        if return_tensors == "pt":
            sozluk = {"input_ids": torch.tensor([idler], dtype=torch.long)}

            class _Tasinabilir(dict):
                def to(self, cihaz):
                    return _Tasinabilir({k: v.to(cihaz) for k, v in self.items()})

            return _Tasinabilir(sozluk)
        cikti = {"input_ids": idler}
        if return_offsets_mapping:
            cikti["offset_mapping"] = None  # native RWKV world tokenizer icin karakter-hizali degil
        return cikti


_RWKV_CUDA_ON_DENENDI = False


def _rwkv_cuda_kernelini_dene_etkinlestir() -> None:
    """`rwkv` paketi, RWKV_CUDA_ON=1 ile (rwkv.model.py satır 200-220
    civarı, WKV_7 sınıfı) token-başına üretimi ELLE YAZILMIŞ, derlenmiş bir
    CUDA kernel'iyle (rwkv7.cu) çalıştırabiliyor -- bu, bizim şu an
    kullandığımız genel PyTorch yolundan (ölçülen: ~16 token/sn, 7.2B
    modelde beklenenden yavaş) kayda değer ölçüde hızlı olabilir.

    RİSK: bu, `torch.utils.cpp_extension.load` ile bir CUDA uzantısını
    JIT DERLER; derleme ortamda nvcc/ninja yoksa ya da mimari uyuşmazsa
    İSTİSNA fırlatır -- ve bu istisna `rwkv.model` İLK import edildiğinde
    modül-seviyesinde gerçekleştiği için, ana süreçte doğrudan denersek
    BAŞARISIZLIK TÜM ÇALIŞTIRMAYI ÇÖKERTİR (geri dönüşü yok, çünkü RWKV
    tek model adayımız). Bu yüzden önce AYRI bir alt süreçte (asıl model
    yüklemesini hiç etkilemeden) "derlenebiliyor mu" diye TEK SEFERLİK
    sınanır; yalnızca o sınama BAŞARILI olursa RWKV_CUDA_ON=1 ana sürece
    de yansıtılır. Başarısız olursa (ya da zaten env var elle verilmişse,
    ya da CUDA yoksa) sessizce şimdiki (her zaman çalışan, ama yavaş)
    PyTorch yoluna devam edilir."""
    global _RWKV_CUDA_ON_DENENDI
    if _RWKV_CUDA_ON_DENENDI:
        return
    _RWKV_CUDA_ON_DENENDI = True

    if os.environ.get("RWKV_CUDA_ON") is not None:
        return  # kullanıcı zaten elle ayarlamış, dokunma
    if not torch.cuda.is_available():
        return  # özel CUDA kernel'i yalnızca GPU'da anlamlı

    import subprocess
    import sys as _sys

    prob_kodu = (
        "import os; os.environ['RWKV_V7_ON']='1'; os.environ['RWKV_CUDA_ON']='1'; "
        "import rwkv.model; print('RWKV_CUDA_PROB_OK')"
    )
    sonuc = None
    try:
        sonuc = subprocess.run(
            [_sys.executable, "-c", prob_kodu],
            capture_output=True, text=True, timeout=300,
        )
        basarili = sonuc.returncode == 0 and "RWKV_CUDA_PROB_OK" in sonuc.stdout
    except Exception as prob_hatasi:
        basarili = False
        print(f"[rwkv_native] RWKV_CUDA_ON sınaması çalıştırılamadı: {prob_hatasi}")

    if basarili:
        os.environ["RWKV_CUDA_ON"] = "1"
        print(
            "[rwkv_native] RWKV_CUDA_ON=1: özel CUDA kernel derlemesi BAŞARILI "
            "(ayrı bir alt süreçte sınandı) -- hızlandırılmış üretim yolu etkinleştiriliyor."
        )
    elif sonuc is not None:
        hata_ozeti = (sonuc.stderr or "")[-1000:]
        print(
            "[rwkv_native] RWKV_CUDA_ON=1 sınaması BAŞARISIZ -- genel (daha yavaş ama "
            f"HER ZAMAN çalışan) PyTorch yoluna devam ediliyor. Alt süreç hatası:\n{hata_ozeti}"
        )


def native_rwkv_yukle(pth_yolu: str, veri_tipi: torch.dtype = torch.bfloat16, cihaz: Optional[str] = None) -> RWKVUyumluModel:
    # RWKV_V7_ON=1 (model_yapilandirmalari.py'de import-oncesi ayarlanir)
    # `rwkv.model.RWKV`'yi DAIMA `RWKV_x070` sinifina cozer -- gercek
    # kurulu rwkv==0.8.32 kaynagi dogrudan okunarak dogrulandi (model.py
    # satir 1679-1680: `if RWKV_V7_ON == '1': RWKV = RWKV_x070`). Eski
    # (v4/5/6) `RWKV` sinifina ozgu `args.n_head`/`args.n_att` yamasi
    # bu yuzden hicbir zaman calismiyordu/gerekmiyordu -- RWKV_x070
    # kendi `self.n_head`/`self.head_size` degerlerini checkpoint'ten
    # dogrudan turetiyor (bkz. RWKVUyumluModel._agirlik_sozlugu).
    _rwkv_cuda_kernelini_dene_etkinlestir()
    from rwkv.model import RWKV

    # coklu_gpu.py, ayni modelin BAGIMSIZ birer kopyasini her GPU'ya
    # yerlestirmek icin `cihaz`'i acikca "cuda:0", "cuda:1" ... olarak
    # verir; `rwkv` paketinin strateji regex'i "cuda:N fp16" bicimini
    # zaten destekliyor.
    if cihaz is not None:
        strateji = f"{cihaz} fp16" if cihaz.startswith("cuda") else f"{cihaz} fp32"
    else:
        strateji = "cuda fp16" if torch.cuda.is_available() else "cpu fp32"
    if pth_yolu.endswith(".pth"):
        model_yolu = pth_yolu[: -len(".pth")]
    else:
        model_yolu = pth_yolu

    print(f"[rwkv_native] `rwkv` pip paketiyle native yükleniyor: {model_yolu} | strateji={strateji}")
    ham_model = RWKV(model=model_yolu, strategy=strateji)
    return RWKVUyumluModel(ham_model, strateji)


def native_rwkv_tokenizer_yukle() -> RWKVUyumluTokenizer:
    from rwkv.utils import PIPELINE

    pipeline = PIPELINE(None, "rwkv_vocab_v20230424")
    return RWKVUyumluTokenizer(pipeline)
