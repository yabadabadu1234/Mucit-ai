#include "kulli_cuda_driver.h"

int KulliShmControlInit(void) {
    int shm_fd = shm_open("/kulli_driver_shm", O_CREAT | O_RDWR, 0666);
    if (shm_fd < 0) {
        return -1;
    }

    if (ftruncate(shm_fd, sizeof(KulliDriverSharedState)) != 0) {
        close(shm_fd);
        return -1;
    }

    g_shared_state = (KulliDriverSharedState*)mmap(
        NULL,
        sizeof(KulliDriverSharedState),
        PROT_READ | PROT_WRITE,
        MAP_SHARED,
        shm_fd,
        0
    );

    if (g_shared_state == MAP_FAILED) {
        close(shm_fd);
        g_shared_state = NULL;
        return -1;
    }

    /* Pshared Mutex ilklendirmeleri */
    pthread_mutexattr_t attr;
    pthread_mutexattr_init(&attr);
    pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
    pthread_mutex_init(&g_shared_state->global_lock, &attr);

    for (int i = 0; i < MAX_GPUS; i++) {
        pthread_mutex_init(&g_shared_state->gpu_locks[i], &attr);
    }
    pthread_mutexattr_destroy(&attr);

    g_shared_state->virtual_base_address = 0x7FFF00000000ULL;
    g_shared_state->toplam_sanal_vram_bayt = 88ULL * 1024ULL * 1024ULL * 1024ULL;
    g_shared_state->guard_page_address = g_shared_state->virtual_base_address + g_shared_state->toplam_sanal_vram_bayt;
    if (g_shared_state->mevcut_sanal_imlec == 0) {
        g_shared_state->mevcut_sanal_imlec = g_shared_state->virtual_base_address;
    }

    return 0;
}

int KulliUnixSocketSendFd(int socket_fd, int fd_to_send) {
    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));
    char buf[CMSG_SPACE(sizeof(int))];
    memset(buf, 0, sizeof(buf));

    struct iovec io;
    char dummy = 'A';
    io.iov_base = &dummy;
    io.iov_len = 1;

    msg.msg_iov = &io;
    msg.msg_iovlen = 1;
    msg.msg_control = buf;
    msg.msg_controllen = sizeof(buf);

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));

    memcpy(CMSG_DATA(cmsg), &fd_to_send, sizeof(int));

    if (sendmsg(socket_fd, &msg, 0) < 0) {
        return -1;
    }
    return 0;
}

int KulliUnixSocketRecvFd(int socket_fd) {
    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));
    char buf[CMSG_SPACE(sizeof(int))];

    struct iovec io;
    char dummy;
    io.iov_base = &dummy;
    io.iov_len = 1;

    msg.msg_iov = &io;
    msg.msg_iovlen = 1;
    msg.msg_control = buf;
    msg.msg_controllen = sizeof(buf);

    if (recvmsg(socket_fd, &msg, 0) < 0) {
        return -1;
    }

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    if (cmsg == NULL || cmsg->cmsg_type != SCM_RIGHTS) {
        return -1;
    }

    int received_fd = -1;
    memcpy(&received_fd, CMSG_DATA(cmsg), sizeof(int));
    return received_fd;
}
