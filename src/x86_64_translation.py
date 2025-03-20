
def x86_64_linux__translate_reg(rname: str) -> str | None:
    base_lookup_table: dict[str, str] = {
        'r0': 'rax',
        'r1': 'rbx',
        'r2': 'rcx',
        'r3': 'rdx',
        'r4': 'rsi',
        'r5': 'rdi',
        'rsp': 'rsp',
        'rbp': 'rbp',
        'r8': 'r8',
        'r9':  'r9',
        'r10': 'r10',
        'r11': 'r11',
        'r12': 'r12',
        'r13': 'r13',
        'r14': 'r14',
        'r15': 'r15',
    }
    return base_lookup_table.get(rname)

