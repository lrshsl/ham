
const msg = "hello";

label main:
    r8 <- msg;
    r9 <- 5;
    call print;

    xor rdi, rdi;
	 call exit;

fn print(r8 'str', r9 'len') {
    rax <- 1;
    rdi <- 1;
    rsi <- r8;
    rdx <- r9;
    syscall;
}

fn exit(rdi 'exit_code') {
    rax <- 60;
    syscall;
}

// src comment
/// sticky comment


// vim: syntax=rust
