#!/usr/bin/env python3
"""Expression evaluator versus an independent Python-AST evaluator with C++ truncation."""
import ast
import os
import random
import subprocess
from pathlib import Path
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
exe = root / 'build/expression_driver'
flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-sanitize-recover']
subprocess.run([CXX, *flags, str(root / 'tests/expression_driver.cpp'), '-o', str(exe)], check=True)
LIMIT = 1 << 62


class Bad(Exception):
    pass


def check(v):
    if abs(v) >= LIMIT:
        raise Bad
    return v


def ev(node):
    if isinstance(node, ast.Expression):
        return ev(node.body)
    if isinstance(node, ast.Constant):
        return check(node.value)
    if isinstance(node, ast.UnaryOp):
        v = ev(node.operand)
        return check(-v if isinstance(node.op, ast.USub) else v)
    if isinstance(node, ast.BinOp):
        a, b = ev(node.left), ev(node.right)
        op = node.op
        if isinstance(op, ast.Add):
            return check(a + b)
        if isinstance(op, ast.Sub):
            return check(a - b)
        if isinstance(op, ast.Mult):
            return check(a * b)
        if isinstance(op, (ast.FloorDiv, ast.Mod)):
            if b == 0:
                raise Bad
            q = abs(a) // abs(b) * (1 if (a >= 0) == (b >= 0) else -1)  # truncation
            return check(q if isinstance(op, ast.FloorDiv) else a - q * b)
        if isinstance(op, ast.Pow):
            if b < 0 or b > 64:
                raise Bad
            r = 1
            for _ in range(b):
                r = check(r * a)
            return r
    raise AssertionError(ast.dump(node))


rng = random.Random(2025)


def gen(depth):
    if depth == 0 or rng.random() < 0.25:
        return str(rng.choice([0, 1, 2, 3, 7, 10, 123, 99999, 3037000499]))
    k = rng.random()
    if k < 0.15:
        return rng.choice(['-', '+']) + rng.choice([' ', '']) + gen(depth - 1)
    if k < 0.3:
        return '(' + gen(depth - 1) + ')'
    op = rng.choice(['+', '-', '*', '/', '%', '^', '+', '*'])
    sp = rng.choice(['', ' '])
    return gen(depth - 1) + sp + op + sp + gen(depth - 1)


def to_python(e):
    # same grammar in Python: ^ -> ** (right-assoc, above unary), / -> // (truncation done in ev)
    return e.replace('^', '**').replace('/', '//')


cases, want = [], []
while len(cases) < 6000:
    e = gen(rng.randint(1, 6))
    try:
        v = ev(ast.parse(to_python(e), mode='eval'))
    except Bad:
        continue
    cases.append(e)
    want.append(str(v))
fixed = [('-2^2', -4), ('2^3^2', 512), ('2^-0', 1), ('-7/2', -3), ('-7%3', -1), ('7%-3', 1), ('--3', 3),
         ('2*-3', -6), ('(1+2)*3-4/2', 7), (' 1 + 2 ', 3), ('3037000499^2', 3037000499 ** 2), ('3037000500^1', 3037000500),
         ('0^0', 1), ('-(2+3)^2', -25)]
cases += [e for e, _ in fixed]
want += [str(v) for _, v in fixed]
out = subprocess.run([str(exe)], input='\n'.join(cases) + '\n', capture_output=True, text=True, check=True).stdout.split()
assert out == want, next((c, o, w) for c, o, w in zip(cases, out, want) if o != w)
print(f'Expression: {len(cases)} random and fixed expressions vs AST evaluator with C++ truncation, sanitizers PASS')
