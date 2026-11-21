CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -Werror -Wshadow -g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer -Iinclude -Itest
KAYNAK = $(wildcard src/*.c)
TESTLER = test_gt911 test_avuc test_sdspi test_msc test_guc test_sayfa_pdf test_ltdc_usb
ARM = arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -Os -ffunction-sections -fdata-sections -std=c11 -Wall -Wextra -Werror -Iinclude

.PHONY: test hedef temizle

test: $(addprefix build/,$(TESTLER)) build/test.jpg
	@set -e; for t in $(TESTLER); do echo "== $$t"; if [ $$t = test_sayfa_pdf ]; then ./build/$$t build/test.jpg build/cikti.pdf; else ./build/$$t; fi; done
	@python3 test/pdf_dogrula.py build/cikti.pdf build/test.jpg

build/test.jpg:
	@mkdir -p build
	@convert -size 64x48 gradient:red-blue build/test.jpg

build/%: test/%.c $(KAYNAK) $(wildcard include/*.h) $(wildcard test/*.h)
	@mkdir -p build
	@$(CC) $(CFLAGS) $< $(KAYNAK) -o $@

hedef:
	@mkdir -p build/arm
	@for k in $(KAYNAK); do $(ARM) -c $$k -o build/arm/$$(basename $$k .c).o; done
	@arm-none-eabi-size build/arm/*.o

temizle:
	rm -rf build
