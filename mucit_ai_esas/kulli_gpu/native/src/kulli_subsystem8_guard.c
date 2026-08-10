#include "kulli_cuda_driver.h"
#include <stdarg.h>

EXPORT CUresult cuGetErrorString(CUresult error, const char **pStr) {
    if (pStr == NULL) return CUDA_ERROR_INVALID_VALUE;

    switch (error) {
        case CUDA_SUCCESS:
            *pStr = "CUDA_SUCCESS: Küllî Sürücü İşlemi Başarılı.";
            break;
        case CUDA_ERROR_INVALID_VALUE:
            *pStr = "CUDA_ERROR_INVALID_VALUE: Geçersiz C-API Parametresi.";
            break;
        case CUDA_ERROR_OUT_OF_MEMORY:
            *pStr = "CUDA_ERROR_OUT_OF_MEMORY: Küllî Sanal VRAM Havuzu Doldu!";
            break;
        case CUDA_ERROR_MAP_FAILED:
            *pStr = "CUDA_ERROR_MAP_FAILED: POSIX mmap Haritalama Başarısız Oldu.";
            break;
        case CUDA_ERROR_ILLEGAL_ADDRESS:
            *pStr = "CUDA_ERROR_ILLEGAL_ADDRESS: GÜVENLİK İHLALİ! Guard Page veya Sınır Dışı Sanal Adrese Temas Edildi!";
            break;
        case CUDA_ERROR_LAUNCH_TIMEOUT:
            *pStr = "CUDA_ERROR_LAUNCH_TIMEOUT: GPU Donanımsal Çit Zaman Aşıldı (Hang).";
            break;
        default:
            *pStr = "CUDA_ERROR_UNKNOWN: Bilinmeyen Küllî Sürücü Hatası.";
            break;
    }
    return CUDA_SUCCESS;
}

EXPORT CUresult cuGetErrorName(CUresult error, const char **pStr) {
    if (pStr == NULL) return CUDA_ERROR_INVALID_VALUE;

    switch (error) {
        case CUDA_SUCCESS: *pStr = "CUDA_SUCCESS"; break;
        case CUDA_ERROR_INVALID_VALUE: *pStr = "CUDA_ERROR_INVALID_VALUE"; break;
        case CUDA_ERROR_OUT_OF_MEMORY: *pStr = "CUDA_ERROR_OUT_OF_MEMORY"; break;
        case CUDA_ERROR_MAP_FAILED: *pStr = "CUDA_ERROR_MAP_FAILED"; break;
        case CUDA_ERROR_ILLEGAL_ADDRESS: *pStr = "CUDA_ERROR_ILLEGAL_ADDRESS"; break;
        case CUDA_ERROR_LAUNCH_TIMEOUT: *pStr = "CUDA_ERROR_LAUNCH_TIMEOUT"; break;
        default: *pStr = "CUDA_ERROR_UNKNOWN"; break;
    }
    return CUDA_SUCCESS;
}

CUresult KulliBoundaryGuardCheck(uint64_t virt_ptr, size_t size_bytes) {
    if (g_shared_state == NULL) return CUDA_SUCCESS;

    uint64_t end_ptr = virt_ptr + size_bytes;
    uint64_t base_addr = g_shared_state->virtual_base_address;
    uint64_t guard_addr = g_shared_state->guard_page_address;

    if (virt_ptr < base_addr) {
        return CUDA_ERROR_INVALID_VALUE;
    }

    if (end_ptr > guard_addr) {
        LogDriverError("GÜVENLİK İHLALİ! Adres Koruma Sayfasına Dokundu: 0x%llx", (unsigned long long)virt_ptr);
        return CUDA_ERROR_ILLEGAL_ADDRESS;
    }

    return CUDA_SUCCESS;
}

void LogDriverError(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    fprintf(stderr, "[KULLI DRIVER ERROR] ");
    vfprintf(stderr, fmt, args);
    fprintf(stderr, "\n");
    va_end(args);
}
