import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="h-8 border-t border-[#2A2A2D] bg-[#0C0C0F] px-4 md:px-6 flex items-center justify-between text-[10px] text-white/40 font-mono shrink-0">
      <div className="flex items-center gap-4">
        <span>ARCH: X64_CUDA_VIRTUAL_V1</span>
        <span className="hidden sm:inline text-white/20">|</span>
        <span className="hidden sm:inline">PAGE_SIZE: 512.0 MB</span>
      </div>

      <div className="flex items-center gap-4">
        <span className="text-[#00FFD0]">P2P DMA: ENABLED</span>
        <span className="hidden md:inline">NVLINK: EMULATED</span>
        <span className="text-[#00FFD0] font-bold">THROUGHPUT: 44.2 GB/S</span>
      </div>
    </footer>
  );
};
