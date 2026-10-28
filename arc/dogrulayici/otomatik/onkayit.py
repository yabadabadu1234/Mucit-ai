import hashlib
import json
import sys
from pathlib import Path

BURA = Path(__file__).resolve().parent

DIS_OLCU = {
    "kaynak": "Weston vd. 2015, Towards AI-Complete Question Answering: A Set of Prerequisite Toy Tasks (arXiv:1502.05698)",
    "gecme": 0.95,
    "ibare": "bir görev, test doğruluğu en az %95 ise geçilmiş sayılır (makalenin ölçüsü)",
    "veri": "tasks_1-20_v1-2, en-10k, tren kısmından öğrenilir, test kısmının altın cevabıyla puanlanır",
}

KOSULAR = {
    "tam": {"hifz": True, "terkip": True, "kip_zaman": True},
    "hifzsiz": {"hifz": False, "terkip": True, "kip_zaman": True},
    "terkipsiz": {"hifz": True, "terkip": False, "kip_zaman": True},
    "zamansiz": {"hifz": True, "terkip": True, "kip_zaman": False},
}

TAHMIN_DUSEN = {
    "tam": [],
    "hifzsiz": list(range(1, 21)),
    "terkipsiz": [2, 3, 5, 11, 13, 15, 16, 17, 18, 19],
    "zamansiz": [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
}


def ozet(yol):
    return hashlib.sha256(Path(yol).read_bytes()).hexdigest()


if __name__ == "__main__":
    arsiv = sys.argv[1]
    kayit = {
        "cozucu.py": ozet(BURA / "cozucu.py"),
        "kos.py": ozet(BURA / "kos.py"),
        "onkayit.py": ozet(BURA / "onkayit.py"),
        "veri_arsivi": ozet(arsiv),
        "dis_olcu": DIS_OLCU,
        "kosular": KOSULAR,
        "tahmin_dusen": TAHMIN_DUSEN,
    }
    (BURA / "ONKAYIT.json").write_text(json.dumps(kayit, ensure_ascii=False, indent=1))
    print(json.dumps(kayit, ensure_ascii=False, indent=1))
