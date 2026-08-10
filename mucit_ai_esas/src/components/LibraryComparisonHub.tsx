import React, { useState } from 'react';
import { LIBRARIES_DATA } from '../data/libraries';
import { LibraryComparison } from '../types';
import { BookOpen, Check, X, Code2, Sparkles, ExternalLink, Cpu, ChevronDown, ChevronUp } from 'lucide-react';

export const LibraryComparisonHub: React.FC = () => {
  const [filterLevel, setFilterLevel] = useState<'all' | 'cpp' | 'python'>('all');
  const [selectedLibraryId, setSelectedLibraryId] = useState<string>('kulli_sanal_gpu');
  const [expandedSnippetId, setExpandedSnippetId] = useState<string | null>('kulli_sanal_gpu');

  const filteredLibraries = LIBRARIES_DATA.filter((lib) => {
    if (filterLevel === 'cpp') return lib.level.includes('C++');
    if (filterLevel === 'python') return lib.level.includes('Python');
    return true;
  });

  const activeLib = LIBRARIES_DATA.find((l) => l.id === selectedLibraryId) || LIBRARIES_DATA[0];

  return (
    <div className="flex flex-col gap-6 font-mono text-[#E4E3E0] p-4 md:p-6 bg-[#0A0A0B] flex-1 overflow-y-auto">
      {/* Header Banner */}
      <div className="border border-[#2A2A2D] bg-[#0F0F12] p-5 rounded relative overflow-hidden">
        <div className="absolute -right-10 -bottom-10 w-64 h-64 bg-[#00FFD0]/5 rounded-full blur-3xl pointer-events-none"></div>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] text-[#00FFD0] uppercase font-bold tracking-widest bg-[#00FFD0]/10 border border-[#00FFD0]/30 px-2 py-0.5 rounded">
                ENDÜSTRİYEL KÜTÜPHANE REHBERİ
              </span>
              <span className="text-[10px] text-white/40">C++ CUDA & PYTHON LLM MATRIX</span>
            </div>
            <h2 className="text-xl font-bold tracking-tight text-white font-serif italic">
              Evrensel Sanal GPU Sürücüsü ve Hazır Kütüphane Karşılaştırma Matrisi
            </h2>
            <p className="text-xs text-white/60 mt-1 max-w-3xl leading-relaxed">
              Çoklu fiziki GPU kartlarını tek bir sanal adres havuzunda birleştiren C++ (cuMemMap, NVSHMEM, Managed Memory) ve Python (DeepSpeed ZeRO-3, vLLM, Accelerate) kütüphanelerinin mimari analizi.
            </p>
          </div>

          {/* Level Filters */}
          <div className="flex items-center bg-[#050507] p-1 border border-[#2A2A2D] rounded text-xs shrink-0">
            <button
              onClick={() => setFilterLevel('all')}
              className={`px-3 py-1.5 rounded transition-colors ${
                filterLevel === 'all' ? 'bg-[#00FFD0]/20 text-[#00FFD0] font-bold' : 'text-white/60 hover:text-white'
              }`}
            >
              Tüm Kütüphaneler (7)
            </button>
            <button
              onClick={() => setFilterLevel('cpp')}
              className={`px-3 py-1.5 rounded transition-colors ${
                filterLevel === 'cpp' ? 'bg-[#38BDF8]/20 text-[#38BDF8] font-bold' : 'text-white/60 hover:text-white'
              }`}
            >
              C++ CUDA (3)
            </button>
            <button
              onClick={() => setFilterLevel('python')}
              className={`px-3 py-1.5 rounded transition-colors ${
                filterLevel === 'python' ? 'bg-[#A78BFA]/20 text-[#A78BFA] font-bold' : 'text-white/60 hover:text-white'
              }`}
            >
              Python (4)
            </button>
          </div>
        </div>
      </div>

      {/* Grid Layout: Comparison Cards List & Detailed Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Library Cards (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <h3 className="font-serif italic text-xs text-white/50 uppercase">Mevcut Kütüphaneler Listesi</h3>
          {filteredLibraries.map((lib) => {
            const isSelected = lib.id === selectedLibraryId;
            return (
              <div
                key={lib.id}
                onClick={() => setSelectedLibraryId(lib.id)}
                className={`p-4 border rounded cursor-pointer transition-all ${
                  isSelected
                    ? 'border-[#00FFD0] bg-[#00FFD0]/10 shadow-[0_0_12px_#00FFD022]'
                    : 'border-[#2A2A2D] bg-[#0F0F12] hover:border-[#00FFD0]/40 hover:bg-[#141417]'
                }`}
              >
                <div className="flex justify-between items-start gap-2 mb-1.5">
                  <h4 className="font-bold text-sm text-white flex items-center gap-2">
                    {lib.name}
                    {lib.id === 'kulli_sanal_gpu' && (
                      <span className="text-[9px] bg-[#00FFD0] text-[#0A0A0B] font-extrabold px-1.5 py-0.2 rounded">
                        VIZYON
                      </span>
                    )}
                  </h4>
                  <div className="text-right shrink-0">
                    <span className="text-[10px] text-[#00FFD0] font-bold font-mono">
                      %{lib.similarityScorePct} Uyum
                    </span>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2 text-[10px] text-white/50 mb-2">
                  <span className="px-1.5 py-0.5 bg-white/5 border border-white/10 rounded">
                    {lib.level}
                  </span>
                  <span>Geliştirici: {lib.developer}</span>
                </div>

                <p className="text-[11px] text-white/70 line-clamp-2 leading-snug">
                  {lib.coreMechanism}
                </p>

                <div className="mt-2 pt-2 border-t border-[#2A2A2D]/60 flex justify-between items-center text-[10px]">
                  <span className="text-white/40">OOM Koruması:</span>
                  <span className="text-white/90 font-mono font-semibold">{lib.oomProtection}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right: Detailed Deep Dive Inspector (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          <div className="border border-[#2A2A2D] bg-[#0F0F12] p-5 rounded space-y-5">
            {/* Header section */}
            <div className="flex justify-between items-start pb-4 border-b border-[#2A2A2D]">
              <div>
                <div className="text-[10px] text-[#00FFD0] font-mono font-bold uppercase mb-1">
                  SEÇİLİ KÜTÜPHANE İNCELEMESİ
                </div>
                <h3 className="text-xl font-bold text-white font-serif italic">{activeLib.name}</h3>
                <div className="text-xs text-white/50 mt-0.5">{activeLib.level} | Geliştirici: {activeLib.developer}</div>
              </div>

              <div className="p-3 border border-[#00FFD0]/40 bg-[#00FFD0]/5 text-center rounded">
                <div className="text-[10px] text-white/40 uppercase">VİZYON BENZERLİĞİ</div>
                <div className="text-2xl font-bold text-[#00FFD0]">%{activeLib.similarityScorePct}</div>
              </div>
            </div>

            {/* Core Specs Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 border border-[#2A2A2D] bg-[#141417] rounded">
                <div className="text-[10px] text-white/40 mb-1">TEMEL MİMARİ MEKANİZMA</div>
                <div className="text-white leading-relaxed font-mono">{activeLib.coreMechanism}</div>
              </div>

              <div className="p-3 border border-[#2A2A2D] bg-[#141417] rounded">
                <div className="text-[10px] text-white/40 mb-1">PAGE FAULT ELE ALMA</div>
                <div className="text-[#00FFD0] font-bold font-mono">{activeLib.pageFaultHandling}</div>
                <div className="text-[10px] text-white/40 mt-2">OOM Koruması: {activeLib.oomProtection}</div>
              </div>
            </div>

            {/* Matrix Attributes Badges */}
            <div className="grid grid-cols-3 gap-2 text-[11px]">
              <div className={`p-2 border rounded flex items-center gap-2 ${
                activeLib.multiGpuUnifiedAddress ? 'border-[#00FFD0]/40 bg-[#00FFD0]/10 text-[#00FFD0]' : 'border-white/10 text-white/30'
              }`}>
                {activeLib.multiGpuUnifiedAddress ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
                <span>Tek Adres Uzayı (Unified Address)</span>
              </div>

              <div className={`p-2 border rounded flex items-center gap-2 ${
                activeLib.zeroCopyDma ? 'border-[#00FFD0]/40 bg-[#00FFD0]/10 text-[#00FFD0]' : 'border-white/10 text-white/30'
              }`}>
                {activeLib.zeroCopyDma ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
                <span>Zero-Copy P2P DMA Transfer</span>
              </div>

              <div className={`p-2 border rounded flex items-center gap-2 ${
                activeLib.frameworkAgnostic ? 'border-[#00FFD0]/40 bg-[#00FFD0]/10 text-[#00FFD0]' : 'border-white/10 text-white/30'
              }`}>
                {activeLib.frameworkAgnostic ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
                <span>Evrensel / Proje Bağımsız</span>
              </div>
            </div>

            {/* Pros & Cons */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="p-3 border border-[#00FFD0]/30 bg-[#00FFD0]/5 rounded space-y-1.5">
                <div className="text-[10px] text-[#00FFD0] font-bold uppercase">AVANTAJLARI (PROS)</div>
                <ul className="space-y-1 text-white/80 text-[11px]">
                  {activeLib.pros.map((p, idx) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-[#00FFD0] font-bold">•</span>
                      <span>{p}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-3 border border-[#F27D26]/30 bg-[#F27D26]/5 rounded space-y-1.5">
                <div className="text-[10px] text-[#F27D26] font-bold uppercase">DEZAVANTAJLARI / SINIRLAMALARI</div>
                <ul className="space-y-1 text-white/80 text-[11px]">
                  {activeLib.cons.map((c, idx) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-[#F27D26] font-bold">•</span>
                      <span>{c}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Code Snippet */}
            {(activeLib.pythonSnippet || activeLib.cppSnippet) && (
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-serif italic text-white/60">ENTETRASYON KOD ÖRNEĞİ</span>
                  <span className="text-[10px] text-white/40">{activeLib.level}</span>
                </div>
                <div className="p-3 border border-[#2A2A2D] bg-[#050507] rounded font-mono text-xs overflow-x-auto text-[#00FFD0] leading-relaxed">
                  <pre>{activeLib.pythonSnippet || activeLib.cppSnippet}</pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
