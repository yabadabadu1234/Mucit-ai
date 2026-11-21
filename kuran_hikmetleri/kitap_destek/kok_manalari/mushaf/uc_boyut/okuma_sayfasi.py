"""İnsan okuyucu için ETİKETLİ sayfa (F 3-I 409 şart g'nin kör nüshası ayrıdır: sekiller/). Şekil aynı formülden; noktalara yalnız numara konur."""
import json, base64, math, pathlib, io, html
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import munasebet_geometri as G
H = pathlib.Path(__file__).resolve().parent
SURE = H.parents[3] / 'kaynak' / 'sure'
AD = {0: 'emir', 1: 'ruhsat', 2: 'yasak', 3: 'gerekçe', 4: 'ilke'}
P = {
 '5:1-2': dict(s=5, r=[1, 2], baslik='Mâide 1–2', parca=[
  ('5:1', 'Ey iman edenler! Akitleri yerine getirin.', 'ahde vefa emri', 'dayandığı birim yok: kökte'),
  ('5:1', 'Sağmal hayvanlar sizin için helâl kılındı.', 'ahdin kapsamından birinci örnek', 'ahde dayanır (0)'),
  ('5:1', 'İhramlı iken avlanmayı helâl saymayın.', 'helâl hükmüne istisna', 'ahde dayanır (0)'),
  ('5:1', 'Allah dilediğine hükmeder.', 'bütün hükümlerin gerekçesi', 'ahde dayanır (0)'),
  ('5:2', 'Allah\'ın şeâirine, haram aya, kurbana, gerdanlıklara, Beyt-i Harâm\'a gelenlere hürmetsizlik etmeyin.', 'ahdin diğer koruma alanı: dinin alâmetleri', 'ahde dayanır (0)'),
  ('5:2', 'İhramdan çıkınca avlanabilirsiniz.', 'İHRAM-AV TEKRARI: ilkinde yasak, burada sınır bitince ruhsat', 'ihram yasağına dayanır (2)'),
  ('5:2', 'Sizi Mescid-i Harâm\'dan men ettiler diye bir kavme olan kininiz sizi haddi aşmaya sevk etmesin.', 'saygıyı bozacak sebebi kapatmak', 'şeâire saygıya dayanır (4)'),
  ('5:2', 'İyilik ve takvâ üzerine yardımlaşın, günah ve düşmanlık üzerine yardımlaşmayın.', 'sınırların genel ilkesi', 'şeâire saygıya dayanır (4)'),
  ('5:2', 'Allah\'tan sakının; Allah\'ın azabı çok şiddetlidir.', 'bütün emirlerin gerekçe uyarısı', 'ahde dayanır (0)')],
  gaye={'G0': 'Ahde vefa; Allah\'ın koyduğu sınırlara riayet (her şeyi kapsayan dış kubbe)', 'G1': 'Helâl–haram sınırını bildirmek (yiyecek ve av)', 'G2': 'Dinin alâmetlerine saygı ve öfkede aşırılığı önlemek', 'G3': 'Yardımlaşma ilkesi ve takva uyarısı'},
  hazif='Birim 0–1 arası: «akitler» denir ama içeriği sayılmaz; sayılanlar sonradan örnek olarak gelir. Hikmet ihtimali: ahdin kapsamı kasten açık bırakıldı.'),
 '88:17-21': dict(s=88, r=[17, 18, 19, 20, 21], baslik='Gâşiye 17–21', parca=[
  ('88:17', 'Develere bakmazlar mı, nasıl yaratılmış?', 'bakış emrinin başı', 'kökte'),
  ('88:18', 'Göğe (bakmazlar mı), nasıl yükseltilmiş?', 'aynı bakışın devamı', 'deve bakışına dayanır (0)'),
  ('88:19', 'Dağlara (bakmazlar mı), nasıl dikilmiş?', 'aynı bakışın devamı', 'deve bakışına dayanır (0)'),
  ('88:20', 'Yere (bakmazlar mı), nasıl yayılmış?', 'aynı bakışın devamı', 'deve bakışına dayanır (0)'),
  ('88:21', 'Öyleyse öğüt ver; sen ancak öğüt vericisin.', 'bakıştan öğüde geçiş', 'dört bakışın hepsine dayanır («fe» = öyleyse)')],
  gaye={'G0': 'Yaratılışa bakıp tevhide ve ahirete dönmek (dış kubbe)', 'G1': 'Yaratılış delillerine bakmayı emretmek', 'G2': 'Tebliğ görevini hatırlatmak'},
  hazif='Birim 3–4 arası: bakışın sonucu (hesap ve dönüş) burada söylenmeden öğüde geçilir. Hikmet ihtimali: sonuç öncesindeki âyetlerde veya sonrasında beklenir.'),
 '2:189-190': dict(s=2, r=[189, 190], baslik='Bakara 189–190', parca=[
  ('2:189', 'Hilâlleri soruyorlar. De ki: «Onlar insanlar ve hac için vakit ölçüleridir.»', 'sorunun cevabı: vakit', 'kökte'),
  ('2:189', 'İyilik, evlere arkalarından girmeniz değildir.', 'vakit/hac usûlündeki yanlış âdet', 'vakit/hac sorusuna dayanır (0)'),
  ('2:189', 'Evlere kapılarından girin ve Allah\'tan sakının.', 'doğru usûl ve takva', 'yanlış âdet reddine dayanır (1)'),
  ('2:190', 'Sizinle savaşanlarla Allah yolunda savaşın.', 'vakitle (haram aylar) bağlı sınır konusuna geçiş', 'vakit sorusuna dayanır (0)'),
  ('2:190', 'Haddi aşmayın; Allah haddi aşanları sevmez.', 'savaşta sınır', 'savaş emrine dayanır (3)')],
  gaye={'G0': 'Vakit ve usûlde sınırı gözetmek (dış kubbe)', 'G1': 'Doğru yoldan, doğru zamanda yapmak', 'G2': 'Savaşta sınır'},
  hazif='Birim 2–3 arası: savaşa geçişin sebebi sayılmaz. Hikmet ihtimali: sınır teması hilâl ve hacla ortak; bağ okuyucuya bırakıldı.')}

