const a = 90;
const msg = "lol",0xa,0;


label main:
    rax <- 1;
    rdi <- 1;
    rsi <- msg;
    rdx <- 5;
    syscall;

    rax <- 60;
    xor rdi, rdi;
    syscall;


// vim: syntax=rust
