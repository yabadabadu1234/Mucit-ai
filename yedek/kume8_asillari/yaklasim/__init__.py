"""
yaklasim -- fonksiyon yaklaşımı ve eniyileme usulleri.

``omega_kategori``/``omega_kategori_nbe`` bir tip teorisi çekirdeğidir:
orada bir şey ya ISPATLANIR ya olmaz. Bu modül başka bir zemindedir:
burada bir şey ya ÖLÇÜLÜR ya olmaz. İkisinin ortak edebi şudur -- hiçbir
usul her yerde iyi değildir, ve her usulün zaafı **gösterilebilir**
olmalıdır.

Katmanlar:

    kara_kutu   -- kara kutu eniyilemenin imkânsızlık sınırları
                   (No Free Lunch, Nemirovski--Yudin sıfır-zinciri)
    tikizlik    -- varlık teoremleri: zorlayıcılık, alt-seviye tıkızlığı
                   ve tıkızlaştırılamayan karşı örnekler
    akislar     -- gradyanın akış olarak okunuşu: vektör akışı, topluluk
                   (Langevin / Fokker--Planck) akışı, ortalama eğrilik
    genisletme  -- Kan genişletmesi ile aradeğerleme ve onun ezber zaafı;
                   RKHS / Sobolev çekirdekleriyle düzeltilmesi
    simgesel    -- simgesel bağlanım (Occam cezalı arama)
    nedensel    -- do-hesabı: bağlanım ile müdahalenin ayrımı
    modern      -- KAN (uçlarda öğrenilen fonksiyon), Fourier işlemci,
                   DeepONet, Sobolev eğitimi

Her katman kendi ``rapor()`` fonksiyonunu taşır ve
``test_yaklasim.py`` bunların hepsini sınar.
"""

__all__ = [
    "kara_kutu",
    "tikizlik",
    "akislar",
    "genisletme",
    "simgesel",
    "nedensel",
    "modern",
]
