static zeros: 4b;
static turn_msg = "Player 0's turn: ";
const turn_msg_len = 18;

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

fn print($sysarg.2 'str', $sysarg.3 'len') {
    $sysarg.0 <- 1;
    $sysarg.1 <- 1;
    syscall;
}

fn exit(rdi 'exit_code') {
    $sysarg.0 <- 60;
    syscall;
}


// vim: syntax=rust
