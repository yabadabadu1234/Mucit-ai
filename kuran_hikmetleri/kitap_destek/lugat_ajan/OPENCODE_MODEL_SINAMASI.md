# Opencode ücretsiz model sınaması (2026-11-20)

Giriş: OpenCode Console hesabı (Google ile, cihaz onayı); anahtar depoya yazılmadı. Çağrı: `~/.opencode/bin/opencode run -m opencode/<model>`; yalnız `*-free` ve `big-pickle` (ücretsiz). Ücretli model ve aşırı kullanım yok.

Örnek metin: خوف maddesinden Mekâyîs cümlesi, Osmanlıca ve Mehmed Âkif ciddiyetinde tercüme istendi.

| Model | Süre | Netice |
| :-- | :-- | :-- |
| deepseek-v4.1-flash-free | ~60 s | En iyi: kurulu Osmanlıca, mana eksiksiz, Arapça artığı yok |
| big-pickle | 37 s | İyi: sade, doğru; biraz kısaltıyor |
| mimo-v2.6-flash-free | 100 s | Orta: Arapçayı çevirmeden bırakıyor, uydurma ilave var |
| beam-free | 12 s | Zayıf: mana kısalıyor, kök adı yanlış (Huf) |
| flint-40b-free, longcat-2.5-free | zaman aşımı | Cevap alınamadı (100–120 s) |

Seçim: deepseek-v4.1-flash-free (birinci), big-pickle (yedek). Düşünme bütçesi: düşük.
