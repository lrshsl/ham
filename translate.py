from sys import argv
import sys

from typing import IO

from collections.abc import Generator

consts: list[str] = []
prog: list[tuple[str, str]] = []

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
            print("usage: python translate.py [SRC_FILE] [OUT_FILE]", file=sys.stderr)
            sys.exit(1)

    rst = translate(src)

    if len(rst) != 0:
        print(f'Unparsed: {rst}')

    if isinstance(out, str):
        with open(argv[2], 'w') as f:
            dump_all(f)
    else:
        dump_all(out)

def dump_all(file: IO[str]) -> None:
    print('\nglobal _start\n', file=file)
    dump_data_section(consts, output=file)
    dump_text_section(prog, output=file)

def next_token(s: str, delimiter: str | None = None) -> tuple[str, str]:
    parts = s.split(delimiter, 1)

    if len(parts) < 2:
         return s.strip(), ''

    token, rst = parts
    return token.strip(), rst

def split_and_strip(s: str, delimiter: str | None = None) -> Generator[str, None, None]:
    return (x.strip() for x in s.split(delimiter))

def parse_const(s: str) -> tuple[str, str]:
    name, rst = next_token(s, '=')
    value, rst = next_token(rst, ';')
    return f'{name}: db {value}', rst

def parse_stmt(s: str) -> tuple[str, str]:
    line, rst = next_token(s, ';')

    if '<-' in line:
        target, line_rst = next_token(line, '<-')
        src = line_rst.strip()

        return f'\tmov {target}, {src}', rst

    cmd, args = next_token(line)
    args = split_and_strip(args, ',')
    # TODO: store signature in hashmap

    return f'\t{cmd} {",".join(args)}', rst

def parse_label(s: str) -> tuple[str, str]:
    name, rst = next_token(s, ':')
    if name == 'main':
        name = '_start'
    return f'{name}:\n', rst

def parse_fn_def(s: str) -> tuple[tuple[str, str], str]:
    name, rst = next_token(s, '(')

    argline, rst = next_token(rst, ')')
    args = list(split_and_strip(argline, ','))
    #registers = (args[i] for i in range(0, len(args), 2))

    tok, rst = next_token(rst)
    assert tok == '{'

    stmts, rst = parse_statements(rst)

#\t{'\npop '.join(registers)}
    return (name, f"""
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

def parse_top_level(s: str) -> str | None:
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
        case '//':
            _, rst = rst.split('\n', maxsplit=1)
        case '///':
            comment, rst = next_token(rst, '\n')
            prog.append(('', '; ' + comment))
        case other:
            x, rst = parse_stmt(' '.join((other, rst)))
            prog.append(('', x))

    return rst


def translate(s: str) -> str:

    while tmp := parse_top_level(s):
        s = tmp

    return s

def dump_data_section(consts: list[str], output: IO[str] | None = None) -> None:
    print('section .data', file=output, end='\n\t')
    print('\n\t'.join(consts), file=output)
    print('\n', file=output)

def dump_text_section(instructions: list[tuple[str, str]], output: IO[str] | None = None) -> None:
    print('section .text\n', file=output)
    print('\n'.join(''.join(pair) for pair in instructions), file=output)
    print(file=output)

if __name__ == '__main__':
    main()

