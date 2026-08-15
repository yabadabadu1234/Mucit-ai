import argparse
import atexit
import signal
import time
from typing import Any, Dict, List, Optional, Tuple

from arc import make_submission, read_tasks_from_single_file
from coz_yurutucu import gorevi_coz
from model_yapilandirmalari import MODEL_ONCELIK_SIRASI
from ttt_lora import lora_adaptoru_kur, temel_model_yukle, tokenizer_yukle

TEST_CHALLENGES_YOLU = "/kaggle/input/competitions/arc-prize-2026-arc-agi-2/arc-agi_test_challenges.json"

# Verilen orijinal koddaki `global_end_time = time.time() + 12*3600 - 600`
# deseniyle aynı usul: 11 saat 30 dakikalık toplam çalışma bütçesi.
CALISMA_SURESI_SANIYE = 11 * 3600 + 30 * 60


class _SonuCuKaydedici:
    """Kod NASIL sona ererse ersin -- hata, dıştan kesme (SIGTERM/SIGINT),
    ya da süre bütçesinin dolması -- o ana kadar üretilmiş TÜM tahminlerin
    submission.json'a mutlaka yazılmasını garanti eder. Ana eğitim
    döngüsünde (main_egitim_dongusu.py) checkpoint'in HER durumda
    kaydolmasını sağlayan usulün aynısı: periyodik ara-kayıt + try/finally
    + sinyal yakalayıcı ile son-kayıt garantisi."""

    def __init__(self, tasks: List[Any], cikti_yolu: str) -> None:
        self.tasks = tasks
        self.cikti_yolu = cikti_yolu
        self.predictions: List[List[Any]] = []
        self._son_yazilan_sayi = -1
        self._kaydedildi = False

        atexit.register(self._son_kayit)
        signal.signal(signal.SIGTERM, self._sinyal_ile_kaydet)
        signal.signal(signal.SIGINT, self._sinyal_ile_kaydet)

    def ekle(self, tahmin: List[Any]) -> None:
        self.predictions.append(tahmin)
        self._ara_kayit()

    def _bekleyen_gorevleri_bos_doldur(self) -> List[List[Any]]:
        eksik = len(self.tasks) - len(self.predictions)
        bos = [[[0, 0], [0, 0]], [[0, 0], [0, 0]]]
        return self.predictions + [bos for _ in range(max(0, eksik))]

    def _ara_kayit(self) -> None:
        # Her görevden sonra diske yazılır; süreç o an ölse bile o ana
        # kadarki tüm sonuçlar submission.json'da kalır.
        if len(self.predictions) == self._son_yazilan_sayi:
            return
        tam_liste = self._bekleyen_gorevleri_bos_doldur()
        try:
            make_submission(self.tasks, tam_liste, path=self.cikti_yolu)
            self._son_yazilan_sayi = len(self.predictions)
        except Exception as yazma_hatasi:
            print(f"[gonderim_uret] ARA KAYIT HATASI (yoksayılıp devam edilecek): {yazma_hatasi}")

    def _son_kayit(self) -> None:
        if self._kaydedildi:
            return
        self._kaydedildi = True
        print(
            f"[gonderim_uret] SON KAYIT: {len(self.predictions)}/{len(self.tasks)} görev tamamlanmış "
            f"haliyle '{self.cikti_yolu}' yazılıyor..."
        )
        tam_liste = self._bekleyen_gorevleri_bos_doldur()
        make_submission(self.tasks, tam_liste, path=self.cikti_yolu)
        print(f"[gonderim_uret] SON KAYIT tamamlandı: '{self.cikti_yolu}'.")

    def _sinyal_ile_kaydet(self, signum: int, frame: Any) -> None:
        print(f"[gonderim_uret] Sinyal {signum} alındı, mevcut sonuçlar kaydedilip çıkılıyor...")
        self._son_kayit()
        raise SystemExit(128 + signum)


def ana_model_ile_dene_yedekle(oncelik_sirasi: List[str] = MODEL_ONCELIK_SIRASI) -> Tuple[str, Any, Any]:
    """oncelik_sirasi[0] ANA modeldir; yuklemesi basarisiz olursa (dosya
    eksik/bozuk, OOM, mimari desteklenmiyor vb.) sirayla sonraki yedek
    modele duser. Hicbiri yuklenemezse son hatayi firlatir."""
    son_hata: Optional[Exception] = None
    for i, aday_aile in enumerate(oncelik_sirasi):
        etiket = "ANA MODEL" if i == 0 else f"YEDEK MODEL #{i}"
        print(f"[gonderim_uret] {etiket} deneniyor: '{aday_aile}' (yerel dosya, internet KAPALI)...")
        try:
            base_model = temel_model_yukle(aday_aile)
            tokenizer = tokenizer_yukle(aday_aile)
            print(f"[gonderim_uret] '{aday_aile}' başarıyla yüklendi, bu model kullanılacak.")
            return aday_aile, base_model, tokenizer
        except Exception as exc:
            print(f"[gonderim_uret] '{aday_aile}' yüklenemedi: {exc}")
            son_hata = exc
    raise RuntimeError(
        f"Öncelik sırasındaki hiçbir model yüklenemedi ({oncelik_sirasi}). Son hata: {son_hata}"
    )


