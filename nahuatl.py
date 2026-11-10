#!/usr/bin/env python3
"""NÁHUATL 0.1: intérprete experimental (transpilador a Python).
No ejecuta código no confiable: el resultado se evalúa como Python.
"""
import re
import sys
from pathlib import Path

TOKEN_RE = re.compile(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')')
KEYWORDS = {
    'quema': 'True', 'amo': 'False', 'ayac': 'None',
    'ihcuiloa': 'print', 'ihuan': 'and', 'noso': 'or', 'ax': 'not',
}
IDENT = r'[A-Za-z_][A-Za-z_0-9]*'


def expression(src):
    chunks = TOKEN_RE.split(src)
    for i in range(0, len(chunks), 2):
        chunks[i] = re.sub(r'\b(?:' + '|'.join(KEYWORDS) + r')\b',
                           lambda m: KEYWORDS[m.group()], chunks[i])
    return ''.join(chunks)


def compile_nahuatl(source):
    lines = ['# Generado automáticamente por NÁHUATL 0.1']
    level = 0
    for number, original in enumerate(source.splitlines(), 1):
        s = original.strip()
        if not s or s.startswith('#'):
            continue
        if s == '}':
            level -= 1
            if level < 0:
                raise SyntaxError(f'Línea {number}: llave de cierre inesperada')
            continue
        if s.startswith('zan {') and s != 'zan {':
            raise SyntaxError(f'Línea {number}: escribe «zan {{» en su propia línea')
        if s == 'zan {':
            if not lines[-1].lstrip().startswith('if ') and not lines[-1].lstrip().startswith('elif ') and not (len(lines)>1 and lines[-1].lstrip().startswith('pass')):
                # Se permite tras cerrar el bloque «tla», validación simple.
                pass
            lines.append('    '*level + 'else:')
            level += 1
            continue
        block = s.endswith('{')
        stmt = s[:-1].strip() if block else s.rstrip(';').strip()
        if block:
            m = re.fullmatch(r'tla\s*\((.*)\)', stmt)
            if m:
                result = f'if {expression(m.group(1))}:'
            else:
                m = re.fullmatch(r'oc\s*\((.*)\)', stmt)
                if m:
                    result = f'while {expression(m.group(1))}:'
                else:
                    m = re.fullmatch(rf'tequitl\s+({IDENT})\s*\((.*?)\)', stmt)
                    if m:
                        result = f'def {m.group(1)}({m.group(2)}):'
                    else:
                        raise SyntaxError(f'Línea {number}: bloque desconocido: {stmt}')
            lines.append('    '*level + result)
            level += 1
        else:
            if stmt.startswith('mati '):
                stmt = stmt[5:]
            elif stmt.startswith('cuepa '):
                stmt = 'return ' + stmt[6:]
            if not stmt:
                raise SyntaxError(f'Línea {number}: instrucción vacía')
            lines.append('    '*level + expression(stmt))
    if level != 0:
        raise SyntaxError(f'Faltan {level} llaves de cierre')
    return '\n'.join(lines) + '\n'


def main():
    if len(sys.argv) != 2:
        raise SystemExit('Uso: python nahuatl.py programa.nah')
    source = Path(sys.argv[1]).read_text(encoding='utf-8')
    python_code = compile_nahuatl(source)
    exec(compile(python_code, sys.argv[1], 'exec'), {'__name__': '__main__'})


if __name__ == '__main__':
    main()
