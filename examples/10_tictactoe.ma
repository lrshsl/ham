static zeros: 4b;
static turn_msg = "Player 0's turn: ";
const turn_msg_len = 18;

const table sysarg = {
	1 = rax,
	2 = rdi,
	3 = rdi,
	ret = rax,
};

fn main() {
	turn_msg -> rsi;
	$turn_msg_len -> rdx;
	call print;

	xor rdi, rdi;
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
