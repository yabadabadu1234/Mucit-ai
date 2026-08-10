/* native/src/kulli_cuda_driver.c
 * Küllî Sanal GPU SÜRÜCÜSÜ - Karakter Aygıtı Kapıları ve UMD ioctl Katmanı
 */

#include "kulli_cuda_driver.h"

int g_gpu_fds[KULLI_MAX_PHYSICAL_GPUS] = {-1};
int g_nvidiactl_fd = -1;

/* Karakter Aygıtı Kapılarını Açan Hakiki C-Fonksiyonu (/dev/nvidiactl & /dev/nvidia0..N) */
EXPORT int KulliOpenCharacterDevices(void) {
    /* 1. Ana Kontrol Aygıtını Aç (/dev/nvidiactl) */
    g_nvidiactl_fd = open("/dev/nvidiactl", O_RDWR | O_CLOEXEC);
    if (g_nvidiactl_fd < 0) {
        g_nvidiactl_fd = open("/dev/dri/card0", O_RDWR | O_CLOEXEC);
    }

    /* 2. Her bir Fiziki GPU Karakter Aygıtını Aç (/dev/nvidia0 .. N) */
    for (int i = 0; i < KULLI_MAX_PHYSICAL_GPUS; i++) {
        char dev_path[64];
        snprintf(dev_path, sizeof(dev_path), "/dev/nvidia%d", i);
        g_gpu_fds[i] = open(dev_path, O_RDWR | O_CLOEXEC);
        if (g_gpu_fds[i] < 0) {
            snprintf(dev_path, sizeof(dev_path), "/dev/dri/renderD%d", 128 + i);
            g_gpu_fds[i] = open(dev_path, O_RDWR | O_CLOEXEC);
        }
    }
    return 0;
}
