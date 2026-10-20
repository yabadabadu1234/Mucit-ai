"""Konu hiperçizgesi: 1800'e yakın konu düğüm, konuların âyetleri hiperkenarın elemanları.

- Konular, Qwen3.5-4B embedding vektörlerinin (konu_vektor.py) kosinüs benzerliğinden klasik MDS ile
  2 boyuta yerleşir: benzer konular birbirine yakın durur.
- Her âyet, bağlı olduğu konuların yerleşim merkezlerinin ortalamasında bir nokta olur.
- Her konunun âyetleri kendi rengiyle gösterilir; âyet birden çok konudaysa renkleri karışır.

Çıktı: `ag_bolumu()` kitaba girecek HTML bölümünü döndürür (tuval + veri gömülü).
"""
import json
from pathlib import Path

import numpy as np

from konu_haritasi import konulari_oku
from konu_vektor import ONBELLEK

BASE = Path(__file__).resolve().parent


def koordinatlar(vektorler):
    """Kosinüs uzaklığında klasik MDS; (N, 2) koordinatları [0, 1] aralığına ölçeklenir."""
    v = vektorler / np.linalg.norm(vektorler, axis=1, keepdims=True)
    benzerlik = v @ v.T
    uzaklik = np.clip(1.0 - benzerlik, 0.0, 2.0) ** 2
    n = uzaklik.shape[0]
    merkez = np.eye(n) - np.ones((n, n)) / n
    b = -0.5 * merkez @ uzaklik @ merkez
    degerler, vektor = np.linalg.eigh(b)
    ilk = np.argsort(degerler)[::-1][:2]
    xy = vektor[:, ilk] * np.sqrt(np.maximum(degerler[ilk], 0.0))
    xy = (xy - xy.min(axis=0)) / (np.ptp(xy, axis=0) + 1e-12)
    return xy


def veri_hazirla():
    npz = np.load(ONBELLEK / "konu_vektorleri.npz")
    adlar = [str(a) for a in npz["adlar"]]
    xy = koordinatlar(npz["vektor"])
    atiflar = {k: a for k, a in konulari_oku() if a}
    konular = []
    for i, ad in enumerate(adlar):
        ayetler = []
        for sure, a, b in atiflar[ad]:
            ayetler.extend((sure, ayet) for ayet in range(a, b + 1))
        konular.append({"ad": ad, "x": float(xy[i, 0]), "y": float(xy[i, 1]), "ayetler": ayetler})
    return konular


