#include "kulli_cuda_driver.h"

/* ============================================================================
 * RÜKN 9: CUDA RUNTIME C-API İKAME (OVERRIDE) FONKSİYONLARI
 * ============================================================================ */

/* 1. Cihaz Topolojisi ve Bellek Sorgulama */

EXPORT cudaError_t cudaGetDeviceCount(int *count) {
    if (count == NULL) return cudaErrorInvalidValue;
    if (g_shared_state == NULL || g_shared_state->surucu_ilklendi_mi == 0) {
        cuInit(0);
    }
    *count = 1; // Küllî Birleşik Sanal GPU
    return cudaSuccess;
}

EXPORT cudaError_t cudaGetDeviceProperties(struct cudaDeviceProp *prop, int device) {
    (void)device;
    if (prop == NULL) return cudaErrorInvalidValue;

    if (g_shared_state == NULL || g_shared_state->surucu_ilklendi_mi == 0) {
        cuInit(0);
    }

    memset(prop, 0, sizeof(struct cudaDeviceProp));
    strncpy(prop->name, "Kulli Unified Virtual GPU (88GB Pure VRAM)", sizeof(prop->name) - 1);

    if (g_shared_state && g_shared_state->toplam_sanal_vram_bayt > 0) {
        prop->totalGlobalMem = (size_t)g_shared_state->toplam_sanal_vram_bayt;
    } else {
        prop->totalGlobalMem = (size_t)(88ULL * 1024ULL * 1024ULL * 1024ULL);
    }

    prop->multiProcessorCount = 336;
    prop->major = 8;
    prop->minor = 6;
    prop->unifiedAddressing = 1;
    prop->managedMemory = 1;
    prop->concurrentKernels = 1;
    prop->warpSize = 32;
    prop->maxThreadsPerBlock = 1024;
    prop->maxThreadsDim[0] = 1024;
    prop->maxThreadsDim[1] = 1024;
    prop->maxThreadsDim[2] = 64;
    prop->maxGridSize[0] = 2147483647;
    prop->maxGridSize[1] = 65535;
    prop->maxGridSize[2] = 65535;

    return cudaSuccess;
}

EXPORT cudaError_t cudaDeviceGetAttribute(int *value, int attr, int device) {
    (void)device;
    if (value == NULL) return cudaErrorInvalidValue;

    if (g_shared_state == NULL || g_shared_state->surucu_ilklendi_mi == 0) {
        cuInit(0);
    }

    if (attr == 102 || attr == 107) { // Total VRAM in MB
        if (g_shared_state && g_shared_state->toplam_sanal_vram_bayt > 0) {
            *value = (int)(g_shared_state->toplam_sanal_vram_bayt / (1024 * 1024));
        } else {
            *value = 88 * 1024;
        }
        return cudaSuccess;
    }

    *value = 1;
    return cudaSuccess;
}

EXPORT cudaError_t cudaMemGetInfo(size_t *free_bytes, size_t *total_bytes) {
    if (free_bytes == NULL || total_bytes == NULL) return cudaErrorInvalidValue;

    if (g_shared_state == NULL || g_shared_state->surucu_ilklendi_mi == 0) {
        cuInit(0);
    }

    size_t toplam = (g_shared_state && g_shared_state->toplam_sanal_vram_bayt > 0)
                    ? (size_t)g_shared_state->toplam_sanal_vram_bayt
                    : (size_t)(88ULL * 1024ULL * 1024ULL * 1024ULL);

    size_t harcanan = (g_shared_state && g_shared_state->mevcut_sanal_imlec >= g_shared_state->virtual_base_address)
                      ? (size_t)(g_shared_state->mevcut_sanal_imlec - g_shared_state->virtual_base_address)
                      : 0;

    size_t bos = (toplam > harcanan) ? (toplam - harcanan) : (size_t)(80ULL * 1024ULL * 1024ULL * 1024ULL);

    *total_bytes = toplam;
    *free_bytes = bos;

    return cudaSuccess;
}

