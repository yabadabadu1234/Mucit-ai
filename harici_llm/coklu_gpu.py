"""
Ayni modelin N adet (azami 4) BAGIMSIZ kopyasini N ayri GPU'ya yerlestirip,
N farkli ARC gorevini GERCEKTEN paralel (donanim seviyesinde) cozer -- ama
TEK bir Python surecinden/thread'inden, HICBIR CPU-seviyesi senkronizasyon
bariyeri (threading.Thread, multiprocessing, Lock, join, barrier) KULLANMADAN.

YONTEM -- round-robin "boru hattı":
Tek bir dongude, sirayla GPU0'a bir token-uretim adimi, GPU1'e bir adim,
GPU2'ye bir adim, GPU3'e bir adim KOMUTU GONDERILIR (CUDA kernel'i
kuyruklanir). CUDA, her cihazin kendi stream'inde bu komutlari BAGIMSIZ
calistirir -- host (CPU) tarafinda tek engelleyici nokta, bir sonraki
tokeni belirlemek icin gereken orneklem (.item()) adimidir, ve bu SADECE
o adimi atan GPU'nun kendi stream'ini bekler; diger 3 GPU'nun COKTAN
kuyruklanmis islerini durdurmaz/etkilemez. Bu yuzden bir sure sonra tum
GPU'lar donanim seviyesinde gercekten paralel calisiyor gibi olur --
hicbir thread/process/lock gerekmeden, TEK surecten "boru hatti" ile.

Bu dosya salt-cikarim (TTT'siz) calisir: gorev-basina ince-ayar (LoRA/
state-tuning backprop) burada YOK -- o, GPU basina ayri, blocklayici bir
egitim adimi gerektirir ve round-robin token-adimlama modeliyle
uyusmuyor. coz_yurutucu.gorevi_coz (tek-GPU, TTT'li) yol olarak kaliyor;
bu modul onun YERINE degil, coklu-GPU cikarim ihtiyaci icin YANINDA var.
"""
import time
from typing import Any, Dict, List, Optional

import torch

from arc import Task
from araclar import CevapDefteri, arac_cagrilarini_ayikla, arac_cagrisini_yurut, tool_response_mesaji_olustur
from coz_yurutucu import BOS_TAHMIN, _ilk_mesajlar, _ARAC_CAGRISI_YOK_UYARISI
from model_yapilandirmalari import RWKV
from transkript import transkript_satiri_yaz
from ttt_lora import mesajlari_metne_donustur, rwkv_tek_mesaji_sar, tokenizer_yukle, uretim_ayarlarini_al, yerel_model_yolu


def dort_kopya_yukle(model_ailesi: str = RWKV, azami_gpu: int = 4):
    """Modelin GPU basina BAGIMSIZ bir kopyasini yukler (agirliklar
    paylasilmaz -- her GPU kendi VRAM'inde tam bir kopya tasir)."""
    from rwkv_native import native_rwkv_yukle, rwkv_ham_pth_mi

    if not torch.cuda.is_available():
        raise RuntimeError("coklu_gpu.dort_kopya_yukle: CUDA yok, GPU başına ayrı kopya yüklenemez.")
    gpu_sayisi = min(torch.cuda.device_count(), azami_gpu)
    if gpu_sayisi < 1:
        raise RuntimeError("coklu_gpu.dort_kopya_yukle: hiç CUDA cihazı görünmüyor.")

    yol = yerel_model_yolu(model_ailesi)
    if not rwkv_ham_pth_mi(yol):
        raise RuntimeError("coklu_gpu şu an yalnızca native RWKV (.pth) yolunu destekliyor.")

    modeller = []
    for i in range(gpu_sayisi):
        print(f"[coklu_gpu] cuda:{i} için model kopyası yükleniyor...")
        modeller.append(native_rwkv_yukle(yol, cihaz=f"cuda:{i}"))

    tokenizer = tokenizer_yukle(model_ailesi)
    print(f"[coklu_gpu] {gpu_sayisi} GPU'da modelin BAĞIMSIZ birer kopyası hazır: {[f'cuda:{i}' for i in range(gpu_sayisi)]}")
    return modeller, tokenizer


