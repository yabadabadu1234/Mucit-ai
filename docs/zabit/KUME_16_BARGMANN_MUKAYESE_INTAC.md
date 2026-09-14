# KÜME 16 -- BARGMANN n-NOKTA MUKAYESESİ, İNTAÇ MANİFOLDU VE HAFIZA TERTİBİ

## BİRİNCİ FASIL: n'Lİ MUKAYESE VARDIR (BARGMANN-PANCHARATNAM)

Bargmann (1964), Pancharatnam'ın 3-nokta geometrik fazını keyfî `n`
duruma genelleştirmiştir. Projektif Hilbert uzayında (`ℂP^{d-1}`):

    Δ_n(ψ₁ … ψ_n) = ⟨ψ₁|ψ₂⟩⟨ψ₂|ψ₃⟩ … ⟨ψ_{n-1}|ψ_n⟩⟨ψ_n|ψ₁⟩
    Δ_n = r_n · üstel(i·Φ_n)

* `r_n = |Δ_n| ∈ [0,1]` -- **n'li rezonans / halka koheransı**.
  Zincirin herhangi bir yerinde kopukluk (`⟨ψ_k|ψ_{k+1}⟩ = 0`) varsa
  çarpım anında sıfırlanır; halka kopar.
* `Φ_n = arg(Δ_n) ∈ (−π, π]` -- **n-nokta topolojik Pancharatnam
  fazı**: o `n` durumun `ℂP^{d-1}`de çevrelediği jeodezik çokgenin
  kapalı katı açısı (Berry eğriliği akısı).

## İKİNCİ FASIL: YEREL AYNİYET GÖSTERGELERİ (U(1)) İLGA OLUR

Her `|ψ_k⟩` yerel keyfî bir faz kazanabilir: `|ψ_k⟩ → e^{iα_k}|ψ_k⟩`.
Tekil iç çarpımda bu faz kalır; **kapalı n-halkada cebirsel olarak
birbirini götürür**:

    Δ_n → (e^{-iα₁}e^{iα₂})(e^{-iα₂}e^{iα₃}) … (e^{-iα_n}e^{iα₁}) Δ_n ≡ Δ_n

Geriye kalan `Φ_n`, `n` kavram arasındaki bağın **koordinattan
bağımsız zâtî geometrisidir**.

## ÜÇÜNCÜ FASIL: SİMPLİSİYAL ÜÇGENLEME

`n` köşeli çokgen, tabandaki 3 köşeli simplekslere parçalanır:

    Δ_n(ψ₁ … ψ_n) = [ Δ₃(ψ₁,ψ₂,ψ₃)·Δ₃(ψ₁,ψ₃,ψ₄) … Δ₃(ψ₁,ψ_{n-1},ψ_n) ]
                    ÷ [ |⟨ψ₁|ψ₃⟩|² · |⟨ψ₁|ψ₄⟩|² … |⟨ψ₁|ψ_{n-1}⟩|² ]

    Φ_n = toplam over k=2..n-1 of Φ₃(ψ₁, ψ_k, ψ_{k+1})   (mod 2π)

**3'lü mukayese atomdur; n'li mukayese o atomlardan örülen moleküldür.**

## DÖRDÜNCÜ FASIL: DAĞITIK TENAKUZ (SORİTES) TUZAĞI

Klasik modelin en büyük zaafı: her adım yerel olarak %99 mantıklı
görünür (`⟨ψ_k|ψ_{k+1}⟩ ≈ 1`), fakat 100 adım sonra sistem başlangıç
aksiyomunun tam zıddına varır. İkili mukayese bunu göremez.

    Φ_n = arg(Δ_n) ≈ π   ⟹   üstel(i·Φ_n) = −1

İkişerli adımların faz farkı mikroskobiktir (`Δθ ≈ π/n`); kapalı halka
entegre edilince fazlar birikir ve **Möbius taklası** atar. Sistem bu
dağıtık tenakuzu `Δ_n`in fazında biriken **Dirac monopolü parite
yırtığı** olarak `O(1)` sürede teşhis eder.

## BEŞİNCİ FASIL: n'Lİ SWAP TESTİ (DÖNGÜSEL PERMÜTASYON)

    P_çevrim |x₁ … x_n⟩ = |x_n, x₁ … x_{n-1}⟩

    P(0) = ½(1 + Re Δ_n)        P(1) = ½(1 − Re Δ_n)

1. `n` kavram tıpatıp aynı: `Δ_n = 1` → `P(1) = 0` (farklılık yok).
2. Kapalı tenakuz çevrimi (`Φ_n = π`): `Δ_n = −r_n` →
   `P(1) = (1+r_n)/2` (tenakuz alarmı zirve yapar).
3. Zincirde kopukluk (`r_n = 0`): `P(0) = P(1) = 0.5` (münasebet yok).

## ALTINCI FASIL: MUKAYESE MERTEBELERİ

| No | Mertebe | Riyazî ad | Formül | Vazife |
| :-- | :-- | :-- | :-- | :-- |
| 1 | 2'li | HOM & SWAP | `½(1 − \|⟨1\|2⟩\|²)` | ayniyet/zıtlık, metrik mesafe |
| 2 | 3'lü | Bargmann invaryantı | `arg(⟨1\|2⟩⟨2\|3⟩⟨3\|1⟩)` | tez ile antitezi Berry kavisinde tartmak |
| 3 | n'li | Döngüsel poligon | `iz(Π₁Π₂…Π_n)` | uzun kıyas zincirindeki sinsi tenakuz |