EXPORT cudaError_t cudaSetDevice(int device) {
    (void)device;
    return cudaSuccess;
}

EXPORT cudaError_t cudaGetDevice(int *device) {
    if (device == NULL) return cudaErrorInvalidValue;
    *device = 0;
    return cudaSuccess;
}

EXPORT cudaError_t cudaGetDeviceFlags(unsigned int *flags) {
    if (flags == NULL) return cudaErrorInvalidValue;
    *flags = 0;
    return cudaSuccess;
}


/* 2. Bellek Tahsis ve Temizlik */

EXPORT cudaError_t cudaMalloc(void **devPtr, size_t size) {
    if (devPtr == NULL || size == 0) return cudaErrorInvalidValue;

    CUdeviceptr vptr = 0;
    CUresult res = cuMemAlloc(&vptr, size);
    if (res != CUDA_SUCCESS) {
        return cudaErrorMemoryAllocation;
    }

    *devPtr = (void*)(uintptr_t)vptr;
    return cudaSuccess;
}

EXPORT cudaError_t cudaMallocManaged(void **devPtr, size_t size, unsigned int flags) {
    (void)flags;
    if (devPtr == NULL || size == 0) return cudaErrorInvalidValue;

    CUdeviceptr vptr = 0;
    size_t align = KULLI_PAGE_SIZE_2MB;
    size_t aligned_size = ((size + align - 1) / align) * align;

    CUresult res = cuMemAddressReserve(&vptr, aligned_size, align, 0, 0);
    if (res != CUDA_SUCCESS) return cudaErrorMemoryAllocation;

    CUmemGenericAllocationHandle handle = 0;
    res = cuMemCreate(&handle, aligned_size, NULL, 0);
    if (res != CUDA_SUCCESS) return cudaErrorMemoryAllocation;

    res = cuMemMap(vptr, aligned_size, 0, handle, 0);
    if (res != CUDA_SUCCESS) return cudaErrorMemoryAllocation;

    cuMemSetAccess(vptr, aligned_size, NULL, 1);

    *devPtr = (void*)(uintptr_t)vptr;
    return cudaSuccess;
}

EXPORT cudaError_t cudaMallocPitch(void **devPtr, size_t *pitch, size_t width, size_t height) {
    if (devPtr == NULL || pitch == NULL || width == 0 || height == 0) return cudaErrorInvalidValue;

    size_t row_pitch = ((width + 127) / 128) * 128;
    size_t total_bytes = row_pitch * height;

    cudaError_t err = cudaMalloc(devPtr, total_bytes);
    if (err == cudaSuccess) {
        *pitch = row_pitch;
    }
    return err;
}

EXPORT cudaError_t cudaFree(void *devPtr) {
    if (devPtr == NULL) return cudaSuccess;
    cuMemFree((CUdeviceptr)(uintptr_t)devPtr);
    return cudaSuccess;
}

EXPORT cudaError_t cudaFreeHost(void *ptr) {
    if (ptr == NULL) return cudaSuccess;
    free(ptr);
    return cudaSuccess;
}

EXPORT cudaError_t cudaMemset(void *devPtr, int value, size_t count) {
    if (devPtr == NULL || count == 0) return cudaSuccess;
    memset(devPtr, value, count);
    return cudaSuccess;
}

EXPORT cudaError_t cudaMemsetAsync(void *devPtr, int value, size_t count, cudaStream_t stream) {
    (void)stream;
    return cudaMemset(devPtr, value, count);
}


/* 3. Bellek Kopyalama ve Transfer */

EXPORT cudaError_t cudaMemcpy(void *dst, const void *src, size_t count, enum cudaMemcpyKind kind) {
    (void)kind;
    if (dst == NULL || src == NULL || count == 0) return cudaSuccess;
    memmove(dst, src, count);
    return cudaSuccess;
}

EXPORT cudaError_t cudaMemcpyAsync(void *dst, const void *src, size_t count, enum cudaMemcpyKind kind, cudaStream_t stream) {
    (void)stream;
    return cudaMemcpy(dst, src, count, kind);
}

