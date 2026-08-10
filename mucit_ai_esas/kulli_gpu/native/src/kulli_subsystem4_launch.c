#include "kulli_cuda_driver.h"

EXPORT CUresult cuModuleLoad(CUmodule *module, const char *fname) {
    (void)fname;
    if (module == NULL) return CUDA_ERROR_INVALID_VALUE;
    KulliModule *mod = (KulliModule*)calloc(1, sizeof(KulliModule));
    if (mod == NULL) return CUDA_ERROR_OUT_OF_MEMORY;
    mod->module_id = GetSystemTimeNanoseconds();
    *module = (CUmodule)mod;
    return CUDA_SUCCESS;
}

EXPORT CUresult cuModuleLoadData(CUmodule *module, const void *image) {
    (void)image;
    return cuModuleLoad(module, "memory_image");
}

EXPORT CUresult cuModuleGetFunction(CUfunction *hfunc, CUmodule hmod, const char *name) {
    (void)name;
    if (hfunc == NULL || hmod == NULL) return CUDA_ERROR_INVALID_VALUE;
    KulliFunction *func = (KulliFunction*)calloc(1, sizeof(KulliFunction));
    if (func == NULL) return CUDA_ERROR_OUT_OF_MEMORY;
    func->func_id = GetSystemTimeNanoseconds();
    func->module = (KulliModule*)hmod;
    *hfunc = (CUfunction)func;
    return CUDA_SUCCESS;
}

EXPORT CUresult cuModuleUnload(CUmodule hmod) {
    if (hmod == NULL) return CUDA_ERROR_INVALID_VALUE;
    free(hmod);
    return CUDA_SUCCESS;
}

void PushToRingBuffer(CUstream hStream, const KulliCommandPacket *pkt) {
    if (hStream == NULL || pkt == NULL) return;
    KulliStream *st = (KulliStream*)hStream;

    uint32_t tail = atomic_load(&st->ring_tail);
    uint32_t next_tail = (tail + 1) % RING_BUFFER_SIZE;

    // Ring-buffer komutunu yerleştir
    st->ring_buffer[tail] = *pkt;
    atomic_store(&st->ring_tail, next_tail);

    // Bitiş similasyonu: Sürücü iş parçacığı anında işler
    atomic_store(&st->ring_head, next_tail);
}

EXPORT CUresult cuLaunchKernel(CUfunction f, unsigned int gridDimX, unsigned int gridDimY, unsigned int gridDimZ,
                               unsigned int blockDimX, unsigned int blockDimY, unsigned int blockDimZ,
                               unsigned int sharedMemBytes, CUstream hStream, void **kernelParams, void **extra) {
    (void)extra;
    if (f == NULL) return CUDA_ERROR_INVALID_VALUE;

    KulliCommandPacket pkt;
    memset(&pkt, 0, sizeof(pkt));
    pkt.cmd_type = CMD_LAUNCH_KERNEL;
    pkt.func_ptr = (uint64_t)(uintptr_t)f;
    pkt.grid_dim.x = gridDimX;
    pkt.grid_dim.y = gridDimY;
    pkt.grid_dim.z = gridDimZ;
    pkt.block_dim.x = blockDimX;
    pkt.block_dim.y = blockDimY;
    pkt.block_dim.z = blockDimZ;
    pkt.shared_mem_bytes = sharedMemBytes;

    if (kernelParams != NULL) {
        for (int i = 0; i < 16 && kernelParams[i] != NULL; i++) {
            pkt.args_buffer[i] = (uint64_t)(uintptr_t)*(void**)kernelParams[i];
        }
    }

    PushToRingBuffer(hStream, &pkt);
    return CUDA_SUCCESS;
}
