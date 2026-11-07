import json, subprocess
from pathlib import Path
B = Path(__file__).resolve().parent
P = B / "kaynak" / "lugat" / "pilot" / "kategori"
d = json.loads((P / "kategori.json").read_text(encoding="utf-8"))
K, A = d["kokler"], d["ad"]
n = len(K)
svg = subprocess.run(["dot", "-Tsvg", str(P / "kategori.dot")], capture_output=True, check=True).stdout.decode()
svg = svg[svg.index("<svg"):]


def tablo(M, baslik, fmt, renk):
    s = f"<h3>{baslik}</h3><table class='m'><tr><th></th>" + "".join(f"<th>{A[k]}</th>" for k in K) + "</tr>"
    for i, k in enumerate(K):
        s += f"<tr><th>{A[k]}</th>"
        for j in range(n):
            v = M[i][j]
            s += f"<td style='background:{renk(v)}'>{fmt(v)}</td>"
        s += "</tr>"
    return s + "</table>"


mx = max(max(r) for r in d["D_ort_derece"])
yakin = lambda v: f"rgba(122,59,29,{max(0.0, 1 - v / mx):.2f})"
kor = lambda v: f"rgba(42,93,122,{min(1.0, abs(v)):.2f})" if v > 0 else f"rgba(160,40,40,{min(1.0, abs(v)):.2f})"
t1 = tablo(d["D_ort_derece"], "Yönlü ortalama açı mesafesi d(satır → sütun), derece", lambda v: f"{v:.1f}", yakin)
t2 = tablo(d["kismi_korelasyon"], "Kısmî korelasyon (öbür on iki merkez sabitken)", lambda v: f"{v:.2f}", kor)
asim = d["asimetri_orani"] * 100
html = f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mana Kategorisi</title><style>
body{{font-family:Georgia,serif;max-width:1100px;margin:auto;padding:16px;line-height:1.6;background:#fbf8f1;color:#222}}
table.m{{border-collapse:collapse;font-size:12px}}table.m td,table.m th{{border:1px solid #ddd;padding:3px 5px;text-align:center}}
.sc{{overflow-x:auto}}code{{background:#eee;padding:0 3px}}svg{{max-width:100%;height:auto}}
</style></head><body>
<p><a href="kuran_hikmetleri_lugat.html">← Lugat</a></p>
<h1>Mana Kategorisi: bir kavram, âyetlerinin bulutudur</h1>
<p>Bu sayfada on üç kavram (kök), kendi geçtiği âyetlerin Türkçe mealinden <code>qwen3-embedding-8b</code> modeliyle ({d['boyut']} boyutlu birim vektörler) çıkarılan birer <b>nokta bulutu</b> olarak alınır. Her kökten en çok 40 âyet, sıra korunarak eşit aralıkla seçilmiştir (adetler: {', '.join(f"{A[k]} {d['adet'][k]}" for k in K)}). Kavramlar arası ilişki, bulutlar arası <b>yönlü açı mesafesi</b> ve <b>Gram matrisinin tersi</b>nden hesaplanır; çizim Graphviz'dir.</p>
<h2>Kullanılan araçlar</h2>
<ul>
<li><b>Lawvere zenginleştirilmiş kategori.</b> Nesneler kavramlar; hom(A,B) = d(A→B) = bulut A'daki her noktanın B'deki en yakın noktaya açısının ortalaması. Kosinüs benzerliği üçgen eşitsizliğini sağlamadığı için ham kosinüs değil <b>arccos</b> (açı) kullanıldı. Üçgen eşitsizliği sınandı: ortalamalı sürümde {d['ucgen_ihlal_ort'][0]}/{d['ucgen_ihlal_ort'][1]}, azamî (Hausdorff) sürümünde {d['ucgen_ihlal_max'][0]}/{d['ucgen_ihlal_max'][1]} ihlâl. Azamî sürüm için eşitsizlik ispatlıdır; ortalamalı sürüm için bu yalnız bu veride görülen bir sonuçtur, ispat değildir.</li>
<li><b>Yoneda görünümü.</b> Her kavram, öbürlerine olan mesafe satırıyla (temsil edilebilir profil) tanıtılır; iki kavramın profili aynıysa ayırt edilemezler. Her kavramın profil bakımından en yakın komşusu JSON'da kayıtlıdır.</li>
<li><b>Kısmî korelasyon (koşullu bağımsızlık).</b> Merkez vektörlerin Gram matrisi G'nin tersi P alınır, ρ_ij = −P_ij/√(P_ii·P_jj). Kondisyon sayısı {d['gram_cond']:.0f}: ters hesaplanabilir (13 vektör 4096 boyutta).</li>
<li><b>Chow-Liu ağacı.</b> |ρ| ağırlıklı en büyük kapsayan ağaç, kesikli mavi çizgilerdir. Eşik konmaz, ağaç parametresizdir.</li>
<li>Kahverengi oklar: her kavramdan en yakın kavrama giden ok (eşiksiz, düğüm başına bir ok).</li>
</ul>
<h2>Şema</h2><div class="sc">{svg}</div>
<h2>Ne çıktı</h2>
<ul>
<li>Şükür ile hamd birbirinin en yakını ve ağaçta bağlıdırlar; küfür ile zulüm karşılıklı en yakındır; havf takvâya bağlanır; sabır tevekküle bağlanır.</li>
<li><b>Kapsama asimetrisi çıkmadı.</b> |d(A→B) − d(B→A)| ortalaması, mesafelerin ortalamasının yalnız %{asim:.1f}'idir ve hiçbir çiftte 3 dereceyi geçmez. Yani bu ölçüyle "A, B'nin içindedir ama B, A'nın içinde değildir" diyebileceğimiz bir çift bulunamadı. Bunun sebebi bulutların hepsinin aynı mealden gelmesi ve modelin üslup boyutunun baskın olması olabilir; bu bir tahmindir, sınanmadı.</li>
<li>Bu yüzden "kapsama" iddiası yapılmaz; kapsama için başka bir kaynak (kavramın tanım cümleleri, lügat metinleri) ayrıca denenmelidir.</li>
</ul>
<h2>Yapıştırılan metne tenkit</h2>
<ul>
<li>"Kosinüs benzerliği kapsamadır" yanlıştır: kosinüs simetriktir, kapsama asimetriktir. Yönlülük ancak bulutlar (kümeler) alınınca, yönlü mesafeyle gelir.</li>
<li>Kosinüs üçgen eşitsizliğini sağlamaz; Lawvere kategorisi için açı mesafesi gerekir.</li>
<li>Kesişim tensörü formülü ve "hacim ∝ ⟨x,y⟩" iddiaları metinde ispatsızdır; bu sayfada kullanılmadı.</li>
<li>Kısmî korelasyon ile Gram tersi sağlam araçtır ve kullanıldı; fakat korelasyon nedensellik veya anlamsal bağımlılık değil, embedding uzayındaki doğrusal bağımlılık söyler.</li>
</ul>
<p>Veri: <a href="kaynak/lugat/pilot/kategori/kategori.json">kategori.json</a> · <a href="kaynak/lugat/pilot/kategori/kategori.dot">kategori.dot</a></p>
{t1.replace("<table", "<div class='sc'><table", 1)}</div>
{t2.replace("<table", "<div class='sc'><table", 1)}</div>
</body></html>"""
(B / "kok_kategori.html").write_text(html, encoding="utf-8")
