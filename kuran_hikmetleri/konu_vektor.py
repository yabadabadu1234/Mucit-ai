"""Konu dizinindeki her konuya bir vektör verir: konu adının token vektörlerinin toplamı.

Model: Qwen/Qwen3.5-4B (Hugging Face). Yalnızca gerekli embedding satırları aralık istekleriyle
çekilir; model tam indirilmez. Önbellek: kuran_hikmetleri/.hf_cache/ (depoya girmez).

Çıktı (önbellek): .hf_cache/konu_vektorleri.npz  →  konular (ad), vektör (N x 2560), token sayısı
"""
import json
import struct
import urllib.request
from pathlib import Path

import numpy as np
from tokenizers import Tokenizer

from konu_haritasi import konulari_oku

BASE = Path(__file__).resolve().parent
ONBELLEK = BASE / ".hf_cache"
DEPO = "https://huggingface.co/Qwen/Qwen3.5-4B/resolve/main"
SHARD = "model.safetensors-00001-of-00002.safetensors"
TENSOR = "model.language_model.embed_tokens.weight"


def indir(uzak, yerel):
    """Dosyayı bir kez indirir; sonraki çalıştırmalarda önbellekten okur."""
    if not yerel.exists():
        yerel.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(uzak, timeout=300) as r, open(yerel, "wb") as f:
            f.write(r.read())
    return yerel


def aralik_oku(url, bas, son):
    req = urllib.request.Request(url, headers={"Range": f"bytes={bas}-{son}"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def embedding_satirlari(id_listesi):
    """{token_id: float32 vektör} — yalnız istenen satırlar, ardışık olanlar tek istekte."""
    url = f"{DEPO}/{SHARD}"
    n = struct.unpack("<Q", aralik_oku(url, 0, 7))[0]
    baslik = json.loads(aralik_oku(url, 8, 8 + n - 1))[TENSOR]
    if baslik["dtype"] != "BF16":
        raise ValueError(f"beklenmeyen dtype: {baslik['dtype']}")
    satir_sayisi, boyut = baslik["shape"]
    veri_bas = 8 + n + baslik["data_offsets"][0]
    satir_bayt = boyut * 2
    ids = sorted(set(id_listesi))
    sonuc = {}
    i = 0
    while i < len(ids):
        j = i
        while j + 1 < len(ids) and ids[j + 1] == ids[j] + 1:
            j += 1
        a = veri_bas + ids[i] * satir_bayt
        b = veri_bas + (ids[j] + 1) * satir_bayt - 1
        blok = np.frombuffer(aralik_oku(url, a, b), dtype="<u2").reshape(-1, boyut)
        for k, tid in enumerate(range(ids[i], ids[j] + 1)):
            # bf16 → float32: üst 16 bit
            sonuc[tid] = (blok[k].astype(np.uint32) << 16).view(np.float32)
        i = j + 1
    return sonuc, boyut


def vektorleri_hesapla():
    konular = [(k, a) for k, a in konulari_oku() if a]
    adlar = [k for k, _ in konular]
    tokenizer = Tokenizer.from_file(str(indir(f"{DEPO}/tokenizer.json", ONBELLEK / "tokenizer.json")))
    kodlar = [tokenizer.encode(ad, add_special_tokens=False).ids for ad in adlar]
    gerekli = {t for kod in kodlar for t in kod}
    satirlar, boyut = embedding_satirlari(gerekli)
    vektorler = np.zeros((len(adlar), boyut), dtype=np.float32)
    for n, kod in enumerate(kodlar):
        for t in kod:
            vektorler[n] += satirlar[t]
    np.savez(ONBELLEK / "konu_vektorleri.npz", adlar=np.array(adlar), vektor=vektorler,
             token_sayisi=np.array([len(k) for k in kodlar]))
    return adlar, vektorler, kodlar


if __name__ == "__main__":
    adlar, vektorler, kodlar = vektorleri_hesapla()
    print(f"konu: {len(adlar)}, vektör boyutu: {vektorler.shape[1]}, "
          f"toplam token: {sum(len(k) for k in kodlar)}, farklı token: {len({t for k in kodlar for t in k})}")