def submission_uret(
    model_ailesi: Optional[str] = None,
    oncelik_sirasi: List[str] = MODEL_ONCELIK_SIRASI,
    cikti_yolu: str = "submission.json",
    cogaltma_n: int = 16,
    ttt_adim_sayisi: int = 20,
    calisma_suresi_saniye: float = CALISMA_SURESI_SANIYE,
) -> Dict[str, Any]:

    bitis_zamani = time.time() + calisma_suresi_saniye
    print(
        f"[gonderim_uret] Çalışma bütçesi: {calisma_suresi_saniye / 3600:.2f} saat "
        f"(bitiş: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(bitis_zamani))})"
    )

    tasks = read_tasks_from_single_file(TEST_CHALLENGES_YOLU, test=True)
    print(f"[gonderim_uret] {len(tasks)} alt-görev bulundu: {TEST_CHALLENGES_YOLU}")

    kaydedici = _SonuCuKaydedici(tasks, cikti_yolu)

    try:
        if model_ailesi is not None:
            print(f"[gonderim_uret] '{model_ailesi}' ailesi icin yerel model yukleniyor (internet KAPALI)...")
            base_model = temel_model_yukle(model_ailesi)
            tokenizer = tokenizer_yukle(model_ailesi)
        else:
            model_ailesi, base_model, tokenizer = ana_model_ile_dene_yedekle(oncelik_sirasi)

        lora_model = lora_adaptoru_kur(base_model, model_ailesi)

        varsayilan_lora_agirliklari = None
        if hasattr(lora_model, "peft_config"):
            from peft import get_peft_model_state_dict

            varsayilan_lora_agirliklari = get_peft_model_state_dict(lora_model, adapter_name="default")
            varsayilan_lora_agirliklari = {k: v.clone().detach() for k, v in varsayilan_lora_agirliklari.items()}

        baslangic = time.time()

        for i, task in enumerate(tasks, start=1):
            if time.time() > bitis_zamani:
                print(
                    f"[gonderim_uret] Çalışma süresi bütçesi doldu "
                    f"({(time.time() - baslangic) / 3600:.2f} saat), kalan {len(tasks) - i + 1} görev "
                    f"boş tahminle bırakılıp durduruluyor."
                )
                break

            try:
                sonuc = gorevi_coz(
                    lora_model, tokenizer, model_ailesi, task,
                    varsayilan_lora_agirliklari=varsayilan_lora_agirliklari,
                    cogaltma_n=cogaltma_n, ttt_adim_sayisi=ttt_adim_sayisi,
                )
                kaydedici.ekle([sonuc["attempt_1"], sonuc["attempt_2"]])
            except Exception as exc:
                print(f"[gonderim_uret] Görev {task.name} başarısız, boş tahmin yazılıyor: {exc}")
                kaydedici.ekle([[[0, 0], [0, 0]], [[0, 0], [0, 0]]])

            gecen = time.time() - baslangic
            print(f"[gonderim_uret] ({i}/{len(tasks)}) {task.name} tamamlandı | toplam süre: {gecen:.1f} sn")

    finally:
        # Hata ile mi, sinyal ile mi, süre bitmesiyle mi, yoksa normal
        # tamamlanma ile mi buraya gelindiği fark etmez -- o ana kadarki
        # tüm sonuçlar burada KESİN olarak diske yazılır.
        kaydedici._son_kayit()

    submission = make_submission(tasks, kaydedici._bekleyen_gorevleri_bos_doldur(), path=cikti_yolu)
    print(f"[gonderim_uret] Yazıldı: {cikti_yolu} ({len(submission)} görev)")
    return submission


def _cli() -> None:
    ayristirici = argparse.ArgumentParser(description="ARC-AGI 2026 TTT+LoRA+arac-cagirma gönderim üretici")
    ayristirici.add_argument(
        "--model_ailesi", type=str, default=None, choices=["rwkv", "mamba", "falcon_mamba"],
        help="Belirtilmezse MODEL_ONCELIK_SIRASI'na göre ana model denenir, başarısız olursa yedeğe düşer.",
    )
    ayristirici.add_argument("--cikti", type=str, default="submission.json")
    ayristirici.add_argument("--cogaltma_n", type=int, default=16)
    ayristirici.add_argument("--ttt_adim_sayisi", type=int, default=20)
    ayristirici.add_argument("--calisma_suresi_saniye", type=float, default=CALISMA_SURESI_SANIYE)
    args = ayristirici.parse_args()

    submission_uret(
        model_ailesi=args.model_ailesi, cikti_yolu=args.cikti,
        cogaltma_n=args.cogaltma_n, ttt_adim_sayisi=args.ttt_adim_sayisi,
        calisma_suresi_saniye=args.calisma_suresi_saniye,
    )


if __name__ == "__main__":
    _cli()
