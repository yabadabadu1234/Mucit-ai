#include "kulli_cuda_driver.h"

EXPORT CUresult cuEventCreate(CUevent *phEvent, unsigned int Flags) {
    if (phEvent == NULL) return CUDA_ERROR_INVALID_VALUE;

    if (g_shared_state == NULL) {
        CUresult res = cuInit(0);
        if (res != CUDA_SUCCESS) return res;
    }

    KulliEvent *evt = (KulliEvent*)calloc(1, sizeof(KulliEvent));
    if (evt == NULL) return CUDA_ERROR_OUT_OF_MEMORY;

    evt->event_id = atomic_fetch_add(&g_shared_state->event_counter, 1) + 1;
    evt->flags = Flags;
    evt->is_recorded = false;

    *phEvent = (CUevent)evt;
    return CUDA_SUCCESS;
}

EXPORT CUresult cuEventDestroy_v2(CUevent hEvent) {
    if (hEvent == NULL) return CUDA_ERROR_INVALID_VALUE;
    free(hEvent);
    return CUDA_SUCCESS;
}

EXPORT CUresult cuEventDestroy(CUevent hEvent) {
    return cuEventDestroy_v2(hEvent);
}

EXPORT CUresult cuEventRecord(CUevent hEvent, CUstream hStream) {
    if (hEvent == NULL) return CUDA_ERROR_INVALID_VALUE;
    KulliEvent *evt = (KulliEvent*)hEvent;

    uint64_t token = atomic_fetch_add(&g_shared_state->fence_token_counter, 1) + 1;

    KulliCommandPacket pkt;
    memset(&pkt, 0, sizeof(pkt));
    pkt.cmd_type = CMD_WRITE_FENCE_MARKER;
    pkt.fence_address = (uint64_t)(uintptr_t)&evt->completion_token;
    pkt.fence_value = token;

    PushToRingBuffer(hStream, &pkt);

    evt->recorded_token = token;
    evt->completion_token = token; // Anında tamamlandı kabul edilir
    evt->record_timestamp_ns = GetSystemTimeNanoseconds();
    evt->is_recorded = true;

    return CUDA_SUCCESS;
}

EXPORT CUresult cuEventSynchronize(CUevent hEvent) {
    if (hEvent == NULL) return CUDA_ERROR_INVALID_VALUE;
    KulliEvent *evt = (KulliEvent*)hEvent;
    if (!evt->is_recorded) return CUDA_SUCCESS;

    uint64_t start = GetSystemTimeMilliseconds();
    while (evt->completion_token != evt->recorded_token) {
        __builtin_ia32_pause();
        if ((GetSystemTimeMilliseconds() - start) > 5000) {
            return CUDA_ERROR_LAUNCH_TIMEOUT;
        }
    }

    return CUDA_SUCCESS;
}

EXPORT CUresult cuEventQuery(CUevent hEvent) {
    if (hEvent == NULL) return CUDA_SUCCESS;
    KulliEvent *evt = (KulliEvent*)hEvent;
    if (!evt->is_recorded || evt->completion_token == evt->recorded_token) {
        return CUDA_SUCCESS;
    }
    return CUDA_ERROR_LAUNCH_TIMEOUT;
}

EXPORT CUresult cuEventElapsedTime(float *pMilliseconds, CUevent hStart, CUevent hEnd) {
    if (pMilliseconds == NULL || hStart == NULL || hEnd == NULL) {
        return CUDA_ERROR_INVALID_VALUE;
    }

    KulliEvent *start_evt = (KulliEvent*)hStart;
    KulliEvent *end_evt = (KulliEvent*)hEnd;

    if (!start_evt->is_recorded || !end_evt->is_recorded) {
        return CUDA_ERROR_INVALID_VALUE;
    }

    uint64_t diff_ns = end_evt->record_timestamp_ns - start_evt->record_timestamp_ns;
    *pMilliseconds = (float)diff_ns / 1000000.0f;
    return CUDA_SUCCESS;
}
