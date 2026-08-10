CC = gcc
CFLAGS = -Wall -Wextra -O3 -fPIC -Iinclude -pthread -D_GNU_SOURCE
LDFLAGS = -shared -pthread -lrt -ldl

SRCS = src/kulli_cuda_driver.c \
       src/kulli_subsystem1_hardware.c \
       src/kulli_subsystem2_vmm.c \
       src/kulli_subsystem3_context.c \
       src/kulli_subsystem4_launch.c \
       src/kulli_subsystem5_p2p_ipc.c \
       src/kulli_subsystem6_posix_ipc.c \
       src/kulli_subsystem7_events.c \
       src/kulli_subsystem8_guard.c \
       src/kulli_subsystem9_runtime.c \
       src/kulli_ioctl.c

OBJS = $(SRCS:.c=.o)
TARGET_SO = libkulli_cuda.so.1

all: $(TARGET_SO)

$(TARGET_SO): $(OBJS)
	$(CC) $(LDFLAGS) -Wl,-soname,$(TARGET_SO) -o $@ $(OBJS)
	ln -sf $(TARGET_SO) libcuda.so.1
	ln -sf $(TARGET_SO) libcuda.so
	ln -sf $(TARGET_SO) libcudart.so.12
	ln -sf $(TARGET_SO) libcudart.so

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET_SO) libcuda.so.1 libcuda.so libcudart.so.12 libcudart.so

.PHONY: all clean
