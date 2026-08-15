import argparse
import json
import time
from typing import Any, Dict

from arc_veri import YOLLAR, tum_test_gorevlerini_yukle
from cozucu import gorevi_coz
from ttt_lora import (
    adaptoru_sifirla,
    gorev_ozelinde_ince_ayar,
    lora_adaptoru_kur,
    temel_model_yukle,
    tokenizer_yukle,
    uret,
)


def submission_uret(
    model_id: str,
    cikti_yolu: str = "submission.json",
    cihaz: str = "cuda",
    cogaltma_hedefi: int = 50,
    ttt_adim_sayisi: int = 20,
) -> Dict[str, Any]:

    print(f"[gonderim_uret] Temel model yükleniyor: {model_id}")
    base_model = temel_model_yukle(model_id, cihaz=cihaz)
    tokenizer = tokenizer_yukle(model_id)
    lora_model = lora_adaptoru_kur(base_model, model_id)

    test_gorevleri = tum_test_gorevlerini_yukle()
    print(f"[gonderim_uret] {len(test_gorevleri)} görev bulundu: {YOLLAR['test_challenges']}")

    def ince_ayar_fn(lm, tok, metinler):
        return gorev_ozelinde_ince_ayar(lm, tok, metinler, adim_sayisi=ttt_adim_sayisi)

    submission: Dict[str, Any] = {}
    baslangic = time.time()

    for i, (task_id, gorev) in enumerate(test_gorevleri.items(), start=1):
        adaptoru_sifirla(lora_model)

        try:
            sonuc = gorevi_coz(
                lora_model, tokenizer, task_id, gorev,
                uret_fn=uret, ince_ayar_fn=ince_ayar_fn,
                cogaltma_hedefi=cogaltma_hedefi, ttt_adim_sayisi=ttt_adim_sayisi,
            )
        except Exception as exc:
            print(f"[gonderim_uret] Görev {task_id} başarısız, boş tahmin yazılıyor: {exc}")
            n_test = len(gorev.get("test", [1]))
            sonuc = [{"attempt_1": [[0, 0], [0, 0]], "attempt_2": [[0, 0], [0, 0]]} for _ in range(n_test)]

        submission[task_id] = sonuc
        gecen = time.time() - baslangic
        print(f"[gonderim_uret] ({i}/{len(test_gorevleri)}) {task_id} tamamlandı | toplam süre: {gecen:.1f} sn")

    with open(cikti_yolu, "w", encoding="utf-8") as f:
        json.dump(submission, f)

    print(f"[gonderim_uret] Yazıldı: {cikti_yolu} ({len(submission)} görev)")
    return submission


def _cli() -> None:
    ayristirici = argparse.ArgumentParser(description="ARC-AGI 2026 TTT+LoRA gönderim üretici")
    ayristirici.add_argument("--model_id", type=str, default="tiiuae/falcon-mamba-7b-instruct")
    ayristirici.add_argument("--cikti", type=str, default="submission.json")
    ayristirici.add_argument("--cihaz", type=str, default="cuda")
    ayristirici.add_argument("--cogaltma_hedefi", type=int, default=50)
    ayristirici.add_argument("--ttt_adim_sayisi", type=int, default=20)
    args = ayristirici.parse_args()

    submission_uret(
        model_id=args.model_id, cikti_yolu=args.cikti, cihaz=args.cihaz,
        cogaltma_hedefi=args.cogaltma_hedefi, ttt_adim_sayisi=args.ttt_adim_sayisi,
    )


if __name__ == "__main__":
    _cli()
