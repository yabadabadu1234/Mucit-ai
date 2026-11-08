import json, pathlib, collections, subprocess, re, html
B = pathlib.Path(__file__).resolve().parent.parent
H = pathlib.Path(__file__).resolve().parent
kenar = json.load(open(H / "metin_kenarlari.json", encoding="utf-8"))
olcu = json.load(open(H / "olcu.json", encoding="utf-8")); olcu2 = json.load(open(H / "olcu_dengeli.json", encoding="utf-8"))
anlam = {x["kok"]: x["turkce"] for x in json.load(open(B / "kaynak/lugat/kok_anlamlari.json", encoding="utf-8"))}
def kisa(k, n=46):
    t = re.split(r"[;(]", anlam.get(k, ""))[0].strip(); return t[:n]
ref = set(); yon = collections.defaultdict(lambda: {"neden": [], "netice": []})
TUR = {"sart": "şart → cevap", "sebep": "sebep → netice", "gaye": "iş → gaye"}
for key, v in kenar.items():
    x, y = key.split("|"); n = sum(v["n"].values())
    e = {"t": v["n"], "n": n, "m": v["m"], "v": v["delil"]}
    ref.update(v["delil"])
    yon[x]["netice"].append({"k": y, **e}); yon[y]["neden"].append({"k": x, **e})
for k in yon:
    for a in ("neden", "netice"): yon[k][a].sort(key=lambda e: -e["m"])
ay = {}
for s in range(1, 115):
    d = json.load(open(B / f"kaynak/sure/{s}.json", encoding="utf-8"))
    for v in d["verses"]:
        key = f"{s}:{v['verseNumber']}"
        if key in ref:
            t = v["turkish"]; t = (eval(t) if t.startswith("{") else {"x": t}) if isinstance(t, str) else t
            ay[key] = [v["arabic"].strip(), re.sub(r"<[^>]+>", "", (t.get("diyanet_vakfi") if isinstance(t.get("diyanet_vakfi"), str) and t.get("diyanet_vakfi") else next((x for x in t.values() if isinstance(x, str) and x), "")))]
veri = {k: {"m": anlam.get(k, ""), **yon[k]} for k in yon}
top = sorted(((v["m"], k) for k, v in kenar.items()), reverse=True)[:40]
dot = ['digraph I { rankdir=LR; bgcolor="transparent"; node [shape=box,style="rounded,filled",fillcolor="#f4efe3",fontname="Amiri",fontsize=12]; edge [fontname="Amiri",fontsize=10];']
renk = {"sart": "#2a5d7a", "sebep": "#7a3b1d", "gaye": "#3a6b3a"}; d = set()
for n, key in top:
    x, y = key.split("|"); 
    for z in (x, y):
        if z not in d: d.add(z); dot.append(f'"{z}" [label="{z}\\n{kisa(z,24).replace(chr(34),"")}"];')
    t = max(kenar[key]["n"], key=kenar[key]["n"].get)
    dot.append(f'"{x}" -> "{y}" [color="{renk[t]}",fontcolor="{renk[t]}",label="{TUR[t]} · {n:.1f}"];')
