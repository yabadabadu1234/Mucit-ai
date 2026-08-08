import { WorkloadPreset } from '../types';

export const WORKLOAD_PRESETS: WorkloadPreset[] = [
  {
    id: 'llm',
    title: 'Yapay Zeka & LLM Çıkarımı',
    subtitle: 'Llama-3 70B / 80B Matrix Tensor Weights & KV Cache',
    iconName: 'Cpu',
    description: 'Devasa Dil Modeli ağırlıkları ve bağlam belleği (KV-Cache) 88 GB sanal VRAM üzerine seri olarak yüklenir.',
    sampleTensors: [
      {
        name: 'LLM-LAYER-ATTN-QKV',
        sizeMb: 16384,
        shape: [32768, 32768],
        dtype: 'float16',
        description: 'Multi-Head Self-Attention Q, K, V Projeksiyon Matrisi (16 GB)'
      },
      {
        name: 'LLM-MLP-GATE-UP',
        sizeMb: 24576,
        shape: [32768, 49152],
        dtype: 'float16',
        description: 'Feed-Forward SwiGLU İleri Beslemeli Katman Ağırıkları (24.5 GB)'
      },
      {
        name: 'LLM-KV-CACHE-CTX',
        sizeMb: 12288,
        shape: [128, 32, 4096, 128],
        dtype: 'float16',
        description: 'Dinamik Uzun Bağlam Bağlam Sayfa Belleği (12 GB)'
      },
      {
        name: 'LLM-EMBEDDING-TOKENS',
        sizeMb: 4096,
        shape: [128000, 8192],
        dtype: 'float32',
        description: 'Kelime Dağarcığı Embedding Vektör Tablosu (4 GB)'
      }
    ]
  },
  {
    id: 'game_engine',
    title: '3D Oyun Motoru & Fizik',
    subtitle: 'Ray-Tracing Mesh VRAM Pool & Voxel Volumetric Data',
    iconName: 'Gamepad2',
    description: '4K Ultra Oyun Sahnesi, Işın İzleme (BVH Acceleration Structure) ve Fizik Parçacık simülasyonu 88GB sanal haritaya aktarılır.',
    sampleTensors: [
      {
        name: 'GAME-BVH-RAYTRACE-TREE',
        sizeMb: 14336,
        shape: [14000000, 16],
        dtype: 'float32',
        description: 'Donanımsal Ray-Tracing Hiyerarşik Hacim Yapısı (14 GB)'
      },
      {
        name: 'GAME-8K-TEXTURE-ATLAS',
        sizeMb: 18432,
        shape: [8192, 8192, 4],
        dtype: 'uint8',
        description: '8K PBR Kaplama ve Normal Haritası Bellek Bloğu (18.4 GB)'
      },
      {
        name: 'GAME-PHYSX-PARTICLES',
        sizeMb: 8192,
        shape: [10000000, 6],
        dtype: 'float32',
        description: '10 Milyon Akışkan Parçacık Pozisyon ve Hız Matrisi (8 GB)'
      },
      {
        name: 'GAME-SHADOW-CASCADE-MAP',
        sizeMb: 6144,
        shape: [4, 4096, 4096],
        dtype: 'float32',
        description: 'Basamaklı Gölge Derinlik Haritaları (6.1 GB)'
      }
    ]
  },
  {
    id: 'dna_genomics',
    title: 'DNA Dizileme & Genomik',
    subtitle: 'Human Genome FastQ Sequence Matrix & Suffix Index',
    iconName: 'Dna',
    description: 'İnsan genomu (3 Milyar baz çifti) hizalama, k-mer frekans matrisleri ve Burrows-Wheeler indeks uzayı.',
    sampleTensors: [
      {
        name: 'DNA-GENOME-ALIGN-MATRIX',
        sizeMb: 20480,
        shape: [500000, 10000],
        dtype: 'int32',
        description: 'Genom Hizasızlık Okuma ve Skorlama Matrisi (20.4 GB)'
      },
      {
        name: 'DNA-SUFFIX-ARRAY-BWT',
        sizeMb: 16384,
        shape: [3200000000, 1],
        dtype: 'int32',
        description: 'Burrows-Wheeler Transformasyon İndeks Bloğu (16 GB)'
      },
      {
        name: 'DNA-KMER-COUNT-TENSOR',
        sizeMb: 10240,
        shape: [65536, 1024],
        dtype: 'float32',
        description: 'K-Mer Sayım ve Genetik Mutasyon Olasılık Haritası (10.2 GB)'
      }
    ]
  },
  {
    id: 'cfd_physics',
    title: 'CFD Akışkanlar & Astrofizik',
    subtitle: '3D Navier-Stokes Grid & N-Body Gravitational Tensor',
    iconName: 'Activity',
    description: 'Yüksek çözünürlüklü 3D Akışkan Dinamiği (CFD) grid çözücüsü ve Astrofizik N-Body galaksi simülasyonu.',
    sampleTensors: [
      {
        name: 'CFD-NAVIER-STOKES-GRID',
        sizeMb: 24576,
        shape: [1024, 1024, 1024, 3],
        dtype: 'float32',
        description: '3D Hacimsel Basınç-Hız Vektör Çözüm Tensorü (24.5 GB)'
      },
      {
        name: 'ASTRO-NBODY-GRAVITY-FIELD',
        sizeMb: 14336,
        shape: [50000000, 4],
        dtype: 'float64',
        description: '50 Milyon Yıldız Çift-Hassasiyet Kütleçekim Vektörü (14.3 GB)'
      },
      {
        name: 'CFD-TURBULENCE-FFT-FREQ',
        sizeMb: 8192,
        shape: [2048, 2048, 512],
        dtype: 'complex64',
        description: 'Hızlı Fourier Dönüşümü (FFT) Türbülans Haritası (8 GB)'
      }
    ]
  }
];
