#include "kulli_cuda_driver.h"

KulliDriverSharedState *g_shared_state = NULL;
static pthread_mutex_t g_init_lock = PTHREAD_MUTEX_INITIALIZER;

EXPORT CUresult cuInit(unsigned int Flags) {
    (void)Flags;
    pthread_mutex_lock(&g_init_lock);
    
    if (g_shared_state != NULL && g_shared_state->surucu_ilklendi_mi == 1) {
        pthread_mutex_unlock(&g_init_lock);
        return CUDA_SUCCESS;
    }

    if (KulliShmControlInit() != 0) {
        pthread_mutex_unlock(&g_init_lock);
        return CUDA_ERROR_UNKNOWN;
    }

    g_shared_state->surucu_ilklendi_mi = 1;
    pthread_mutex_unlock(&g_init_lock);
    return CUDA_SUCCESS;
}

EXPORT CUresult cuDeviceGetCount(int *count) {
    if (count == NULL) {
        return CUDA_ERROR_INVALID_VALUE;
    }
    
    if (g_shared_state == NULL || g_shared_state->surucu_ilklendi_mi == 0) {
        CUresult res = cuInit(0);
        if (res != CUDA_SUCCESS) {
            return res;
        }
    }

    /* Küllî Sanal GPU Havuzu aktif olduğunda PyTorch'a 1 birleşik sanal GPU sunulur */
    *count = 1;
    return CUDA_SUCCESS;
}

EXPORT CUresult cuDeviceTotalMem_v2(size_t *bytes, CUdevice dev) {
    (void)dev;
    if (bytes == NULL) {
        return CUDA_ERROR_INVALID_VALUE;
    }

    if (g_shared_state == NULL || g_shared_state->surucu_ilklendi_mi == 0) {
        CUresult res = cuInit(0);
        if (res != CUDA_SUCCESS) {
            return res;
        }
    }

    if (g_shared_state && g_shared_state->toplam_sanal_vram_bayt > 0) {
        *bytes = (size_t)g_shared_state->toplam_sanal_vram_bayt;
    } else {
        *bytes = (size_t)(88ULL * 1024ULL * 1024ULL * 1024ULL);
    }
    return CUDA_SUCCESS;
}

EXPORT CUresult cuDeviceTotalMem(size_t *bytes, CUdevice dev) {
    return cuDeviceTotalMem_v2(bytes, dev);
}

EXPORT CUresult cuDeviceGet(CUdevice *device, int ordinal) {
    if (device == NULL || ordinal < 0) {
        return CUDA_ERROR_INVALID_VALUE;
    }
    *device = 0; // Sanal GPU cihaz ordinal 0
    return CUDA_SUCCESS;
}

EXPORT CUresult cuDeviceGetName(char *name, int len, CUdevice dev) {
    (void)dev;
    if (name == NULL || len <= 0) {
        return CUDA_ERROR_INVALID_VALUE;
    }
    snprintf(name, (size_t)len, "Kulli Unified Virtual GPU (88GB Pure VRAM)");
    return CUDA_SUCCESS;
}

EXPORT CUresult cuDeviceGetAttribute(int *pi, int attrib, CUdevice dev) {
    (void)dev;
    if (pi == NULL) {
        return CUDA_ERROR_INVALID_VALUE;
    }
    
    // PyTorch C++ Runtime Total Memory sorgusu (Attribute 102 veya 107)
    if (attrib == 102 || attrib == 107) {
        if (g_shared_state && g_shared_state->toplam_sanal_vram_bayt > 0) {
            *pi = (int)(g_shared_state->toplam_sanal_vram_bayt / (1024 * 1024));
        } else {
            *pi = 88 * 1024; // 88192 MB Fallback
        }
        return CUDA_SUCCESS;
    }

    // Standart CUDA Nitelikleri Mock / Maskeleme
    switch (attrib) {
        case 1: // CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK
            *pi = 1024;
            break;
        case 2: // CU_DEVICE_ATTRIBUTE_MAX_BLOCK_DIM_X
            *pi = 1024;
            break;
        case 5: // CU_DEVICE_ATTRIBUTE_WARP_SIZE
            *pi = 32;
            break;
        case 16: // CU_DEVICE_ATTRIBUTE_CONCURRENT_KERNELS
            *pi = 1;
            break;
        case 75: // CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR
            *pi = 8; // Ampere / Hopper mimarisi
            break;
        case 76: // CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR
            *pi = 6;
            break;
        case 85: // CU_DEVICE_ATTRIBUTE_UNIFIED_ADDRESSING
            *pi = 1;
            break;
        default:
            *pi = 1;
            break;
    }
    return CUDA_SUCCESS;
}
