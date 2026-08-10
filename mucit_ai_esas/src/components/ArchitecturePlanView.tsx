import React, { useState } from 'react';
import { ARCHITECTURE_MODULES } from '../data/architectureModules';
import { ArchitectureModule } from '../types';
import { 
  Layers, 
  GitMerge, 
  Copy, 
  Check, 
  Cpu, 
  ArrowRight, 
  Zap, 
  ShieldCheck, 
  Network, 
  Box, 
  FileCode,
  Terminal,
  Search,
  ExternalLink
} from 'lucide-react';

export const ArchitecturePlanView: React.FC = () => {
  const [selectedModuleId, setSelectedModuleId] = useState<string | null>('MOD1');
  const [copiedMermaid, setCopiedMermaid] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const mermaidCode = `graph TD
    %% Stil Tanımlamaları
    classDef fileStyle fill:#1e1b4b,stroke:#6366f1,stroke-width:2px,color:#fff;
    classDef classStyle fill:#0f2942,stroke:#0284c7,stroke-width:1.5px,color:#fff;
    classDef funcStyle fill:#1e293b,stroke:#38bdf8,stroke-width:1px,color:#e2e8f0;

    subgraph MOD1["1. GİRİŞ NOKTASI: kulli_gpu/__init__.py"]
        direction TB
        F1_1["baslat(config: Dict = None) -> SanalGPUSurucu<br/>• Girdi: config [Dict]<br/>• Çıktı: SanalGPUSurucu [Nesne]<br/>• Husus: Tek satırlık enjeksiyon"]:::funcStyle
    end

    subgraph MOD2["2. KANCA VE MASKELEME: kulli_gpu/interception/hook_manager.py"]
        direction TB
        C2["Sınıf: CUDAHookManager"]:::classStyle
        F2_1["install_hooks() -> bool<br/>• Girdi: Yok | Çıktı: Basari [bool]<br/>• Husus: libcuda.so/libcudart.so dynamic linking devredışı"]:::funcStyle
        F2_2["get_virtual_device_properties() -> Dict<br/>• Girdi: Yok | Çıktı: CihazOzellikleri [Dict]<br/>• Husus: 1 adet birleşik 88 GB VRAM ve 4x SM raporlar"]:::funcStyle
        C2 --- F2_1
        C2 --- F2_2
    end

    subgraph MOD3["3. TAHMİN MOTORU: kulli_gpu/scheduler/predictive_engine.py"]
        direction TB
        C3["Sınıf: ErkenDevletEngine"]:::classStyle
        F3_1["on_hesapla(operasyon_grafik) -> List[Step]<br/>• Girdi: Graph | Çıktı: Step Listesi<br/>• Husus: 5-10 adım önceden matris tahmini"]:::funcStyle
        F3_2["tertip_et(step) -> PageMap<br/>• Girdi: Step | Çıktı: PageMap<br/>• Husus: Hangi tensör hangi fiziksel GPU sayfasında"]:::funcStyle
        F3_3["sevk_et(step, bus) -> None<br/>• Girdi: step, bus | Çıktı: Void<br/>• Husus: NVSHMEM asenkron sayfa ön yükleme"]:::funcStyle
        C3 --- F3_1
        C3 --- F3_2
        C3 --- F3_3
    end

    subgraph MOD4["4. SANAL BELLEK YÖNETİCİSİ: kulli_gpu/memory/vmm_allocator.py"]
        direction TB
        C4["Sınıf: SanalBellekYoneticisi"]:::classStyle
        F4_1["cuMemAddressReserve(size: 88GB) -> VirtAddr<br/>• Girdi: 88GB | Çıktı: uint64<br/>• Husus: Bitişik 88 GB sanal adres uzayı ayırır"]:::funcStyle
        F4_2["cuMemMap(virt_addr, phys_handle) -> status<br/>• Girdi: virt_addr, phys_handle | Çıktı: int<br/>• Husus: Fiziksel GPU parçalarını dinamik eşler"]:::funcStyle
        F4_3["allocate_pages(num_pages) -> List[Page]<br/>• Girdi: int | Çıktı: Page Listesi<br/>• Husus: Sayfa seviyesinde tahsis"]:::funcStyle
        C4 --- F4_1
        C4 --- F4_2
        C4 --- F4_3
    end

    subgraph MOD5["5. SANAL İŞLEMCİ HAVUZU: kulli_gpu/compute/vcompute_pool.py"]
        direction TB
        C5["Sınıf: SanalIslemciHavuzu"]:::classStyle
        F5_1["aggregate_sm_cores() -> int<br/>• Girdi: Yok | Çıktı: Toplam SM<br/>• Husus: 4 GPU SM birimlerini birleştirir"]:::funcStyle
        F5_2["dispatch_kernel(kernel_code, stream) -> Handle<br/>• Girdi: Binary, Stream | Çıktı: ExecutionHandle<br/>• Husus: Mikro parçalara bölüp dağıtır"]:::funcStyle
        C5 --- F5_1
        C5 --- F5_2
    end

    subgraph MOD6["6. NVSHMEM VERİ YOLU: kulli_gpu/comm/nvshmem_bus.py"]
        direction TB
        C6["Sınıf: NVSHMEMVeriyolu"]:::classStyle
        F6_1["init_pgas_space() -> bool<br/>• Girdi: Yok | Çıktı: bool<br/>• Husus: PGAS ile 4 GPU VRAM bağlar"]:::funcStyle
        F6_2["p2p_transfer_async(src_page, dst_page) -> Event<br/>• Girdi: src_page, dst_page | Çıktı: Event<br/>• Husus: CPU bypass, 1.8 TB/s P2P aktarım"]:::funcStyle
        C6 --- F6_1
        C6 --- F6_2
    end

    subgraph MOD7["7. SAF VRAM PARÇALAYICI: kulli_gpu/engine/zero3_sharder.py"]
        direction TB
        C7["Sınıf: ZeRO3PureVRAMSharder"]:::classStyle
        F7_1["shard_tensor(tensor) -> List[Shard]<br/>• Girdi: Tensor | Çıktı: Shard Listesi<br/>• Husus: Ram/Disk offload OLMADAN 4 GPU VRAM biler"]:::funcStyle
        F7_2["verify_pure_vram() -> bool<br/>• Girdi: Yok | Çıktı: bool<br/>• Husus: Sistem RAM taşma riskini sıfırlar"]:::funcStyle
        C7 --- F7_1
        C7 --- F7_2
    end

    subgraph MOD8["8. FİZİKSEL DONANIM KATMANI"]
        HW["4x 22GB RTX 3090 (Toplam 88 GB Physical VRAM)"]:::fileStyle
    end

    MOD1 -->|Tetikler| MOD2
    MOD1 -->|Tetikler| MOD3
    MOD2 -->|Sorgu/İstek| MOD3
    MOD2 -->|Bellek İsteği| MOD4
    MOD3 -->|Sayfa Değişim Talimatı| MOD6
    MOD3 -->|Tahmin Adresi| MOD4
    MOD4 -->|Fiziksel Eşleme| MOD8
    MOD5 -->|Kernel Koşturma| MOD8
    MOD6 -->|NVLink P2P Aktarım| MOD4
    MOD6 -->|Sayfa Senkronu| MOD7
    MOD7 -->|Saf VRAM Yönetimi| MOD4`;

  const handleCopyMermaid = () => {
    navigator.clipboard.writeText(mermaidCode);
    setCopiedMermaid(true);
    setTimeout(() => setCopiedMermaid(false), 2000);
  };

  const selectedModule = ARCHITECTURE_MODULES.find(m => m.id === selectedModuleId) || ARCHITECTURE_MODULES[0];

  const filteredModules = ARCHITECTURE_MODULES.filter(m => 
    m.filePath.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.subsystemRole.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (m.className && m.className.toLowerCase().includes(searchQuery.toLowerCase())) ||
    m.functions.some(f => f.name.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-[#0A0A0B] text-slate-200">
      {/* View Header */}
      <div className="p-4 bg-[#121316] border-b border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-emerald-950/60 text-emerald-400 border border-emerald-500/30">
              Mimarî Tertibat Plânı
            </span>
            <span className="text-xs text-slate-400 font-mono">kulli_gpu v1.0.0-spec</span>
          </div>
          <h2 className="text-lg font-bold text-white tracking-tight mt-1 flex items-center gap-2">
            <Layers className="w-5 h-5 text-emerald-400" />
            Sanal GPU Sürücüsü Mimarî Şeması & Tertibat Münasebetleri
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Sınıflar, fonksiyonlar, girdi/çıktı protokolleri, hususiyetler ve modüller arası veri akış tertibatı.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleCopyMermaid}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-950/50 border border-indigo-500/40 text-indigo-300 text-xs font-mono hover:bg-indigo-900/60 transition"
          >
            {copiedMermaid ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            {copiedMermaid ? 'Mermaid Kodu Kopyalandı!' : 'Mermaid Şema Kodunu Kopyala'}
          </button>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Architecture Overview Stat Banner */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="p-3 bg-[#121316] border border-slate-800/80 rounded-xl flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <Box className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[11px] font-mono text-slate-400 uppercase">Modül Sayısı</div>
              <div className="text-lg font-bold text-white font-mono">8 Subsystem Module</div>
            </div>
          </div>

          <div className="p-3 bg-[#121316] border border-slate-800/80 rounded-xl flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <Terminal className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[11px] font-mono text-slate-400 uppercase">Ayrılmış Sınıf & Fonksiyon</div>
              <div className="text-lg font-bold text-white font-mono">14 Core Functions</div>
            </div>
          </div>

          <div className="p-3 bg-[#121316] border border-slate-800/80 rounded-xl flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <GitMerge className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[11px] font-mono text-slate-400 uppercase">Tertibat Münasebeti</div>
              <div className="text-lg font-bold text-white font-mono">12 Inter-Module Links</div>
            </div>
          </div>

          <div className="p-3 bg-[#121316] border border-slate-800/80 rounded-xl flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[11px] font-mono text-slate-400 uppercase">Bitişik Sanal Hafıza</div>
              <div className="text-lg font-bold text-emerald-400 font-mono">88 GB Pure VRAM</div>
            </div>
          </div>
        </div>

        {/* Interactive Topology Graph Visualizer */}
        <div className="bg-[#121316] border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Network className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-semibold text-white font-mono uppercase tracking-wider">
                Sürücü Tertibat Düzeni (Module Relations Flow)
              </h3>
            </div>
            <span className="text-xs text-slate-400 font-mono">
              Bir modüle tıklayarak tertibat detayını görün
            </span>
          </div>

          {/* Module Nodes Grid representation */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {ARCHITECTURE_MODULES.map((mod) => {
              const isSelected = selectedModuleId === mod.id;
              const isRelatedToSelected = selectedModule.relationships.includes(mod.id) || 
                ARCHITECTURE_MODULES.some(m => m.id === selectedModuleId && m.relationships.includes(mod.id)) ||
                ARCHITECTURE_MODULES.some(m => m.id === mod.id && m.relationships.includes(selectedModuleId));

              return (
                <button
                  key={mod.id}
                  onClick={() => setSelectedModuleId(mod.id)}
                  className={`text-left p-3.5 rounded-xl border transition-all relative overflow-hidden group ${
                    isSelected
                      ? 'bg-slate-900/90 border-emerald-500/80 ring-1 ring-emerald-500/40 shadow-lg shadow-emerald-950/50'
                      : isRelatedToSelected
                      ? 'bg-[#181a20] border-cyan-500/50 hover:border-cyan-400'
                      : 'bg-[#15161a] border-slate-800/80 hover:border-slate-700 hover:bg-[#1c1e24]'
                  }`}
                >
                  {/* Top Header */}
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${mod.badgeColor}`}>
                      MOD{mod.moduleNumber}
                    </span>
                    {isSelected && (
                      <span className="flex h-2 w-2 relative">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                      </span>
                    )}
                  </div>

                  <div className="font-mono text-xs font-bold text-white truncate group-hover:text-emerald-300">
                    {mod.filePath}
                  </div>
                  
                  {mod.className && (
                    <div className="text-[11px] text-cyan-400 font-mono mt-0.5 font-semibold">
                      sınıf {mod.className}
                    </div>
                  )}

                  <div className="text-[11px] text-slate-400 mt-1 line-clamp-1">
                    {mod.title}
                  </div>

                  {/* Connecting Badges */}
                  <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] font-mono text-slate-400">
                    <span className="flex items-center gap-1 text-slate-400">
                      <FileCode className="w-3 h-3 text-emerald-400" />
                      {mod.functions.length} Fonksiyon
                    </span>
                    <span className="flex items-center gap-1 text-slate-400">
                      <GitMerge className="w-3 h-3 text-cyan-400" />
                      {mod.relationships.length} Bağlantı
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Search & Selected Module Deep-Dive Inspector */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Module List Sidebar Filter */}
          <div className="lg:col-span-4 bg-[#121316] border border-slate-800 rounded-xl p-4 flex flex-col">
            <div className="mb-3">
              <label className="text-xs font-mono text-slate-400 uppercase mb-1.5 block">
                Modüller & Arama
              </label>
              <div className="relative">
                <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Sınıf, dosya veya fonksiyon ara..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 bg-slate-900/80 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-emerald-500/50"
                />
              </div>
            </div>

            <div className="space-y-2 overflow-y-auto max-h-[500px] pr-1">
              {filteredModules.map((m) => (
                <button
                  key={m.id}
                  onClick={() => setSelectedModuleId(m.id)}
                  className={`w-full text-left p-2.5 rounded-lg border text-xs font-mono transition flex items-center justify-between ${
                    selectedModuleId === m.id
                      ? 'bg-emerald-950/40 border-emerald-500/60 text-emerald-300'
                      : 'bg-slate-900/40 border-slate-800/60 text-slate-300 hover:border-slate-700 hover:bg-slate-800/40'
                  }`}
                >
                  <div className="truncate">
                    <div className="font-bold">{m.filePath}</div>
                    <div className="text-[10px] text-slate-400 truncate">{m.title}</div>
                  </div>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded border ml-2 ${m.badgeColor}`}>
                    {m.id}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Module Inspector Detail View */}
          <div className="lg:col-span-8 bg-[#121316] border border-slate-800 rounded-xl p-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4 mb-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-mono px-2 py-0.5 rounded border ${selectedModule.badgeColor}`}>
                    {selectedModule.id}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">Modül #{selectedModule.moduleNumber}</span>
                </div>
                <h3 className="text-lg font-bold text-white font-mono mt-1">
                  {selectedModule.filePath}
                </h3>
                {selectedModule.className && (
                  <div className="text-sm font-semibold text-cyan-400 font-mono mt-0.5">
                    Sınıf (Class): {selectedModule.className}
                  </div>
                )}
              </div>

              <div className="bg-slate-900/80 border border-slate-800 p-2.5 rounded-lg">
                <div className="text-[10px] uppercase font-mono text-slate-400">Alt Sistem Rolü</div>
                <div className="text-xs font-mono text-emerald-400 font-semibold">{selectedModule.subsystemRole}</div>
              </div>
            </div>

            {/* Fonksiyonlar / Metotlar Listesi */}
            <div className="space-y-4">
              <h4 className="text-xs font-mono uppercase text-slate-400 flex items-center gap-2">
                <Terminal className="w-4 h-4 text-emerald-400" />
                Fonksiyonlar & Metot İmzaları (Inputs / Outputs / Features)
              </h4>

              <div className="space-y-3">
                {selectedModule.functions.map((fn, idx) => (
                  <div key={idx} className="p-3.5 bg-slate-900/80 border border-slate-800/90 rounded-lg space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-cyan-300 flex items-center gap-1.5">
                        <Zap className="w-3.5 h-3.5 text-amber-400" />
                        {fn.name}
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        {selectedModule.filePath}
                      </span>
                    </div>

                    <div className="font-mono text-xs p-2 bg-[#0A0A0B] border border-slate-800/80 rounded text-emerald-400 overflow-x-auto">
                      <code>{fn.signature}</code>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs font-mono pt-1">
                      <div className="p-2 bg-slate-950/60 border border-slate-800/60 rounded">
                        <span className="text-[10px] text-slate-500 uppercase block">Girdi (Input)</span>
                        <span className="text-slate-200">{fn.input}</span>
                      </div>
                      <div className="p-2 bg-slate-950/60 border border-slate-800/60 rounded">
                        <span className="text-[10px] text-slate-500 uppercase block">Çıktı (Output)</span>
                        <span className="text-slate-300">{fn.output}</span>
                      </div>
                    </div>

                    <div className="p-2 bg-emerald-950/20 border border-emerald-500/20 rounded text-xs font-sans text-emerald-200/90 flex items-start gap-2">
                      <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <div>
                        <span className="font-mono text-[10px] uppercase font-bold text-emerald-400 block">Hususiyet (Key Feature)</span>
                        {fn.feature}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Tertibat Münasebetleri (Connected Modules) */}
              <div className="pt-3 border-t border-slate-800">
                <h4 className="text-xs font-mono uppercase text-slate-400 flex items-center gap-2 mb-2">
                  <GitMerge className="w-4 h-4 text-cyan-400" />
                  Tertibat Münasebetleri (Doğrudan İlişkili Modüller)
                </h4>

                {selectedModule.relationships.length > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 font-mono text-xs">
                    {selectedModule.relationships.map((relId) => {
                      const relMod = ARCHITECTURE_MODULES.find(m => m.id === relId);
                      if (!relMod) return null;
                      return (
                        <button
                          key={relId}
                          onClick={() => setSelectedModuleId(relId)}
                          className="p-2.5 bg-slate-900/60 border border-slate-800 hover:border-cyan-500/50 rounded-lg text-left transition flex items-center justify-between group"
                        >
                          <div>
                            <span className="text-cyan-400 font-bold group-hover:underline">
                              {relMod.id}: {relMod.filePath}
                            </span>
                            <span className="text-[10px] text-slate-400 block mt-0.5">
                              {relMod.subsystemRole}
                            </span>
                          </div>
                          <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 group-hover:translate-x-0.5 transition" />
                        </button>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-xs font-mono text-slate-500 italic p-3 bg-slate-900/40 rounded border border-slate-800">
                    Fiziksel donanım katmanı - En alt seviye yapıdır.
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Code representation snippet of the Driver Initialization */}
        <div className="bg-[#121316] border border-slate-800 rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileCode className="w-4 h-4 text-amber-400" />
              <h3 className="text-sm font-mono font-bold text-white uppercase">
                Tek Satır Kullanım Örneği (kulli_gpu Integration)
              </h3>
            </div>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-950/50 px-2 py-0.5 rounded border border-emerald-500/30">
              Zero-Code Modification
            </span>
          </div>

          <pre className="p-4 bg-[#0A0A0B] border border-slate-800 rounded-lg text-xs font-mono text-slate-300 overflow-x-auto">
<code>{`# 1. Küllî Sanal GPU Sürücüsü Enjeksiyonu
import kulli_gpu

# Tek satırla kancalar kurulur, 4x 22GB VRAM sanal olarak 88GB bitişik blok halinde maskelenir
gpu_surucu = kulli_gpu.baslat(config={
    "virtual_vram_gb": 88,
    "physical_gpus": 4,
    "pure_vram_mode": True,  # %100 Saf VRAM (Sistem RAM / Disk Offload YASAK)
    "nvshmem_p2p": True
})

# 2. Herhangi bir standart AI / Oyun / Biyoenformatik kütüphanesi çağrılabilir:
import torch
print(f"Tespit Edilen Sanal GPU: {torch.cuda.get_device_name(0)}") # "Küllî Virtual GPU (88GB Unified VRAM)"
print(f"Toplam Kullanılabilir Bellek: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB") # 88.00 GB

# 3. Model veya Matris İşlemleri doğrudan 88 GB sınırıyla çalıştırılır:
model = torch.nn.Linear(32768, 32768).cuda() # 88GB alan üzerinde kesintisiz çalışır`}</code>
          </pre>
        </div>
      </div>
    </div>
  );
};
