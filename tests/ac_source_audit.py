"""Attachment AC shortest-pattern propagation versus literal suffix matching."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
out = root / 'build/automata-source'
out.mkdir(parents=True, exist_ok=True)
pdf = root / 'build/issue11-reference.pdf'
assert hashlib.sha256(pdf.read_bytes()).hexdigest() == 'b5ce46f7cf542be2d9846d8f01898c8ccd7f4619521036b0b7895206895745f3'
section = (root / 'build/issue11-reference.txt').read_text().split('代码：ac_automaton.cpp', 1)[1].split('代码：', 1)[0]
lines = []
for line in section.splitlines():
    m = re.match(r'^\s*(\d+)(?:[ \t]+(.*))?$', line)
    if m and int(m[1]) == len(lines) + 1:
        lines.append(m[2] or '')
    if len(lines) == 69:
        break
assert len(lines) == 69
source = '\n'.join(lines) + '\n'
(out / 'ac_automaton.cpp').write_text(source)
results = {}
for mode in ['normal', 'sanitizer']:
    flags = ['-std=c++20', '-O2']
    if mode == 'sanitizer':
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-D_GLIBCXX_ASSERTIONS']
    exe = out / ('ac-' + mode)
    subprocess.run([CXX, *flags, str(root / 'tests/ac_source.cpp'), '-o', str(exe)], check=True)
    p = subprocess.run([str(exe)], text=True, capture_output=True, env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'), timeout=120)
    assert p.returncode == 0 and not p.stderr, p.stderr
    results[mode] = p.stdout.strip()
    print(mode, p.stdout.strip(), flush=True)
report = {'source_pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(), 'source_sha256': hashlib.sha256(source.encode()).hexdigest(), 'source_lines': 69, 'files': {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in ['tests/ac_source.cpp', 'tests/ac_source_audit.py', 'src/compact/string.hpp', 'src/compact/ac_shortest.hpp']}, 'runs': results, 'scope': 'Original unchanged Clear/Insert/Build plus missing declarations; positive pattern lengths, build once, literal suffix oracle; no new online AC'}
(root / 'verification/ac-source-audit.json').write_text(json.dumps(report, indent=2) + '\n')
