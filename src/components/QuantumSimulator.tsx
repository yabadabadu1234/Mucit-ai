import React, { useState, useEffect } from 'react';
import { QuditState } from '../types';
import { Cpu, Zap, Activity, ShieldAlert, Sliders, RefreshCw, BarChart3, Atom } from 'lucide-react';

export const QuantumSimulator: React.FC = () => {
  const [quditCount, setQuditCount] = useState<number>(16);
  const [levelDim, setLevelDim] = useState<number>(4);
  const [cartanAngle, setCartanAngle] = useState<number>(0.785); // pi/4
  const [gateDepth, setGateDepth] = useState<number>(8);
  const [loading, setLoading] = useState(false);
  const [simData, setSimData] = useState<{
    states: QuditState[];
    vonNeumannEntropy: number;
    bargmannInvariant: number;
    uhlmannFidelity: number;
  } | null>(null);

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

            {/* Qudit Count */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-[#ece3cf]">Qudit Sayısı (N):</span>
                <span className="font-mono-code text-[#e08856] font-bold">{quditCount} qudit</span>
              </div>
              <input
                type="range"
                min="4"
                max="32"
                step="4"
                value={quditCount}
                onChange={(e) => setQuditCount(Number(e.target.value))}
                className="w-full accent-[#e08856] bg-[#16130e] h-1.5 rounded-lg cursor-pointer"
              />
              <span className="text-[10px] text-[#6f6449] block">
                Zırh kapasitesi: {quditCount} × {levelDim} = {quditCount * levelDim} serbestlik derecesi
              </span>
            </div>

            {/* Level Dimension q */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-[#ece3cf]">Qudit Tabanı (q):</span>
                <span className="font-mono-code text-[#e08856] font-bold">{levelDim} seviye</span>
              </div>
              <div className="grid grid-cols-4 gap-2">
                {[2, 4, 8, 16].map((qVal) => (
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

            {/* Lie-Cartan Phase Angle */}
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

            {/* Gate Depth */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-[#ece3cf]">Kapı Derinliği (51 Kapı Çevrimi):</span>
                <span className="font-mono-code text-[#e08856] font-bold">{gateDepth} katman</span>
              </div>
              <input
                type="range"
                min="1"
                max="24"
                step="1"
                value={gateDepth}
                onChange={(e) => setGateDepth(Number(e.target.value))}
                className="w-full accent-[#e08856] bg-[#16130e] h-1.5 rounded-lg cursor-pointer"
              />
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
                Mahallî Yazmaç Qudit Genlik Dağılımı (|Ψ_k|²)
              </span>
              <span className="text-xs font-mono-code text-[#a89a78]">
                N = {quditCount} qudit
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
    </div>
  );
};
