static b0 = '0',0xa,0;
static ba = 'a',0xa,0;

label square:
	imul    eax, eax;
	ret;

label main:
	rax <- 5;
	call square;

	mov rsi, QWORD [b0];
	add rsi, rax;
	rdx <- 2;
	call print;

	xor rdi, rdi;
	call exit;

fn print(rsi 'str', rdx 'len') {
	rax <- 1;
	rdi <- 1;
	syscall;
}

fn exit(rdi 'exit_code') {
	rax <- 60;
	syscall;
}

// vim: syntax=rust