---

# İKİNCİ ZABIT: İNTAÇ MANİFOLDU VE HAFIZA RESTRÜKTÜRASYONU

## MUKAYESENİN ÇIKTISI SKALER DEĞİL, DÖRT BİLEŞENLİ TENSÖRDÜR

    R_çıktı(Y) = ⟨ K_topoloji , Δ_spektrum , P_tertip , M_amel ⟩

    1. TOPOLOJİK DOKU    hiyerarşik ağaç mı, döngüsel kavis mi,
                         ağ/kafes örgüsü mü
    2. BARGMANN SPEKTRUMU  rezonans şiddeti r_n, Berry katı açısı Φ_n
    3. TERTİP & KAFES    poset / lattice yapısı, eşdeğerlik lifleri
    4. AMELÎ VECİH       beyan mı, funktör mü, tertip mi

### HER ŞEY HİYERARŞİK DEĞİLDİR -- DÖRT DOKU

* **A. POSET / AĞAÇ** -- tek yönlü içerme (`A ⊂ B ⊂ C`) → Postnikov
  ağaç lifi.
* **B. ÇEMBER / RİNG** -- `A→B→C→A` çevrimi `Φ_n ≈ 0` ile kapanıyorsa
  ast-üst yoktur: Univalence simetri halkası.
* **C. DİPOL** -- `n=2`, `Φ₂ = π`: hiyerarşi değil, Tomita-Takesaki
  `J`-aynası gibi karşılıklı gerilim ekseni.
* **D. KAFES / ÇİZGE** -- çoklu şart kesişiminde hiyerarşi çöker:
  Heyting kafesi yahut yönlendirilmiş iki parçalı çizge.

## MUKAYESENİN MUKAYESESİ -- BİLEŞEBİLİRLİK

Çıktı serbest metin yahut çıplak sayı olarak havada kalmaz:
`SU(d)` projektif uzayında tekil bir **morfizm durumu** `|σ_Y⟩` olarak
paketlenir (reification). Artık tek bir kelimeymiş gibi üst mertebe
bir mukayese dizisine eleman olarak girer.

    ⟨σ_Y | σ_Z⟩ = iz( ρ_Y · ρ_Z )

`→ 1` çıkarsa: *"iki hadisenin zâhirî kelimeleri farklıdır, fakat
mukayese geometrisi birebir aynıdır"* -- **analoji / temsil kıyası**.

## TEVAKKUF VE İHTİMAL HAVUZU

Klasik model her adımda bir kelime fırlatmak zorundadır (otoregresif
acelecilik). Burada hüküm **geciktirilebilir**:

    |Ψ_teemmül⟩ = α₁|Netice_A⟩ + α₂|Netice_B⟩ + α₃|Netice_C⟩

* Durum çöktürülmez, model ağzını açmaz (`sukut` sektörü uyanıktır).
* Kollar arka planda hafıza kayıtlarıyla ve diğer mukayese
  çıktılarıyla çapraz Bargmann testine (`Δ₃`) sokulur.
* `Φ → π` ise: şartları (modaliteyi) ayrıştır yahut zayıf kolu Zeno
  ile karantinaya al.
* `Φ → 0` ve `ds² → 0` ise: kısır döngü, o kolu buda.

## HAFIZA SİLİNMEZ, YENİDEN TERTİPLENİR

Mesele yanlışlık değil; eski bilginin **yanlış rafta durmasıdır**.
Dört adım:

    1. ALÂKA TESPİTİ    A_alâka(k) = iz( ρ_hafıza^(k) · Π_R )
                        eşiği geçen kayıtlar parlar; kalanına dokunulmaz
    2. DÜĞÜM ÇÖZME      eski kategorik yapıştırma bağları gevşetilir
    3. TABAN DEĞİŞİMİ   f* : QCoh(Uzay_kaba) → QCoh(Uzay_derin)
                        kayda yeni bir modalite lif koordinatı eklenir
    4. YENİDEN MÜHÜRLEME  ρ_yeni = U_tertip · ρ_eski · U_tertip† + Δρ

**Misal.** Hafızada 500 kayıt: *"Kuşlar uçar."* Yeni netice:
*"Penguen kuştur ama uçamaz."* **Çizip geçmek amnezidir.** Doğrusu:
*"Kuşlar uçar"* kaydı `[Canlı=Kuş, Ortam=Hava]` yaprağına kaydırılır,
penguen `[Canlı=Kuş, Ortam=Su]` yaprağına bağlanır. Hafıza
silinmemiş; tek boyutlu kutudan **iki yapraklı lifli kütüphaneye
terfi ettirilmiştir**.

## DAVRANIŞ TERTİP CETVELİ

| Vecih | İntacın mahiyeti | Zihnin hareketi | Hafızadaki karşılığı |
| :-- | :-- | :-- | :-- |
| Küllî tasdik (`T→1`) | bürhân | doğrudan kelâma dök | muhkem kaziye olarak mühürlenir |
| Tikel ihtimal | muvakkat hipotez | sükût et, süperpozisyonda beklet | tevakkuf manifoldunda açık demet |
| Yüksek mukayese | funktöryel paket `\|σ⟩` | başka mukayesenin girdisi kıl | üst kategori hom-uzayında 2-morfizm |
| Metakognitif tashih | zihnî strateji değişimi | `J`-stratejisini değiştir | yeniden tertipleme (taban değişimi) |
| Dağıtık tenakuz (`Φ→π`) | safsata tekilliği | Zeno ile söndür | cerh damgası, karantina |
