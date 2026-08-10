import React, { useState } from 'react';
import { TensorAllocation, DomainType } from '../types';
import { Trash2, RefreshCw, Search, Shield, Cpu, Dna, Gamepad2, Activity, HardDrive } from 'lucide-react';

interface AllocationTableProps {
  allocations: TensorAllocation[];
  onTerminate: (id: string) => void;
  onSwapAllocation: (id: string) => void;
}

export const AllocationTable: React.FC<AllocationTableProps> = ({
  allocations,
  onTerminate,
  onSwapAllocation
}) => {
  const [search, setSearch] = useState('');
  const [selectedDomain, setSelectedDomain] = useState<DomainType | 'all'>('all');

  const getDomainIcon = (domain: DomainType) => {
    switch (domain) {
      case 'llm':
        return <Cpu className="w-3.5 h-3.5 text-[#38BDF8]" />;
      case 'game_engine':
        return <Gamepad2 className="w-3.5 h-3.5 text-[#F472B6]" />;
      case 'dna_genomics':
        return <Dna className="w-3.5 h-3.5 text-[#00FFD0]" />;
      case 'cfd_physics':
        return <Activity className="w-3.5 h-3.5 text-[#A78BFA]" />;
    }
  };

  const filteredAllocations = allocations.filter((alloc) => {
    const matchesSearch = alloc.name.toLowerCase().includes(search.toLowerCase()) ||
                          alloc.id.toLowerCase().includes(search.toLowerCase());
    const matchesDomain = selectedDomain === 'all' || alloc.domain === selectedDomain;
    return matchesSearch && matchesDomain;
  });

  return (
    <section className="flex flex-col gap-2 font-mono text-[#E4E3E0] flex-1 min-h-0">
      {/* Table Header & Search Filter */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
        <h2 className="font-serif italic text-sm text-white/90">
          ACTIVE_PROCESS_SEGMENTS ({allocations.length} Tensör Tahsisi)
        </h2>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          {/* Domain Filter Buttons */}
          <div className="flex items-center bg-[#0F0F12] border border-[#2A2A2D] p-0.5 rounded text-[10px]">
            <button
              onClick={() => setSelectedDomain('all')}
              className={`px-2 py-1 rounded transition-colors ${
                selectedDomain === 'all' ? 'bg-[#00FFD0]/20 text-[#00FFD0] font-bold' : 'text-white/50 hover:text-white'
              }`}
            >
              Tümü
            </button>
            <button
              onClick={() => setSelectedDomain('llm')}
              className={`px-2 py-1 rounded transition-colors ${
                selectedDomain === 'llm' ? 'bg-[#38BDF8]/20 text-[#38BDF8] font-bold' : 'text-white/50 hover:text-white'
              }`}
            >
              LLM
            </button>
            <button
              onClick={() => setSelectedDomain('game_engine')}
              className={`px-2 py-1 rounded transition-colors ${
                selectedDomain === 'game_engine' ? 'bg-[#F472B6]/20 text-[#F472B6] font-bold' : 'text-white/50 hover:text-white'
              }`}
            >
              Oyun
            </button>
            <button
              onClick={() => setSelectedDomain('dna_genomics')}
              className={`px-2 py-1 rounded transition-colors ${
                selectedDomain === 'dna_genomics' ? 'bg-[#00FFD0]/20 text-[#00FFD0] font-bold' : 'text-white/50 hover:text-white'
              }`}
            >
              DNA
            </button>
            <button
              onClick={() => setSelectedDomain('cfd_physics')}
              className={`px-2 py-1 rounded transition-colors ${
                selectedDomain === 'cfd_physics' ? 'bg-[#A78BFA]/20 text-[#A78BFA] font-bold' : 'text-white/50 hover:text-white'
              }`}
            >
              CFD
            </button>
          </div>

          {/* Search Bar */}
          <div className="relative flex-1 sm:w-48">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-white/40" />
            <input
              type="text"
              placeholder="Tensör ara..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[#0F0F12] border border-[#2A2A2D] rounded pl-8 pr-2 py-1 text-xs text-white placeholder-white/30 focus:outline-none focus:border-[#00FFD0]/50"
            />
          </div>
        </div>
      </div>

      {/* Table Container */}
      <div className="flex-1 border border-[#2A2A2D] bg-[#0F0F12] rounded overflow-hidden overflow-y-auto max-h-[300px]">
        {filteredAllocations.length === 0 ? (
          <div className="p-8 text-center text-white/40 text-xs">
            Aktif tensör tahsisi bulunamadı. Sol panelden hızlı iş yükü testlerini çalıştırabilirsiniz.
          </div>
        ) : (
          <table className="w-full text-left text-[11px] border-collapse">
            <thead className="bg-[#141417] text-[10px] text-white/40 uppercase sticky top-0 border-b border-[#2A2A2D] backdrop-blur-md">
              <tr>
                <th className="p-2.5 font-medium">Process / Tensor Name</th>
                <th className="p-2.5 font-medium">Domain</th>
                <th className="p-2.5 font-medium">Sanal Sayfa Aralığı</th>
                <th className="p-2.5 font-medium">Haritalanan GPU'lar</th>
                <th className="p-2.5 font-medium">Boyut (MB / GB)</th>
                <th className="p-2.5 font-medium">DType & Shape</th>
                <th className="p-2.5 font-medium">Durum</th>
                <th className="p-2.5 font-medium text-right">Eylem</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#2A2A2D]">
              {filteredAllocations.map((alloc) => {
                const startPage = alloc.allocatedPages[0];
                const endPage = alloc.allocatedPages[alloc.allocatedPages.length - 1];
                const startAddressGb = ((startPage * 512) / 1024).toFixed(2);
                const endAddressGb = (((endPage + 1) * 512) / 1024).toFixed(2);

                // Determine mapped physical GPUs
                const mappedGpus = Array.from(
                  new Set(alloc.allocatedPages.map((pId) => Math.floor((pId * 512) / 22528)))
                );

                return (
                  <tr key={alloc.id} className="hover:bg-[#00FFD0]/5 transition-colors group">
                    <td className="p-2.5 font-bold text-white flex items-center gap-2">
                      <div
                        className="w-2 h-2 rounded-full shrink-0"
                        style={{ backgroundColor: alloc.colorHex || '#00FFD0' }}
                      ></div>
                      <span className="truncate max-w-[180px]" title={alloc.name}>
                        {alloc.name}
                      </span>
                    </td>

                    <td className="p-2.5">
                      <div className="flex items-center gap-1.5 capitalize text-white/70">
                        {getDomainIcon(alloc.domain)}
                        <span>{alloc.domain.replace('_', ' ')}</span>
                      </div>
                    </td>

                    <td className="p-2.5 text-white/70 font-mono text-[10px]">
                      {startAddressGb}G - {endAddressGb}G ({alloc.allocatedPages.length} Sayfa)
                    </td>

                    <td className="p-2.5">
                      <div className="flex gap-1">
                        {mappedGpus.map((gpuId) => (
                          <span
                            key={gpuId}
                            className="px-1.5 py-0.5 text-[9px] bg-white/5 border border-white/20 text-[#00FFD0] rounded font-mono"
                          >
                            cuda:{gpuId}
                          </span>
                        ))}
                      </div>
                    </td>

                    <td className="p-2.5 font-mono text-white">
                      {alloc.sizeMb.toLocaleString()} MB ({(alloc.sizeMb / 1024).toFixed(2)} GB)
                    </td>

                    <td className="p-2.5 text-white/50 font-mono text-[10px]">
                      {alloc.dtype} [{alloc.shape.join(' × ')}]
                    </td>

                    <td className="p-2.5">
                      <span className="text-[#00FFD0] bg-[#00FFD0]/10 px-1.5 py-0.5 rounded text-[9px] border border-[#00FFD0]/30 font-semibold">
                        SANAL HARİTALANDI
                      </span>
                    </td>

                    <td className="p-2.5 text-right">
                      <div className="flex justify-end items-center gap-1 opacity-80 group-hover:opacity-100">
                        <button
                          onClick={() => onSwapAllocation(alloc.id)}
                          className="p-1 hover:bg-[#F27D26]/20 text-[#F27D26] rounded border border-[#F27D26]/30 transition-colors"
                          title="Host CPU RAM'e Swap Yap"
                        >
                          <RefreshCw className="w-3 h-3" />
                        </button>
                        <button
                          onClick={() => onTerminate(alloc.id)}
                          className="p-1 hover:bg-red-500/20 text-red-400 rounded border border-red-500/30 transition-colors"
                          title="Tensörü Sil ve VRAM'i Boşalt"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
};
