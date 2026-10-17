"""Doğrulanmış eğitim satırları (uret_mantik.py'den) ve cevaba göre doğruluk mesafesi.

Kullanım: python3 mantik_veri.py N_HER_AILE TOHUM CIKTI_DIZINI
Çıktı: train.jsonl (%90) ve held.jsonl (%10, eğitimde kullanılmaz).

Her satır:
  messages   [kullanıcı: soru, asistan: çözüm]   (SFT/CLM kaybı için)
  verified   true (denetçi kaydı kabul etti)
  route      0 = A (mantık), 1 = B (sıralama), 2 = C (sayfa/kademe), 3 = C (kalan)
  compiler_score 1.0 (denetçiden geçti)
  distance   0.0 (doğru çözüm)
  prompt     soru metni (modelin kendi cevabını üretmesi için)
  kayit      denetçi kaydı (doğruluk mesafesini hesaplamak için)

Mesafe [0,1]: yanlış etiket / parse edilemeyen cevap = 1.0; B'de yanlış konum oranı; C'de
|tahmin - b| / max(1, |b|) (1'de kırpılır). Hiçbir değer insan tarafından girilmez.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uret_mantik as U  # noqa: E402

ETIKETLER = ("kesin doğru", "kesin yanlış", "belirsiz")


def route_of(kayit):
    if kayit["aile"] == "A":
        return 0
    if kayit["aile"] == "B":
        return 1
    return 3 if kayit["tür"] == "kalan" else 2


def cevap_satiri(metin):
    for satir in reversed(metin.strip().splitlines()):
        s = satir.strip()
        if s.startswith("Cevap:"):
            return s[len("Cevap:"):].strip()
    return None


def mesafe(kayit, metin):
    """Modelin cevap metninden doğruluk mesafesi, [0, 1]."""
    pred = cevap_satiri(metin or "")
    aile = kayit["aile"]
    if pred is None:
        return 1.0
    if aile == "A":
        return 0.0 if pred == kayit["cevap"] else 1.0
    if aile == "B":
        n = kayit["n"]
        ad = kayit["isimler"]
        ayrik = {}
        for parca in pred.split(","):
            if "=" not in parca:
                return 1.0
            k, v = parca.split("=", 1)
            try:
                ayrik[k.strip()] = int(v.strip())
            except ValueError:
                return 1.0
        yanlis = sum(1 for p in range(n) if ayrik.get(ad[p]) != kayit["cevap"][p] + 1)
        return yanlis / n
    try:
        tahmin = int(pred)
    except ValueError:
        return 1.0
    b = kayit["cevap"]
    return min(1.0, abs(tahmin - b) / max(1, abs(b)))


def satir_uret(kayit, metin):
    """Denetçiden geçmiş bir kayıt ve metninden eğitim satırı."""
    soru, cozum = metin.split("\nÇözüm", 1)
    cozum = "Çözüm" + cozum
    return {
        "messages": [{"role": "user", "content": soru}, {"role": "assistant", "content": cozum}],
        "verified": True,
        "route": route_of(kayit),
        "compiler_score": 1.0,
        "distance": 0.0,
        "prompt": soru,
        "kayit": kayit,
    }


def uret(n_aile, tohum):
    rng = random.Random(tohum)
    satirlar, gorulen = [], set()
    for aile in "ABC":
        got, tries = 0, 0
        while got < n_aile and tries < n_aile * 20:
            tries += 1
            if aile == "A":
                r = U.ornek_A(rng, rng.choice(list(ETIKETLER)))
            else:
                r = U.URE[aile](rng)
            if not r or not U.DEN[aile](r):
                continue
            metin = U.MET[aile](r, rng)
            if "\nÇözüm" not in metin:
                continue
            soru = metin.split("\nÇözüm", 1)[0]
            if soru in gorulen:
                continue
            gorulen.add(soru)
            satirlar.append(satir_uret(r, metin))
            got += 1
    rng.shuffle(satirlar)
    return satirlar


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    tohum = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    cikti = sys.argv[3] if len(sys.argv) > 3 else "."
    satirlar = uret(n, tohum)
    bolme = max(1, len(satirlar) // 10)
    held, train = satirlar[:bolme], satirlar[bolme:]
    os.makedirs(cikti, exist_ok=True)
    for ad, veri in (("train.jsonl", train), ("held.jsonl", held)):
        with open(os.path.join(cikti, ad), "w", encoding="utf-8") as f:
            for s in veri:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
    rota = [sum(1 for s in train if s["route"] == g) for g in range(4)]
    print(f"train={len(train)} held={len(held)} rota(train)={rota}")


if __name__ == "__main__":
    main()
