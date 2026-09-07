from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np

from ogrenme.optimize import en_iyiyi_ara, had, kuyudan_cik

__all__ = ["ara"]


def ara(f=None, ne: str = "en_iyi", yol: str = "dürr", **kw) -> Any:
    if ne == "en_iyi":
        return en_iyiyi_ara(f, ne=yol, **kw)
    if ne == "kaçış":
        return kuyudan_cik(ne=kw.pop("nasil", "ısıl"), **kw)
    if ne == "bedel":
        return kuyudan_cik(ne="bedel", **kw)
    if ne == "had":
        return had(**kw)
    raise ValueError("arama fiilinin kipi bilinmiyor: %r" % (ne,))