class _Oturum:
    """Tek bir GPU'daki tek bir gorevin cozum durumu (kendi RNN state'i,
    kendi mesaj gecmisi, kendi CevapDefteri'i). adim() cagrildikca TEK
    token uretir; tur bittiginde arac-cagirma/parse islemlerini (ucuz,
    CPU-agirlikli) senkron yapar ve bir sonraki turu baslatir."""

    def __init__(self, gpu_index: int, model: Any, tokenizer: Any, task: Task,
                 azami_tur: int, azami_yeni_token: int, uretim_ayarlari: Dict[str, Any]):
        self.gpu_index = gpu_index
        self.model = model
        self.tokenizer = tokenizer
        self.task = task
        self.azami_tur = azami_tur
        self.azami_yeni_token = azami_yeni_token
        self.uretim_ayarlari = uretim_ayarlari

        # uret_devam_adim yalnizca do_sample/temperature kabul ediyor;
        # pad_token_id (tur-sonu tespiti icin) burada AYRI tutulur,
        # model'e KWARGS olarak GECIRILMEZ.
        self._adim_ayarlari = {k: v for k, v in uretim_ayarlari.items() if k in ("do_sample", "temperature")}

        self.defter = CevapDefteri()
        self.mesajlar = _ilk_mesajlar(task)
        self.durum = model.baslangic_durumu_kopyala() if hasattr(model, "baslangic_durumu_kopyala") else None
        self.son_logits: Any = None
        self.tur = 0
        self.uretilenler: List[int] = []
        self.bitti = False
        self.cevap: Optional[List[List[int]]] = None
        self.gonderildi_mi = False

        self._metin_isle(mesajlari_metne_donustur(tokenizer, RWKV, self.mesajlar))
        self._yeni_tur_baslat()

    def _metin_isle(self, metin: str) -> None:
        token_idler = self.tokenizer.encode(metin)
        if not token_idler:
            return
        self.son_logits, self.durum = self.model.ileri_besle_tokenler(token_idler, self.durum)

    def _yeni_tur_baslat(self) -> None:
        self.tur += 1
        self.uretilenler = []
        if self.tur > self.azami_tur:
            self.bitti = True

    def adim(self) -> None:
        """TEK token uretim adimi (bu oturumun GPU'sunda kuyruklanir)."""
        if self.bitti:
            return
        token, self.son_logits, self.durum = self.model.uret_devam_adim(
            self.son_logits, self.durum, **self._adim_ayarlari
        )
        self.uretilenler.append(token)
        pad_id = self.tokenizer.pad_token_id
        tamam = (pad_id is not None and token == pad_id) or len(self.uretilenler) >= self.azami_yeni_token
        if tamam:
            self._tur_bitir()

    def _tur_bitir(self) -> None:
        metin = self.tokenizer.decode(self.uretilenler, skip_special_tokens=True)
        self.mesajlar.append({"role": "assistant", "content": metin})
        transkript_satiri_yaz({
            "gorev": self.task.name, "deneme": f"gpu{self.gpu_index}", "tur": self.tur,
            "rol": "assistant", "icerik": metin,
        })

        cagrilar = arac_cagrilarini_ayikla(metin)
        if not cagrilar:
            mesaj = {"role": "user", "content": _ARAC_CAGRISI_YOK_UYARISI}
            self.mesajlar.append(mesaj)
            self._metin_isle(rwkv_tek_mesaji_sar(mesaj))
            self._yeni_tur_baslat()
            return

        for cagri in cagrilar:
            sonuc = arac_cagrisini_yurut(cagri, self.defter)
            mesaj = {"role": "user", "content": tool_response_mesaji_olustur(sonuc)}
            self.mesajlar.append(mesaj)
            self._metin_isle(rwkv_tek_mesaji_sar(mesaj))
            transkript_satiri_yaz({
                "gorev": self.task.name, "deneme": f"gpu{self.gpu_index}", "tur": self.tur,
                "rol": "arac-sonucu", "arac": cagri.get("name"), "icerik": sonuc,
            })
            if cagri.get("name") == "submit_answer" and sonuc.get("basarili"):
                self.cevap = self.defter.kaydedilen_cevap
                self.gonderildi_mi = True
                self.bitti = True
                return

        self._yeni_tur_baslat()


