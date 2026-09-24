import React, { useState, useEffect } from 'react';
import { QuditState } from '../types';
import { Cpu, Zap, Activity, ShieldAlert, Sliders, RefreshCw, BarChart3, Atom, Play, CheckCircle2, Shield, Sparkles } from 'lucide-react';

export const QuantumSimulator: React.FC = () => {
  const [quditCount, setQuditCount] = useState<number>(1048576);
  const [levelDim, setLevelDim] = useState<number>(64);
  const [cartanAngle, setCartanAngle] = useState<number>(0.785);
  const [gateDepth, setGateDepth] = useState<number>(51);
  const [loading, setLoading] = useState(false);
  const [simData, setSimData] = useState<{
    states: QuditState[];
    vonNeumannEntropy: number;
    bargmannInvariant: number;
    uhlmannFidelity: number;
    N?: number;
    q?: number;
    mahalliSerbestlik?: number;
    kapasite?: string;
    aktifQudit?: number;
    seyirciQudit?: number;
    seyirciNorm?: number;
    temsilNizami?: string;
  } | null>(null);

  const [loadingTest, setLoadingTest] = useState(false);
  const [testSonuc, setTestSonuc] = useState<any[] | null>(null);
  const [loadingEgitim, setLoadingEgitim] = useState(false);
  const [egitimSonuc, setEgitimSonuc] = useState<any>(null);
  const [loadingCikarim, setLoadingCikarim] = useState(false);
  const [cikarimMetni, setCikarimMetni] = useState('Penguen bir kuştur fakat suda yüzer');
  const [cikarimSonuc, setCikarimSonuc] = useState<any>(null);

  const fetchKulliyatTest = async () => {
    setLoadingTest(true);
    try {
      const res = await fetch('/api/kulliyat/test');
      const data = await res.json();
      if (data.success && data.data?.raporlar) {
        setTestSonuc(data.data.raporlar);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingTest(false);
    }
  };

  const fetchKulliyatEgitim = async () => {
    setLoadingEgitim(true);
    try {
      const res = await fetch('/api/kulliyat/egit', { method: 'POST' });
      const data = await res.json();
      if (data.success && data.data) {
        setEgitimSonuc(data.data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingEgitim(false);
    }
  };

  const fetchKulliyatCikarim = async (metinGirdi?: string) => {
    const metin = metinGirdi || cikarimMetni;
    setLoadingCikarim(true);
    try {
      const res = await fetch('/api/kulliyat/cikarim', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ metin })
      });
      const data = await res.json();
      if (data.success && data.data) {
        setCikarimSonuc(data.data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingCikarim(false);
    }
  };

  const fetchSimulation = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/qudit/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          N: quditCount,
          q: levelDim,
          cartanAngle,
          gateCount: gateDepth
        })
      });
      const data = await res.json();
      if (data.success) {
        setSimData(data);
      }
    } catch (err) {
      console.error('Simulation fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSimulation();
  }, [quditCount, levelDim, cartanAngle, gateDepth]);

  return (
    <div className="flex flex-col space-y-6 w-full">
      {/* Overview Banner */}
      <div className="bg-[#1c1810] border border-[#362f22] p-5 rounded-xl flex flex-wrap gap-4 items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-[#3a2418] text-[#e08856] rounded-lg">
            <Atom className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-serif-fraunces font-bold text-[#ece3cf]">
              Kuantum Qudit &amp; KAN-NQS Fonksiyonel Simülatörü
            </h3>
            <p className="text-xs text-[#a89a78]">
              Mahallî yazmaç ℂ^(N×q), Lie-Cartan açıları ve Chebyshev polinom tabanlı KAN genlik üretimi.
            </p>
          </div>
        </div>

        <button
          onClick={fetchSimulation}
          className="flex items-center gap-2 bg-[#16130e] hover:bg-[#251f16] border border-[#362f22] px-3.5 py-1.5 rounded-lg text-xs text-[#ece3cf] transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-[#e08856] ${loading ? 'animate-spin' : ''}`} />
          Yeniden Hesapla
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Parameter Controls */}
        <div className="lg:col-span-4 space-y-5">
          <div className="bg-[#1c1810] border border-[#362f22] p-5 rounded-xl space-y-5">
            <span className="text-xs font-mono-code text-[#a89a78] uppercase tracking-wider flex items-center gap-2 border-b border-[#362f22] pb-3">
              <Sliders className="w-4 h-4 text-[#e08856]" />
              Fiziksel Parametreler
            </span>

            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-[#ece3cf]">Qudit Sayısı (N):</span>
                <span className="font-mono-code text-[#e08856] font-bold">{quditCount.toLocaleString()} qudit</span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { n: 1048576, etiket: '1 Milyon Zırh (1048576)' },
                  { n: 65536, etiket: '65,536 Qudit' },
                  { n: 4096, etiket: '4,096 Qudit' },
                  { n: 64, etiket: '64 Qudit' }
                ].map((item) => (
                  <button
                    key={item.n}
                    onClick={() => setQuditCount(item.n)}
                    className={`py-1.5 px-2 text-[11px] rounded border transition-colors font-mono-code ${
                      quditCount === item.n
                        ? 'bg-[#3a2418] border-[#e08856] text-[#e08856] font-bold'
                        : 'bg-[#16130e] border-[#362f22] text-[#a89a78] hover:text-[#ece3cf]'
                    }`}
                  >
                    {item.etiket}
                  </button>
                ))}
              </div>
              <span className="text-[10px] text-[#6f6449] block">
                Kapasite: {levelDim}^{quditCount} | Mahallî Serbestlik: 2N = {(2 * quditCount).toLocaleString()}
              </span>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-[#ece3cf]">Qudit Tabanı (q):</span>
                <span className="font-mono-code text-[#e08856] font-bold">{levelDim} seviye</span>
              </div>
              <div className="grid grid-cols-4 gap-2">
                {[2, 4, 16, 64].map((qVal) => (
                  <button
                    key={qVal}
                    onClick={() => setLevelDim(qVal)}
                    className={`py-1.5 text-xs rounded border transition-colors font-mono-code ${
                      levelDim === qVal
                        ? 'bg-[#3a2418] border-[#e08856] text-[#e08856] font-bold'
                        : 'bg-[#16130e] border-[#362f22] text-[#a89a78] hover:text-[#ece3cf]'
                    }`}
                  >
                    q={qVal}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-[#ece3cf]">Lie-Cartan Açısı (θ):</span>
                <span className="font-mono-code text-[#e08856] font-bold">
                  {(cartanAngle / Math.PI).toFixed(2)}π ({cartanAngle.toFixed(3)} rad)
                </span>
              </div>
              <input
                type="range"
                min="-3.14"
                max="3.14"
                step="0.05"
                value={cartanAngle}
                onChange={(e) => setCartanAngle(Number(e.target.value))}
                className="w-full accent-[#e08856] bg-[#16130e] h-1.5 rounded-lg cursor-pointer"
              />
              <span className="text-[10px] text-[#6f6449] block">
                Fermân 1-A #36: Sürekli Lie-Cartan açısı θ ∈ [−π, π]
              </span>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-[#ece3cf]">Kapı Derinliği (51 Kapı Tetabuku):</span>
                <span className="font-mono-code text-[#e08856] font-bold">{gateDepth} kapı</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {[8, 24, 51].map((gVal) => (
                  <button
                    key={gVal}
                    onClick={() => setGateDepth(gVal)}
                    className={`py-1.5 text-xs rounded border transition-colors font-mono-code ${
                      gateDepth === gVal
                        ? 'bg-[#3a2418] border-[#e08856] text-[#e08856] font-bold'
                        : 'bg-[#16130e] border-[#362f22] text-[#a89a78] hover:text-[#ece3cf]'
                    }`}
                  >
                    {gVal} Kapı
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Invariants & Fidelity Metric Card */}
          {simData && (
            <div className="bg-[#1c1810] border border-[#362f22] p-5 rounded-xl space-y-4">
              <span className="text-xs font-mono-code text-[#a89a78] uppercase tracking-wider block border-b border-[#362f22] pb-3">
                Topolojik Değişmezler &amp; Sadakat
              </span>

              <div className="space-y-3">
                <div className="flex items-center justify-between p-2.5 bg-[#16130e] rounded-lg border border-[#362f22]">
                  <span className="text-xs text-[#ece3cf]">Uhlmann Sadakati</span>
                  <span className="text-sm font-mono-code font-bold text-emerald-400">
                    {simData.uhlmannFidelity}
                  </span>
                </div>

                <div className="flex items-center justify-between p-2.5 bg-[#16130e] rounded-lg border border-[#362f22]">
                  <span className="text-xs text-[#ece3cf]">Bargmann 3-Durum Değişmezi</span>
                  <span className="text-sm font-mono-code font-bold text-[#e08856]">
                    {simData.bargmannInvariant}
                  </span>
                </div>

                <div className="flex items-center justify-between p-2.5 bg-[#16130e] rounded-lg border border-[#362f22]">
                  <span className="text-xs text-[#ece3cf]">von Neumann Dolaşıklık Entropisi</span>
                  <span className="text-sm font-mono-code font-bold text-sky-400">
                    {simData.vonNeumannEntropy} bit
                  </span>
                </div>
              </div>

              <p className="text-[11px] text-[#6f6449] leading-relaxed">
                Fermân 2-Ø: χ ≤ 64 alan kanunu sınırında tutulur; ara hesap artıkları sıfırlanarak durum kararlılığı korunur.
              </p>
            </div>
          )}
        </div>

        {/* Right Column: Qudit States & Amplitude Visualization */}
        <div className="lg:col-span-8 space-y-5">
          <div className="bg-[#1c1810] border border-[#362f22] p-5 rounded-xl space-y-4">
            <div className="flex items-center justify-between border-b border-[#362f22] pb-3">
              <span className="text-sm font-semibold text-[#ece3cf] flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-[#e08856]" />
                Küllî Zırh Aktif Penceresi &amp; Qudit Dağılımı (|Ψ_k|²)
              </span>
              <span className="text-xs font-mono-code text-[#a89a78]">
                N = {quditCount.toLocaleString()} qudit ({simData?.seyirciQudit?.toLocaleString() || 0} Seyirci)
              </span>
            </div>

            {simData ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-2">
                  {simData.states.map((s) => {
                    const heightPercent = Math.max(12, Math.min(100, s.probability * 300));
                    return (
                      <div
                        key={s.quditIndex}
                        className="bg-[#16130e] p-2.5 rounded-lg border border-[#362f22] flex flex-col items-center justify-between space-y-2"
                      >
                        <span className="text-[10px] font-mono-code text-[#a89a78]">
                          q_{s.quditIndex}
                        </span>

                        {/* Visual Bar */}
                        <div className="w-full bg-[#221d14] h-24 rounded flex flex-col justify-end p-1">
                          <div
                            className="w-full rounded-sm transition-all duration-300"
                            style={{
                              height: `${heightPercent}%`,
                              backgroundColor: `hsl(${Math.abs(s.cartanPhase * 40) % 360}, 70%, 55%)`
                            }}
                          />
                        </div>

                        <div className="text-center w-full">
                          <span className="text-[10px] font-mono-code text-[#ece3cf] block font-bold">
                            {(s.probability * 100).toFixed(1)}%
                          </span>
                          <span className="text-[8px] font-mono-code text-[#6f6449] block truncate" title={`θ=${s.cartanPhase}`}>
                            θ={s.cartanPhase}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* State Vector Table */}
                <div className="overflow-x-auto mt-4 border border-[#362f22] rounded-lg">
                  <table className="w-full text-left text-xs text-[#ece3cf]">
                    <thead className="bg-[#16130e] text-[#a89a78] font-mono-code text-[11px] border-b border-[#362f22]">
                      <tr>
                        <th className="p-2.5">Qudit İndisi</th>
                        <th className="p-2.5">Cartan Fazı (θ)</th>
                        <th className="p-2.5">Reel Bileşen (T_j)</th>
                        <th className="p-2.5">İmajiner Bileşen (U_j)</th>
                        <th className="p-2.5">Ölçüm Olasılığı</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#362f22]/50 font-mono-code text-[11px]">
                      {simData.states.slice(0, 8).map((s) => (
                        <tr key={s.quditIndex} className="hover:bg-[#1f1a13] transition-colors">
                          <td className="p-2.5 text-[#e08856] font-semibold">q_{s.quditIndex}</td>
                          <td className="p-2.5">{s.cartanPhase} rad</td>
                          <td className="p-2.5">{s.real}</td>
                          <td className="p-2.5">{s.imag}i</td>
                          <td className="p-2.5 text-emerald-400">{(s.probability * 100).toFixed(2)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-[#a89a78]">
                Hesaplama yapılıyor...
              </div>
            )}
          </div>

          {/* Mathematical formulation block */}
          <div className="bg-[#1c1810] border border-[#362f22] p-5 rounded-xl space-y-3 font-mono-code text-xs text-[#a89a78]">
            <span className="text-xs font-semibold text-[#ece3cf] block">
              Fermân 2-T &amp; KAN-NQS Fonksiyonel Eşitliği:
            </span>
            <div className="bg-[#16130e] p-3 rounded-lg border border-[#362f22] text-[#e08856] overflow-x-auto">
              Ψ(w; θ) = (1 / √Z) · exp( ∑_k Φ_k(ω(w; θ)) )
              <br />
              Φ_k = ∑_j C[k,j] · T_j(u) + i ∑_j S[k,j] · U_j(u)
            </div>
            <p className="text-[11px] text-[#6f6449]">
              Burada T_j Chebyshev birinci nevi, U_j Chebyshev ikinci nevi polinomlarıdır. Matris tersi (κ = 1.0) yoktur, küsürat korunur.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-[#1c1810] border border-[#362f22] rounded-2xl p-6 space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-[#362f22]">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Shield className="w-5 h-5 text-[#e08856]" />
              <h3 className="text-lg font-serif-fraunces font-bold text-[#ece3cf]">
                Külliyât Tahkik ve Test Laboratuvarı
              </h3>
            </div>
            <p className="text-xs text-[#a89a78]">
              Bargmann İntacı, Wilson-Wilczek Holonomisi, Möbius Yıkıcı Girişimi, Tomita Modüler Akışı, Toda Sıralaması, Nyaya ve Silojizma Kıyasları.
            </p>
          </div>

          <div className="flex flex-wrap gap-2.5">
            <button
              onClick={fetchKulliyatTest}
              disabled={loadingTest}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#e08856] text-[#16130e] font-semibold text-xs hover:bg-[#eb9d70] disabled:opacity-50 transition-all shadow"
            >
              {loadingTest ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
              <span>Testleri Çalıştır</span>
            </button>

            <button
              onClick={fetchKulliyatEgitim}
              disabled={loadingEgitim}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#261f16] border border-[#e08856]/40 text-[#e08856] font-medium text-xs hover:bg-[#332a1e] disabled:opacity-50 transition-all"
            >
              {loadingEgitim ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Cpu className="w-4 h-4" />}
              <span>Eğitimi Koştur</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-3">
            <h4 className="text-xs font-mono-code font-semibold text-[#ece3cf] flex items-center justify-between">
              <span>8 Küllî Teorem Raporu</span>
              <span className="text-[#a89a78]">{testSonuc ? `${testSonuc.length} Test Geçti` : 'Beklemede'}</span>
            </h4>

            <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
              {!testSonuc ? (
                <div className="p-8 text-center text-xs text-[#a89a78] bg-[#16130e] rounded-xl border border-[#362f22]">
                  "Testleri Çalıştır" butonuna tıklayarak teorem ve kanunları sınayabilirsiniz.
                </div>
              ) : (
                testSonuc.map((r: any, idx: number) => (
                  <div key={idx} className="p-3 rounded-xl bg-[#16130e] border border-[#362f22] text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono-code font-semibold text-[#e08856]">{r.test}</span>
                      <span className="inline-flex items-center gap-1 text-[10px] font-mono-code text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-800/40">
                        <CheckCircle2 className="w-3 h-3" />
                        {r.durum}
                      </span>
                    </div>
                    <p className="text-[#a89a78] font-mono-code text-[11px] leading-relaxed">{r.detay}</p>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="text-xs font-mono-code font-semibold text-[#ece3cf] flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-[#e08856]" />
              <span>Canlı İntaç ve Kıyas Çıkarımı</span>
            </h4>

            <div className="space-y-2">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={cikarimMetni}
                  onChange={(e) => setCikarimMetni(e.target.value)}
                  className="flex-1 bg-[#16130e] border border-[#362f22] rounded-xl px-3.5 py-2 text-xs text-[#ece3cf] focus:outline-none focus:border-[#e08856]"
                  placeholder="Örnek: Penguen bir kuştur fakat suda yüzer..."
                />
                <button
                  onClick={() => fetchKulliyatCikarim()}
                  disabled={loadingCikarim}
                  className="px-3.5 py-2 rounded-xl bg-[#3a2418] text-[#e08856] border border-[#e08856]/40 hover:bg-[#4a2e1f] text-xs font-medium transition-all"
                >
                  {loadingCikarim ? <RefreshCw className="w-4 h-4 animate-spin" /> : 'Çıkarım Yap'}
                </button>
              </div>

              <div className="flex flex-wrap gap-1.5">
                {[
                  'Penguen bir kuştur fakat suda yüzer',
                  'Ahmet şirkette amir olarak yetki verdi',
                  'Bu önerme aynı anda hem doğrudur hem yanlıştır'
                ].map((orn, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setCikarimMetni(orn);
                      fetchKulliyatCikarim(orn);
                    }}
                    className="text-[10px] px-2 py-0.5 rounded bg-[#16130e] text-[#a89a78] border border-[#362f22] hover:text-[#ece3cf] hover:border-[#e08856]/40 transition-all"
                  >
                    {orn}
                  </button>
                ))}
              </div>

              <div className="p-3 rounded-xl bg-[#16130e] border border-[#362f22] text-xs font-mono-code max-h-[260px] overflow-y-auto space-y-2">
                {!cikarimSonuc ? (
                  <div className="text-center py-8 text-[#a89a78]">
                    Bir önerme seçip "Çıkarım Yap" butonuna basınız.
                  </div>
                ) : (
                  <>
                    {cikarimSonuc.bir_milyon_qudit_zirhi && (
                      <div className="p-2 rounded bg-[#1e1912] border border-[#e08856]/40 text-[#ece3cf] text-[11px] space-y-1">
                        <div className="flex justify-between font-bold text-[#e08856]">
                          <span>Küllî Zırh (1,048,576 Qudit)</span>
                          <span>2N = {cikarimSonuc.bir_milyon_qudit_zirhi.mahalli_serbestlik?.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-[#a89a78] text-[10px]">
                          <span>Aktif: {cikarimSonuc.bir_milyon_qudit_zirhi.aktif_qudit} &middot; Seyirci: {cikarimSonuc.bir_milyon_qudit_zirhi.seyirci_qudit?.toLocaleString()}</span>
                          <span className="text-emerald-400">Norm = {cikarimSonuc.bir_milyon_qudit_zirhi.seyirci_ic_carpim_norm}</span>
                        </div>
                        <div className="text-[10px] text-[#a89a78] flex justify-between">
                          <span>FS: {cikarimSonuc.bir_milyon_qudit_zirhi.fubini_study_mesafe} &middot; KAN: {cikarimSonuc.bir_milyon_qudit_zirhi.kan_genlik_norm}</span>
                          <span className="text-emerald-400">51 Kapı: {cikarimSonuc.bir_milyon_qudit_zirhi.kapi_51_tetabuk?.sadakat}</span>
                        </div>
                        <div className="text-[10px] text-[#6f6449]">
                          Çift Yazmaç: {cikarimSonuc.bir_milyon_qudit_zirhi.cift_yazmac_kenet?.kulliyet}
                        </div>
                      </div>
                    )}
                    <div className="flex justify-between border-b border-[#362f22] pb-1">
                      <span className="text-[#a89a78]">Tip &amp; Mertebe:</span>
                      <span className="text-[#e08856] font-semibold">{cikarimSonuc.vecih?.tip} ({cikarimSonuc.vecih?.mertebe})</span>
                    </div>
                    <div className="flex justify-between border-b border-[#362f22] pb-1">
                      <span className="text-[#a89a78]">İntaç &amp; Holonomi:</span>
                      <span className="text-[#ece3cf]">{cikarimSonuc.intac_manifoldu?.topoloji} &middot; {cikarimSonuc.holonomi_devridaim?.cins}</span>
                    </div>
                    <div className="flex justify-between border-b border-[#362f22] pb-1">
                      <span className="text-[#a89a78]">Mantikî Silojizma:</span>
                      <span className="text-[#ece3cf]">{cikarimSonuc.kuantum_mantik_usulleri?.barbara_aaa1}</span>
                    </div>
                    {cikarimSonuc.sheaf_re_gluing && (
                      <div className="p-1.5 rounded bg-amber-950/20 border border-amber-800/40 text-amber-200 text-[11px]">
                        Sheaf Re-Gluing: {cikarimSonuc.sheaf_re_gluing.yeni_lif} lifi eklendi!
                      </div>
                    )}
                    <div className="p-2 rounded bg-[#261f16] border border-[#e08856]/40 text-[#ece3cf] text-xs font-serif-fraunces">
                      {cikarimSonuc.nihai_hukum}
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {egitimSonuc && (
          <div className="p-4 rounded-xl bg-[#16130e] border border-[#362f22] space-y-2">
            <div className="flex justify-between text-xs font-mono-code">
              <span className="font-semibold text-[#ece3cf]">Küllî Eğitim Neticesi (1,048,576 Qudit Zırhı)</span>
              <span className="text-[#e08856]">Makam: {egitimSonuc.nihai_rust_makami}</span>
            </div>
            {egitimSonuc.bir_milyon_qudit_zirhi && (
              <div className="p-2 rounded bg-[#1e1912] border border-[#e08856]/40 text-[#ece3cf] text-[11px] flex flex-wrap justify-between gap-2 font-mono-code">
                <span>1,048,576 Qudit Çift Yazmaç: <strong>{egitimSonuc.bir_milyon_qudit_zirhi.cift_yazmac_kenet?.kulliyet}</strong></span>
                <span>Fubini-Study: <strong>{egitimSonuc.bir_milyon_qudit_zirhi.fubini_study_mesafe}</strong></span>
                <span>KAN-Norm: <strong>{egitimSonuc.bir_milyon_qudit_zirhi.kan_genlik_norm}</strong></span>
                <span>51 Kapı Sadakati: <strong className="text-emerald-400">{egitimSonuc.bir_milyon_qudit_zirhi.kapi_51_tetabuk?.sadakat}</strong></span>
              </div>
            )}
            <div className="text-[11px] font-mono-code text-[#a89a78] grid grid-cols-1 md:grid-cols-2 gap-2 pt-1">
              <div>
                <span className="text-[#ece3cf] block mb-1">Tahfîz Adımları (Bebeklik):</span>
                {egitimSonuc.tahfiz_adimlari?.map((t: any, i: number) => (
                  <div key={i} className="py-1 border-b border-[#362f22]/50 last:border-0">
                    <div className="flex justify-between">
                      <span className="text-[#ece3cf]">{t.kutup}</span>
                      <span className="text-[#e08856]">α={t.alpha_rust} &middot; Hata: {t.hata}</span>
                    </div>
                    <div className="text-[10px] text-[#6f6449] flex justify-between">
                      <span>{t.zirh_aktif_qudit} aktif / {t.zirh_seyirci_qudit?.toLocaleString()} seyirci</span>
                      <span>FS={t.fubini_study_mesafe} &middot; 51 Kapı: {t.kapi_51_sadakat}</span>
                    </div>
                  </div>
                ))}
              </div>
              <div>
                <span className="text-[#ece3cf] block mb-1">ARC $K$-Bargmann Tahkik:</span>
                {egitimSonuc.tahkik_arc?.map((a: any, i: number) => (
                  <div key={i} className="py-1 border-b border-[#362f22]/50 last:border-0">
                    <div className="flex justify-between">
                      <span className="text-[#ece3cf]">Görev {a.gorev}</span>
                      <span className="text-emerald-400">r_K={a.r_K} &middot; Sadakat: {String(a.mantiga_sadakat)}</span>
                    </div>
                    <div className="text-[10px] text-[#6f6449] flex justify-between">
                      <span>{a.zirh_aktif_qudit} aktif qudit</span>
                      <span>FS={a.zirh_fubini_study} &middot; KAN={a.kan_genlik_norm}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
