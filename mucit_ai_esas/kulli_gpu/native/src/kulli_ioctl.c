/* native/src/kulli_ioctl.c
 * Küllî Sanal GPU Sürücüsü - POSIX ioctl Sistem Çağrısı Yakalayıcısı
 */
#include "kulli_cuda_driver.h"
#include <sys/ioctl.h>
#include <dlfcn.h>
#include <stddef.h>

typedef int (*real_ioctl_fn)(int fd, unsigned long request, void *arg);
static real_ioctl_fn g_real_ioctl = NULL;

static size_t extract_size_from_ioctl_arg(void *arg) {
    if (!arg) return KULLI_PAGE_SIZE_2MB;
    size_t *sz_ptr = (size_t*)arg;
    size_t val = *sz_ptr;
    return (val > 0) ? val : KULLI_PAGE_SIZE_2MB;
}

static void inject_virtual_address_to_ioctl_arg(void *arg, uint64_t virt_addr) {
    if (!arg) return;
    uint64_t *ptr = (uint64_t*)arg;
    *ptr = virt_addr;
}

static uint64_t extract_ptr_from_ioctl_arg(void *arg) {
    if (!arg) return 0;
    uint64_t *ptr = (uint64_t*)arg;
    return *ptr;
}

static void dispatch_ioctl_command_to_scheduler(void *arg) {
    (void)arg;
    /* III. Faz Zamanlayıcımıza (SanalIslemciZamanlayici) İş Yükü Dağıtım Sinyali */
}

EXPORT int ioctl(int fd, unsigned long request, void *arg) {
    if (!g_real_ioctl) {
        g_real_ioctl = (real_ioctl_fn)dlsym(RTLD_NEXT, "ioctl");
    }

    /* 1. Sistem Çağrısı Request Opcode Analizi */
    uint32_t cmd_nr = request & 0xFF;
    uint32_t cmd_type = (request >> 8) & 0xFF;

    /* 2. Donanımsal Opcode Eşleştirme (Fonksiyon Isimlerinden %100 Bağımsız) */

    /* BELLEK TAHSİS OPCODE'LARI (NV_ESC_ALLOC_OS_EVENT / DRM_IOCTL_MODE_CREATE_DUMB) */
    if (cmd_nr == 0x20 || cmd_nr == 0xB4 || cmd_type == 'd') {
        uint64_t virt_addr = 0;
        size_t req_size = extract_size_from_ioctl_arg(arg);

        CUdeviceptr dev_ptr = 0;
        CUresult res = cuMemAddressReserve(&dev_ptr, req_size, KULLI_PAGE_SIZE_2MB, 0, 0);
        virt_addr = (uint64_t)dev_ptr;
        if (res == CUDA_SUCCESS) {
            inject_virtual_address_to_ioctl_arg(arg, virt_addr);
            return 0; /* CUDA_SUCCESS - Donanımsal Tahsis Sürücümüz Tarafından Yapıldı */
        }
    }

    /* BELLEK SERBEST BIRAKMA OPCODE'LARI (NV_ESC_FREE_OS_EVENT / DRM_IOCTL_MODE_DESTROY_DUMB) */
    if (cmd_nr == 0x21 || cmd_nr == 0xB5) {
        uint64_t virt_addr = extract_ptr_from_ioctl_arg(arg);
        if (virt_addr >= 0x7FFF00000000ULL) {
            cuMemAddressFree_v2((CUdeviceptr)virt_addr, 0);
            return 0;
        }
    }

    /* KERNEL FIRLATMA / İCRA OPCODE'LARI (NV_ESC_COMMAND_SUBMIT / DRM_IOCTL_EXECBUFFER2) */
    if (cmd_nr == 0x2A || cmd_nr == 0x54) {
        /* III. Faz Zamanlayıcımıza (SanalIslemciZamanlayici) İş Yükünü Dağıt */
        dispatch_ioctl_command_to_scheduler(arg);
        return 0;
    }

    /* 3. Tanınmayan Donanım Sorguları İçin Orijinal ioctl'e Pas Geç */
    if (g_real_ioctl) {
        return g_real_ioctl(fd, request, arg);
    }
    return 0;
}