class CokluGPUCozucu:
    """N GPU'daki N bağımsız model kopyasını, N görevi round-robin (tek
    token adımı sırayla her GPU'ya) ilerleterek kullanır. Bir GPU'nun
    görevi bitince, kuyruktaki bir sonraki görev o GPU'ya atanır --
    böylece tüm GPU'lar sürekli meşgul kalır."""

    def __init__(self, modeller: List[Any], tokenizer: Any, azami_tur: int = 1,
                 azami_yeni_token: int = 60000, uretim_ayarlari: Optional[Dict[str, Any]] = None):
        self.modeller = modeller
        self.tokenizer = tokenizer
        self.azami_tur = azami_tur
        self.azami_yeni_token = azami_yeni_token
        self.uretim_ayarlari = uretim_ayarlari if uretim_ayarlari is not None else uretim_ayarlarini_al(RWKV, tokenizer)

    def _yeni_oturum(self, gpu_index: int, task: Task) -> _Oturum:
        return _Oturum(
            gpu_index, self.modeller[gpu_index], self.tokenizer, task,
            self.azami_tur, self.azami_yeni_token, self.uretim_ayarlari,
        )

    def coz(self, tasks: List[Task], bitis_zamani: Optional[float] = None) -> Dict[str, Dict[str, Any]]:
        """Verilen tum gorevleri, GPU sayisi kadar EL ILE round-robin
        yürütür. `bitis_zamani` (time.time() cinsinden) verilirse, o ana
        kadar bitmemiş oturumlar bos tahminle kapatılır (ana `gonderim_
        uret.py`'deki bütçe-doldu davranışının aynısı)."""
        gpu_sayisi = len(self.modeller)
        sonuclar: Dict[str, Dict[str, Any]] = {}
        kuyruk = list(tasks)
        oturumlar: List[Optional[_Oturum]] = [None] * gpu_sayisi

        toplam = len(tasks)
        bitirilen = 0
        baslangic = time.time()

        while True:
            for gpu_index in range(gpu_sayisi):
                if oturumlar[gpu_index] is None and kuyruk:
                    oturumlar[gpu_index] = self._yeni_oturum(gpu_index, kuyruk.pop(0))

            if all(o is None for o in oturumlar):
                break

            if bitis_zamani is not None and time.time() > bitis_zamani:
                for o in oturumlar:
                    if o is not None and not o.bitti:
                        sonuclar[o.task.name] = {"attempt_1": BOS_TAHMIN, "attempt_1_gonderildi_mi": False}
                for kalan_gorev in kuyruk:
                    sonuclar[kalan_gorev.name] = {"attempt_1": BOS_TAHMIN, "attempt_1_gonderildi_mi": False}
                print(f"[coklu_gpu] Süre bütçesi doldu, kalan görevler boş tahminle bırakıldı.")
                break

            # -- BURASI round-robin cekirdegi: hicbir GPU'nun sonucunu
            # BEKLEMEDEN sirayla hepsine BIRER adim gonderiyoruz. --
            for gpu_index in range(gpu_sayisi):
                oturum = oturumlar[gpu_index]
                if oturum is None:
                    continue
                oturum.adim()
                if oturum.bitti:
                    sonuclar[oturum.task.name] = {
                        "attempt_1": oturum.cevap if oturum.cevap is not None else BOS_TAHMIN,
                        "attempt_1_gonderildi_mi": oturum.gonderildi_mi,
                    }
                    bitirilen += 1
                    gecen = time.time() - baslangic
                    print(f"[coklu_gpu] (cuda:{gpu_index}) ({bitirilen}/{toplam}) {oturum.task.name} tamamlandı | toplam süre: {gecen:.1f} sn")
                    oturumlar[gpu_index] = None

        return sonuclar