dot.append("}")
svg = subprocess.run(["dot", "-Tsvg"], input="\n".join(dot).encode(), capture_output=True, check=True).stdout.decode(); svg = svg[svg.index("<svg"):]
J = json.dumps({"k": veri, "a": ay, "tur": TUR}, ensure_ascii=False)
sayfa = f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kök İlliyeti</title><style>
body{{font-family:Georgia,serif;max-width:1000px;margin:auto;padding:16px;line-height:1.6;background:#fbf8f1;color:#222}}
input{{width:100%;padding:8px;font-size:16px}}.k{{cursor:pointer;margin:2px;padding:2px 8px;border:1px solid #bbb;border-radius:12px;display:inline-block;background:#fff}}
.col{{display:inline-block;vertical-align:top;width:48%;min-width:300px}}.e{{border-bottom:1px solid #ddd;padding:6px 0}}.ar{{font-family:Amiri,serif;font-size:20px;direction:rtl}}
.t{{font-size:12px;color:#7a3b1d}}small{{color:#555}}svg{{max-width:100%;height:auto}}.uyari{{background:#fff3d6;padding:8px;border-radius:6px}}
</style></head><body><p><a href="kuran_hikmetleri_lugat.html">← Lugat</a></p>
<h1>Kök İlliyeti: Kur'ân kendi bağlaçlarıyla neyi neye bağlıyor</h1>
<p>Burada her ok, Kur'ân'ın <b>kendi cümlesinde</b> kurduğu bir bağdır: <i>eğer … ise …</i> (şart → cevap), <i>…; bu yüzden …</i> (sebep → netice), <i>… için …</i> (iş → gaye). Kökler bu bağların iki yanındaki kelimelerin kökleridir. Her bağın altında okuyabileceğiniz âyet gösterilir.</p>
<p class="uyari">Bu, Kur'ân'ın <b>beyan ettiği</b> illiyettir (bağlaçların yakın penceresi), felsefî anlamda ispatlanmış sebep–sonuç değildir. Pencere her iki yandan sekiz kelimedir; yan cümleler karışmış olabilir, o yüzden âyeti okuyun.</p>
<h2>En sık kurulan 40 bağ</h2>{svg}
<h2>Köke göre bakın</h2><input id="q" placeholder="Arapça kök veya Türkçe anlam yazın (ör. صبر, sabır, ateş)…"><div id="liste"></div><div id="sonuc"></div>
<h2>Gömme (embedding) denemesi: ne çıktı</h2>
<p>Yalnız metinden çıkan bağların ötesine geçmek için her kökü, anlamı ve geçtiği bütün âyetlerin vektörlerinden oluşan bir temsille ifade edip sebep→netice yönünü öğrenen iki-doğrusal bir tensör modeli denedim. Sayılar, bağların %20'sini saklayıp modelin onları bulup bulamadığıyla ölçüldü.</p>
<table border="1" cellpadding="4" style="border-collapse:collapse"><tr><th>Ölçü</th><th>Yalnız kök derecesi</th><th>Tam model</th><th>Yalnız anlam/bağlam</th></tr>
<tr><td>Rastgele olumsuz örneklerle AUC</td><td>{olcu['derece_yalniz']['AUC']}</td><td>{olcu['tam_model']['AUC']}</td><td>{olcu['icerik_yalniz']['AUC']}</td></tr>
<tr><td>Derece-dengeli olumsuz örneklerle AUC</td><td>{olcu2['derece_yalniz']['AUC']}</td><td>{olcu2['tam_model']['AUC']}</td><td>{olcu2['icerik_yalniz']['AUC']}</td></tr>
<tr><td>Yön doğruluğu (dengeli)</td><td>{olcu2['derece_yalniz']['yon_dogrulugu']}</td><td>{olcu2['tam_model']['yon_dogrulugu']}</td><td>{olcu2['icerik_yalniz']['yon_dogrulugu']}</td></tr></table>
<p><b>İkinci deneme (yalnız tensör cebiri):</b> Âyet vektörlerini Mushaf sırasıyla dizip bir sonraki âyeti önceki âyetten tahmin eden doğrusal bir akış operatörü (kapalı formlu ridge/VAR) kurdum; kök köklerin bu operatör altındaki yönlü etkisinden sebep→netice okunmaya çalışıldı. Boyut 64–256, gecikme 1–3 âyet ve iki ceza katsayısı denendi; en iyi AUC 0,54, yön doğruluğu 0,47–0,52, yani şans düzeyi. Mushaf sırası sebep sırası değildir ve vektör uzayı kendi başına yön taşımaz.</p><p><b>Yorum:</b> Rastgele olumsuzlarla yüksek görünen başarı, bazı köklerin zaten çok bağda yer almasından geliyor (kök derecesi tek başına 0,98). Bu etki çıkarıldığında anlam ve bağlam vektörlerinin eklediği bilgi zayıf kalıyor (AUC 0,57–0,60; yön doğruluğu yaklaşık yarı yarıya). Bu nedenle sayfada <b>modelin tahmin ettiği hiçbir bağ gösterilmiyor</b>; yalnız Kur'ân'ın kendi kurduğu bağlar gösteriliyor.</p>
<script>const V={J};const L=document.getElementById('liste'),S=document.getElementById('sonuc'),Q=document.getElementById('q');
function ara(){{const t=Q.value.trim().toLowerCase();L.innerHTML='';let c=0;for(const k in V.k){{const m=V.k[k].m.toLowerCase();if(!t||k.includes(t)||m.includes(t)){{if(c++>60)break;const b=document.createElement('span');b.className='k';b.textContent=k+' · '+(V.k[k].m.split(/[;(]/)[0].slice(0,24));b.onclick=()=>goster(k);L.appendChild(b)}}}}}}
function satir(e){{const tt=Object.entries(e.t).map(([a,n])=>V.tur[a]+' '+n+'×').join(', ');const m=(V.k[e.k]||{{}}).m||'';return '<div class="e"><b>'+e.k+'</b> <small>'+m.split(/[;(]/)[0]+'</small><div class="t">'+tt+'</div>'+e.v.map(r=>{{const a=V.a[r]||['',''];return '<div class="ar">'+a[0]+'</div><small>'+r+' — '+a[1]+'</small>'}}).join('')+'</div>'}}
function goster(k){{const v=V.k[k];S.innerHTML='<h3>'+k+' <small>'+v.m+'</small></h3><div class="col"><h4>Sebepleri / öncesindekiler ('+v.neden.length+')</h4>'+v.neden.slice(0,25).map(satir).join('')+'</div><div class="col"><h4>Neticeleri / sonrasındakiler ('+v.netice.length+')</h4>'+v.netice.slice(0,25).map(satir).join('')+'</div>'}}
Q.oninput=ara;ara();</script></body></html>"""
(B / "kok_illiyet.html").write_text(sayfa, encoding="utf-8")
print(len(sayfa)//1024, "KB;", len(veri), "kök;", len(ay), "âyet")