def resim(ad):
    mk, K = G.yukle(ad); S = G.kur(mk, K); X, Y, Z = G.izgara(S); ids = S['ids']
    px = [S['x'][u] for u in ids]; py = [S['y'][u] for u in ids]
    pz = [float(G.z_at(S, np.array([[S['x'][u]]]), np.array([[S['y'][u]]]))[0, 0]) for u in ids]
    th = [S['th'][u] for u in ids]
    fig = plt.figure(figsize=(14, 6), dpi=100)
    a = fig.add_subplot(1, 2, 1, projection='3d'); a.plot_surface(X, Y, Z, cmap='viridis', alpha=.7, linewidth=0, rstride=2, cstride=2)
    a.scatter(px, py, pz, c=th, cmap='hsv', vmin=0, vmax=2 * math.pi, s=80, edgecolor='k', depthshade=False); a.plot(px, py, pz, 'k-', lw=1)
    for i in range(len(ids)): a.text(px[i], py[i], pz[i] + .25, str(i), fontsize=13, weight='bold')
    a.view_init(28, -62); a.set_xlabel('sıra'); a.set_ylabel('illet derinliği'); a.set_zlabel('gaye kubbesi')
    d = fig.add_subplot(1, 2, 2); d.plot(X[0], Z.max(axis=0), 'k-')
    d.scatter(px, pz, c=th, cmap='hsv', vmin=0, vmax=2 * math.pi, s=80, edgecolor='k', zorder=3)
    for i in range(len(ids)): d.annotate(str(i), (px[i], pz[i]), xytext=(0, 9), textcoords='offset points', ha='center', fontsize=13, weight='bold')
    d.set_xlabel('sıra (birim numarası)'); d.set_ylabel('gaye kubbesinin yüksekliği'); d.set_xticks(range(len(ids)))
    for c in ('top', 'right'): d.spines[c].set_visible(False)
    fig.tight_layout(); b = io.BytesIO(); fig.savefig(b, format='png'); plt.close(fig)
    return base64.b64encode(b.getvalue()).decode(), mk, K, S

