import json
import logging
import os
import time
from typing import Any, Dict, Iterator, List, Optional, Tuple

import numpy as np

logger = logging.getLogger("TokenliVeriDeposu")


BIN_UZANTI = ".bin"
IDX_UZANTI = ".idx"
DEPO_SURUM = "1.0.0-mucit-indeksli-token-deposu"


def ayrac_tokeni_bul(tokenizer: Any, V_size: int) -> int:






    for alan in ("eot_token", "eos_token_id", "eot_token_id"):
        deger = getattr(tokenizer, alan, None)
        if isinstance(deger, int) and 0 <= deger < V_size:
            return deger
    return 0


class TokenliVeriDeposuInsaEdici:






    def __init__(self, depo_yolu: str, tokenizer: Any, V_size: int):
        self.depo_yolu = depo_yolu
        self.tokenizer = tokenizer
        self.V_size = V_size
        self.ayrac = ayrac_tokeni_bul(tokenizer, V_size)

    def _bin_yolu(self) -> str:
        return self.depo_yolu + BIN_UZANTI

    def _idx_yolu(self) -> str:
        return self.depo_yolu + IDX_UZANTI

    def guncel_mi(self, kaynak_dosyalar: List[str]) -> bool:






        if not (os.path.isfile(self._bin_yolu()) and os.path.isfile(self._idx_yolu())):
            return False
        try:
            with open(self._idx_yolu(), "r", encoding="utf-8") as f:
                idx = json.load(f)
        except Exception:
            return False

        if idx.get("surum") != DEPO_SURUM:
            return False
        if idx.get("ayrac") != self.ayrac or idx.get("V_size") != self.V_size:
            return False

        kayitli = idx.get("kaynaklar", {})
        if set(kayitli.keys()) != set(os.path.abspath(d) for d in kaynak_dosyalar):
            return False
        for yol, imza in kayitli.items():
            try:
                st = os.stat(yol)
            except OSError:
                return False
            if int(st.st_size) != imza.get("boyut") or int(st.st_mtime) != imza.get("mtime"):
                return False
        return True

    def insa_et(self, kaynak_dosyalar: List[str], okuma_bloku: int = 1 << 20) -> Dict[str, Any]:






        os.makedirs(os.path.dirname(os.path.abspath(self._bin_yolu())) or ".", exist_ok=True)
        gecici_bin = self._bin_yolu() + ".tmp"

        dokuman_baslangiclari: List[int] = []
        kaynak_imzalari: Dict[str, Dict[str, int]] = {}
        toplam_token = 0
        baslangic = time.time()

        with open(gecici_bin, "wb") as cikti:
            for yol in kaynak_dosyalar:
                mutlak = os.path.abspath(yol)
                try:
                    st = os.stat(mutlak)
                except OSError as exc:
                    logger.warning(f"  [Token Deposu] Atlandı ({exc}): {mutlak}")
                    continue

                dokuman_baslangiclari.append(toplam_token)
                kaynak_imzalari[mutlak] = {"boyut": int(st.st_size), "mtime": int(st.st_mtime)}

                artik_metin = ""
                try:
                    with open(mutlak, "r", encoding="utf-8", errors="ignore") as girdi:
                        while True:
                            blok = girdi.read(okuma_bloku)
                            if not blok:
                                break





                            birlesik = artik_metin + blok
                            kesme = birlesik.rfind("\n")
                            if kesme <= 0:
                                artik_metin = birlesik
                                continue
                            islenecek, artik_metin = birlesik[:kesme + 1], birlesik[kesme + 1:]

                            idler = self.tokenizer.encode(islenecek)
                            if idler:
                                dizi = np.asarray(idler, dtype=np.uint32) % self.V_size
                                cikti.write(dizi.tobytes())
                                toplam_token += int(dizi.size)

                        if artik_metin:
                            idler = self.tokenizer.encode(artik_metin)
                            if idler:
                                dizi = np.asarray(idler, dtype=np.uint32) % self.V_size
                                cikti.write(dizi.tobytes())
                                toplam_token += int(dizi.size)
                except Exception as exc:
                    logger.warning(f"  [Token Deposu] Okuma hatası ({mutlak}): {exc}")




                cikti.write(np.asarray([self.ayrac], dtype=np.uint32).tobytes())
                toplam_token += 1

        os.replace(gecici_bin, self._bin_yolu())

        idx = {
            "surum": DEPO_SURUM,
            "toplam_token": toplam_token,
            "dtype": "uint32",
            "ayrac": self.ayrac,
            "V_size": self.V_size,
            "dokuman_baslangiclari": dokuman_baslangiclari,
            "kaynaklar": kaynak_imzalari,
            "olusturma_zamani": time.time(),
        }
        gecici_idx = self._idx_yolu() + ".tmp"
        with open(gecici_idx, "w", encoding="utf-8") as f:
            json.dump(idx, f)
        os.replace(gecici_idx, self._idx_yolu())

        gecen = time.time() - baslangic
        logger.info(
            f"  [Token Deposu] İnşa edildi: {toplam_token:,} token, "
            f"{len(dokuman_baslangiclari)} doküman, "
            f"{os.path.getsize(self._bin_yolu()) / (1024 ** 2):.1f} MB, {gecen:.1f} sn. "
            f"Doküman ayracı: {self.ayrac}"
        )
        return idx


class TokenliVeriDeposuOkuyucu:






    def __init__(self, depo_yolu: str):
        self.depo_yolu = depo_yolu
        with open(depo_yolu + IDX_UZANTI, "r", encoding="utf-8") as f:
            self.idx = json.load(f)
        self.toplam_token = int(self.idx["toplam_token"])
        self.ayrac = int(self.idx["ayrac"])
        self.dokuman_baslangiclari = list(self.idx.get("dokuman_baslangiclari", []))




        self.tokenlar = np.memmap(
            depo_yolu + BIN_UZANTI, dtype=np.uint32, mode="r", shape=(self.toplam_token,)
        )
        logger.info(
            f"  [Token Deposu] mmap ile açıldı: {self.toplam_token:,} token, "
            f"{len(self.dokuman_baslangiclari)} doküman "
            f"(RAM'e yüklenmedi, sayfa sayfa okunuyor)."
        )

    def pencere_sayisi(self, N: int) -> int:
        return max(self.toplam_token // N, 0)

    def pencereler(self, N: int) -> Iterator[Tuple[np.ndarray, bool]]:





        toplam = self.pencere_sayisi(N)
        for i in range(toplam):
            bas = i * N
            yield np.asarray(self.tokenlar[bas:bas + N]), (i == toplam - 1)
