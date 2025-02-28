builddir=build
bin=$(builddir)/translated
pysrc=translate.py
asmsrc=$(bin).asm
obj=$(bin).o

asmarch=elf64
ldarch=elf_x86_64

asm=nasm
ld=ld

.PHONY: run clean

$(bin): $(obj)
	$(ld) -m $(ldarch) $< -o $@

$(obj): $(asmsrc) $(builddir)
	$(asm) -f $(asmarch) $< -o $@

$(asmsrc): $(pysrc) $(builddir)
	python $< > $@

$(builddir):
	mkdir $(builddir)

run: $(bin)
	@echo
	@./$(bin)

clean:
	rm $(asmsrc) $(obj) $(bin)
	rmdir $(builddir)

# vim: et!
