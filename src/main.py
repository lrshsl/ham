from sys import argv
import sys
from typing import IO
from collections.abc import Generator

from x86_64_translation import x86_64_linux__translate_reg as translate_reg

consts: list[str] = []
statics: list[str] = []
uinit_statics: list[str] = []
prog: list[tuple[str, str]] = []

Value = str | int | float | dict[str, "Value"]
const_symbols: dict[str, Value] = {}


def main():
    out: str | IO[str]
    match len(argv):
        case 1:
            src = sys.stdin.read()
            out = sys.stdout
        case 2:
            src = open(argv[1], 'r').read()
            out = sys.stdout
        case 3:
            src = open(argv[1], 'r').read()
            out = argv[2]
        case _:
            print(f"usage: python {argv[0]} [SRC_FILE] [OUT_FILE]", file=sys.stderr)
            sys.exit(1)

    rst = translate(src)

    if len(rst) != 0:
        print(f'Unparsed: {rst}')

    if isinstance(out, str):
        with open(argv[2], 'w') as f:
            dump_all(f)
    else:
        dump_all(out)


##################################################
# Dump functions
##################################################


def dump_all(file: IO[str]) -> None:
    print('\nglobal _start\n', file=file)
    dump_data_section(consts, output=file)
    dump_text_section(prog, output=file)


def dump_data_section(consts: list[str], output: IO[str] | None = None) -> None:
    print('section .rodata', file=output, end='\n\t')
    print('\n\t'.join(consts), file=output, end='\n\n')
    print('section .data', file=output, end='\n\t')
    print('\n\t'.join(statics), file=output, end='\n\n')
    print('section .bss', file=output, end='\n\t')
    print('\n\t'.join(uinit_statics), file=output, end='\n\n')


def dump_text_section(instructions: list[tuple[str, str]], output: IO[str] | None = None) -> None:
    print('section .text\n', file=output)
    for label, inst in instructions:
        if label:
            print(f'\n{label}:\n', file=output)
        print(inst, file=output)
    print(file=output)


##################################################
# Utils
##################################################


def next_token(s: str, delimiter: str | None = None) -> tuple[str, str]:
    parts = s.split(delimiter, 1)

    if len(parts) < 2:
         return s.strip(), ''

    token, rst = parts
    return token.strip(), rst


def split_and_strip(s: str, delimiter: str | None = None) -> Generator[str, None, None]:
    return (x.strip() for x in s.split(delimiter))


##################################################
# Parsing functions
##################################################


def parse_top_level(s: str) -> str | None:
    if not len(s.strip()):
        return

    fst, rst = next_token(s)
    match fst:
        case 'const':
            x, rst = parse_const_decl(rst)
            consts.append(x)
        case 'static':
            if '=' in rst.split(';', maxsplit=1)[0]:
                x, rst = parse_db_decl(rst)
                statics.append(x)
            else:
                x, rst = parse_resb_decl(rst)
                uinit_statics.append(x)
        case 'fn':
            x, rst = parse_fn_def(rst)
            prog.append(x)
        case 'label':
            label, rst = parse_label(rst)
            inst, rst = parse_stmt(rst)
            prog.append((label, inst))
        case '//':
            _, rst = rst.split('\n', maxsplit=1)
            rst = rst if '\n' in rst else ''
        case '///':
            comment, rst = next_token(rst, '\n')
            prog.append(('', '; ' + comment))
            rst = rst if '\n' in rst else ''
        case other:
            x, rst = parse_stmt(' '.join((other, rst)))
            prog.append(('', x))

    return rst


def parse_resb_decl(s: str) -> tuple[str, str]:
    # Uninitialized data (set to 0)
    # Example: `static a: 4b;`
    line, rst = s.split(';', maxsplit=1)
    name, line_rst = next_token(line, ':')
    n_bytes, line_rst = next_token(line_rst, 'b')
    assert line_rst.strip() == '', f'Unexpected trailing token: {line_rst.strip()}'
    return f'{name}: resb {n_bytes}', rst


def parse_db_decl(s: str) -> tuple[str, str]:
    # Initialized
    # Example: `static a = 4;`
    name, rst = next_token(s, '=')
    value, rst = next_token(rst, ';')
    value = process_arg(value)
    const_symbols[name] = value
    return f'{name}: db {value}', rst


def parse_const_decl(s: str) -> tuple[str, str]:
    # Examples:
    # `const a = 4;`
    # `const table t = { a = 7, b = 1 };`
    #
    name, rst = next_token(s, '=')
    value, rst = next_token(rst, ';')

    if ' ' in name:
        _type, name = next_token(name)
        if _type == 'table':
            return parse_table_decl(name, value), rst

    value = process_arg(value)
    const_symbols[name] = value
    return f'{name}: db {value}', rst


def parse_table_decl(name: str, s: str) -> str:
    content = s.lstrip().lstrip('{')
    content, _ = content.split('}')

    entries = (list(split_and_strip(e, '=')) for e in content.split(','))
    entries = ((e[0], process_arg(e[1])) for e in entries if len(e) == 2)
    const_symbols[name] = dict(entries)
    
    return ''


def process_arg(arg: str) -> Value:
    if arg.strip().startswith('$'):
        if value := lookup_pathident(arg[1:]):
            return value
        
    elif r := translate_reg(arg):
        return r
    return arg


def lookup_pathident(path: str) -> Value | None:
    pathidents = path.split('.')
    namespace = const_symbols
    for ident in pathidents:
        e = namespace[ident]
        if isinstance(e, dict):
            namespace = e
        else:
            return e

def parse_stmt(s: str) -> tuple[str, str]:
    line, rst = next_token(s, ';')

    mov_left: bool = '<-' in line
    mov_right: bool = '->' in line
    assert not (mov_left and mov_right)

    if mov_left or mov_right:
        ch = '<-' if mov_left else '->'
        target, line_rst = next_token(line, ch)
        src = line_rst.strip()
        src, target = process_arg(src), process_arg(target)

        if mov_right:
            target, src = src, target

        return f'\tmov {target}, {src}', rst

    cmd, args = next_token(line)
    args = map(process_arg, split_and_strip(args, ','))
    args = map(str, args)
    # TODO: store signature in hashmap

    return f'\t{cmd} {", ".join(args)}', rst


def parse_label(s: str) -> tuple[str, str]:
    name, rst = next_token(s, ':')
    if name == 'main':
        name = '_start'
    return f'{name}', rst


def parse_fn_def(s: str) -> tuple[tuple[str, str], str]:
    name, rst = next_token(s, '(')
    if name == 'main':
        name = '_start'

    argline, rst = next_token(rst, ')')
    params = list(split_and_strip(argline, ','))
    #registers = (params[i] for i in range(0, len(params), 2))

    tok, rst = next_token(rst)
    assert tok == '{'

    stmts, rst = parse_statements(rst)

#\t{'\npop '.join(registers)}
    return (f'; fn\n{name}', f"""\
{'\n'.join(stmts)}
\tret
"""), rst


def parse_statements(s: str) -> tuple[list[str], str]:
    stmts: list[str] = []
    while True:
        tok, rst = next_token(s)
        if tok in ('}', ''):
            break
        stmt, s = parse_stmt(s)
        stmts.append(stmt)
    return stmts, rst


def translate(s: str) -> str:

    while tmp := parse_top_level(s):
        s = tmp

    return s

if __name__ == '__main__':
    main()

