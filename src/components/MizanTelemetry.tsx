import React, { useState, useEffect } from 'react';
import { TelemetrySummary } from '../types';
import { Activity, Clock, ShieldCheck, Cpu, AlertTriangle, CheckCircle, BarChart2, Terminal } from 'lucide-react';

export const MizanTelemetry: React.FC = () => {
  const [telemetry, setTelemetry] = useState<TelemetrySummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTelemetry() {
      try {
        const res = await fetch('/api/telemetry');
        const data = await res.json();
        if (data.success) {
          setTelemetry(data.data);
        }
      } catch (err) {
        console.error('Failed to load telemetry:', err);
      } finally {
        setLoading(false);
      }
    }
    loadTelemetry();
  }, []);

  if (loading) {
    return (
      <div className="p-12 text-center text-[#a89a78] bg-[#1c1810] rounded-xl border border-[#362f22]">
        <Activity className="w-6 h-6 animate-pulse mx-auto mb-2 text-[#e08856]" />
        Telemetri ve ölçüm verileri taranıyor...
      </div>
    );
  }

  if (!telemetry) {
    return (
      <div className="p-12 text-center text-[#a89a78] bg-[#1c1810] rounded-xl border border-[#362f22]">
        Telemetri verisi bulunamadı.
      </div>
    );
  }

  return (
    <div className="flex flex-col space-y-6 w-full">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#1c1810] border border-[#362f22] p-4 rounded-xl flex items-center justify-between">
          <div>
            <span className="text-xs text-[#a89a78] font-mono-code">Mîzân Sadakati</span>
            <h4 className="text-2xl font-serif-fraunces font-bold text-emerald-400 mt-1">
              %{(telemetry.son_sadakat * 100).toFixed(1)}
            </h4>
            <span className="text-[10px] text-[#6f6449]">Uhlmann Metriği</span>
          </div>
          <div className="p-2.5 bg-emerald-950/40 text-emerald-400 rounded-lg border border-emerald-800/30">
            <ShieldCheck className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#1c1810] border border-[#362f22] p-4 rounded-xl flex items-center justify-between">
          <div>
            <span className="text-xs text-[#a89a78] font-mono-code">İdrak Süresi / Çağrı</span>
            <h4 className="text-2xl font-serif-fraunces font-bold text-[#e08856] mt-1">
              {telemetry.sure_sn.toFixed(2)} sn
            </h4>
            <span className="text-[10px] text-[#6f6449]">B=128 küme hacmi</span>
          </div>
          <div className="p-2.5 bg-[#3a2418] text-[#e08856] rounded-lg border border-[#e08856]/30">
            <Clock className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#1c1810] border border-[#362f22] p-4 rounded-xl flex items-center justify-between">
          <div>
            <span className="text-xs text-[#a89a78] font-mono-code">Canlı Parametreler</span>
            <h4 className="text-2xl font-serif-fraunces font-bold text-[#ece3cf] mt-1">
              {telemetry.parametre}
            </h4>
            <span className="text-[10px] text-[#6f6449]">Profil: {telemetry.ayar}</span>
          </div>
          <div className="p-2.5 bg-[#1b2533] text-sky-400 rounded-lg border border-sky-800/30">
            <Cpu className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#1c1810] border border-[#362f22] p-4 rounded-xl flex items-center justify-between">
          <div>
            <span className="text-xs text-[#a89a78] font-mono-code">Kayıp Çağrısı</span>
            <h4 className="text-2xl font-serif-fraunces font-bold text-[#ece3cf] mt-1">
              0 (Sıfır)
            </h4>
            <span className="text-[10px] text-emerald-400 font-mono-code">Fermân 2-P: Analitik Eğim</span>
          </div>
          <div className="p-2.5 bg-[#2a1d2e] text-[#b06ec9] rounded-lg border border-[#b06ec9]/30">
            <CheckCircle className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Bottlenecks & Breakdown from docs/MELEKE_HARITASI.md */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 bg-[#1c1810] border border-[#362f22] p-5 rounded-xl space-y-4">
          <div className="flex items-center justify-between border-b border-[#362f22] pb-3">
            <span className="text-sm font-semibold text-[#ece3cf] flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-[#e08856]" />
              44 QMeleke İçi Darboğaz Tensip Haritası (%54 Yükü Taşıyan 6 Meleke)
            </span>
            <span className="text-xs font-mono-code text-[#a89a78]">MPO Sektörleri</span>
          </div>

          <p className="text-xs text-[#a89a78] leading-relaxed">
            Fasıl 1 gereğince tek tek ölçülen süre payları. 38 meleke toplam %6 pay tutarken, aşağıdaki 6 meleke işlem zamanının %54'ünü oluşturur.
          </p>

          <div className="space-y-3 pt-2">
            {telemetry.darbogazlar.map((d, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex items-center justify-between text-xs font-mono-code">
                  <span className="text-[#ece3cf] font-semibold flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-[#e08856]" />
                    {d.meleke}
                  </span>
                  <div className="flex items-center gap-3">
                    <span className="text-[#6f6449]">{d.sure} sn</span>
                    <span className="text-[#e08856] font-bold w-12 text-right">%{d.pay}</span>
                  </div>
                </div>
                <div className="w-full bg-[#16130e] h-2 rounded-full overflow-hidden border border-[#362f22]">
                  <div
                    className="bg-[#e08856] h-full rounded-full"
                    style={{ width: `${d.pay * 3.5}%` }}
                  />
                </div>
                <span className="text-[10px] font-mono-code text-[#6f6449] block pl-4">
                  Ameliye: {d.ameliye}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Multi-Objective Loss Vector & Training Diary */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-[#1c1810] border border-[#362f22] p-5 rounded-xl space-y-4">
            <span className="text-sm font-semibold text-[#ece3cf] flex items-center gap-2 border-b border-[#362f22] pb-3">
              <Activity className="w-4 h-4 text-[#7ba05b]" />
              Mîzân Kefeler Vektörü (ℒ = (ℓ₁, …, ℓ_m))
            </span>

            <div className="bg-[#16130e] p-3 rounded-lg border border-[#362f22] space-y-2 text-xs font-mono-code">
              <div className="flex justify-between py-1 border-b border-[#362f22]/50">
                <span className="text-[#a89a78]">ℓ_Dizi (Merkez Kefe):</span>
                <span className="text-[#ece3cf] font-semibold">22.919</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#362f22]/50">
                <span className="text-[#a89a78]">ℓ_Keyfiyet (Kabul Şartı):</span>
                <span className="text-emerald-400 font-semibold">0.002</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#362f22]/50">
                <span className="text-[#a89a78]">ℓ_Sadakat (Uhlmann):</span>
                <span className="text-emerald-400 font-semibold">0.016</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#362f22]/50">
                <span className="text-[#a89a78]">ℓ_Monogami (CKW Eşitsizliği):</span>
                <span className="text-[#ece3cf] font-semibold">0.097</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-[#a89a78]">ℓ_Hodge (Topolojik Ayrışım):</span>
                <span className="text-[#ece3cf] font-semibold">0.024</span>
              </div>
            </div>

            <p className="text-[11px] text-[#6f6449] leading-relaxed">
              Fermân 1-V: Kayıp skaler değildir; ℒ vektördür. Toplama ancak en sonda eniyileyici sıralama isterken açıkça yapılır.
            </p>
          </div>

          {/* Training Diary Stream */}
          <div className="bg-[#1c1810] border border-[#362f22] p-5 rounded-xl space-y-3">
            <span className="text-sm font-semibold text-[#ece3cf] flex items-center gap-2 border-b border-[#362f22] pb-3">
              <Terminal className="w-4 h-4 text-[#e08856]" />
              Tâlim Günlüğü Akışı
            </span>

            <div className="bg-[#16130e] p-3 rounded-lg border border-[#362f22] max-h-48 overflow-y-auto space-y-1 font-mono-code text-[11px] text-[#a89a78]">
              {telemetry.talim_gunlugu.length > 0 ? (
                telemetry.talim_gunlugu.map((entry, idx) => (
                  <div key={idx} className="hover:text-[#ece3cf] transition-colors">
                    {typeof entry === 'string' ? entry : JSON.stringify(entry)}
                  </div>
                ))
              ) : (
                <div className="text-[#6f6449] italic">Son adımda ölçülen telemetri kayıtları günceldir.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
