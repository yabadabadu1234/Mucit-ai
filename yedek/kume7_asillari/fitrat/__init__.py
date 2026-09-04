"""fitrat — tabii denge, ayrışma, değişmezlik ve hüküm motoru.

* ``denge``          — oyun dengesi, en iyi karşılık, kapalı formlar
* ``ayrisma``        — d-ayrışması (Bayes topları), arka/ön kapı
* ``serbest_enerji`` — ELBO, ``F ≥ −ln p(X)``, açık = KL
* ``tevafuk``        — çoklu kanal tevafuku ve eşikleri
* ``havuz``          — sorgu havuzu, karantina
* ``karsi_olgusal``  — karşıolgusal 3-pas (abduction/action/prediction),
  NOTEARS çevrimsizlik değişmezi, örtük değişken, denge lokusu
"""

__all__ = ["denge", "ayrisma", "serbest_enerji", "tevafuk", "havuz",
           "karsi_olgusal"]
