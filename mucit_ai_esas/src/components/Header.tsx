import React from 'react';
import { Cpu, Terminal, Layers, BookOpen, ShieldCheck, Zap, GitFork } from 'lucide-react';
import { TabType } from '../types';

interface HeaderProps {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  allocatedMb: number;
  totalVirtualVramMb: number;
  swappedMb: number;
  uptimeSeconds: number;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  allocatedMb,
  totalVirtualVramMb,
  swappedMb,
  uptimeSeconds
}) => {
  const formatUptime = (sec: number) => {
    const hrs = Math.floor(sec / 3600);
    const mins = Math.floor((sec % 3600) / 60);
    const secs = sec % 60;
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const usagePct = ((allocatedMb / totalVirtualVramMb) * 100).toFixed(1);

  return (
    <header className="h-16 border-b border-[#2A2A2D] bg-[#0F0F12] px-4 md:px-6 flex items-center justify-between shrink-0 font-mono text-[#E4E3E0]">
      {/* Brand Title */}
      <div className="flex items-center gap-3">
        <div className="relative flex items-center justify-center">
          <div className="w-3 h-3 bg-[#00FFD0] rounded-full shadow-[0_0_12px_#00FFD0]"></div>
          <div className="absolute w-5 h-5 border border-[#00FFD0]/40 rounded-full animate-ping"></div>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-bold tracking-tight uppercase flex items-center gap-2">
              KÜLLÎ SANAL GPU <span className="text-[#00FFD0] text-xs font-normal opacity-90 px-1.5 py-0.5 border border-[#00FFD0]/30 rounded bg-[#00FFD0]/10">v1.0.4-DRIVER</span>
            </h1>
          </div>
          <p className="text-[10px] text-white/40 hidden sm:block tracking-wide">
            UNIVERSAL VIRTUAL GPU DRIVER & ZERO-OOM MEMORY MANAGER
          </p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav className="hidden lg:flex items-center gap-1 bg-[#050507] p-1 border border-[#2A2A2D] rounded">
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`flex items-center gap-2 px-3 py-1.5 text-xs rounded transition-all ${
            activeTab === 'dashboard'
              ? 'bg-[#00FFD0]/15 text-[#00FFD0] border border-[#00FFD0]/40 shadow-[0_0_8px_#00FFD022]'
              : 'text-white/60 hover:text-white hover:bg-white/5'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Sanal Harita & VMM</span>
        </button>

        <button
          onClick={() => setActiveTab('architecture')}
          className={`flex items-center gap-2 px-3 py-1.5 text-xs rounded transition-all ${
            activeTab === 'architecture'
              ? 'bg-[#00FFD0]/15 text-[#00FFD0] border border-[#00FFD0]/40 shadow-[0_0_8px_#00FFD022]'
              : 'text-white/60 hover:text-white hover:bg-white/5'
          }`}
        >
          <GitFork className="w-3.5 h-3.5" />
          <span>Mimarî Tertibat Plânı</span>
        </button>

        <button
          onClick={() => setActiveTab('matmul')}
          className={`flex items-center gap-2 px-3 py-1.5 text-xs rounded transition-all ${
            activeTab === 'matmul'
              ? 'bg-[#00FFD0]/15 text-[#00FFD0] border border-[#00FFD0]/40 shadow-[0_0_8px_#00FFD022]'
              : 'text-white/60 hover:text-white hover:bg-white/5'
          }`}
        >
          <Zap className="w-3.5 h-3.5" />
          <span>MatMul Interceptor</span>
        </button>

        <button
          onClick={() => setActiveTab('comparison')}
          className={`flex items-center gap-2 px-3 py-1.5 text-xs rounded transition-all ${
            activeTab === 'comparison'
              ? 'bg-[#00FFD0]/15 text-[#00FFD0] border border-[#00FFD0]/40 shadow-[0_0_8px_#00FFD022]'
              : 'text-white/60 hover:text-white hover:bg-white/5'
          }`}
        >
          <BookOpen className="w-3.5 h-3.5" />
          <span>Kütüphane Karşılaştırmaları</span>
        </button>

        <button
          onClick={() => setActiveTab('code')}
          className={`flex items-center gap-2 px-3 py-1.5 text-xs rounded transition-all ${
            activeTab === 'code'
              ? 'bg-[#00FFD0]/15 text-[#00FFD0] border border-[#00FFD0]/40 shadow-[0_0_8px_#00FFD022]'
              : 'text-white/60 hover:text-white hover:bg-white/5'
          }`}
        >
          <Terminal className="w-3.5 h-3.5" />
          <span>Sürücü Kodu (Python & C++)</span>
        </button>
      </nav>

      {/* System Quick Metrics */}
      <div className="flex items-center gap-4 text-[11px] uppercase tracking-wider">
        <div className="hidden sm:flex flex-col text-right">
          <div className="text-white/40 text-[9px]">Sanal VRAM Doluluk</div>
          <div className="font-semibold text-[#00FFD0]">
            {(allocatedMb / 1024).toFixed(1)} / {(totalVirtualVramMb / 1024).toFixed(0)} GB ({usagePct}%)
          </div>
        </div>

        {swappedMb > 0 && (
          <div className="hidden xl:flex items-center gap-1.5 text-[#F27D26] bg-[#F27D26]/10 px-2 py-1 border border-[#F27D26]/30 rounded animate-pulse">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span className="text-[10px]">SWAP: {(swappedMb / 1024).toFixed(1)} GB</span>
          </div>
        )}

        <div className="hidden md:flex flex-col text-right opacity-60">
          <div className="text-[9px]">Sürücü Uptime</div>
          <div className="text-white font-mono">{formatUptime(uptimeSeconds)}</div>
        </div>
      </div>
    </header>
  );
};
