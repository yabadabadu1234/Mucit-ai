#include "kulli_cuda_driver.h"

EXPORT CUresult cuMemAddressReserve(CUdeviceptr *ptr, size_t size, size_t alignment, CUdeviceptr addr, unsigned long long flags) {
    (void)addr;
    (void)flags;
    if (ptr == NULL || size == 0) {
        return CUDA_ERROR_INVALID_VALUE;
    }

    if (g_shared_state == NULL) {
        CUresult res = cuInit(0);
        if (res != CUDA_SUCCESS) return res;
    }

    pthread_mutex_lock(&g_shared_state->global_lock);

    size_t align = alignment > 0 ? alignment : (2 * 1024 * 1024);
    size_t aligned_size = ((size + align - 1) / align) * align;

    uint64_t reserved_addr = g_shared_state->mevcut_sanal_imlec;
    g_shared_state->mevcut_sanal_imlec += aligned_size;

    pthread_mutex_unlock(&g_shared_state->global_lock);

    *ptr = (CUdeviceptr)reserved_addr;
    return CUDA_SUCCESS;
}

EXPORT CUresult cuMemCreate(CUmemGenericAllocationHandle *handle, size_t size, const void *prop, unsigned long long flags) {
    (void)prop;
    (void)flags;
    if (handle == NULL || size == 0) {
        return CUDA_ERROR_INVALID_VALUE;
    }

    if (g_shared_state == NULL) {
        CUresult res = cuInit(0);
        if (res != CUDA_SUCCESS) return res;
    }

    pthread_mutex_lock(&g_shared_state->global_lock);

    if (g_shared_state->handle_count >= MAX_HANDLES) {
        pthread_mutex_unlock(&g_shared_state->global_lock);
        return CUDA_ERROR_OUT_OF_MEMORY;
    }

    int h_idx = g_shared_state->handle_count++;
    char shm_name[64];
    snprintf(shm_name, sizeof(shm_name), "/kulli_vmm_alloc_%d", h_idx);

    int fd = shm_open(shm_name, O_CREAT | O_RDWR, 0666);
    if (fd < 0) {
        pthread_mutex_unlock(&g_shared_state->global_lock);
        return CUDA_ERROR_OUT_OF_MEMORY;
    }

    if (ftruncate(fd, (off_t)size) != 0) {
        close(fd);
        pthread_mutex_unlock(&g_shared_state->global_lock);
        return CUDA_ERROR_OUT_OF_MEMORY;
    }

    g_shared_state->handle_table[h_idx].handle_id = h_idx + 1;
    g_shared_state->handle_table[h_idx].fd = fd;
    g_shared_state->handle_table[h_idx].gpu_id = 0;
    g_shared_state->handle_table[h_idx].size_bytes = size;

    *handle = (CUmemGenericAllocationHandle)(uint64_t)(h_idx + 1);

    pthread_mutex_unlock(&g_shared_state->global_lock);
    return CUDA_SUCCESS;
}

EXPORT CUresult cuMemMap(CUdeviceptr ptr, size_t size, size_t offset, CUmemGenericAllocationHandle handle, unsigned long long flags) {
    (void)flags;
    if (ptr == 0 || size == 0 || handle == 0) {
        return CUDA_ERROR_INVALID_VALUE;
    }

    if (g_shared_state == NULL) return CUDA_ERROR_NOT_INITIALIZED;

    pthread_mutex_lock(&g_shared_state->global_lock);

    int h_id = (int)handle - 1;
    if (h_id < 0 || h_id >= g_shared_state->handle_count) {
        pthread_mutex_unlock(&g_shared_state->global_lock);
        return CUDA_ERROR_INVALID_VALUE;
    }

    int fd = g_shared_state->handle_table[h_id].fd;

    void *mapped_ptr = mmap(
        (void*)(uintptr_t)ptr,
        size,
        PROT_READ | PROT_WRITE,
        MAP_SHARED | MAP_FIXED,
        fd,
        (off_t)offset
    );

    if (mapped_ptr == MAP_FAILED) {
        pthread_mutex_unlock(&g_shared_state->global_lock);
        return CUDA_ERROR_MAP_FAILED;
    }

    if (g_shared_state->active_map_count < MAX_MAPS) {
        int idx = g_shared_state->active_map_count++;
        g_shared_state->active_maps[idx].virt_addr = (uint64_t)ptr;
        g_shared_state->active_maps[idx].size_bytes = size;
        g_shared_state->active_maps[idx].gpu_id = 0;
        g_shared_state->active_maps[idx].mapped_ptr = mapped_ptr;
        g_shared_state->active_maps[idx].fd = fd;
    }

    pthread_mutex_unlock(&g_shared_state->global_lock);
    return CUDA_SUCCESS;
}

EXPORT CUresult cuMemSetAccess(CUdeviceptr ptr, size_t size, const void *desc, size_t count) {
    (void)ptr;
    (void)size;
    (void)desc;
    (void)count;
    return CUDA_SUCCESS;
}

EXPORT CUresult cuMemUnmap(CUdeviceptr ptr, size_t size) {
    if (ptr == 0 || size == 0) return CUDA_ERROR_INVALID_VALUE;
    munmap((void*)(uintptr_t)ptr, size);
    return CUDA_SUCCESS;
}

EXPORT CUresult cuMemRelease(CUmemGenericAllocationHandle handle) {
    (void)handle;
    return CUDA_SUCCESS;
}

EXPORT CUresult cuMemAlloc(CUdeviceptr *dptr, size_t bytesize) {
    if (dptr == NULL || bytesize == 0) return CUDA_ERROR_INVALID_VALUE;

    CUdeviceptr vptr = 0;
    CUresult res = cuMemAddressReserve(&vptr, bytesize, 2*1024*1024, 0, 0);
    if (res != CUDA_SUCCESS) return res;

    CUmemGenericAllocationHandle handle = 0;
    res = cuMemCreate(&handle, bytesize, NULL, 0);
    if (res != CUDA_SUCCESS) return res;

    res = cuMemMap(vptr, bytesize, 0, handle, 0);
    if (res != CUDA_SUCCESS) return res;

    cuMemSetAccess(vptr, bytesize, NULL, 1);
    *dptr = vptr;
    return CUDA_SUCCESS;
}

EXPORT CUresult cuMemAddressFree_v2(CUdeviceptr ptr, size_t size) {
    (void)ptr;
    (void)size;
    return CUDA_SUCCESS;
}

EXPORT CUresult cuMemAddressFree(CUdeviceptr ptr, size_t size) {
    return cuMemAddressFree_v2(ptr, size);
}

EXPORT CUresult cuMemFree(CUdeviceptr dptr) {
    if (dptr == 0) return CUDA_SUCCESS;
    // unmap
    return CUDA_SUCCESS;
}
