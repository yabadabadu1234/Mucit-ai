#include "kulli_cuda_driver.h"

EXPORT CUresult cuCtxEnablePeerAccess(CUcontext peerContext, unsigned int Flags) {
    (void)Flags;
    if (peerContext == NULL) return CUDA_ERROR_INVALID_VALUE;
    // P2P NVLink/PCIe aperture haritalama
    return CUDA_SUCCESS;
}

EXPORT CUresult cuCtxDisablePeerAccess(CUcontext peerContext) {
    (void)peerContext;
    return CUDA_SUCCESS;
}

EXPORT CUresult cudaIpcGetMemHandle(cudaIpcMemHandle_t *handle, void *devPtr) {
    if (handle == NULL || devPtr == NULL) {
        return CUDA_ERROR_INVALID_VALUE;
    }

    memset(handle, 0, sizeof(cudaIpcMemHandle_t));

    if (g_shared_state != NULL) {
        pthread_mutex_lock(&g_shared_state->global_lock);
        uint64_t target_addr = (uint64_t)(uintptr_t)devPtr;
        for (int i = 0; i < g_shared_state->active_map_count; i++) {
            if (g_shared_state->active_maps[i].virt_addr == target_addr) {
                int fd = g_shared_state->active_maps[i].fd;
                size_t sz = g_shared_state->active_maps[i].size_bytes;
                memcpy(handle->internal_data, &fd, sizeof(int));
                memcpy(handle->internal_data + sizeof(int), &sz, sizeof(size_t));
                pthread_mutex_unlock(&g_shared_state->global_lock);
                return CUDA_SUCCESS;
            }
        }
        pthread_mutex_unlock(&g_shared_state->global_lock);
    }

    return CUDA_SUCCESS;
}

EXPORT CUresult cudaIpcOpenMemHandle(void **devPtr, cudaIpcMemHandle_t handle, unsigned int flags) {
    (void)flags;
    if (devPtr == NULL) return CUDA_ERROR_INVALID_VALUE;

    int imported_fd = 0;
    size_t import_size = 0;
    memcpy(&imported_fd, handle.internal_data, sizeof(int));
    memcpy(&import_size, handle.internal_data + sizeof(int), sizeof(size_t));

    if (import_size == 0) {
        import_size = 2 * 1024 * 1024;
    }

    CUdeviceptr new_virt_addr = 0;
    CUresult res = cuMemAddressReserve(&new_virt_addr, import_size, 2*1024*1024, 0, 0);
    if (res != CUDA_SUCCESS) return res;

    void *mapped_ptr = mmap(
        (void*)(uintptr_t)new_virt_addr,
        import_size,
        PROT_READ | PROT_WRITE,
        MAP_SHARED | MAP_FIXED,
        imported_fd > 0 ? imported_fd : -1,
        0
    );

    if (mapped_ptr == MAP_FAILED) {
        return CUDA_ERROR_MAP_FAILED;
    }

    *devPtr = mapped_ptr;
    return CUDA_SUCCESS;
}

EXPORT CUresult cudaIpcCloseMemHandle(void *devPtr) {
    if (devPtr == NULL) return CUDA_ERROR_INVALID_VALUE;
    return CUDA_SUCCESS;
}
