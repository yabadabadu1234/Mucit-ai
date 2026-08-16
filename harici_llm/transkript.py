"""
Modelin GERCEKTEN urettigi HER metni (arac cagirdi mi/cagirmadi mi
farketmeksizin, dogru mu yanlis mi farketmeksizin) diske kaydeder.

Neden: bir gorev cok uzun surup (ornegin ~3200 saniye) sonunda BOS
tahminle (submit_answer hic basarili cagrilmadan) bitebilir. Bu durumda
modelin o sure icinde GERCEKTE ne urettigini (kural akil yurutmesi mi
yaptı, hicbir sey mi uretmedi, ayni seyi mi tekrarladi, arac cagirma
formatini mi tutturamadi) gormeden "gercekten calisti mi calismadi mi"
sorusuna cevap verilemez. gonderim_uret.py'deki "ne olursa olsun kaydet"
usulunun (checkpoint mantigi) aynisi: her turden hemen sonra, bellekte
biriktirmeden, ANINDA diske yazip flush+fsync ediyoruz -- surec o an
olse/zaman asimina ugrasa bile o ana kadarki tum transkript diskte kalir.
"""
import json
import os
import threading
import time
from typing import Any, Dict

TRANSKRIPT_YOLU = os.environ.get("MUCIT_TRANSKRIPT_YOLU", "/kaggle/working/konusma_transkriptleri.jsonl")

# coklu_gpu.py'nin GERÇEK OS thread'leri (padişah/vezir havuzu) aynı anda
# bu dosyaya yazabilir. Python'ın f.write() çağrısı büyük (birkaç KB'lık
# model metni içeren) satırlar için TEK bir atomik sistem çağrısı OLMAK
# ZORUNDA DEĞİLDİR -- kilitsiz bırakılırsa iki thread'in satırları iç içe
# geçip .jsonl dosyasını BOZABİLİR. Bu yüzden yazma tamamen bu kilit
# altında yapılır.
_YAZMA_KILIDI = threading.Lock()


def transkript_satiri_yaz(kayit: Dict[str, Any]) -> None:
    kayit = dict(kayit)
    kayit.setdefault("zaman", time.strftime("%Y-%m-%d %H:%M:%S"))
    try:
        with _YAZMA_KILIDI:
            with open(TRANSKRIPT_YOLU, "a", encoding="utf-8") as f:
                f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())
    except OSError as yazma_hatasi:
        print(f"[transkript] YAZMA HATASI (yoksayılıp devam edilecek): {yazma_hatasi}")
