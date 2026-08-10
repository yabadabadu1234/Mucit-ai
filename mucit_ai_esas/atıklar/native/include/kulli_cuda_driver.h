#ifndef KULLI_CUDA_DRIVER_H
#define KULLI_CUDA_DRIVER_H

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <pthread.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <stdatomic.h>
#include <time.h>

#ifdef __cplusplus
extern "C" {
#endif

#define EXPORT __attribute__((visibility("default")))

/* ============================================================================
 * SÜRÜCÜ SABİTLERİ VE BİT BAYRAKLARI
 * ============================================================================ */
#define KULLI_PAGE_SIZE_2MB        (2ULL * 1024ULL * 1024ULL)
#define KULLI_GUARD_PAGE_SIZE      (2ULL * 1024ULL * 1024ULL)
#define KULLI_MAX_PHYSICAL_GPUS    16
#define KULLI_MAX_STREAMS_PER_CTX  256
#define KULLI_MAX_EVENTS_PER_CTX   1024
#define KULLI_RING_BUFFER_SLOTS    4096
#define KULLI_SHM_NAME             "/kulli_vmm_shm_block"
#define MAX_MAPS                   1024
#define MAX_HANDLES                1024

/* Sanal Bellek Durum Bayrakları */
typedef enum {
    KULLI_MEM_FREE        = 0x00,
    KULLI_MEM_RESERVED    = 0x01,
    KULLI_MEM_MAPPED      = 0x02,
    KULLI_MEM_LOCKED      = 0x04,
    KULLI_MEM_GUARD_PAGE  = 0x08,
    KULLI_MEM_SHARED_IPC  = 0x10
} KulliMemFlags;

/* Komut Paket Tipleri */
typedef enum {
    KULLI_CMD_NOP             = 0x00,
    KULLI_CMD_LAUNCH_KERNEL   = 0x01,
    KULLI_CMD_MEMCPY_ASYNC    = 0x02,
    KULLI_CMD_MEMSET_ASYNC    = 0x03,
    KULLI_CMD_SIGNAL_EVENT    = 0x04,
    KULLI_CMD_WAIT_EVENT      = 0x05,
    KULLI_CMD_BARRIER         = 0x06
} KulliCmdType;

/* CUDA C-API Hata Kodları (CUresult) */
typedef enum CUresult_enum {
    CUDA_SUCCESS = 0,
    CUDA_ERROR_INVALID_VALUE = 1,
    CUDA_ERROR_OUT_OF_MEMORY = 2,
    CUDA_ERROR_NOT_INITIALIZED = 3,
    CUDA_ERROR_DEINITIALIZED = 4,
    CUDA_ERROR_MAP_FAILED = 14,
    CUDA_ERROR_UNMAP_FAILED = 15,
    CUDA_ERROR_NO_DEVICE = 100,
    CUDA_ERROR_INVALID_DEVICE = 101,
    CUDA_ERROR_INVALID_CONTEXT = 201,
    CUDA_ERROR_ILLEGAL_ADDRESS = 700,
    CUDA_ERROR_LAUNCH_TIMEOUT = 702,
    CUDA_ERROR_UNKNOWN = 999
} CUresult;

typedef int CUdevice;
typedef uint64_t CUdeviceptr;
typedef struct CUctx_st *CUcontext;
typedef struct CUstream_st *CUstream;
typedef struct CUevent_st *CUevent;
typedef struct CUmod_st *CUmodule;
typedef struct CUfunc_st *CUfunction;
typedef uint64_t CUmemGenericAllocationHandle;

typedef struct cudaIpcMemHandle_st {
    char internal_data[64];
} cudaIpcMemHandle_t;

typedef enum cudaError_enum {
    cudaSuccess = 0,
    cudaErrorInvalidValue = 1,
    cudaErrorMemoryAllocation = 2,
    cudaErrorInitializationError = 3,
    cudaErrorIllegalAddress = 700,
    cudaErrorUnknown = 999
} cudaError_t;

typedef enum cudaMemcpyKind {
    cudaMemcpyHostToHost = 0,
    cudaMemcpyHostToDevice = 1,
    cudaMemcpyDeviceToHost = 2,
    cudaMemcpyDeviceToDevice = 3,
    cudaMemcpyDefault = 4
} cudaMemcpyKind;

typedef struct CUstream_st *cudaStream_t;
typedef struct CUevent_st *cudaEvent_t;

struct cudaDeviceProp {
    char name[256];
    size_t totalGlobalMem;
    size_t sharedMemPerBlock;
    int regsPerBlock;
    int warpSize;
    size_t memPitch;
    int maxThreadsPerBlock;
    int maxThreadsDim[3];
    int maxGridSize[3];
    int clockRate;
    size_t totalConstMem;
    int major;
    int minor;
    size_t textureAlignment;
    size_t texturePitchAlignment;
    int deviceOverlap;
    int multiProcessorCount;
    int kernelExecTimeoutEnabled;
    int integrated;
    int canMapHostMemory;
    int computeMode;
    int maxTexture1D;
    int maxTexture1DLinear;
    int maxTexture2D[2];
    int maxTexture2DLinear[3];
    int maxTexture3D[3];
    int concurrentKernels;
    int ECCEnabled;
    int pciBusID;
    int pciDeviceID;
    int pciDomainID;
    int tbf;
    int asyncEngineCount;
    int unifiedAddressing;
    int memoryClockRate;
    int memoryBusWidth;
    int l2CacheSize;
    int maxThreadsPerMultiProcessor;
    int streamPrioritiesSupported;
    int globalL1CacheSupported;
    int localL1CacheSupported;
    size_t sharedMemPerMultiprocessor;
    int regsPerMultiprocessor;
    int managedMemory;
    int isMultiGpuBoard;
    int multiGpuBoardGroupID;
    char padding[256];
};

#ifndef DIM3_DEFINED
#define DIM3_DEFINED
typedef struct dim3 {
    unsigned int x, y, z;
} dim3;
#endif

/* ============================================================================
 * HAKİKİ C-STRUCT VERİ YAPILARI
 * ============================================================================ */

/* 1. Sanal Bellek Tahsis Başlığı (Allocation Header) */
typedef struct KulliMemChunk {
    uint64_t virtual_addr;            /* 64-bit Sanal Başlangıç Adresi */
    size_t   size_bytes;              /* Hizalanmış Bayt Boyutu */
    uint32_t flags;                   /* KulliMemFlags Bitmask */
    int      primary_gpu_id;          /* Birincil Fiziki GPU ID */
    int      mmap_fds[KULLI_MAX_PHYSICAL_GPUS]; /* GPU Bazlı Resource1 FD'leri */
    void*    mapped_ptrs[KULLI_MAX_PHYSICAL_GPUS]; /* Canlı mmap C-Pointer'ları */
    struct KulliMemChunk* next;       /* Çift Yönlü Bağlı Liste */
    struct KulliMemChunk* prev;
} KulliMemChunk;

/* 2. Ring-Buffer Komut Paketi (64-Byte Cacheline Aligned) */
typedef struct __attribute__((aligned(64))) {
    uint32_t cmd_type;                /* KulliCmdType / KulliCommandType */
    uint32_t stream_id;               /* İlgili Akış ID */
    uint64_t fence_token;             /* Donanımsal Çit Jetonu */
    uint64_t kernel_func_ptr;         /* C-ABI Function Pointer */
    uint32_t grid_dim_x, grid_dim_y, grid_dim_z;
    uint32_t block_dim_x, block_dim_y, block_dim_z;
    uint32_t shared_mem_bytes;
    uint64_t args_buffer[8];          /* Kernel Argüman İbreleri (ParamPointers) */
} KulliCommandPacket;

typedef struct {
    uint64_t virt_addr;
    size_t size_bytes;
    int gpu_id;
    void *mapped_ptr;
    int fd;
} KulliMapEntry;

typedef struct {
    int handle_id;
    int fd;
    int gpu_id;
    size_t size_bytes;
} KulliHandleEntry;

/* 3. POSIX Paylaşımlı Bellek Kontrol Bloğu (/dev/shm) */
typedef struct {
    pthread_mutex_t global_lock;      /* Process-Shared Mutex */
    pthread_mutex_t gpu_locks[KULLI_MAX_PHYSICAL_GPUS];
    int surucu_ilklendi_mi;
    int physical_gpu_count;           /* Taranan Fiziki GPU Sayısı */
    uint64_t toplam_sanal_vram_bayt;  /* Canlı Toplam Sanal GB */
    uint64_t virtual_base_address;    /* 0x7FFF00000000 */
    uint64_t guard_page_address;      /* Guard Page Başlangıcı */
    uint64_t mevcut_sanal_imlec;      /* Dinamik Sanal Adres İmleci */
    
    size_t gpu_vram_capacities[KULLI_MAX_PHYSICAL_GPUS];
    size_t gpu_free_vram[KULLI_MAX_PHYSICAL_GPUS];
    
    KulliMapEntry active_maps[MAX_MAPS];
    int active_map_count;
    
    KulliHandleEntry handle_table[MAX_HANDLES];
    int handle_count;
    
    atomic_uint_fast64_t ctx_counter;
    atomic_uint_fast64_t event_counter;
    atomic_uint_fast64_t global_fence_token_counter;
} KulliDriverSharedState;

typedef KulliDriverSharedState KulliSharedControlBlock;

/* 4. Donanımsal Akış Yapısı (Stream Object) */
typedef struct CUstream_st {
    uint32_t stream_id;
    int      gpu_id;
    uint32_t priority;
    uint32_t flags;
    volatile uint64_t* fence_register; /* MMIO Mapped Fence Memory */
    uint64_t last_submitted_token;
    uint64_t last_completed_token;
    KulliCommandPacket ring_buffer[KULLI_RING_BUFFER_SLOTS];
    volatile uint32_t head_idx;
    volatile uint32_t tail_idx;
    pthread_spinlock_t lock;
    struct CUctx_st *ctx;
} KulliStream;

/* 5. Olay/Zamanlama Yapısı (Event Object) */
typedef struct CUevent_st {
    uint32_t event_id;
    uint32_t flags;
    volatile uint32_t is_recorded;
    volatile uint64_t completion_token;
    uint64_t recorded_token;
    uint64_t record_timestamp_ns;
    KulliStream* associated_stream;
} KulliEvent;

/* 6. GPU Bağlam Yapısı (Context Object) */
typedef struct CUctx_st {
    uint32_t ctx_id;
    int      primary_gpu_id;
    uint32_t flags;
    uint32_t active_p2p_mask;         /* Bitmask: Hangi GPU'larla P2P Açık? */
    KulliStream* streams[KULLI_MAX_STREAMS_PER_CTX];
    KulliEvent*  events[KULLI_MAX_EVENTS_PER_CTX];
    KulliMemChunk* allocations_head;  /* Bağlı Sanal Aralıklar */
    pthread_mutex_t ctx_lock;
} KulliContext;

/* Module / Function Stubs */
typedef struct CUmod_st {
    uint64_t module_id;
    void *code_ptr;
} KulliModule;

typedef struct CUfunc_st {
    uint64_t func_id;
    void *kernel_entry;
    KulliModule *module;
} KulliFunction;

/* Global Sürücü Paylaşımlı Durum İşaretçisi */
extern KulliDriverSharedState *g_shared_state;

/* ZAMAN YARDIMCI FONKSİYONLARI */
static inline uint64_t GetSystemTimeNanoseconds(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

static inline uint64_t GetSystemTimeMilliseconds(void) {
    return GetSystemTimeNanoseconds() / 1000000ULL;
}

/* 8 SUBSYSTEM C-API FONKSİYON BİLDİRİMLERİ */

/* RÜKN 1: C-API Sembol İhraç & Teşhis */
EXPORT CUresult cuInit(unsigned int Flags);
EXPORT CUresult cuDeviceGetCount(int *count);
EXPORT CUresult cuDeviceTotalMem(size_t *bytes, CUdevice dev);
EXPORT CUresult cuDeviceTotalMem_v2(size_t *bytes, CUdevice dev);
EXPORT CUresult cuDeviceGet(CUdevice *device, int ordinal);
EXPORT CUresult cuDeviceGetName(char *name, int len, CUdevice dev);
EXPORT CUresult cuDeviceGetAttribute(int *pi, int attrib, CUdevice dev);

/* RÜKN 2: VMM Sanal Bellek & mmap */
EXPORT CUresult cuMemAddressReserve(CUdeviceptr *ptr, size_t size, size_t alignment, CUdeviceptr addr, unsigned long long flags);
EXPORT CUresult cuMemAddressFree(CUdeviceptr ptr, size_t size);
EXPORT CUresult cuMemAddressFree_v2(CUdeviceptr ptr, size_t size);
EXPORT CUresult cuMemCreate(CUmemGenericAllocationHandle *handle, size_t size, const void *prop, unsigned long long flags);
EXPORT CUresult cuMemMap(CUdeviceptr ptr, size_t size, size_t offset, CUmemGenericAllocationHandle handle, unsigned long long flags);
EXPORT CUresult cuMemSetAccess(CUdeviceptr ptr, size_t size, const void *desc, size_t count);
EXPORT CUresult cuMemUnmap(CUdeviceptr ptr, size_t size);
EXPORT CUresult cuMemRelease(CUmemGenericAllocationHandle handle);
EXPORT CUresult cuMemAlloc(CUdeviceptr *dptr, size_t bytesize);
EXPORT CUresult cuMemFree(CUdeviceptr dptr);

/* RÜKN 3: Context & Stream Durum Makinesi */
EXPORT CUresult cuCtxCreate(CUcontext *pctx, unsigned int flags, CUdevice dev);
EXPORT CUresult cuCtxCreate_v2(CUcontext *pctx, unsigned int flags, CUdevice dev);
EXPORT CUresult cuCtxDestroy(CUcontext ctx);
EXPORT CUresult cuCtxGetCurrent(CUcontext *pctx);
EXPORT CUresult cuCtxSetCurrent(CUcontext ctx);
EXPORT CUresult cuStreamCreate(CUstream *phStream, unsigned int Flags);
EXPORT CUresult cuStreamDestroy(CUstream hStream);
EXPORT CUresult cuStreamSynchronize(CUstream hStream);
EXPORT CUresult cuStreamQuery(CUstream hStream);

/* RÜKN 4: Kernel Fırlatma & Ring-Buffer */
EXPORT CUresult cuModuleLoad(CUmodule *module, const char *fname);
EXPORT CUresult cuModuleLoadData(CUmodule *module, const void *image);
EXPORT CUresult cuModuleGetFunction(CUfunction *hfunc, CUmodule hmod, const char *name);
EXPORT CUresult cuModuleUnload(CUmodule hmod);
EXPORT CUresult cuLaunchKernel(CUfunction f, unsigned int gridDimX, unsigned int gridDimY, unsigned int gridDimZ,
                               unsigned int blockDimX, unsigned int blockDimY, unsigned int blockDimZ,
                               unsigned int sharedMemBytes, CUstream hStream, void **kernelParams, void **extra);
void PushToRingBuffer(CUstream hStream, const KulliCommandPacket *pkt);

/* RÜKN 5: P2P DMA & Biyortogonal IPC */
EXPORT CUresult cuCtxEnablePeerAccess(CUcontext peerContext, unsigned int Flags);
EXPORT CUresult cuCtxDisablePeerAccess(CUcontext peerContext);
EXPORT CUresult cudaIpcGetMemHandle(cudaIpcMemHandle_t *handle, void *devPtr);
EXPORT CUresult cudaIpcOpenMemHandle(void **devPtr, cudaIpcMemHandle_t handle, unsigned int flags);
EXPORT CUresult cudaIpcCloseMemHandle(void *devPtr);

/* RÜKN 6: Sürücü İçi POSIX Paylaşımlı Bellek & İletişim */
int KulliShmControlInit(void);
int KulliUnixSocketSendFd(int socket_fd, int fd_to_send);
int KulliUnixSocketRecvFd(int socket_fd);

/* RÜKN 7: Donanımsal Çit & Senkronizasyon */
EXPORT CUresult cuEventCreate(CUevent *phEvent, unsigned int Flags);
EXPORT CUresult cuEventDestroy(CUevent hEvent);
EXPORT CUresult cuEventDestroy_v2(CUevent hEvent);
EXPORT CUresult cuEventRecord(CUevent hEvent, CUstream hStream);
EXPORT CUresult cuEventSynchronize(CUevent hEvent);
EXPORT CUresult cuEventQuery(CUevent hEvent);
EXPORT CUresult cuEventElapsedTime(float *pMilliseconds, CUevent hStart, CUevent hEnd);

/* RÜKN 8: Hata Teşhis & Güvenlik Muhafızı */
EXPORT CUresult cuGetErrorString(CUresult error, const char **pStr);
EXPORT CUresult cuGetErrorName(CUresult error, const char **pStr);
CUresult KulliBoundaryGuardCheck(uint64_t virt_ptr, size_t size_bytes);
void LogDriverError(const char *fmt, ...);

/* RÜKN 9: CUDA Runtime C-API Overrides */
EXPORT cudaError_t cudaGetDeviceCount(int *count);
EXPORT cudaError_t cudaGetDeviceProperties(struct cudaDeviceProp *prop, int device);
EXPORT cudaError_t cudaDeviceGetAttribute(int *value, int attr, int device);
EXPORT cudaError_t cudaMemGetInfo(size_t *free, size_t *total);
EXPORT cudaError_t cudaSetDevice(int device);
EXPORT cudaError_t cudaGetDevice(int *device);
EXPORT cudaError_t cudaGetDeviceFlags(unsigned int *flags);

EXPORT cudaError_t cudaMalloc(void **devPtr, size_t size);
EXPORT cudaError_t cudaMallocManaged(void **devPtr, size_t size, unsigned int flags);
EXPORT cudaError_t cudaMallocPitch(void **devPtr, size_t *pitch, size_t width, size_t height);
EXPORT cudaError_t cudaFree(void *devPtr);
EXPORT cudaError_t cudaFreeHost(void *ptr);
EXPORT cudaError_t cudaMemset(void *devPtr, int value, size_t count);
EXPORT cudaError_t cudaMemsetAsync(void *devPtr, int value, size_t count, cudaStream_t stream);

EXPORT cudaError_t cudaMemcpy(void *dst, const void *src, size_t count, enum cudaMemcpyKind kind);
EXPORT cudaError_t cudaMemcpyAsync(void *dst, const void *src, size_t count, enum cudaMemcpyKind kind, cudaStream_t stream);
EXPORT cudaError_t cudaMemcpyPeer(void *dst, int dstDevice, const void *src, int srcDevice, size_t count);
EXPORT cudaError_t cudaMemcpyPeerAsync(void *dst, int dstDevice, const void *src, int srcDevice, size_t count, cudaStream_t stream);

EXPORT cudaError_t cudaStreamCreate(cudaStream_t *pStream);
EXPORT cudaError_t cudaStreamCreateWithFlags(cudaStream_t *pStream, unsigned int flags);
EXPORT cudaError_t cudaStreamSynchronize(cudaStream_t stream);
EXPORT cudaError_t cudaStreamQuery(cudaStream_t stream);

EXPORT cudaError_t cudaEventCreate(cudaEvent_t *event);
EXPORT cudaError_t cudaEventRecord(cudaEvent_t event, cudaStream_t stream);
EXPORT cudaError_t cudaEventSynchronize(cudaEvent_t event);
EXPORT cudaError_t cudaEventElapsedTime(float *ms, cudaEvent_t start, cudaEvent_t end);

EXPORT cudaError_t cudaLaunchKernel(const void *func, dim3 gridDim, dim3 blockDim, void **args, size_t sharedMem, cudaStream_t stream);
EXPORT cudaError_t cudaDeviceSynchronize(void);
EXPORT cudaError_t cudaDeviceReset(void);
EXPORT cudaError_t cudaGetLastError(void);
EXPORT const char* cudaGetErrorString(cudaError_t error);

#ifdef __cplusplus
}
#endif

#endif /* KULLI_CUDA_DRIVER_H */

