export type DomainType = 'llm' | 'game_engine' | 'dna_genomics' | 'cfd_physics';
export type TabType = 'dashboard' | 'architecture' | 'matmul' | 'comparison' | 'code';

export interface ModuleFunction {
  name: string;
  signature: string;
  input: string;
  output: string;
  feature: string; // Husus
}

export interface ArchitectureModule {
  id: string;
  moduleNumber: number;
  filePath: string;
  className?: string;
  title: string;
  subsystemRole: string;
  badgeColor: string;
  functions: ModuleFunction[];
  relationships: string[]; // Connected target module IDs
}

export interface PhysicalGpu {
  id: number;
  name: string;
  totalVramMb: number;
  usedVramMb: number;
  temperatureC: number;
  utilizationPct: number;
  p2pBandwidthGBs: number;
}

export interface VirtualPage {
  id: number;
  virtualAddressStartMb: number;
  virtualAddressEndMb: number;
  sizeMb: number;
  physicalGpuId: number | null; // null if swapped to CPU Pinned RAM
  isSwappedToCpu: boolean;
  isAllocated: boolean;
  ownerProcessId?: string;
  ownerProcessName?: string;
  lastAccessedMs: number;
  accessCount: number;
  colorHex?: string;
}

export interface TensorAllocation {
  id: string;
  name: string;
  domain: DomainType;
  sizeMb: number;
  pageCount: number;
  allocatedPages: number[];
  dtype: string;
  shape: number[];
  createdAt: number;
  colorHex: string;
}

export interface LibraryComparison {
  id: string;
  name: string;
  level: 'C++ CUDA Low-Level' | 'Python Framework';
  developer: string;
  coreMechanism: string;
  pageFaultHandling: 'Hardware Page Fault' | 'Software Interceptor' | 'Static Chunking' | 'Compile-Time Graph';
  oomProtection: 'Infinite (CPU/NVMe Swap)' | 'VRAM Only' | 'Managed Paging';
  multiGpuUnifiedAddress: boolean;
  zeroCopyDma: boolean;
  frameworkAgnostic: boolean; // Works for game engine, DNA, LLM
  keyApis: string[];
  cppSnippet?: string;
  pythonSnippet?: string;
  pros: string[];
  cons: string[];
  similarityScorePct: number; // How close to Küllî Sanal GPU vision
}

export interface WorkloadPreset {
  id: DomainType;
  title: string;
  subtitle: string;
  iconName: string;
  description: string;
  sampleTensors: {
    name: string;
    sizeMb: number;
    shape: number[];
    dtype: string;
    description: string;
  }[];
}

export interface ExecutionLog {
  id: string;
  timestamp: string;
  level: 'info' | 'warn' | 'success' | 'dispatch';
  message: string;
  details?: string;
}