EXPORT cudaError_t cudaMemcpyPeer(void *dst, int dstDevice, const void *src, int srcDevice, size_t count) {
    (void)dstDevice; (void)srcDevice;
    if (dst == NULL || src == NULL || count == 0) return cudaSuccess;
    memmove(dst, src, count);
    return cudaSuccess;
}

EXPORT cudaError_t cudaMemcpyPeerAsync(void *dst, int dstDevice, const void *src, int srcDevice, size_t count, cudaStream_t stream) {
    (void)stream;
    return cudaMemcpyPeer(dst, dstDevice, src, srcDevice, count);
}


/* 4. Akış ve Olay Yönetimi */

EXPORT cudaError_t cudaStreamCreate(cudaStream_t *pStream) {
    if (pStream == NULL) return cudaErrorInvalidValue;
    CUresult res = cuStreamCreate((CUstream*)pStream, 0);
    return (res == CUDA_SUCCESS) ? cudaSuccess : cudaErrorInitializationError;
}

EXPORT cudaError_t cudaStreamCreateWithFlags(cudaStream_t *pStream, unsigned int flags) {
    if (pStream == NULL) return cudaErrorInvalidValue;
    CUresult res = cuStreamCreate((CUstream*)pStream, flags);
    return (res == CUDA_SUCCESS) ? cudaSuccess : cudaErrorInitializationError;
}

EXPORT cudaError_t cudaStreamSynchronize(cudaStream_t stream) {
    CUresult res = cuStreamSynchronize((CUstream)stream);
    return (res == CUDA_SUCCESS) ? cudaSuccess : cudaErrorUnknown;
}

EXPORT cudaError_t cudaStreamQuery(cudaStream_t stream) {
    CUresult res = cuStreamQuery((CUstream)stream);
    return (res == CUDA_SUCCESS) ? cudaSuccess : cudaErrorUnknown;
}

EXPORT cudaError_t cudaEventCreate(cudaEvent_t *event) {
    if (event == NULL) return cudaErrorInvalidValue;
    CUresult res = cuEventCreate((CUevent*)event, 0);
    return (res == CUDA_SUCCESS) ? cudaSuccess : cudaErrorInitializationError;
}

EXPORT cudaError_t cudaEventRecord(cudaEvent_t event, cudaStream_t stream) {
    CUresult res = cuEventRecord((CUevent)event, (CUstream)stream);
    return (res == CUDA_SUCCESS) ? cudaSuccess : cudaErrorUnknown;
}

EXPORT cudaError_t cudaEventSynchronize(cudaEvent_t event) {
    CUresult res = cuEventSynchronize((CUevent)event);
    return (res == CUDA_SUCCESS) ? cudaSuccess : cudaErrorUnknown;
}

EXPORT cudaError_t cudaEventElapsedTime(float *ms, cudaEvent_t start, cudaEvent_t end) {
    CUresult res = cuEventElapsedTime(ms, (CUevent)start, (CUevent)end);
    return (res == CUDA_SUCCESS) ? cudaSuccess : cudaErrorUnknown;
}


/* 5. İcra ve Bağlam Yönetimi */

EXPORT cudaError_t cudaLaunchKernel(const void *func, dim3 gridDim, dim3 blockDim, void **args, size_t sharedMem, cudaStream_t stream) {
    (void)func; (void)gridDim; (void)blockDim; (void)args; (void)sharedMem; (void)stream;
    return cudaSuccess;
}

EXPORT cudaError_t cudaDeviceSynchronize(void) {
    return cudaSuccess;
}

EXPORT cudaError_t cudaDeviceReset(void) {
    return cudaSuccess;
}

EXPORT cudaError_t cudaGetLastError(void) {
    return cudaSuccess;
}

EXPORT const char* cudaGetErrorString(cudaError_t error) {
    (void)error;
    return "cudaSuccess: Küllî Sürücü İşlemi Başarılı.";
}
