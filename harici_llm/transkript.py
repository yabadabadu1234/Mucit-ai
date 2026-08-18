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
from typing import Any, Dict, Optional

TRANSKRIPT_YOLU = os.environ.get("MUCIT_TRANSKRIPT_YOLU", "/kaggle/working/konusma_transkriptleri.jsonl")

# coklu_gpu.py'nin GERÇEK OS thread'leri (padişah/vezir havuzu) aynı anda
# bu dosyaya yazabilir. Python'ın f.write() çağrısı büyük (birkaç KB'lık
# model metni içeren) satırlar için TEK bir atomik sistem çağrısı OLMAK
# ZORUNDA DEĞİLDİR -- kilitsiz bırakılırsa iki thread'in satırları iç içe
# geçip .jsonl dosyasını BOZABİLİR. Bu yüzden yazma tamamen bu kilit
# altında yapılır.
_YAZMA_KILIDI = threading.Lock()

# HIZ (kullanıcının açık talebi -- "model forward'ında değil diye
# ehemmiyet vermediğin ne varsa istisnasız düzelt"): bu fonksiyon,
# coz_yurutucu_toplu.py'nin PAYLAŞILAN batched üretim döngüsünden
# (tüm B slotu aynı anda ilerleten döngü) HER araç-çağrısı/İKAZ/yozlaşmış-
# döngü olayında SENKRON çağrılır -- yani burada geçen HER milisaniye,
# O ANDA TÜM batch'i (diğer B-1 slot dahil) bekletir. Eski uygulama HER
# TEK çağrıda dosyayı YENİDEN AÇIYOR (open/close syscall çifti) VE
# os.fsync() ÇAĞIRIYORDU -- fsync, işletim sistemine "veriyi FİZİKSEL
# diske/SSD'ye yaz, önbellekte bırakma" der ve tipik olarak birkaç
# milisaniyeye kadar sürebilir; bu, GÜÇ KESİLMESİ/OS çökmesi gibi çok
# daha güçlü bir garanti verir. Ama docstring'in belirttiği asıl ihtiyaç
# ("surec o an olse... diskte kalir") yalnızca SÜRECİN KENDİSİNİN
# çökmesi/zaman aşımına uğramasına karşı korumadır -- bunun için tek
# gereken, verinin İŞLETİM SİSTEMİ arabelleğine ulaşmış olmasıdır
# (f.flush()), ki bu süreç öldüğünde/kesildiğinde bile veri OS'ta kalır
# ve dosyadan HEMEN okunabilir. fsync'in verdiği EK garanti (donanım güç
# kesintisine karşı) burada gerekli değildi. Artık dosya bir kez açılıp
# (modül düzeyinde) açık tutuluyor -- her çağrıda open/close YOK -- ve
# yalnızca flush() yapılıyor, fsync() KALDIRILDI.
_dosya_tutamaci: Optional[Any] = None


def _dosyayi_ac() -> Any:
    global _dosya_tutamaci
    if _dosya_tutamaci is None or _dosya_tutamaci.closed:
        _dosya_tutamaci = open(TRANSKRIPT_YOLU, "a", encoding="utf-8")
    return _dosya_tutamaci


def transkript_satiri_yaz(kayit: Dict[str, Any]) -> None:
    kayit = dict(kayit)
    kayit.setdefault("zaman", time.strftime("%Y-%m-%d %H:%M:%S"))
    try:
        with _YAZMA_KILIDI:
            f = _dosyayi_ac()
            # NOT (Turkce): kullanicinin gercek Kaggle logunda gordugu
            # "Object of type ndarray is not JSON serializable" cokmesinin
            # KOK NEDENI burasiydi -- modelin execute_python koduyla
            # (numpy serbestce import edilebiliyor) urettigi bir sonuc
            # (ornegin bir numpy dizisi) "icerik" olarak buraya geldiginde
            # json.dumps TypeError firlatiyordu, ama asagida SADECE
            # OSError yakalaniyordu -- TypeError yakalanmadan yukari
            # firlayip TUM 65 gorevlik SUREKLI ADMISYON partisini
            # coksturuyordu. default=str, JSON'un DOGRUDAN temsil
            # edemedigi HERHANGI bir nesneyi (ndarray, custom sinif, vb.)
            # sessizce metne cevirir -- gelecekte baska bir tur icin de
            # ayni cokme bir daha YASANMAZ.
            f.write(json.dumps(kayit, ensure_ascii=False, default=str) + "\n")
            f.flush()
    except (OSError, TypeError, ValueError) as yazma_hatasi:
        print(f"[transkript] YAZMA HATASI (yoksayılıp devam edilecek): {yazma_hatasi}")
        global _dosya_tutamaci
        if _dosya_tutamaci is not None:
            try:
                _dosya_tutamaci.close()
            except OSError:
                pass
            _dosya_tutamaci = None
