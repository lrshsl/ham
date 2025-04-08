static zeros: 4b;
static turn_msg = "Hi there",0xa,0;
const turn_msg_len = 10;

const table sysarg = {
	0 = rax,
	1 = rdi,
	2 = rsi,
	3 = rdx,
	4 = r10,
	5 = r8,
	6 = r9,
	ret = rax,
};

fn main() {
	turn_msg -> $sysarg.2;
	$turn_msg_len -> $sysarg.3;
	call print;

	xor $sysarg.1, $sysarg.1;
	call exit;
}

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
