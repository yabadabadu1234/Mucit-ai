"""olcek — performans muhasebesi: FLOP/token, çatı modeli, boyut denetimi.

* ``hiz`` — L4 raporunun doğrulanması, yığın şartı (M34), veri akış
  risalesinin aritmetik ve boyut hataları (M31-M33)
* ``gercek`` — bu makinede 30/60 saniyelik pencerelerde SÜREKLİ ölçüm;
  ısınma atılıyor, sistem yükü her ölçümün yanına yazılıyor
"""

__all__ = ["hiz", "gercek"]
