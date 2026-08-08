import React, { useState } from 'react';
import { Play, RotateCcw, Zap, CheckCircle2, ArrowRight, ShieldCheck, Cpu } from 'lucide-react';

interface MatMulSimulatorProps {
  onExecute: (dimM: number, dimK: number, dimN: number) => void;
  logs: string[];
}

export const MatMulSimulator: React.FC<MatMulSimulatorProps> = ({ onExecute, logs }) => {
  const [dimM, setDimM] = useState<number>(32768);
  const [dimK, setDimK] = useState<number>(32768);
  const [dimN, setDimN] = useState<number>(32768);

  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [resultMatrixSizeGb, setResultMatrixSizeGb] = useState<number>(4.0);

  const calculateMatrixGb = (m: number, n: number) => {
    return ((m * n * 4) / (1024 * 1024 * 1024)).toFixed(2);
  };

  const handleRunSimulation = () => {
    setIsRunning(true);
    setCurrentStep(1);

    setTimeout(() => {
      setCurrentStep(2);
    }, 800);

    setTimeout(() => {
      setCurrentStep(3);
    }, 1600);

    setTimeout(() => {
      setCurrentStep(4);
      setIsRunning(false);
      onExecute(dimM, dimK, dimN);
    }, 2400);
  };

  const matrixAGb = calculateMatrixGb(dimM, dimK);
  const matrixBGb = calculateMatrixGb(dimK, dimN);
  const matrixCGb = calculateMatrixGb(dimM, dimN);

  return (
    <div className="flex flex-col gap-6 font-mono text-[#E4E3E0] p-4 md:p-6 bg-[#0A0A0B] flex-1 overflow-y-auto">
      {/* Title Header */}
      <div className="border border-[#2A2A2D] bg-[#0F0F12] p-5 rounded relative overflow-hidden">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] text-[#00FFD0] uppercase font-bold tracking-widest bg-[#00FFD0]/10 border border-[#00FFD0]/30 px-2 py-0.5 rounded flex items-center gap-1">
                <Zap className="w-3 h-3" /> OPERATÖR KANCASI SİMÜLATÖRÜ
              </span>
              <span className="text-[10px] text-white/40">TRANSPARENT OPERATOR HOOK</span>
            </div>
            <h2 className="text-xl font-bold tracking-tight text-white font-serif italic">
              Şeffaf Tensör Çarpımı & Fiziki CUDA Sevk Simülatörü
            </h2>
            <p className="text-xs text-white/60 mt-1 max-w-3xl leading-relaxed">
              Ana program sanal 88 GB adres uzayında devasa <code className="text-[#00FFD0] font-bold">A @ B</code> matris çarpımı istediğinde, sürücü bu emri yakalar (hook), tensörleri fiziki GPU&apos;lara böler ve sonucu ana programa teslim eder.
            </p>
          </div>
        </div>
      </div>

      {/* Interceptor Setup & Execution Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Input Matrix Config (5 cols) */}
        <div className="lg:col-span-5 border border-[#2A2A2D] bg-[#0F0F12] p-5 rounded space-y-4">
          <h3 className="font-serif italic text-xs text-white/60 uppercase">
            Sanal Matris Boyutları Ayarı
          </h3>

          <div className="space-y-3">
            <div>
              <label className="text-[11px] text-white/70 block mb-1">
                Matris A Satır Boyutu (M): <span className="text-[#00FFD0] font-bold">{dimM.toLocaleString()}</span>
              </label>
              <input
                type="range"
                min="8192"
                max="65536"
                step="4096"
                value={dimM}
                onChange={(e) => setDimM(Number(e.target.value))}
                className="w-full accent-[#00FFD0]"
              />
            </div>

            <div>
              <label className="text-[11px] text-white/70 block mb-1">
                Çarpım İç Boyut (K): <span className="text-[#00FFD0] font-bold">{dimK.toLocaleString()}</span>
              </label>
              <input
                type="range"
                min="8192"
                max="65536"
                step="4096"
                value={dimK}
                onChange={(e) => setDimK(Number(e.target.value))}
                className="w-full accent-[#00FFD0]"
              />
            </div>

            <div>
              <label className="text-[11px] text-white/70 block mb-1">
                Matris B Sütun Boyutu (N): <span className="text-[#00FFD0] font-bold">{dimN.toLocaleString()}</span>
              </label>
              <input
                type="range"
                min="8192"
                max="65536"
                step="4096"
                value={dimN}
                onChange={(e) => setDimN(Number(e.target.value))}
                className="w-full accent-[#00FFD0]"
              />
            </div>
          </div>

          {/* Matrix Specs Cards */}
          <div className="grid grid-cols-3 gap-2 pt-2 text-[10px]">
            <div className="p-2 border border-[#2A2A2D] bg-[#141417] rounded text-center">
              <div className="text-white/40">MATRİS A</div>
              <div className="text-xs font-bold text-[#00FFD0] font-mono">{matrixAGb} GB</div>
              <div className="text-[9px] text-white/50">{dimM} × {dimK}</div>
            </div>

            <div className="p-2 border border-[#2A2A2D] bg-[#141417] rounded text-center">
              <div className="text-white/40">MATRİS B</div>
              <div className="text-xs font-bold text-[#38BDF8] font-mono">{matrixBGb} GB</div>
              <div className="text-[9px] text-white/50">{dimK} × {dimN}</div>
            </div>

            <div className="p-2 border border-[#2A2A2D] bg-[#141417] rounded text-center">
              <div className="text-white/40">SONUÇ C</div>
              <div className="text-xs font-bold text-[#A78BFA] font-mono">{matrixCGb} GB</div>
              <div className="text-[9px] text-white/50">{dimM} × {dimN}</div>
            </div>
          </div>

          <button
            onClick={handleRunSimulation}
            disabled={isRunning}
            className={`w-full py-3 px-4 font-bold text-xs rounded border transition-all flex items-center justify-center gap-2 ${
              isRunning
                ? 'bg-[#00FFD0]/20 text-[#00FFD0] border-[#00FFD0]/50 animate-pulse'
                : 'bg-[#00FFD0] text-[#0A0A0B] border-[#00FFD0] hover:bg-[#00FFD0]/90 shadow-[0_0_15px_#00FFD044]'
            }`}
          >
            <Play className={`w-4 h-4 ${isRunning ? 'animate-spin' : 'fill-current'}`} />
            <span>{isRunning ? 'ÇARPIIM OPERATÖRÜ YÜRÜTÜLÜYOR...' : 'Sanal Matris Çarpımını Yürüt (A @ B)'}</span>
          </button>
        </div>

        {/* Right Live Execution Pipeline Visualization (7 cols) */}
        <div className="lg:col-span-7 border border-[#2A2A2D] bg-[#0F0F12] p-5 rounded space-y-4">
          <h3 className="font-serif italic text-xs text-white/60 uppercase flex justify-between items-center">
            <span>Sanal Sürücü Operasyon Hattı</span>
            <span className="text-[10px] text-[#00FFD0]">DMA BANDWIDTH: 44.2 GB/S</span>
          </h3>

          <div className="space-y-3">
            {/* Step 1 */}
            <div className={`p-3 border rounded transition-all flex items-start gap-3 ${
              currentStep >= 1 ? 'border-[#00FFD0]/60 bg-[#00FFD0]/10 text-white' : 'border-[#2A2A2D] bg-[#141417] opacity-40'
            }`}>
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                currentStep >= 1 ? 'bg-[#00FFD0] text-[#0A0A0B]' : 'bg-[#2A2A2D] text-white/60'
              }`}>
                1
              </div>
              <div className="flex-1 text-xs">
                <div className="font-bold text-[#00FFD0] uppercase">1. Operatör Kancalanması (Operator Interceptor)</div>
                <p className="text-[11px] text-white/70 mt-0.5">
                  <code className="text-[#00FFD0]">sanal_matris_carpimi(A, B)</code> çağrısı yakalandı. Sanal adres haritasından tensör lokasyonları okundu.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className={`p-3 border rounded transition-all flex items-start gap-3 ${
              currentStep >= 2 ? 'border-[#00FFD0]/60 bg-[#00FFD0]/10 text-white' : 'border-[#2A2A2D] bg-[#141417] opacity-40'
            }`}>
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                currentStep >= 2 ? 'bg-[#00FFD0] text-[#0A0A0B]' : 'bg-[#2A2A2D] text-white/60'
              }`}>
                2
              </div>
              <div className="flex-1 text-xs">
                <div className="font-bold text-[#38BDF8] uppercase">2. Arka Plan P2P DMA Sanal Adres Hizalama</div>
                <p className="text-[11px] text-white/70 mt-0.5">
                  Farklı fiziki GPU&apos;lardaki (cuda:0, cuda:1, cuda:2) tensör dilimleri PCIe P2P DMA veri yolu ile şeffafça hizalandı.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className={`p-3 border rounded transition-all flex items-start gap-3 ${
              currentStep >= 3 ? 'border-[#00FFD0]/60 bg-[#00FFD0]/10 text-white' : 'border-[#2A2A2D] bg-[#141417] opacity-40'
            }`}>
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                currentStep >= 3 ? 'bg-[#00FFD0] text-[#0A0A0B]' : 'bg-[#2A2A2D] text-white/60'
              }`}>
                3
              </div>
              <div className="flex-1 text-xs">
                <div className="font-bold text-[#A78BFA] uppercase">3. Fiziki CUDA Kernel Sevkleri (Zero-OOM)</div>
                <p className="text-[11px] text-white/70 mt-0.5">
                  Parçalı cuBLAS / GEMM matris çarpımı 4 fiziki GPU üzerinde aynı anda yürütüldü. VRAM taşma engellendi.
                </p>
              </div>
            </div>

            {/* Step 4 */}
            <div className={`p-3 border rounded transition-all flex items-start gap-3 ${
              currentStep >= 4 ? 'border-[#00FFD0] bg-[#00FFD0]/20 text-white shadow-[0_0_10px_#00FFD033]' : 'border-[#2A2A2D] bg-[#141417] opacity-40'
            }`}>
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                currentStep >= 4 ? 'bg-[#00FFD0] text-[#0A0A0B]' : 'bg-[#2A2A2D] text-white/60'
              }`}>
                4
              </div>
              <div className="flex-1 text-xs">
                <div className="font-bold text-[#00FFD0] uppercase">4. Tek Parça Sanal Tensör Teslimatı</div>
                <p className="text-[11px] text-white/70 mt-0.5">
                  Sonuç matrisi C ({matrixCGb} GB) ana bilgisayara tek bir sanal cihaz tensörü olarak teslim edildi!
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
