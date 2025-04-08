static inbuf: 2b;
static turn_msg = "Player 0's turn: ";
const player_n_index = 7;
const nl = 0xa,0xa;
const turn_msg_len = 18;

const table syscall = {
	read = 0,
	write = 1,
	exit = 60,
};
const table fd = { stdin = 0, stdout = 1 };
const table sysarg = {
	0 = rax,
	1 = rdi,
	2 = rsi,
	3 = rdx,
	4 = r10,
	5 = r8,
	6 = r9,
	ret = rax,
	syscall_code = rax,
};

fn main() {
	turn_msg -> $sysarg.2;
	$turn_msg_len -> $sysarg.3;
	call print;

	$syscall.read -> $sysarg.syscall_code;
	$sysarg.1 <- $fd.stdin;
	$sysarg.2 <- inbuf;
	$sysarg.3 <- 1;
	syscall;

	call newline;

	r10 <- turn_msg;
	r11 <- $player_n_index;
	BYTE [r11 + r10] <- '1';
	turn_msg -> $sysarg.2;
	$turn_msg_len -> $sysarg.3;
	call print;

	xor $sysarg.1, $sysarg.1;
	call exit;
}

fn newline($sysarg.3 'count (1-2)') {
	$sysarg.syscall_code <- $syscall.write;
	$sysarg.1 <- $fd.stdout;
	$sysarg.2 <- nl;
	$sysarg.3 <- 1;
	syscall;
}

fn print($sysarg.2 'str', $sysarg.3 'len') {
	$sysarg.0 <- $syscall.write;
	$sysarg.1 <- $fd.stdout;
	syscall;
}

fn exit(rdi 'exit_code') {
	$sysarg.0 <- $syscall.exit;
	syscall;
}


// vim: syntax=rust
