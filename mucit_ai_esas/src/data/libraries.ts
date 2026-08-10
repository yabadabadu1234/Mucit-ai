import { LibraryComparison } from '../types';

export const LIBRARIES_DATA: LibraryComparison[] = [
  {
    id: 'kulli_sanal_gpu',
    name: 'Küllî Sanal GPU (Universal Virtual GPU)',
    level: 'Python Framework',
    developer: 'Özel / Vizyoner Mimari',
    coreMechanism: 'Küllî Sanal Adres Haritası (Page Table) + Şeffaf Operatör Kancası (Operator Interceptor) + 512MB Sanal Sayfalama',
    pageFaultHandling: 'Software Interceptor',
    oomProtection: 'Infinite (CPU/NVMe Swap)',
    multiGpuUnifiedAddress: true,
    zeroCopyDma: true,
    frameworkAgnostic: true,
    similarityScorePct: 100,
    keyApis: ['KulliSanalGPU()', 'sanal_tensor_tahsis_et()', 'sanal_matris_carpimi()'],
    pythonSnippet: `from kulli_sanal_gpu import KulliSanalGPU

# 4x 22GB fiziki GPU'yu ana programa 88 GB TEK GPU olarak sunar
sanal_gpu = KulliSanalGPU(sayfa_boyutu_mb=512.0)

# Devasa matris tahsis et (OOM riski yok):
sanal_A = sanal_gpu.sanal_tensor_tahsis_et((32768, 32768))
sanal_B = sanal_gpu.sanal_tensor_tahsis_et((32768, 32768))

# Matris Çarpımı Interceptor arka planda fiziki CUDA sevklerini idare eder
C = sanal_gpu.sanal_matris_carpimi(sanal_A, sanal_B)`,
    pros: [
      'Oyun Motoru, DNA Genomik, LLM ve CFD dahil HER türlü projede evrensel çalışır',
      '88 GB (veya sınırsız) kesintisiz sanal VRAM adresi sunar',
      'Hafıza taşmasını (OOM) LRU Host CPU Swapping ile %100 engeller',
      'Ana bilgisayar kodunda sıfır karmaşıklık — tek bir sanal cihaz görür'
    ],
    cons: [
      'P2P DMA PCI-Express veri transferinde yüksek bant genişliği optimize edilmiş sürücü kancası gerektirir'
    ]
  },
  {
    id: 'cuda_vmm',
    name: 'NVIDIA CUDA VMM API (cuMemMap)',
    level: 'C++ CUDA Low-Level',
    developer: 'NVIDIA Corporation',
    coreMechanism: 'cuMemAddressReserve + cuMemMap + cuMemSetAccess ile C++ sürücü seviyesinde fiziki bellek parçalarını sanal adrese düğümleme',
    pageFaultHandling: 'Hardware Page Fault',
    oomProtection: 'Managed Paging',
    multiGpuUnifiedAddress: true,
    zeroCopyDma: true,
    frameworkAgnostic: true,
    similarityScorePct: 92,
    keyApis: ['cuMemAddressReserve()', 'cuMemCreate()', 'cuMemMap()', 'cuMemSetAccess()'],
    cppSnippet: `CUdeviceptr ptr;
size_t size = 88ULL * 1024 * 1024 * 1024; // 88 GB Virtual Address
cuMemAddressReserve(&ptr, size, 0, 0, 0);

// GPU 0, 1, 2, 3 fiziki belleklerini bu sanal ptr adresine haritala
for (int i = 0; i < 4; i++) {
    CUmemGenericAllocationHandle handle;
    cuMemCreate(&handle, 22ULL * 1024 * 1024 * 1024, &prop, 0);
    cuMemMap(ptr + (i * 22ULL * 1024 * 1024 * 1024), 22ULL * 1024 * 1024 * 1024, 0, handle, 0);
}`,
    pros: [
      'En alt katman C++ sürücü performansı — sıfır overhead',
      'Tamamen evrensel: C++, Rust, CUDA, PhysX, PyTorch üstüne inşa edilebilir',
      'Fiziki GPU sınırlarını uygulama kodundan tamamen gizler'
    ],
    cons: [
      'C++ CUDA Sürücü API bilgisi gerektirir, yüksek seviye Python kanca yazılması icap eder'
    ]
  },
  {
    id: 'deepspeed_zero3',
    name: 'Microsoft DeepSpeed (ZeRO-3 & ZeRO-Infinity)',
    level: 'Python Framework',
    developer: 'Microsoft AI Research',
    coreMechanism: 'Model parametrelerini, gradyanları ve optimizer durumlarını sanal bir GPU havuzuna böler + CPU RAM/NVMe offloading',
    pageFaultHandling: 'Software Interceptor',
    oomProtection: 'Infinite (CPU/NVMe Swap)',
    multiGpuUnifiedAddress: true,
    zeroCopyDma: true,
    frameworkAgnostic: false, // Designed for Deep Learning Neural Nets
    similarityScorePct: 85,
    keyApis: ['deepspeed.initialize()', 'ZeRO-3 Partitioning', 'NVMe Offload Engine'],
    pythonSnippet: `import deepspeed

ds_config = {
    "zero_optimization": {
        "stage": 3,
        "offload_optimizer": {"device": "cpu", "pin_memory": True},
        "offload_param": {"device": "nvme", "nvme_path": "/mnt/nvme"}
    }
}
model, optimizer, _, _ = deepspeed.initialize(model=model, config=ds_config)`,
    pros: [
      'Sınırsız model boyutlarını (Trilyon parametre) CPU/NVMe swap ile çalıştırır',
      'PyTorch ile doğrudan entegre',
      'Endüstri standardı LLM eğitim ve çıkarım kütüphanesi'
    ],
    cons: [
      'Yalnızca Yapay Zeka / Sinir Ağı katmanları için tasarlanmıştır, Oyun motoru veya DNA algoritmalarına uyarlamak zordur'
    ]
  },
  {
    id: 'vllm_pagedattention',
    name: 'UC Berkeley vLLM (PagedAttention)',
    level: 'Python Framework',
    developer: 'UC Berkeley LMSYS',
    coreMechanism: 'İşletim sistemlerindeki Virtual Memory Paging (Sanal Sayfalama) mantığını KV-Cache belleğine uygulayan C++/Python motoru',
    pageFaultHandling: 'Software Interceptor',
    oomProtection: 'VRAM Only',
    multiGpuUnifiedAddress: true,
    zeroCopyDma: true,
    frameworkAgnostic: false,
    similarityScorePct: 78,
    keyApis: ['PagedAttentionKernel', 'BlockAllocator', 'PhysicalTokenBlock'],
    pythonSnippet: `from vllm import LLM, SamplingParams

# Virtual Paging ile GPU VRAM'ini fiziki parçalı sayfalara ayırır
llm = LLM(model="meta-llama/Llama-2-70b-hf", tensor_parallel_size=4)
outputs = llm.generate("DNA Dizileme Analizi ve GPU Sanallaştırma...")`,
    pros: [
      'GPU belleğindeki parçalanmayı (fragmentation) sıfıra indirir',
      'Çok yüksek throughput (2x-4x hız artışı)',
      'Sanal sayfa adresleme mimarisi Küllî Sanal GPU ile birebir örtüşür'
    ],
    cons: [
      'Yalnızca Transformer LLM KV-Cache optimizasyonu odaklıdır'
    ]
  },
  {
    id: 'cuda_nvshmem',
    name: 'NVIDIA NVSHMEM (PGAS Driver)',
    level: 'C++ CUDA Low-Level',
    developer: 'NVIDIA Corporation',
    coreMechanism: 'Partitioned Global Address Space (PGAS) ile tüm GPU VRAM haritalarını tek bir global adres uzayına bağlar',
    pageFaultHandling: 'Hardware Page Fault',
    oomProtection: 'VRAM Only',
    multiGpuUnifiedAddress: true,
    zeroCopyDma: true,
    frameworkAgnostic: true,
    similarityScorePct: 88,
    keyApis: ['nvshmem_init()', 'nvshmem_ptr()', 'nvshmem_malloc()', 'nvshmem_put()'],
    cppSnippet: `#include <nvshmem.h>

nvshmem_init();
int* global_vram = (int*) nvshmem_malloc(1024 * sizeof(int));

// GPU 0, GPU 3'ün VRAM'indeki sanal adrese doğrudan erişir!
int val = nvshmem_ptr(global_vram, 3)[0];`,
    pros: [
      'Süper bilgisayar ve HPC (High-Performance Computing) seviyesinde düşük gecikme',
      'NVLink ve NVSwitch donanımları ile hat hızında erişim',
      'Genom dizileme ve moleküler simülasyonlar için C++ standardı'
    ],
    cons: [
      'Sadece GPU belleklerini birleştirir; CPU RAM/NVMe swap otomatik değildir'
    ]
  },
  {
    id: 'cuda_uvm',
    name: 'CUDA Unified Memory (cudaMallocManaged)',
    level: 'C++ CUDA Low-Level',
    developer: 'NVIDIA Corporation',
    coreMechanism: 'GPU ve CPU adres alanını tek bir sanal belleğe (Unified Memory) indirgeyen donanımsal sayfa yönlendiricisi',
    pageFaultHandling: 'Hardware Page Fault',
    oomProtection: 'Infinite (CPU/NVMe Swap)',
    multiGpuUnifiedAddress: true,
    zeroCopyDma: false,
    frameworkAgnostic: true,
    similarityScorePct: 80,
    keyApis: ['cudaMallocManaged()', 'cudaMemAdvise()', 'cudaMemPrefetchAsync()'],
    cppSnippet: `float *data;
// 88 GB'lik tek bir sanal bellek blogu tahsis et:
cudaMallocManaged(&data, 88ULL * 1024 * 1024 * 1024);

// CUDA sürücüsü erişilen veriyi hangi GPU talep ediyorsa oraya taşır (Page Fault)
cudaMemAdvise(data, size, cudaMemAdviseSetPreferredLocation, 0);`,
    pros: [
      'Kullanımı çok kolay C++ komutu (`cudaMallocManaged`)',
      'CPU ve GPU arasında otomatik sayfa taşıma',
      'Tüm CUDA programlarında çalışır'
    ],
    cons: [
      'Sayfa hatası (Page Fault) gecikmeleri yüksek olabilir, manuel prefetch optimizasyonu ister'
    ]
  },
  {
    id: 'hf_accelerate',
    name: 'HuggingFace Accelerate (device_map="auto")',
    level: 'Python Framework',
    developer: 'Hugging Face',
    coreMechanism: 'Cihaz topolojisi taraması (Device Topology Map) ile modül katmanlarını fiziki GPU\'lara ve CPU RAM\'ine dağıtır',
    pageFaultHandling: 'Static Chunking',
    oomProtection: 'Infinite (CPU/NVMe Swap)',
    multiGpuUnifiedAddress: false,
    zeroCopyDma: false,
    frameworkAgnostic: false,
    similarityScorePct: 70,
    keyApis: ['infer_auto_device_map()', 'dispatch_model()', 'load_checkpoint_and_dispatch()'],
    pythonSnippet: `from accelerate import infer_auto_device_map, dispatch_model

device_map = infer_auto_device_map(model, max_memory={
    0: "22GB", 1: "22GB", 2: "22GB", 3: "22GB", "cpu": "64GB"
})
model = dispatch_model(model, device_map=device_map)`,
    pros: [
      'Kurulumu ve Python kullanım sadeliği',
      'Farklı boyutlardaki GPU kartlarını destekler',
      'Model yükleme esnasında bellek taşmasını önler'
    ],
    cons: [
      'Dinamik matris bazlı sanal sayfalama yapmaz; sabit katman bölmesi yapar'
    ]
  }
];
