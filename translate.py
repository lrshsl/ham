from sys import argv

#assert(len(argv) == 2, "usage: python translate.py <SRC_FILE>")
#src = open(argv[1], 'r').read()

t1 = """
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
"""

t2 = """
const msg = "hello";

fn print (r8 'str', r9 'len') {
    rax <- 1;
    rdi <- 1;
    rsi <- r8;
    rdx <- r9;
    syscall;
}

label main:
    r8 <- msg;
    r9 <- 5;
    call print;

    rax <- 60;
    xor rdi, rdi;
    syscall;
"""

consts = []
prog = []

def next_token(s: str, delimiter: str | None = None) -> (str, str):
    parts = s.split(delimiter, 1)

    if len(parts) < 2:
         return s.strip(), ''

    token, rst = parts
    return token.strip(), rst

def split_and_strip(s: str, delimiter: str | None = None) -> (str, str):
    return (x.strip() for x in s.split(delimiter))

def parse_const(s: str) -> (str, str):
    name, rst = next_token(s, '=')
    value, rst = next_token(rst, ';')
    return f'{name}: db {value}', rst

def parse_stmt(s: str) -> (str, str):
    line, rst = next_token(s, ';')

    if '<-' in line:
        target, line_rst = next_token(line, '<-')
        src = line_rst.strip()

        return f'\tmov {target}, {src}', rst

    cmd, args = next_token(line)
    args = split_and_strip(args, ',')

    return f'\t{cmd} {",".join(args)}', rst

def parse_label(s: str) -> (str, str):
    name, rst = next_token(s, ':')
    if name == 'main':
        name = '_start'
    return f'{name}:\n', rst

def parse_fn_def(s: str) -> (str, str):
    name, rst = next_token(s, '(')

    argline, rst = next_token(rst, ')')
    args = list(split_and_strip(argline, ','))
    #registers = (args[i] for i in range(0, len(args), 2))

    tok, rst = next_token(rst)
    assert tok == '{'

    stmts, rst = parse_statements(rst)

#\t{'\npop '.join(registers)}
    return f"""
{name}:
{'\n'.join(stmts)}
\tret
""", rst

def parse_statements(s: str) -> str:
    stmts = []
    while True:
        tok, rst = next_token(s)
        if tok in ('}', ''):
            return stmts, rst
        stmt, s = parse_stmt(s)
        stmts.append(stmt)

def parse_top_level(s: str) -> str:
    if not len(s.strip()):
        return

    fst, rst = next_token(s)
    match fst:
        case 'const':
            x, rst = parse_const(rst)
            consts.append(x)
        case 'fn':
            x, rst = parse_fn_def(rst)
            prog.append(x)
        case 'label':
            label, rst = parse_label(rst)
            inst, rst = parse_stmt(rst)
            prog.append((label, inst))
        case other:
            x, rst = parse_stmt(' '.join((other, rst)))
            prog.append(('', x))

    return rst


def translate(s: str) -> str:
    while s := parse_top_level(s):
        pass

def dump_data_section(consts: list[str], output = None) -> None:
    print('section .data', file=output, end='\n\t')
    print('\n\t'.join(consts), file=output)
    print('\n', file=output)

def dump_text_section(instructions: list[(str, str)], output = None) -> None:
    print('section .text\n', file=output)
    print('\n'.join(''.join(pair) for pair in prog), file=output)
    print(file=output)

if __name__ == '__main__':
    translate(t2)
    print()
    print('global _start\n')
    dump_data_section(consts)
    dump_text_section(prog)

