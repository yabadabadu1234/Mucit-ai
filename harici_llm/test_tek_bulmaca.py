import sys
from typing import Any, List

import torch
import torch.nn as nn

from cozucu import gorevi_coz
from kod_ajani import kodu_egitim_ornekleriyle_dogrula, kodu_guvenle_calistir, kodu_metinden_cikar

_DOGRU_TRANSFORM_KODU = '''
def transform(grid):
    h = len(grid)
    w = len(grid[0])

    bolucu_col = None
    for c in range(w):
        renkler = {grid[r][c] for r in range(h)}
        if len(renkler) != 1:
            continue
        renk = next(iter(renkler))
        if renk == 0:
            continue
        renk_baska_yerde_var = any(
            grid[r][cc] == renk for r in range(h) for cc in range(w) if cc != c
        )
        if not renk_baska_yerde_var:
            bolucu_col = c
            break
    if bolucu_col is None:
        return [row[:] for row in grid]

    sol_toplam = sum(1 for r in range(h) for c in range(bolucu_col) if grid[r][c] != 0)
    sag_toplam = sum(1 for r in range(h) for c in range(bolucu_col + 1, w) if grid[r][c] != 0)
    kaynak_sol = sol_toplam >= sag_toplam

    sonuc = [row[:] for row in grid]

    for r in range(h):
        if kaynak_sol:
            kaynak_hucreler = [(bolucu_col - c, grid[r][c]) for c in range(bolucu_col) if grid[r][c] != 0]
            hedef_uzunluk = w - bolucu_col - 1
        else:
            kaynak_hucreler = [(c - bolucu_col, grid[r][c]) for c in range(bolucu_col + 1, w) if grid[r][c] != 0]
            hedef_uzunluk = bolucu_col

        if not kaynak_hucreler:
            continue

        periyot = {}
        min_mesafe = {}
        for mesafe, renk in kaynak_hucreler:
            periyot[renk] = periyot.get(renk, 0) + 1
            min_mesafe[renk] = min(min_mesafe.get(renk, mesafe), mesafe)

        for d in range(1, hedef_uzunluk + 1):
            adaylar = [renk for renk, p in periyot.items() if (d - 1) % p == 0]
            if not adaylar:
                continue
            kazanan = min(adaylar, key=lambda renk: min_mesafe[renk])

            if kaynak_sol:
                hedef_col = bolucu_col + d
            else:
                hedef_col = bolucu_col - d
            sonuc[r][hedef_col] = kazanan

    return sonuc
'''.strip()

_MODEL_CANNED_YANIT = f"""### Final Rule Sentence

**"On one side of the vertical divider line, every color's total pixel count becomes that
color's repetition period, and it is placed moving away from the divider toward the other
side; when placements from different colors collide, the color that was closer to the
divider takes priority and is written on top of the others."**

```python
{_DOGRU_TRANSFORM_KODU}
```
"""


def _sentetik_1ae2feb7_gorevi() -> dict:
    train_girdi_1 = [
        [1, 1, 0, 5, 0, 0, 0, 0, 0],
        [4, 3, 4, 5, 0, 0, 0, 0, 0],
    ]
    train_cikti_1 = [
        [1, 1, 0, 5, 1, 0, 1, 0, 1],
        [4, 3, 4, 5, 4, 3, 4, 3, 4],
    ]

    train_girdi_2 = [
        [2, 0, 2, 5, 0, 0, 0, 0, 0],
    ]
    train_cikti_2 = [
        [2, 0, 2, 5, 2, 0, 2, 0, 2],
    ]

    test_girdi = [
        [0, 0, 0, 5, 2, 6, 2, 0, 0],
    ]
    test_beklenen_cikti = [
        [2, 6, 2, 5, 2, 6, 2, 0, 0],
    ]

    return {
        "train": [
            {"input": train_girdi_1, "output": train_cikti_1},
            {"input": train_girdi_2, "output": train_cikti_2},
        ],
        "test": [
            {"input": test_girdi, "output": test_beklenen_cikti},
        ],
    }


class _VasifsizMockDil(nn.Module):

    def __init__(self, canned_yanit: str):
        super().__init__()
        self.canned_yanit = canned_yanit
        self.gomulu = nn.Embedding(64, 8)
        self.baslik = nn.Linear(8, 64)
        self.egitim_adim_sayaci = 0

    def parameters(self, recurse: bool = True):
        return super().parameters(recurse)

    def forward(self, girdi_idler: torch.Tensor) -> torch.Tensor:
        x = self.gomulu(girdi_idler % 64)
        return self.baslik(x)


class _VasifsizMockTokenizer:

    def __call__(self, metin: str, return_tensors: str = "pt", truncation: bool = True, max_length: int = 1024):
        kodlar = [ord(c) % 64 for c in metin[:max_length]]
        if not kodlar:
            kodlar = [0]
        return {"input_ids": torch.tensor([kodlar], dtype=torch.long)}


