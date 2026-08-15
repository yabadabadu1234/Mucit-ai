import argparse
import time
from typing import Any, Dict, List, Optional, Tuple

from arc import make_submission, read_tasks_from_single_file
from coz_yurutucu import gorevi_coz
from model_yapilandirmalari import MODEL_ONCELIK_SIRASI
from ttt_lora import lora_adaptoru_kur, temel_model_yukle, tokenizer_yukle

TEST_CHALLENGES_YOLU = "/kaggle/input/competitions/arc-prize-2026-arc-agi-2/arc-agi_test_challenges.json"


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
) -> Dict[str, Any]:

    if model_ailesi is not None:
        print(f"[gonderim_uret] '{model_ailesi}' ailesi icin yerel model yukleniyor (internet KAPALI)...")
        base_model = temel_model_yukle(model_ailesi)
        tokenizer = tokenizer_yukle(model_ailesi)
    else:
        model_ailesi, base_model, tokenizer = ana_model_ile_dene_yedekle(oncelik_sirasi)

    lora_model = lora_adaptoru_kur(base_model, model_ailesi)

    from peft import get_peft_model_state_dict

    varsayilan_lora_agirliklari = get_peft_model_state_dict(lora_model, adapter_name="default")
    varsayilan_lora_agirliklari = {k: v.clone().detach() for k, v in varsayilan_lora_agirliklari.items()}

    tasks = read_tasks_from_single_file(TEST_CHALLENGES_YOLU, test=True)
    print(f"[gonderim_uret] {len(tasks)} alt-görev bulundu: {TEST_CHALLENGES_YOLU}")

    predictions = []
    baslangic = time.time()

    for i, task in enumerate(tasks, start=1):
        try:
            sonuc = gorevi_coz(
                lora_model, tokenizer, model_ailesi, task,
                varsayilan_lora_agirliklari=varsayilan_lora_agirliklari,
                cogaltma_n=cogaltma_n, ttt_adim_sayisi=ttt_adim_sayisi,
            )
            predictions.append([sonuc["attempt_1"], sonuc["attempt_2"]])
        except Exception as exc:
            print(f"[gonderim_uret] Görev {task.name} başarısız, boş tahmin yazılıyor: {exc}")
            predictions.append([[[0, 0], [0, 0]], [[0, 0], [0, 0]]])

        gecen = time.time() - baslangic
        print(f"[gonderim_uret] ({i}/{len(tasks)}) {task.name} tamamlandı | toplam süre: {gecen:.1f} sn")

    submission = make_submission(tasks, predictions, path=cikti_yolu)
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
    args = ayristirici.parse_args()

    submission_uret(
        model_ailesi=args.model_ailesi, cikti_yolu=args.cikti,
        cogaltma_n=args.cogaltma_n, ttt_adim_sayisi=args.ttt_adim_sayisi,
    )


if __name__ == "__main__":
    _cli()
