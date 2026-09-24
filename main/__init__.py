"""
main/__init__.py - Mucit-AI / Nefs-i Müdrike Eğitim ve Çıkarım Giriş Noktası
"""

from main.egitim import EgitimHatti, egitimi_baslat
from main.cikarim import CikarimHatti, cikarimi_calistir

__all__ = [
    "EgitimHatti",
    "egitimi_baslat",
    "CikarimHatti",
    "cikarimi_calistir"
]