def ag_bolumu():
    konular = veri_hazirla()
    veri = json.dumps(konular, ensure_ascii=False, separators=(",", ":"))
    return f"""
    <div class="page doc-page konu-ag">
      <h2>Konu ağı · hiperçizge</h2>
      <p class="kag-not">Her renkli bölge bir konu. Konular, embedding benzerliğine göre yerleşir: yakın konular yakında durur.
      Âyetler konularının renkleriyle gösterilir; birden çok konuda geçen âyetin renkleri karışır. Üzerine gelin: konu adı.</p>
      <canvas id="kag-tuval" width="1400" height="1000"></canvas>
      <div id="kag-ipucu" class="kag-ipucu"></div>
    </div>
    <style>
      .konu-ag canvas {{ width:100%; height:auto; background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; }}
      .kag-not {{ font-size:9.5pt; color:#475569; margin:6px 0; }}
      .kag-ipucu {{ font-size:10pt; min-height:1.4em; margin-top:6px; color:#0f172a; }}
    </style>
    <script>
    (function () {{
      const konular = {veri};
      const tuval = document.getElementById('kag-tuval');
      const g = tuval.getContext('2d');
      const W = tuval.width, H = tuval.height, PAD = 60;
      const px = x => PAD + x * (W - 2 * PAD), py = y => PAD + y * (H - 2 * PAD);
      const renk = i => `hsl(${{Math.round(i * 137.508) % 360}}, 70%, 45%)`;
      const rgb = i => {{ const h = (i * 137.508) % 360, s = .7, l = .45;
        const c = (1 - Math.abs(2 * l - 1)) * s, x = c * (1 - Math.abs((h / 60) % 2 - 1)), m = l - c / 2;
        let r, g2, b; if (h < 60) [r, g2, b] = [c, x, 0]; else if (h < 120) [r, g2, b] = [x, c, 0];
        else if (h < 180) [r, g2, b] = [0, c, x]; else if (h < 240) [r, g2, b] = [0, x, c];
        else if (h < 300) [r, g2, b] = [x, 0, c]; else [r, g2, b] = [c, 0, x];
        return [(r + m) * 255, (g2 + m) * 255, (b + m) * 255]; }};
      // âyet → konu indisleri; konum: bağlı konuların merkezlerinin ortalaması + sabit küçük sapma
      const ayetKonu = new Map();
      konular.forEach((k, i) => k.ayetler.forEach(a => {{
        const anahtar = a[0] * 1000 + a[1];
        if (!ayetKonu.has(anahtar)) ayetKonu.set(anahtar, []);
        ayetKonu.get(anahtar).push(i);
      }}));
      const noktalar = [];
      ayetKonu.forEach((liste, anahtar) => {{
        let mx = 0, my = 0;
        liste.forEach(i => {{ mx += konular[i].x; my += konular[i].y; }});
        mx /= liste.length; my /= liste.length;
        const sapma = ((anahtar * 9301 + 49297) % 233280) / 233280;
        const aci = ((anahtar * 7919) % 6283) / 1000;
        const r = 0.02 + 0.03 * sapma;
        noktalar.push({{ x: mx + r * Math.cos(aci), y: my + r * Math.sin(aci), liste }});
      }});
      function ciz() {{
        g.clearRect(0, 0, W, H);
        // konu bölgeleri: kendi renginde yarı saydam halo
        konular.forEach((k, i) => {{
          const r = 18 + 6 * Math.sqrt(k.ayetler.length);
          const [cr, cg, cb] = rgb(i);
          const gr = g.createRadialGradient(px(k.x), py(k.y), 0, px(k.x), py(k.y), r);
          gr.addColorStop(0, `rgba(${{cr}},${{cg}},${{cb}},0.22)`);
          gr.addColorStop(1, `rgba(${{cr}},${{cg}},${{cb}},0)`);
          g.fillStyle = gr;
          g.beginPath(); g.arc(px(k.x), py(k.y), r, 0, 2 * Math.PI); g.fill();
        }});
        // âyetler (hiperkenar elemanları): konu renklerinin karışımı
        noktalar.forEach(p => {{
          let R = 0, G = 0, B = 0;
          p.liste.forEach(i => {{ const c = rgb(i); R += c[0]; G += c[1]; B += c[2]; }});
          const n = p.liste.length;
          g.fillStyle = `rgba(${{Math.round(R / n)}},${{Math.round(G / n)}},${{Math.round(B / n)}},0.85)`;
          g.beginPath(); g.arc(px(p.x), py(p.y), 2.2, 0, 2 * Math.PI); g.fill();
        }});
      }}
      ciz();
      const ipucu = document.getElementById('kag-ipucu');
      tuval.addEventListener('mousemove', e => {{
        const r = tuval.getBoundingClientRect();
        const mx = (e.clientX - r.left) * W / r.width, my = (e.clientY - r.top) * H / r.height;
        let en = null, d2 = 1e9;
        konular.forEach(k => {{ const dx = px(k.x) - mx, dy = py(k.y) - my, d = dx * dx + dy * dy;
          if (d < d2) {{ d2 = d; en = k; }} }});
        ipucu.textContent = en && d2 < 40 * 40 ? `${{en.ad}} · ${{en.ayetler.length}} âyet` : '';
      }});
    }})();
    </script>
    """
