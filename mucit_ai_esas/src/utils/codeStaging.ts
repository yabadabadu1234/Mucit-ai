/**
 * NİZAMNAME & TALİMAT-I KATİYE: STAGING & APPROVAL ENGINE
 * İkinci & Üçüncü & Dördüncü Vazife: Staging, Diff Computation, User Approval Seal & User Editing
 */

import { codeBackupRepo, injectPrePostGuards } from './codeGuardBackup';

export interface DiffLine {
  type: 'added' | 'removed' | 'unchanged';
  oldLineNumber?: number;
  newLineNumber?: number;
  content: string;
}

export interface StagedProposal {
  id: string;
  fileId: string;
  filePath: string;
  fileLanguage: 'python' | 'cpp';
  title: string;
  description: string;
  originalCode: string;
  proposedCode: string;
  userEditedCode: string; // Live editable code by user
  status: 'pending' | 'approved' | 'rejected';
  createdAt: string;
  proposedBy: string;
}

/**
 * Computes a standard line-by-line diff between two code strings.
 */
export function computeLineDiff(oldCode: string, newCode: string): {
  lines: DiffLine[];
  additionsCount: number;
  deletionsCount: number;
} {
  const oldLines = oldCode.split('\n');
  const newLines = newCode.split('\n');
  const diffLines: DiffLine[] = [];

  let oldIdx = 0;
  let newIdx = 0;
  let additionsCount = 0;
  let deletionsCount = 0;

  // Simple Myers/LCS inspired line diff algorithm for visual presentation
  while (oldIdx < oldLines.length || newIdx < newLines.length) {
    if (oldIdx < oldLines.length && newIdx < newLines.length && oldLines[oldIdx] === newLines[newIdx]) {
      diffLines.push({
        type: 'unchanged',
        oldLineNumber: oldIdx + 1,
        newLineNumber: newIdx + 1,
        content: oldLines[oldIdx]
      });
      oldIdx++;
      newIdx++;
    } else {
      // Look ahead in newLines
      const matchInNew = newLines.slice(newIdx, newIdx + 5).indexOf(oldLines[oldIdx]);
      // Look ahead in oldLines
      const matchInOld = oldLines.slice(oldIdx, oldIdx + 5).indexOf(newLines[newIdx]);

      if (matchInNew !== -1 && (matchInOld === -1 || matchInNew <= matchInOld)) {
        // Lines were added in newCode
        while (newIdx < newLines.length && oldLines[oldIdx] !== newLines[newIdx]) {
          diffLines.push({
            type: 'added',
            newLineNumber: newIdx + 1,
            content: newLines[newIdx]
          });
          additionsCount++;
          newIdx++;
        }
      } else if (matchInOld !== -1) {
        // Lines were removed from oldCode
        while (oldIdx < oldLines.length && oldLines[oldIdx] !== newLines[newIdx]) {
          diffLines.push({
            type: 'removed',
            oldLineNumber: oldIdx + 1,
            content: oldLines[oldIdx]
          });
          deletionsCount++;
          oldIdx++;
        }
      } else {
        // Mismatch: record old as removed, new as added
        if (oldIdx < oldLines.length) {
          diffLines.push({
            type: 'removed',
            oldLineNumber: oldIdx + 1,
            content: oldLines[oldIdx]
          });
          deletionsCount++;
          oldIdx++;
        }
        if (newIdx < newLines.length) {
          diffLines.push({
            type: 'added',
            newLineNumber: newIdx + 1,
            content: newLines[newIdx]
          });
          additionsCount++;
          newIdx++;
        }
      }
    }
  }

  return { lines: diffLines, additionsCount, deletionsCount };
}

// Preset Sample Proposals for Demonstration
export const INITIAL_PROPOSALS: StagedProposal[] = [
  {
    id: 'PROP_001',
    fileId: 'MOD3_PY',
    filePath: 'kulli_gpu/scheduler/predictive_engine.py',
    fileLanguage: 'python',
    title: 'ErkenDevlet Tarafı 16-Adım Matris Tahmin & Asenkron Prefetching Yükseltmesi',
    description: 'Lookahead derinliği 8 adımdan 16 adıma çıkarılarak NVSHMEM üzerindeki sayfa gecikmesi %42 düşürülmüştür.',
    proposedBy: 'Küllî Mimarî Ajanı',
    createdAt: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }),
    status: 'pending',
    originalCode: `    def __init__(self, allocator: Any, bus: Any):
        self.allocator = allocator
        self.bus = bus
        self.lookahead_depth = 8
        self.prediction_cache: List[ExecutionStep] = []`,
    proposedCode: `    def __init__(self, allocator: Any, bus: Any):
        self.allocator = allocator
        self.bus = bus
        self.lookahead_depth = 16  # [NİZAMNAME İYİLEŞTİRMESİ] Lookahead 16 adıma yükseltildi
        self.prediction_cache: List[ExecutionStep] = []
        self.async_prefetch_enabled = True  # Asenkron prefetch hattı aktif edildi`,
    userEditedCode: `    def __init__(self, allocator: Any, bus: Any):
        self.allocator = allocator
        self.bus = bus
        self.lookahead_depth = 16  # [NİZAMNAME İYİLEŞTİRMESİ] Lookahead 16 adıma yükseltildi
        self.prediction_cache: List[ExecutionStep] = []
        self.async_prefetch_enabled = True  # Asenkron prefetch hattı aktif edildi`
  },
  {
    id: 'PROP_002',
    fileId: 'MOD8_CPP',
    filePath: 'cpp_driver/kulli_vmm_cuda.cpp',
    fileLanguage: 'cpp',
    title: 'C++ CUDA Low-Level Driver 128 GB Sanal Bellek Genişletme & Pinned Memory Ayarı',
    description: 'cuMemAddressReserve çağrısı 88GB sınırından 128GB unified sanal adres aralığına yükseltilmiştir.',
    proposedBy: 'Küllî C++ Zabit Mimarisi',
    createdAt: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }),
    status: 'pending',
    originalCode: `#define KULLI_VIRTUAL_VRAM_GB 88ULL
#define KULLI_TOTAL_BYTES (KULLI_VIRTUAL_VRAM_GB * 1024ULL * 1024ULL * 1024ULL)
#define PHYSICAL_GPU_COUNT 4`,
    proposedCode: `#define KULLI_VIRTUAL_VRAM_GB 128ULL // [NİZAMNAME MÜHÜRÜ] 88GB -> 128GB Sanal Adres Uzayı
#define KULLI_TOTAL_BYTES (KULLI_VIRTUAL_VRAM_GB * 1024ULL * 1024ULL * 1024ULL)
#define PHYSICAL_GPU_COUNT 4
#define KULLI_PINNED_POOL_MB 16384ULL // 16GB Pinned DMA Transfer Buffer`,
    userEditedCode: `#define KULLI_VIRTUAL_VRAM_GB 128ULL // [NİZAMNAME MÜHÜRÜ] 88GB -> 128GB Sanal Adres Uzayı
#define KULLI_TOTAL_BYTES (KULLI_VIRTUAL_VRAM_GB * 1024ULL * 1024ULL * 1024ULL)
#define PHYSICAL_GPU_COUNT 4
#define KULLI_PINNED_POOL_MB 16384ULL // 16GB Pinned DMA Transfer Buffer`
  }
];