def _mock_uret_fn(lora_model: Any, tokenizer: Any, sistem: str, kullanici: str,
                   sicaklik: float, ornekleme: bool) -> str:

    girdi = tokenizer(sistem + kullanici)
    with torch.no_grad():
        _ = lora_model(girdi["input_ids"].to(next(lora_model.parameters()).device))
    return lora_model.canned_yanit


def _mock_ince_ayar_fn(lora_model: Any, tokenizer: Any, egitim_metinleri: List[str]) -> List[float]:
    optimizer = torch.optim.AdamW(lora_model.parameters(), lr=1e-3)
    kayip_gecmisi = []
    cihaz = next(lora_model.parameters()).device
    for adim in range(5):
        metin = egitim_metinleri[adim % len(egitim_metinleri)]
        girdi = tokenizer(metin)["input_ids"].to(cihaz)
        cikti = lora_model(girdi)
        hedef = torch.zeros_like(cikti)
        kayip = torch.nn.functional.mse_loss(cikti, hedef)
        optimizer.zero_grad()
        kayip.backward()
        optimizer.step()
        kayip_gecmisi.append(float(kayip.item()))
        lora_model.egitim_adim_sayaci += 1
    return kayip_gecmisi


def calistir() -> None:
    print("[test] 1) Kod çıkarma ve tekil sağlamlık testleri...")
    kod = kodu_metinden_cikar(_MODEL_CANNED_YANIT)
    assert kod is not None, "kod bloğu çıkarılamadı"
    assert "def transform" in kod

    gorev = _sentetik_1ae2feb7_gorevi()
    train_ciftleri = [(o["input"], o["output"]) for o in gorev["train"]]

    dogrulandi = kodu_egitim_ornekleriyle_dogrula(kod, train_ciftleri)
    assert dogrulandi, "üretilen kod kendi train örneklerini bile doğrulayamadı"
    print("    -> kod her iki train örneğinde de train_output ile bit-bit eşleşiyor.")

    basarili, tahmin = kodu_guvenle_calistir(kod, gorev["test"][0]["input"])
    assert basarili, f"test girdisinde çalıştırma başarısız: {tahmin}"
    assert tahmin == gorev["test"][0]["output"], f"test tahmini yanlış: {tahmin}"
    print("    -> kod, test girdisinde de gerçek beklenen çıktıyla birebir eşleşiyor (yön bağımsızlığı doğrulandı).")

    print("[test] 2) Güvenlik denetimi negatif testi (tehlikeli kod reddedilmeli)...")
    tehlikeli_kod = "import os\ndef transform(grid):\n    os.system('echo tehlike')\n    return grid\n"
    basarili_kotu, hata = kodu_guvenle_calistir(tehlikeli_kod, gorev["test"][0]["input"])
    assert not basarili_kotu, "tehlikeli kod güvenlik denetiminden geçmemeliydi ama geçti"
    print(f"    -> tehlikeli kod doğru şekilde reddedildi: {hata}")

    print("[test] 3) Uçtan uca gorevi_coz() + vasıfsız mock model + gerçek TTT-benzeri gradyan adımları...")
    mock_model = _VasifsizMockDil(_MODEL_CANNED_YANIT)
    mock_tokenizer = _VasifsizMockTokenizer()

    sonuc = gorevi_coz(
        mock_model, mock_tokenizer, "1ae2feb7", gorev,
        uret_fn=_mock_uret_fn, ince_ayar_fn=_mock_ince_ayar_fn,
        cogaltma_hedefi=8, ttt_adim_sayisi=5,
    )

    assert mock_model.egitim_adim_sayaci == 5, (
        f"TTT ince ayar adımları çalışmadı: beklenen 5, gerçek {mock_model.egitim_adim_sayaci}"
    )
    print(f"    -> TTT ince ayar {mock_model.egitim_adim_sayaci} gerçek gradyan adımı çalıştırdı.")

    assert len(sonuc) == 1, "tek test girdisi için tek sonuç bekleniyordu"
    assert "attempt_1" in sonuc[0] and "attempt_2" in sonuc[0], "submission şeması eksik"
    assert sonuc[0]["attempt_1"] == gorev["test"][0]["output"], (
        f"attempt_1 beklenen çıktıyla eşleşmiyor: {sonuc[0]['attempt_1']}"
    )
    print(f"    -> attempt_1 == gerçek beklenen çıktı: {sonuc[0]['attempt_1']}")
    print(f"    -> submission şeması doğru: {list(sonuc[0].keys())}")

    print("\n[test] TÜMÜ BAŞARILI: veri yükleme -> artırma -> prompt -> TTT -> kod üretimi -> "
          "güvenli çalıştırma -> train-set doğrulama -> test tahmini -> submission şeması "
          "uçtan uca doğru çalışıyor (gerçek Kaggle dosyaları bu geliştirme ortamında "
          "bulunmadığından, 1ae2feb7'nin gerçek kuralını birebir taklit eden yerel sentetik "
          "veri ve vasıfsız/mock bir dil modeliyle test edildi).")


if __name__ == "__main__":
    calistir()
