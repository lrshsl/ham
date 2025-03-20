static b0 = '0',0xa,0;
static ba = "text",0;

label square:
    push    rbp;
    mov     rbp, rsp;
    mov     DWORD [rbp-4], edi;
    mov     eax, DWORD [rbp-4];
    imul    eax, eax;
    pop     rbp;
    ret;

label main:
    edi <- 5;
    xor rax, rax
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
