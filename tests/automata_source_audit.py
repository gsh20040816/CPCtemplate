"""Unchanged attachment SAM/general-SAM/PAM with independent source and driver checks."""
from pathlib import Path
import hashlib
import json
import os
import random
import re
import subprocess
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
out = root / 'build/automata-source'
out.mkdir(parents=True, exist_ok=True)
pdf = root / 'build/issue11-reference.pdf'
assert hashlib.sha256(pdf.read_bytes()).hexdigest() == 'b5ce46f7cf542be2d9846d8f01898c8ccd7f4619521036b0b7895206895745f3'
text = (root / 'build/issue11-reference.txt').read_text()
sources = {}
for name, count in [('sam', 47), ('exSAM', 119), ('PAM', 56)]:
    section = text.split('代码：' + name + '.cpp', 1)[1].split('代码：', 1)[0]
    lines = []
    for line in section.splitlines():
        match = re.match(r'^\s*(\d+)(?:[ \t]+(.*))?$', line)
        if match and int(match[1]) == len(lines) + 1:
            lines.append(match[2] or '')
        elif lines and line.lstrip().startswith('+ 5], total, last;'):
            lines[-1] += ' ' + line.strip()
        if len(lines) == count:
            break
    assert len(lines) == count
    sources[name] = '\n'.join(lines) + '\n'
    (out / (name + '.cpp')).write_text(sources[name])

rng = random.Random(61395496)
multi_cases = [['aa', 'ab', 'bac', 'caa'], ['ab', 'b'], ['a', 'a'], ['abcbc', 'bcbc', 'cbc']]
for _ in range(36):
    multi_cases.append([''.join(rng.choices('abcd', k=rng.randrange(1, 12))) for _ in range(rng.randrange(1, 7))])

def multi_truth(words):
    ends = {}
    for i, s in enumerate(words):
        for l in range(len(s)):
            for r in range(l, len(s)):
                ends.setdefault(s[l:r + 1], set()).add((i, r))
    return [len(ends), 1 + len({frozenset(v) for v in ends.values()})]

pam_cases = []
for _ in range(40):
    encoded = ''.join(rng.choices('abcz', k=rng.randrange(1, 80)))
    decoded = ''
    answer = []
    previous = 0
    for c in encoded:
        decoded += chr(97 + (ord(c) - 97 + previous) % 26)
        previous = sum(decoded[l:] == decoded[l:][::-1] for l in range(len(decoded)))
        answer.append(previous)
    pam_cases.append((encoded, answer))
# At the original PAM capacity, encode plaintext with closed-form suffix counts.
n = 500000
pam_cases.append((''.join(chr(97 + (-i) % 26) for i in range(n)), list(range(1, n + 1))))
pam_cases.append((''.join(chr(97 + (i % 2 - (i + 1) // 2) % 26) for i in range(n)), [(i + 2) // 2 for i in range(n)]))
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
results = {}
for mode in ['normal', 'sanitizer']:
    flags = ['-std=c++20', '-O2']
    if mode == 'sanitizer':
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-D_GLIBCXX_ASSERTIONS']
    programs = {
        'source-structure': root / 'tests/automata_source.cpp',
        'source-general': out / 'exSAM.cpp',
        'current-general': root / 'verify/luogu/P6139.compact.cpp',
        'source-pam': out / 'PAM.cpp',
        'current-pam': root / 'verify/luogu/P5496.compact.cpp',
    }
    for name, source in programs.items():
        exe = out / (name + '-' + mode)
        subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)
        def run(data):
            p = subprocess.run([str(exe)], input=data, text=True, capture_output=True, env=env, timeout=120)
            assert p.returncode == 0 and not p.stderr, (name, mode, p.stderr[:2000])
            return p.stdout
        if name == 'source-structure':
            result = run('').strip()
        elif name.endswith('general'):
            for words in multi_cases:
                data = str(len(words)) + '\n' + '\n'.join(words) + '\n'
                assert list(map(int, run(data).split())) == multi_truth(words)
            result = str(len(multi_cases)) + ' complete endpos protocols PASS'
        else:
            for encoded, answer in pam_cases:
                assert list(map(int, run(encoded + '\n').split())) == answer
            result = str(len(pam_cases)) + ' complete decoded protocols incl. 500000 equal/alternating PASS'
        results[name + '-' + mode] = result
        print(name, mode, result, flush=True)
report = {
    'source_pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
    'source_line_counts': {'sam': 47, 'exSAM': 119, 'PAM': 56},
    'source_sha256': {name: hashlib.sha256(s.encode()).hexdigest() for name, s in sources.items()},
    'files': {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in ['tests/automata_source.cpp', 'tests/automata_source_audit.py', 'src/compact/string.hpp', 'src/compact/online_sam.hpp', 'src/compact/general_sam.hpp', 'src/compact/palindromic_tree.hpp', 'verify/luogu/P6139.compact.cpp', 'verify/luogu/P5496.compact.cpp']},
    'runs': results,
    'limitations': ['No new online verdict or performance ranking', 'General-SAM source maximum million-character recursion not run; current implementation prior stress evidence is separate', 'Harness clears generalized edge vectors between cases; original Clear does not reset Solve edges', 'Original ordinary SAM endpos is a raw external tag, not a frequency'],
}
(root / 'verification/automata-source-audit.json').write_text(json.dumps(report, indent=2) + '\n')
