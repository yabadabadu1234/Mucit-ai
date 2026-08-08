import React, { useState, useEffect } from 'react';
import { PhysicalGpu, VirtualPage, TensorAllocation, DomainType, ExecutionLog, TabType } from './types';
import { WORKLOAD_PRESETS } from './data/presets';
import { Header } from './components/Header';
import { SidebarTopology } from './components/SidebarTopology';
import { VirtualPageGrid } from './components/VirtualPageGrid';
import { AllocationTable } from './components/AllocationTable';
import { LibraryComparisonHub } from './components/LibraryComparisonHub';
import { MatMulSimulator } from './components/MatMulSimulator';
import { CodeVault } from './components/CodeVault';
import { ArchitecturePlanView } from './components/ArchitecturePlanView';
import { KernelConsole } from './components/KernelConsole';
import { Footer } from './components/Footer';

const PAGE_SIZE_MB = 512;
const TOTAL_PAGES = 176; // 88 GB / 0.5 GB
const INITIAL_VRAM_GB = 88.0;

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [uptimeSeconds, setUptimeSeconds] = useState<number>(5124);

  // Physical GPUs (4x 22 GB)
  const [physicalGpus, setPhysicalGpus] = useState<PhysicalGpu[]>([
    { id: 0, name: 'NVIDIA RTX 3090', totalVramMb: 22528, usedVramMb: 16896, temperatureC: 62, utilizationPct: 78, p2pBandwidthGBs: 56.4 },
    { id: 1, name: 'NVIDIA RTX 3090', totalVramMb: 22528, usedVramMb: 18432, temperatureC: 65, utilizationPct: 82, p2pBandwidthGBs: 56.4 },
    { id: 2, name: 'NVIDIA RTX 3090', totalVramMb: 22528, usedVramMb: 14336, temperatureC: 59, utilizationPct: 68, p2pBandwidthGBs: 56.4 },
    { id: 3, name: 'NVIDIA RTX 3090', totalVramMb: 22528, usedVramMb: 12288, temperatureC: 57, utilizationPct: 60, p2pBandwidthGBs: 56.4 }
  ]);

  // Virtual Page Table (176 Pages)
  const [pages, setPages] = useState<VirtualPage[]>(() => {
    const initialPages: VirtualPage[] = [];
    for (let i = 0; i < TOTAL_PAGES; i++) {
      const gpuId = Math.floor(i / 44); // 44 pages per 22GB GPU
      initialPages.push({
        id: i,
        virtualAddressStartMb: i * PAGE_SIZE_MB,
        virtualAddressEndMb: (i + 1) * PAGE_SIZE_MB,
        sizeMb: PAGE_SIZE_MB,
        physicalGpuId: gpuId,
        isSwappedToCpu: false,
        isAllocated: false,
        lastAccessedMs: Date.now() - Math.floor(Math.random() * 10000),
        accessCount: 0
      });
    }
    return initialPages;
  });

  // Active Tensor Allocations
  const [allocations, setAllocations] = useState<TensorAllocation[]>([]);
  const [logs, setLogs] = useState<ExecutionLog[]>([]);

  // Add Log Helper
  const addLog = (level: 'info' | 'warn' | 'success' | 'dispatch', message: string, details?: string) => {
    const newLog: ExecutionLog = {
      id: Math.random().toString(36).substring(2, 9),
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
      level,
      message,
      details
    };
    setLogs((prev) => [newLog, ...prev.slice(0, 99)]);
  };

  // Uptime Timer
  useEffect(() => {
    const timer = setInterval(() => {
      setUptimeSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Initial Seed Workloads
  useEffect(() => {
    addLog('info', '[INIT] Küllî Sanal GPU Sürücüsü (v1.0.4-DRIVER) başarıyla başlatıldı.');
    addLog('info', '[VMM] 4x 22 GB Fiziki GPU sanal adres haritasına bağlandı (0x00000000 - 0x15FFFFFFF / 88 GB).');
    
    // Seed initial allocations
    loadSeedAllocations();
  }, []);

  const loadSeedAllocations = () => {
    const llmPageCount = 125; // ~64 GB
    const dnaPageCount = 15;  // ~7.6 GB
    const physxPageCount = 20; // ~10 GB

    // Color definitions
    const colorLlm = '#38BDF8';
    const colorDna = '#00FFD0';
    const colorPhysx = '#A78BFA';

    setPages((prevPages) => {
      const updated = [...prevPages];

      // Allocate LLM (Pages 0..124)
      for (let i = 0; i < llmPageCount; i++) {
        updated[i] = {
          ...updated[i],
          isAllocated: true,
          ownerProcessId: 'proc_llm_1',
          ownerProcessName: 'LLM-80B-INFERENCE',
          colorHex: colorLlm,
          accessCount: Math.floor(Math.random() * 500) + 100
        };
      }

      // Allocate DNA (Pages 125..139)
      for (let i = llmPageCount; i < llmPageCount + dnaPageCount; i++) {
        updated[i] = {
          ...updated[i],
          isAllocated: true,
          ownerProcessId: 'proc_dna_1',
          ownerProcessName: 'DNA-GENOM-v4',
          colorHex: colorDna,
          accessCount: Math.floor(Math.random() * 300) + 50
        };
      }

      // Allocate PhysX (Pages 140..159)
      for (let i = llmPageCount + dnaPageCount; i < llmPageCount + dnaPageCount + physxPageCount; i++) {
        updated[i] = {
          ...updated[i],
          isAllocated: true,
          ownerProcessId: 'proc_physx_1',
          ownerProcessName: 'PHYSX-PARTICLE-SIM',
          colorHex: colorPhysx,
          accessCount: Math.floor(Math.random() * 200) + 20
        };
      }

      return updated;
    });

    setAllocations([
      {
        id: 'proc_llm_1',
        name: 'LLM-80B-INFERENCE',
        domain: 'llm',
        sizeMb: 64000,
        pageCount: llmPageCount,
        allocatedPages: Array.from({ length: llmPageCount }, (_, i) => i),
        dtype: 'float16',
        shape: [32768, 32768],
        createdAt: Date.now(),
        colorHex: colorLlm
      },
      {
        id: 'proc_dna_1',
        name: 'DNA-GENOM-v4',
        domain: 'dna_genomics',
        sizeMb: 7680,
        pageCount: dnaPageCount,
        allocatedPages: Array.from({ length: dnaPageCount }, (_, i) => i + llmPageCount),
        dtype: 'int32',
        shape: [500000, 10000],
        createdAt: Date.now(),
        colorHex: colorDna
      },
      {
        id: 'proc_physx_1',
        name: 'PHYSX-PARTICLE-SIM',
        domain: 'game_engine',
        sizeMb: 10240,
        pageCount: physxPageCount,
        allocatedPages: Array.from({ length: physxPageCount }, (_, i) => i + llmPageCount + dnaPageCount),
        dtype: 'float32',
        shape: [10000000, 6],
        createdAt: Date.now(),
        colorHex: colorPhysx
      }
    ]);

    addLog('dispatch', '[HOOK] LLM-80B, DNA-GENOM-v4 ve PHYSX tensörleri 88 GB sanal uzaya haritalandı.');
  };

  // Compute VRAM Usage totals
  const allocatedPages = pages.filter((p) => p.isAllocated);
  const swappedPages = pages.filter((p) => p.isAllocated && p.isSwappedToCpu);
  const allocatedMb = allocatedPages.length * PAGE_SIZE_MB;
  const swappedMb = swappedPages.length * PAGE_SIZE_MB;

  // Load Preset Handler
  const handleLoadPreset = (domain: DomainType) => {
    const preset = WORKLOAD_PRESETS.find((p) => p.id === domain);
    if (!preset) return;

    let availablePages = pages.filter((p) => !p.isAllocated);
    if (availablePages.length < 10) {
      addLog('warn', '[LRU SWAP] Sanal VRAM doluluğu kritik seviyede! Zero-OOM koruması devreye giriyor...');
      handleTriggerLruSwap();
      availablePages = pages.filter((p) => !p.isAllocated);
    }

    const sample = preset.sampleTensors[Math.floor(Math.random() * preset.sampleTensors.length)];
    const neededPagesCount = Math.ceil(sample.sizeMb / PAGE_SIZE_MB);

    if (availablePages.length < neededPagesCount) {
      addLog('warn', `[ZERO-OOM HOST SWAP] ${sample.name} (${sample.sizeMb} MB) için VRAM yetmedi. En az kullanılan sayfalar Host CPU RAM'e swap ediliyor...`);
      // Force swap older pages
      setPages((prev) =>
        prev.map((p, idx) => (idx < neededPagesCount ? { ...p, isSwappedToCpu: true } : p))
      );
    }

    // Allocate new pages
    const freePageIndices = pages.filter((p) => !p.isAllocated).slice(0, neededPagesCount).map((p) => p.id);
    const allocId = 'alloc_' + Math.random().toString(36).substring(2, 7);
    const color = domain === 'llm' ? '#38BDF8' : domain === 'game_engine' ? '#F472B6' : domain === 'dna_genomics' ? '#00FFD0' : '#A78BFA';

    setPages((prev) =>
      prev.map((p) =>
        freePageIndices.includes(p.id)
          ? {
              ...p,
              isAllocated: true,
              ownerProcessId: allocId,
              ownerProcessName: sample.name,
              colorHex: color,
              lastAccessedMs: Date.now(),
              accessCount: 1
            }
          : p
      )
    );

    const newAlloc: TensorAllocation = {
      id: allocId,
      name: sample.name,
      domain: preset.id,
      sizeMb: sample.sizeMb,
      pageCount: neededPagesCount,
      allocatedPages: freePageIndices,
      dtype: sample.dtype,
      shape: sample.shape,
      createdAt: Date.now(),
      colorHex: color
    };

    setAllocations((prev) => [newAlloc, ...prev]);
    addLog('success', `[SANAL TAHSİS] ${sample.name} (${(sample.sizeMb / 1024).toFixed(2)} GB) sanal adrese yerleştirildi.`, `Sayfalar: [${freePageIndices.slice(0, 3).join(', ')}...]`);
  };

  // Terminate Allocation
  const handleTerminateAllocation = (id: string) => {
    const alloc = allocations.find((a) => a.id === id);
    if (!alloc) return;

    setPages((prev) =>
      prev.map((p) =>
        alloc.allocatedPages.includes(p.id)
          ? {
              ...p,
              isAllocated: false,
              isSwappedToCpu: false,
              ownerProcessId: undefined,
              ownerProcessName: undefined,
              colorHex: undefined
            }
          : p
      )
    );

    setAllocations((prev) => prev.filter((a) => a.id !== id));
    addLog('info', `[SERBEST BIRAKILDI] ${alloc.name} silindi. ${alloc.sizeMb} MB VRAM temizlendi.`);
  };

  // Trigger LRU Swap
  const handleTriggerLruSwap = () => {
    setPages((prev) => {
      // Find allocated pages that are not yet swapped
      const allocatedUnswapped = prev.filter((p) => p.isAllocated && !p.isSwappedToCpu);
      if (allocatedUnswapped.length === 0) return prev;

      // Swap 10 least accessed pages to CPU
      const sortedByAccess = [...allocatedUnswapped].sort((a, b) => a.accessCount - b.accessCount);
      const targetIds = sortedByAccess.slice(0, 10).map((p) => p.id);

      addLog('warn', `[LRU SWAP TETİKLENDİ] En az erişilen 10 sanal sayfa (${targetIds.length * 512} MB) Host CPU Pinned RAM'e aktarıldı.`, `Sayfa ID'leri: ${targetIds.join(', ')}`);

      return prev.map((p) => (targetIds.includes(p.id) ? { ...p, isSwappedToCpu: true } : p));
    });
  };

  // Force Swap single page or allocation
  const handleForceSwapPage = (pageId: number) => {
    setPages((prev) =>
      prev.map((p) =>
        p.id === pageId ? { ...p, isSwappedToCpu: !p.isSwappedToCpu } : p
      )
    );
    addLog('info', `[MANUEL SAYFA SWAP] Sayfa #${pageId} swap durumu değiştirildi.`);
  };

  const handleSwapAllocation = (id: string) => {
    const alloc = allocations.find((a) => a.id === id);
    if (!alloc) return;

    setPages((prev) => {
      const anyUnswapped = alloc.allocatedPages.some((pId) => !prev[pId].isSwappedToCpu);
      const targetState = anyUnswapped; // If any is unswapped, swap all to CPU

      addLog('warn', `[PROCESS SWAP] ${alloc.name} (${alloc.sizeMb} MB) ${targetState ? "Host CPU RAM'e indirildi (Swap Out)" : "VRAM'e geri çekildi (Page In)"}.`);

      return prev.map((p) =>
        alloc.allocatedPages.includes(p.id) ? { ...p, isSwappedToCpu: targetState } : p
      );
    });
  };

  // Reset all
  const handleResetVram = () => {
    setPages((prev) =>
      prev.map((p) => ({
        ...p,
        isAllocated: false,
        isSwappedToCpu: false,
        ownerProcessId: undefined,
        ownerProcessName: undefined,
        colorHex: undefined
      }))
    );
    setAllocations([]);
    addLog('info', '[VRAM SIFIRLANDI] Tüm sanal bellek sayfaları ve tensörler serbest bırakıldı.');
  };

  // Execute MatMul
  const handleExecuteMatMul = (dimM: number, dimK: number, dimN: number) => {
    const outputGb = ((dimM * dimN * 4) / (1024 * 1024 * 1024)).toFixed(2);
    addLog('dispatch', `[INTERCEPTOR HOOK] torch.matmul(${dimM}x${dimK}, ${dimK}x${dimN}) yakalandı!`, `Sonuç Matrisi: ${outputGb} GB`);
    addLog('success', `[CUDA KERNEL] 4x Fiziki GPU üzerinde parçalı matris çarpımı başarıyla tamamlandı.`);

    // Automatically trigger tab view or allocate result tensor
    handleLoadPreset('llm');
  };

  return (
    <div className="w-full h-screen bg-[#0A0A0B] text-[#E4E3E0] font-mono flex flex-col overflow-hidden">
      {/* Top Header Navigation */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        allocatedMb={allocatedMb}
        totalVirtualVramMb={INITIAL_VRAM_GB * 1024}
        swappedMb={swappedMb}
        uptimeSeconds={uptimeSeconds}
      />

      {/* Main Body */}
      <div className="flex-1 flex flex-col lg:flex-row min-h-0 overflow-hidden">
        {/* Left Sidebar: Topology & Resource Controls */}
        <SidebarTopology
          physicalGpus={physicalGpus}
          totalVirtualVramMb={INITIAL_VRAM_GB * 1024}
          allocatedMb={allocatedMb}
          swappedMb={swappedMb}
          onLoadPreset={handleLoadPreset}
          onReset={handleResetVram}
          onTriggerLruSwap={handleTriggerLruSwap}
          onSimulateMatMul={() => setActiveTab('matmul')}
        />

        {/* Center/Right Dynamic View Content */}
        <main className="flex-1 bg-[#0A0A0B] p-4 md:p-5 flex flex-col gap-4 overflow-y-auto min-w-0">
          {activeTab === 'dashboard' && (
            <>
              {/* Virtual Page Grid Map */}
              <VirtualPageGrid
                pages={pages}
                totalVramGb={INITIAL_VRAM_GB}
                allocatedMb={allocatedMb}
                swappedMb={swappedMb}
                onForceSwapPage={handleForceSwapPage}
              />

              {/* Process Allocation Data Grid Table */}
              <AllocationTable
                allocations={allocations}
                onTerminate={handleTerminateAllocation}
                onSwapAllocation={handleSwapAllocation}
              />

              {/* Bottom Kernel Console Stream */}
              <KernelConsole logs={logs} onClearLogs={() => setLogs([])} />
            </>
          )}

          {activeTab === 'architecture' && <ArchitecturePlanView />}

          {activeTab === 'matmul' && (
            <MatMulSimulator
              onExecute={handleExecuteMatMul}
              logs={logs.map((l) => `${l.timestamp} ${l.message}`)}
            />
          )}

          {activeTab === 'comparison' && <LibraryComparisonHub />}

          {activeTab === 'code' && <CodeVault />}
        </main>
      </div>

      {/* Bottom Technical Status Bar */}
      <Footer />
    </div>
  );
}
