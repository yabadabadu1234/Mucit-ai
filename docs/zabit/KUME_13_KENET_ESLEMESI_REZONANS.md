# PARAMETRE KENETLENMESİ VE EŞLEMENİN HAKİKİ MEMBÂI
### ("Bağlam basamağı" garabetinin ilgası, all-to-all'ın reddi, dinamik lif tayini)

## BİRİNCİ FASIL: "BAĞLAM BASAMAĞI" NEYDİ VE NİÇİN GARABETTİR

> *"Ben bu bağlam basamağının ne olduğunu da anlamadım, eskiden kalma
> bir garabet gibi."*

* **Eski köhne dünya (klasik LLM):** metin `1, 2, … T` diye ardışık
  belirteçlerden ibarettir; "bağlam basamağı" dikkat penceresindeki
  `t`. sıradır (positional index).
* **Bizim kâinatımız (`q^N` simetrisi):** veri yazmacı da parametre
  yazmacı gibi `N = 1 048 576` quditlik, tabanı `q = 64` olan bir
  süperpozisyon okyanusudur. Okyanusta "1. basamak, 2. basamak" diye
  ipe boncuk dizmek, diferansiyel geometriyi abaküse indirgemektir.
* **"Bağlam basamağı" tabiri çöpe atılmıştır.** Ortada ardışık bir
  basamak değil, **veri manifoldu üzerindeki rezonans noktaları
  (qudit koordinatları)** vardır.

## İKİNCİ FASIL: ÜÇ YOLUN MUHASEBESİ

    YOL 1  HER KONTROL BÜTÜN DÜĞÜMLERE (all-to-all)
           51 × 1 048 576 = 53 477 376 bağlantı. Maliyet fırlar, L1
           çöker, yerel ayrım kaybolur. Dolanıklık monogamisi (CKW)
           çiğnenir: her şey her şeyle dolanırsa dalga beyaz gürültüye,
           azamî entropili termal kuyuya çöker. Odaklanma ölür.

    YOL 2  SIRF MELEKENİN LİF ADRESİ (statik / mimarî)
           "11. meleke daima 186. sektöre bağlansın." Maliyet 51 işlem,
           çok ucuz; LÂKİN veri değiştikçe adaptasyon SIFIRDIR. Tenakuz
           500. quditte patlarsa 100. qudite bakan meleke kör kalır.
           Elle yazılmış bir kukla tiyatrosudur.

    YOL 3  MÜNASEBET HARİTASININ AÇTIĞI DİNAMİK LİF  ← HAKİKİ
           Ne elle yazılır, ne kaba all-to-all yapılır. Münasebet
           tensörü verideki topolojik yırtığı gösterir; meleke lifi
           doğrudan o yırtığın koordinatına kenetlenir.

## ÜÇÜNCÜ FASIL: DİNAMİK LİF TAYİNİ

1. **Münasebet haritası sinyali üretir.** Veri yazmacı aktığında
   Fubini-Study metriği yahut Dirac Laplasyeni üzerinde nerede bir
   gerilim (topolojik yırtık / yüksek eğim) varsa o quditlerin indisi
   **rezonans tepesi** olarak parlar:

       j* = argmax over j of  ∇g_FS(j)      yahut  topolojik yırtık indisi

2. **Meleke o rezonansa kilitlenir.** 51 kapının her biri önceden
   belirlenmiş sabit bir numaraya değil, münasebet haritasının fâş
   ettiği `j*` koordinatına **faz kilidiyle** kenetlenir:

       U_kapı = üstel( −i · Bağ_k · Z_parametre(k) ⊗ Z_veri(j*) )

3. **Maliyet:** 53 milyon değil, tamı tamına 51 saat çevrimi.

## DÖRDÜNCÜ FASIL: CETVEL

| Mesele | Köhne usul | Hakiki nizam |
| :--- | :--- | :--- |
| "Bağlam basamağı" | 1-B pencerede `t = 1, 2, …` sıra numarası | **Lağvedildi.** `N` manifold koordinatı |
| Eşleme yolu | Her kontrolü bir milyon noktaya çarpmak | **Rezonans indisi:** gerilim noktasına `O(1)` temas |
| Mimari tayini | Melekenin adresini elle gömmek | **Dinamik fibrasyon:** meleke yırtığın koordinatına akar |
| İşlem yükü | `51 × 10⁶` döngü hamallığı | 51 paralel skaler faz etkileşimi |
