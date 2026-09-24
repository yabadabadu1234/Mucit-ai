import React, { useState } from 'react';
import { Play, CheckCircle2, AlertTriangle, Shield, Sparkles, RefreshCw, Cpu, BookOpen, Layers } from 'lucide-react';

interface TestRapor {
  test: string;
  durum: string;
  detay: string;
}

export function KulliyatTestLab() {
  const [loadingTest, setLoadingTest] = useState(false);
  const [testSonuc, setTestSonuc] = useState<TestRapor[] | null>(null);

  const [loadingEgitim, setLoadingEgitim] = useState(false);
  const [egitimSonuc, setEgitimSonuc] = useState<any>(null);

  const [loadingCikarim, setLoadingCikarim] = useState(false);
  const [cikarimMetni, setCikarimMetni] = useState('Ahmet şirkette amir olarak Mehmet\'e yetki verdi');
  const [cikarimSonuc, setCikarimSonuc] = useState<any>(null);

  async function testleriCalistir() {
    setLoadingTest(true);
    try {
      const res = await fetch('/api/kulliyat/test');
      const json = await res.json();
      if (json.success && json.data?.raporlar) {
        setTestSonuc(json.data.raporlar);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingTest(false);
    }
  }

  async function egitimiCalistir() {
    setLoadingEgitim(true);
    try {
      const res = await fetch('/api/kulliyat/egit', { method: 'POST' });
      const json = await res.json();
      if (json.success && json.data) {
        setEgitimSonuc(json.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingEgitim(false);
    }
  }

  async function cikarimiCalistir(ozelMetin?: string) {
    const metin = ozelMetin || cikarimMetni;
    setLoadingCikarim(true);
    try {
      const res = await fetch('/api/kulliyat/cikarim', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ metin })
      });
      const json = await res.json();
      if (json.success && json.data) {
        setCikarimSonuc(json.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingCikarim(false);
    }
  }

  return (
    <div className="space-y-8 pb-12">
      <div className="bg-[#1c1810] border border-[#362f22] rounded-2xl p-6 relative overflow-hidden shadow-xl">
        <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none">
          <Layers className="w-64 h-64 text-[#e08856]" />
        </div>
        <div className="relative z-10 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono-code bg-[#3a2418] text-[#e08856] border border-[#e08856]/40">
                FASIL I - XVI BÜTÜNLEŞİK NİZAM
              </span>
              <span className="text-xs text-[#a89a78] font-mono-code">Qudit $\mathbb&#123;C&#125;^d$ &middot; Grothendieck Lifleri</span>
            </div>
            <h2 className="text-2xl font-serif-fraunces font-bold text-[#ece3cf]">
              Külliyât Tahkik ve Test Laboratuvarı
            </h2>
            <p className="text-sm text-[#a89a78] max-w-3xl mt-1">
              n-li Bargmann İntacı, Wilson-Wilczek Holonomisi, Möbius Yıkıcı Girişimi, Hodge Spektral Saflaştırması,
              Zeno, Kato, Baker-Akhiezer ve Sıkıştırılmış Vakum imkânlarını tek tıkla canlı olarak sınayınız.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={testleriCalistir}
              disabled={loadingTest}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#e08856] text-[#16130e] font-semibold text-xs transition-all hover:bg-[#eb9d70] disabled:opacity-50 shadow-md"
            >
              {loadingTest ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
              <span>Testleri Çalıştır</span>
            </button>

            <button
              onClick={egitimiCalistir}
              disabled={loadingEgitim}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#261f16] border border-[#e08856]/40 text-[#e08856] font-medium text-xs transition-all hover:bg-[#332a1e] disabled:opacity-50"
            >
              {loadingEgitim ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Cpu className="w-4 h-4" />}
              <span>Eğitimi Koştur</span>
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-[#1c1810] border border-[#362f22] rounded-2xl p-5 flex flex-col h-full">
          <div className="flex items-center justify-between pb-3 border-b border-[#362f22] mb-4">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-[#e08856]" />
              <h3 className="text-sm font-serif-fraunces font-semibold text-[#ece3cf]">
                Teorik İspat ve Kanun Doğrulama Raporu
              </h3>
            </div>
            <span className="text-[11px] font-mono-code text-[#a89a78]">
              {testSonuc ? `${testSonuc.length} Test Geçti` : 'Henüz çalıştırılmadı'}
            </span>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto max-h-[500px] pr-1">
            {!testSonuc ? (
              <div className="text-center py-16 text-[#a89a78]">
                <BookOpen className="w-10 h-10 mx-auto mb-3 opacity-30 text-[#e08856]" />
                <p className="text-sm">Yukarıdaki "Testleri Çalıştır" butonuna basarak 8 küllî nizamı test ediniz.</p>
              </div>
            ) : (
              testSonuc.map((r, i) => (
                <div key={i} className="p-3.5 rounded-xl bg-[#16130e] border border-[#362f22] text-xs">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-mono-code font-semibold text-[#e08856]">{r.test}</span>
                    <span className="inline-flex items-center gap-1 text-[11px] font-mono-code text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-800/40">
                      <CheckCircle2 className="w-3 h-3" />
                      {r.durum}
                    </span>
                  </div>
                  <p className="text-[#a89a78] leading-relaxed font-mono-code text-[11px]">{r.detay}</p>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="bg-[#1c1810] border border-[#362f22] rounded-2xl p-5 flex flex-col h-full space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#362f22]">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#e08856]" />
              <h3 className="text-sm font-serif-fraunces font-semibold text-[#ece3cf]">
                Canlı İntaç ve Çıkarım Laboratuvarı
              </h3>
            </div>
            <span className="text-[11px] font-mono-code text-[#a89a78]">Bağımlı Lif Açılımı</span>
          </div>

          <div className="space-y-2">
            <label className="text-xs text-[#a89a78] font-medium">Muhakeme Girdisi (Önerme / Cümle):</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={cikarimMetni}
                onChange={(e) => setCikarimMetni(e.target.value)}
                className="flex-1 bg-[#16130e] border border-[#362f22] rounded-xl px-3.5 py-2 text-xs text-[#ece3cf] focus:outline-none focus:border-[#e08856]"
                placeholder="Örnek: Penguen kuştur fakat suda yüzer..."
              />
              <button
                onClick={() => cikarimiCalistir()}
                disabled={loadingCikarim}
                className="px-3.5 py-2 rounded-xl bg-[#3a2418] text-[#e08856] border border-[#e08856]/40 hover:bg-[#4a2e1f] text-xs font-medium transition-all"
              >
                {loadingCikarim ? <RefreshCw className="w-4 h-4 animate-spin" /> : 'Çıkarım Yap'}
              </button>
            </div>

            <div className="flex flex-wrap gap-1.5 pt-1">
              {[
                'Ahmet şirkette amir olarak yetki verdi',
                'Ahmet ile Mehmet deruni takva muhasebesi yaptılar',
                'Penguen bir kuştur fakat suda yüzer',
                'Bu önerme aynı anda hem doğrudur hem yanlıştır'
              ].map((ornek, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setCikarimMetni(ornek);
                    cikarimiCalistir(ornek);
                  }}
                  className="text-[10px] px-2 py-1 rounded bg-[#16130e] text-[#a89a78] border border-[#362f22] hover:text-[#ece3cf] hover:border-[#e08856]/40 transition-all truncate max-w-full"
                >
                  {ornek}
                </button>
              ))}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto max-h-[360px] p-3 rounded-xl bg-[#16130e] border border-[#362f22] text-xs font-mono-code">
            {!cikarimSonuc ? (
              <div className="text-center py-12 text-[#a89a78]">
                Bir cümle seçiniz veya yazıp "Çıkarım Yap" butonuna basınız.
              </div>
            ) : (
              <div className="space-y-2.5 text-[11px]">
                <div className="flex justify-between border-b border-[#362f22] pb-1.5">
                  <span className="text-[#a89a78]">Seçilen Tip:</span>
                  <span className="text-[#e08856] font-semibold">{cikarimSonuc.tip} ({cikarimSonuc.mertebe})</span>
                </div>
                <div className="flex justify-between border-b border-[#362f22] pb-1.5">
                  <span className="text-[#a89a78]">Kategori / Kaide:</span>
                  <span className="text-[#ece3cf]">{cikarimSonuc.kaideler?.kural}</span>
                </div>
                <div className="flex justify-between border-b border-[#362f22] pb-1.5">
                  <span className="text-[#a89a78]">J-Aynası Zıt Kutbu:</span>
                  <span className="text-[#ece3cf]">{cikarimSonuc.j_aynasi_zit_kutup}</span>
                </div>
                <div className="flex justify-between border-b border-[#362f22] pb-1.5">
                  <span className="text-[#a89a78]">İntaç Dokusu:</span>
                  <span className="text-[#e08856]">{cikarimSonuc.intac?.topoloji} &middot; r={cikarimSonuc.intac?.r_n} &middot; Φ={cikarimSonuc.intac?.phi_n} rad</span>
                </div>
                <div className="flex justify-between border-b border-[#362f22] pb-1.5">
                  <span className="text-[#a89a78]">Devridaim / Holonomi:</span>
                  <span className="text-[#ece3cf]">{cikarimSonuc.holonomi?.cins} &middot; Norm={cikarimSonuc.holonomi?.norm}</span>
                </div>
                {cikarimSonuc.sheaf_re_gluing && (
                  <div className="p-2 rounded bg-amber-950/20 border border-amber-800/40 text-amber-200">
                    Sheaf Re-Gluing: {cikarimSonuc.sheaf_re_gluing.yeni_lif} lifi kütüphaneye eklendi!
                  </div>
                )}
                <div className="p-2.5 rounded bg-[#261f16] border border-[#e08856]/40 text-[#ece3cf] font-serif-fraunces text-xs">
                  {cikarimSonuc.hukum}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {egitimSonuc && (
        <div className="bg-[#1c1810] border border-[#362f22] rounded-2xl p-5">
          <div className="flex items-center justify-between pb-3 border-b border-[#362f22] mb-4">
            <h3 className="text-sm font-serif-fraunces font-semibold text-[#ece3cf]">
              Küllî Eğitim Raporu (Tahfîz Fıtrat Kalibrasyonu ve ARC K-Bargmann)
            </h3>
            <span className="text-xs font-mono-code text-[#e08856]">Makam: {egitimSonuc.rust_makami}</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="text-xs font-mono-code text-[#a89a78] mb-2">1. Safha: Bebeklik Tahfîz Adımları</h4>
              <div className="space-y-1.5">
                {egitimSonuc.tahfiz_adimlari?.map((t: any, idx: number) => (
                  <div key={idx} className="p-2 rounded bg-[#16130e] border border-[#362f22] text-[11px] font-mono-code flex justify-between">
                    <span className="text-[#ece3cf]">{t.cift}</span>
                    <span className="text-[#a89a78]">Hata: {t.hata} &middot; α={t.alpha}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-xs font-mono-code text-[#a89a78] mb-2">2. Safha: ARC-AGI-2 K-Bargmann Numuneleri</h4>
              <div className="space-y-1.5">
                {egitimSonuc.arc_egitimi?.map((a: any, idx: number) => (
                  <div key={idx} className="p-2 rounded bg-[#16130e] border border-[#362f22] text-[11px] font-mono-code flex justify-between">
                    <span className="text-[#ece3cf]">Görev {a.gorev}</span>
                    <span className="text-[#e08856]">r_K={a.r_K} &middot; {a.topoloji}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