font = base64.b64encode(open(H.parents[1] / 'yazi' / 'Amiri-Regular.ttf', 'rb').read()).decode()
out = ['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Münâsebet şekli</title><style>@font-face{font-family:Amiri;src:url(data:font/ttf;base64,%s)}body{font:16px/1.6 Georgia,serif;max-width:960px;margin:auto;padding:16px;background:#fbf8f1;color:#222}h1,h2{font-weight:600}.ar{font:30px/2 Amiri;direction:rtl;text-align:right;background:#fff;border:1px solid #ddd;padding:8px 14px;border-radius:6px}.meal{margin:4px 0 14px;color:#333}table{border-collapse:collapse;width:100%%;margin:10px 0}td,th{border:1px solid #ccc;padding:6px 8px;font-size:15px;vertical-align:top}th{background:#eee}img{width:100%%;border:1px solid #ccc;background:#fff}.k{display:inline-block;width:12px;height:12px;border:1px solid #000;border-radius:7px;vertical-align:middle}.n{font-size:14px;color:#555}</style>' % font]
out.append('<h1>Âyet ile şekil arasındaki münasebet</h1><p class=n>Her noktanın yanındaki numara, aşağıdaki tabloda hangi cümleye karşılık geldiğini söyler. Renk: kırmızı emir · sarı-yeşil ruhsat · yeşil yasak · mavi gerekçe · mor ilke. Yükseklik gayedir: üst üste binen tepeler iç içe gayedir. Çukur söylenmeyendir. Tablodaki illet ve gaye cümleleri <b>hikmet ihtimalidir</b>, müfessire nisbet edilmiş hüküm değildir. Meal: Hayrat Neşriyat; 88. sûre için Diyanet.</p>')
for ad, d in P.items():
    b64, mk, K, S = resim(ad)
    out.append('<h2>%s</h2>' % d['baslik'])
    V = json.load(open(SURE / ('%d.json' % d['s']), encoding='utf-8'))['verses']
    for a in d['r']:
        v = V[a - 1]; t = v['turkish']; m = t.get('hayrat_nesriyat') if d['s'] != 88 else t.get('hayrat_nesriyat')
        out.append('<div class=ar>%s ﴿%s﴾</div><div class=meal>%s</div>' % (html.escape(v['arabic'].strip()), a, html.escape(m)))
    out.append('<img src="data:image/png;base64,%s">' % b64)
    out.append('<table><tr><th>No<th>Âyet<th>Cümle (mealden)<th>Neden burada (hikmet ihtimali)<th>Nereye dayanır (illet)<th>Makam<th>Gayesi')
    for i, (ay, c, ned, dy) in enumerate(d['parca']):
        u = K['birimler'][i]; out.append('<tr><td><b>%d</b><td>%s<td>%s<td>%s<td>%s<td>%s<td>%s' % (i, ay, html.escape(c), html.escape(ned), html.escape(dy), u['makam'], html.escape(d['gaye'][u['gaye']])))
    out.append('</table><p><b>Gaye kubbeleri:</b> ' + ' · '.join('%s = %s' % (g, html.escape(x)) for g, x in d['gaye'].items()) + '</p>')
    out.append('<p><b>Hazif (çukur):</b> %s</p>' % html.escape(d['hazif']))
    for a, b in K['tekrar']: out.append('<p><b>Tekrar:</b> %d ile %d aynı mesele (ihram–av); ikisi aynı yükseklikte değildir, çünkü gayeleri farklıdır.</p>' % ([x['id'] for x in K['birimler']].index(a), [x['id'] for x in K['birimler']].index(b)))
open(H / 'OKUMA_SAYFASI.html', 'w', encoding='utf-8').write(''.join(out))
