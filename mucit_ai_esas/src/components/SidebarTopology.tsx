import React from 'react';
import { PhysicalGpu, DomainType } from '../types';
import { WORKLOAD_PRESETS } from '../data/presets';
import { ShieldAlert, Play, RotateCcw, Cpu, HardDrive, RefreshCw, Layers } from 'lucide-react';

interface SidebarTopologyProps {
  physicalGpus: PhysicalGpu[];
  totalVirtualVramMb: number;
  allocatedMb: number;
  swappedMb: number;
  onLoadPreset: (domain: DomainType) => void;
  onReset: () => void;
  onTriggerLruSwap: () => void;
  onSimulateMatMul: () => void;
}

export const SidebarTopology: React.FC<SidebarTopologyProps> = ({
  physicalGpus,
  totalVirtualVramMb,
  allocatedMb,
  swappedMb,
  onLoadPreset,
  onReset,
  onTriggerLruSwap,
  onSimulateMatMul
}) => {
  const freeVramMb = totalVirtualVramMb - allocatedMb;

  return (
    <aside className="w-full lg:w-72 border-r border-[#2A2A2D] bg-[#0C0C0F] p-4 flex flex-col gap-5 shrink-0 font-mono text-[#E4E3E0] overflow-y-auto">
      {/* System Resources Card */}
      <div>
        <h2 className="font-serif italic text-xs text-white/50 mb-2 flex items-center justify-between">
          <span>SYSTEM_RESOURCES</span>
          <span className="text-[10px] text-[#00FFD0]">VMM_ACTIVE</span>
        </h2>
        <div className="grid grid-cols-2 gap-2">
          <div className="p-3 border border-[#2A2A2D] bg-[#141417] rounded">
            <div className="text-[10px] text-white/40 mb-1 uppercase">TOTAL_VIRTUAL_VRAM</div>
            <div className="text-xl font-light text-[#00FFD0]">
              {(totalVirtualVramMb / 1024).toFixed(1)} <span className="text-xs text-white/60">GB</span>
            </div>
            <div className="text-[9px] text-white/40 mt-1">176 Sanal Sayfa</div>
          </div>

          <div className="p-3 border border-[#2A2A2D] bg-[#141417] rounded">
            <div className="text-[10px] text-white/40 mb-1 uppercase">PHYSICAL_DEVICES</div>
            <div className="text-xl font-light text-white">
              {physicalGpus.length.toString().padStart(2, '0')} <span className="text-xs text-white/60">GPU</span>
            </div>
            <div className="text-[9px] text-white/40 mt-1">4x 22 GB VRAM</div>
          </div>
        </div>
      </div>

      {/* Device Topology */}
      <div>
        <h2 className="font-serif italic text-xs text-white/50 mb-2.5 flex items-center justify-between">
          <span>PHYSICAL_TOPOLOGY</span>
          <span className="text-[10px] text-white/40">NVLINK / P2P DMA</span>
        </h2>
        <div className="space-y-2">
          {physicalGpus.map((gpu) => {
            const gpuUsedPct = Math.min(100, (gpu.usedVramMb / gpu.totalVramMb) * 100);
            return (
              <div
                key={gpu.id}
                className="p-2.5 border border-[#2A2A2D] bg-[#0F0F12] rounded hover:border-[#00FFD0]/40 transition-colors"
              >
                <div className="flex justify-between items-center text-[11px] mb-1">
                  <span className="font-semibold text-white/90">
                    GPU_{gpu.id}: {gpu.name}
                  </span>
                  <span className="text-[#00FFD0] font-mono text-[10px]">
                    {(gpu.usedVramMb / 1024).toFixed(1)} / {(gpu.totalVramMb / 1024).toFixed(0)} GB
                  </span>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-[#1A1A1D] h-1.5 rounded-full overflow-hidden mb-1.5">
                  <div
                    className="bg-[#00FFD0] h-full transition-all duration-300 shadow-[0_0_8px_#00FFD0]"
                    style={{ width: `${gpuUsedPct}%` }}
                  ></div>
                </div>

                <div className="flex justify-between items-center text-[9px] text-white/40">
                  <span>Sıcaklık: {gpu.temperatureC}°C</span>
                  <span>Yük: {gpu.utilizationPct}%</span>
                  <span>P2P: {gpu.p2pBandwidthGBs} GB/s</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Zero-OOM Status */}
      <div className={`p-3 border rounded transition-colors ${
        swappedMb > 0 
          ? 'border-[#F27D26]/60 bg-[#F27D26]/10 text-[#F27D26]' 
          : 'border-[#00FFD0]/30 bg-[#00FFD0]/5 text-[#00FFD0]'
      }`}>
        <div className="flex items-center gap-2 mb-1">
          <ShieldAlert className="w-4 h-4 shrink-0" />
          <span className="text-[11px] font-bold tracking-wide uppercase">
            ZERO_OOM_PROTECTION: ACTIVE
          </span>
        </div>
        <p className="text-[10px] leading-relaxed text-white/70">
          Sanal sayfalama sistemi VRAM sınırı aşıldığında LRU (En Az Son Kullanılan) sayfaları şeffafça CPU Pinned RAM&apos;ine kaydırır.
        </p>
        <div className="mt-2 text-[10px] font-semibold flex justify-between items-center">
          <span>Host CPU Pinned Swap:</span>
          <span className="font-mono text-white">{(swappedMb / 1024).toFixed(2)} GB</span>
        </div>
      </div>

      {/* Quick Workload Launchers */}
      <div>
        <h2 className="font-serif italic text-xs text-white/50 mb-2">QUICK_WORKLOAD_PRESETS</h2>
        <div className="grid grid-cols-2 gap-1.5">
          {WORKLOAD_PRESETS.map((preset) => (
            <button
              key={preset.id}
              onClick={() => onLoadPreset(preset.id)}
              className="p-2 border border-[#2A2A2D] bg-[#141417] hover:border-[#00FFD0]/50 hover:bg-[#00FFD0]/5 rounded text-left transition-all group"
            >
              <div className="text-[10px] font-bold text-white group-hover:text-[#00FFD0] transition-colors truncate">
                {preset.title}
              </div>
              <div className="text-[9px] text-white/40 truncate mt-0.5">
                {preset.sampleTensors.length} Tensör Tahsisi
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Action Controls */}
      <div className="mt-auto pt-2 space-y-2 border-t border-[#2A2A2D]">
        <button
          onClick={onSimulateMatMul}
          className="w-full py-2 px-3 bg-[#00FFD0]/10 border border-[#00FFD0]/40 text-[#00FFD0] hover:bg-[#00FFD0]/20 text-xs font-semibold rounded flex items-center justify-center gap-2 transition-all shadow-[0_0_10px_#00FFD015]"
        >
          <Play className="w-3.5 h-3.5 fill-[#00FFD0]" />
          <span>MatMul Çarpımı Çalıştır</span>
        </button>

        <div className="grid grid-cols-2 gap-1.5">
          <button
            onClick={onTriggerLruSwap}
            className="py-1.5 px-2 bg-[#F27D26]/10 border border-[#F27D26]/30 text-[#F27D26] hover:bg-[#F27D26]/20 text-[10px] rounded flex items-center justify-center gap-1 transition-all"
          >
            <RefreshCw className="w-3 h-3" />
            <span>LRU Swap Tetikle</span>
          </button>

          <button
            onClick={onReset}
            className="py-1.5 px-2 bg-white/5 border border-[#2A2A2D] text-white/70 hover:text-white hover:bg-white/10 text-[10px] rounded flex items-center justify-center gap-1 transition-all"
          >
            <RotateCcw className="w-3 h-3" />
            <span>VRAM Sıfırla</span>
          </button>
        </div>
      </div>
    </aside>
  );
};
