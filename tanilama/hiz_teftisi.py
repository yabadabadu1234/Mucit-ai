from __future__ import annotations

__all__ = ["HEDEF", "had", "had_sifirla", "BUTCE_SANIYESI"]

HEDEF: float = 1_000_000.0
_HAD: list = []


def had(yazmac_boyu: int = 0, kapi: int = 0) -> float:
    if _HAD:
        return float(_HAD[0])
    from nefs.donanim import tamsayi_hizi
    t = tamsayi_hizi()
    sn = float(t["sn"])
    assert sn > 0.0, (
        "tamsayı hızı yoklanamadı -- had ölçüsüz konamaz (ferman 5-B)")
    kelime = float(t["satır"]) * float(t["kelime"])
    d = float(yazmac_boyu) if int(yazmac_boyu) > 0 else kelime
    k = float(kapi) if int(kapi) > 0 else 1.0
    _HAD.append(kelime / sn / max(d / kelime, 1.0) / k)
    return float(_HAD[0])


def had_sifirla() -> None:
    _HAD.clear()

BUTCE_SANIYESI: float = 86_400.0
