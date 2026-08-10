#include "kulli_cuda_driver.h"

static __thread KulliContext *g_tls_current_context = NULL;

EXPORT CUresult cuCtxCreate_v2(CUcontext *pctx, unsigned int flags, CUdevice dev) {
    if (pctx == NULL) {
        return CUDA_ERROR_INVALID_VALUE;
    }

    if (g_shared_state == NULL) {
        CUresult res = cuInit(0);
        if (res != CUDA_SUCCESS) return res;
    }

    KulliContext *ctx = (KulliContext*)calloc(1, sizeof(KulliContext));
    if (ctx == NULL) return CUDA_ERROR_OUT_OF_MEMORY;

    ctx->ctx_id = (uint32_t)(atomic_fetch_add(&g_shared_state->ctx_counter, 1) + 1);
    ctx->primary_gpu_id = (int)dev;
    ctx->flags = flags;

    g_tls_current_context = ctx;
    *pctx = (CUcontext)ctx;
    return CUDA_SUCCESS;
}

EXPORT CUresult cuCtxCreate(CUcontext *pctx, unsigned int flags, CUdevice dev) {
    return cuCtxCreate_v2(pctx, flags, dev);
}

EXPORT CUresult cuCtxDestroy(CUcontext ctx) {
    if (ctx == NULL) return CUDA_ERROR_INVALID_VALUE;
    if (g_tls_current_context == (KulliContext*)ctx) {
        g_tls_current_context = NULL;
    }
    free(ctx);
    return CUDA_SUCCESS;
}

EXPORT CUresult cuCtxGetCurrent(CUcontext *pctx) {
    if (pctx == NULL) return CUDA_ERROR_INVALID_VALUE;
    *pctx = (CUcontext)g_tls_current_context;
    return CUDA_SUCCESS;
}

EXPORT CUresult cuCtxSetCurrent(CUcontext ctx) {
    g_tls_current_context = (KulliContext*)ctx;
    return CUDA_SUCCESS;
}

EXPORT CUresult cuStreamCreate(CUstream *phStream, unsigned int Flags) {
    (void)Flags;
    if (phStream == NULL) return CUDA_ERROR_INVALID_VALUE;

    KulliStream *st = (KulliStream*)calloc(1, sizeof(KulliStream));
    if (st == NULL) return CUDA_ERROR_OUT_OF_MEMORY;

    st->stream_id = GetSystemTimeNanoseconds();
    st->ctx = g_tls_current_context;
    st->fence_register = 0;
    atomic_store(&st->ring_head, 0);
    atomic_store(&st->ring_tail, 0);

    *phStream = (CUstream)st;
    return CUDA_SUCCESS;
}

EXPORT CUresult cuStreamDestroy(CUstream hStream) {
    if (hStream == NULL) return CUDA_ERROR_INVALID_VALUE;
    free(hStream);
    return CUDA_SUCCESS;
}

EXPORT CUresult cuStreamSynchronize(CUstream hStream) {
    if (hStream == NULL) {
        return CUDA_SUCCESS;
    }

    KulliStream *st = (KulliStream*)hStream;
    uint64_t start = GetSystemTimeMilliseconds();

    /* Donanımsal polling döngüsü: Ring buffer tamamen boşalana kadar bekle */
    while (atomic_load(&st->ring_head) != atomic_load(&st->ring_tail)) {
        __builtin_ia32_pause();
        if ((GetSystemTimeMilliseconds() - start) > 5000) {
            return CUDA_ERROR_LAUNCH_TIMEOUT;
        }
    }

    return CUDA_SUCCESS;
}

EXPORT CUresult cuStreamQuery(CUstream hStream) {
    if (hStream == NULL) return CUDA_SUCCESS;
    KulliStream *st = (KulliStream*)hStream;
    if (atomic_load(&st->ring_head) == atomic_load(&st->ring_tail)) {
        return CUDA_SUCCESS;
    }
    return CUDA_ERROR_LAUNCH_TIMEOUT;
}
