import React, { useState } from 'react';
import { VirtualPage } from '../types';
import { Layers, HardDrive, Info, ShieldAlert, Cpu } from 'lucide-react';

interface VirtualPageGridProps {
  pages: VirtualPage[];
  totalVramGb: number;
  allocatedMb: number;
  swappedMb: number;
  onSelectPage?: (page: VirtualPage) => void;
  onForceSwapPage?: (pageId: number) => void;
}

export const VirtualPageGrid: React.FC<VirtualPageGridProps> = ({
  pages,
  totalVramGb,
  allocatedMb,
  swappedMb,
  onSelectPage,
  onForceSwapPage
}) => {
  const [hoveredPage, setHoveredPage] = useState<VirtualPage | null>(null);

  const getGpuColorClass = (gpuId: number | null, isSwapped: boolean, isAllocated: boolean) => {
    if (!isAllocated) return 'bg-[#1A1A1D] border-white/5 hover:border-white/30';
    if (isSwapped) return 'bg-[#F27D26]/30 border-[#F27D26] text-[#F27D26] animate-pulse shadow-[0_0_8px_#F27D2666]';
    
    switch (gpuId) {
      case 0:
        return 'bg-[#00FFD0]/80 border-[#00FFD0] text-[#0A0A0B] shadow-[0_0_6px_#00FFD044]';
      case 1:
        return 'bg-[#38BDF8]/80 border-[#38BDF8] text-[#0A0A0B] shadow-[0_0_6px_#38BDF844]';
      case 2:
        return 'bg-[#A78BFA]/80 border-[#A78BFA] text-[#0A0A0B] shadow-[0_0_6px_#A78BFA44]';
      case 3:
        return 'bg-[#F472B6]/80 border-[#F472B6] text-[#0A0A0B] shadow-[0_0_6px_#F472B644]';
      default:
        return 'bg-[#00FFD0]/50 border-[#00FFD0]';
    }
  };

  const allocatedPagesCount = pages.filter((p) => p.isAllocated).length;
  const swappedPagesCount = pages.filter((p) => p.isSwappedToCpu).length;

  return (
    <section className="flex flex-col gap-3 font-mono text-[#E4E3E0]">
      {/* Title & Legend Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-2">
        <div>
          <h2 className="font-serif italic text-sm text-white/90 flex items-center gap-2">
            <span>SANAL_ADRES_HARITASI (88GB VRAM_SPACE)</span>
            <span className="text-[10px] text-white/40 font-mono not-italic uppercase">
              [1 Sayfa Block = 512MB]
            </span>
          </h2>
          <p className="text-[10px] text-white/40">
            Fiziki 4x GPU VRAM bellekleri ana programa kesintisiz 0 - 88 GB tekil adres olarak haritalanmıştır.
          </p>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-3 text-[10px] bg-[#0F0F12] px-3 py-1.5 border border-[#2A2A2D] rounded">
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 bg-[#00FFD0] rounded-sm"></div>
            <span className="text-white/70">GPU_0 (0-22G)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 bg-[#38BDF8] rounded-sm"></div>
            <span className="text-white/70">GPU_1 (22-44G)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 bg-[#A78BFA] rounded-sm"></div>
            <span className="text-white/70">GPU_2 (44-66G)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 bg-[#F472B6] rounded-sm"></div>
            <span className="text-white/70">GPU_3 (66-88G)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 bg-[#F27D26] rounded-sm animate-pulse"></div>
            <span className="text-[#F27D26] font-semibold">CPU Pinned Swap</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 bg-[#1A1A1D] border border-white/20 rounded-sm"></div>
            <span className="text-white/40">Boş</span>
          </div>
        </div>
      </div>

      {/* Grid Container (176 Pages, 22 columns on desktop) */}
      <div className="relative border border-[#2A2A2D] bg-[#0F0F12] p-3 rounded">
        <div className="grid grid-cols-11 sm:grid-cols-22 gap-1 max-h-[220px] overflow-y-auto p-1">
          {pages.map((page) => (
            <button
              key={page.id}
              onMouseEnter={() => setHoveredPage(page)}
              onClick={() => onSelectPage && onSelectPage(page)}
              className={`w-full aspect-square border rounded-xs transition-all duration-150 cursor-pointer relative ${getGpuColorClass(
                page.physicalGpuId,
                page.isSwappedToCpu,
                page.isAllocated
              )}`}
              title={`Sayfa #${page.id}: ${(page.virtualAddressStartMb / 1024).toFixed(2)} GB - ${(page.virtualAddressEndMb / 1024).toFixed(2)} GB`}
            >
              {page.isSwappedToCpu && (
                <div className="absolute inset-0 bg-[radial-gradient(#F27D26_1px,transparent_1px)] [background-size:4px_4px]"></div>
              )}
            </button>
          ))}
        </div>

        {/* Dynamic Tooltip / Status Footer */}
        <div className="mt-2.5 pt-2 border-t border-[#2A2A2D] flex flex-col sm:flex-row justify-between items-start sm:items-center text-[11px] gap-2 min-h-[28px]">
          {hoveredPage ? (
            <div className="flex flex-wrap items-center gap-3 text-white">
              <span className="font-semibold text-[#00FFD0]">
                Sanal Sayfa #{hoveredPage.id.toString().padStart(3, '0')}
              </span>
              <span className="text-white/60">
                Adres: {(hoveredPage.virtualAddressStartMb / 1024).toFixed(2)} GB - {(hoveredPage.virtualAddressEndMb / 1024).toFixed(2)} GB
              </span>
              <span className="text-white/80">
                Konum:{' '}
                {hoveredPage.isSwappedToCpu ? (
                  <span className="text-[#F27D26] font-bold">Host CPU Pinned RAM (Swapped)</span>
                ) : hoveredPage.physicalGpuId !== null ? (
                  <span className="text-[#00FFD0]">cuda:{hoveredPage.physicalGpuId} (Fiziki GPU #{hoveredPage.physicalGpuId})</span>
                ) : (
                  <span className="text-white/30">Tahsis Edilmedi</span>
                )}
              </span>
              {hoveredPage.ownerProcessName && (
                <span className="px-1.5 py-0.5 bg-white/10 text-white text-[10px] rounded border border-white/20">
                  {hoveredPage.ownerProcessName}
                </span>
              )}
              {hoveredPage.isAllocated && onForceSwapPage && (
                <button
                  onClick={() => onForceSwapPage(hoveredPage.id)}
                  className="px-2 py-0.5 text-[9px] bg-[#F27D26]/20 text-[#F27D26] hover:bg-[#F27D26]/30 border border-[#F27D26]/40 rounded transition-colors"
                >
                  {hoveredPage.isSwappedToCpu ? 'VRAM\'e Geri Çek (Page In)' : 'CPU RAM\'e Kaydır (Swap Out)'}
                </button>
              )}
            </div>
          ) : (
            <div className="text-white/40 flex items-center gap-2">
              <Info className="w-3.5 h-3.5 text-[#00FFD0]" />
              <span>Sanal sayfa detaylarını incelemek ve swap durumunu değiştirmek için bir bloğun üzerine gelin.</span>
            </div>
          )}

          <div className="text-white/50 text-[10px] shrink-0">
            Dolu Sayfa: <span className="text-[#00FFD0] font-bold">{allocatedPagesCount}</span> / 176 | Swap: <span className="text-[#F27D26] font-bold">{swappedPagesCount}</span> Sayfa
          </div>
        </div>
      </div>
    </section>
  );
};
