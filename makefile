N        = 01
INPUT    = $(wildcard examples/$(N)*.ma)

builddir = build
bin      = $(builddir)/translated
pysrc    = src/main.py
asmsrc   = $(bin).asm
obj      = $(bin).o

asmarch  = elf64
ldarch   = elf_x86_64

asm      = nasm
ld       = ld

.PHONY: run clean

$(bin): $(obj)
	@$(ld) -m $(ldarch) $< -o $@

$(obj): $(asmsrc) $(builddir)
	@$(asm) -f $(asmarch) $< -o $@

$(asmsrc): $(pysrc) $(builddir) $(INPUT)
	@python $< $(INPUT) $@

$(builddir):
	@mkdir $(builddir)

run: $(bin)
	@echo
	@./$(bin)

clean:
	@rm $(asmsrc) $(obj) $(bin)
	@rmdir $(builddir)

# vim: et!
