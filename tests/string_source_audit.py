"""Audit unchanged issue11 string snippets against independent finite oracles."""
from pathlib import Path
import hashlib
import itertools
import json
import os
import random
import re
import subprocess
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
out = root / 'build/string-source'
out.mkdir(parents=True, exist_ok=True)
pdf = root / 'build/issue11-reference.pdf'
assert hashlib.sha256(pdf.read_bytes()).hexdigest() == 'b5ce46f7cf542be2d9846d8f01898c8ccd7f4619521036b0b7895206895745f3'
text = (root / 'build/issue11-reference.txt').read_text()
names = ['manacher1', 'manacher2', 'suffix_array1', 'suffix_array2']
counts = [40, 24, 61, 79]
sources = {}
for name, count in zip(names, counts):
    section = text.split('代码：' + name + '.cpp', 1)[1].split('代码：', 1)[0]
    lines = []
    for line in section.splitlines():
        match = re.match(r'^\s*(\d+)(?:[ \t]+(.*))?$', line)
        if match and int(match[1]) == len(lines) + 1:
            lines.append(match[2] or '')
        elif lines and line.lstrip().startswith(('+ w]', 'y[sa[i + 1]]', 'rk[i] - 1] + k]')):
            lines[-1] += ' ' + line.strip()
        if len(lines) == count:
            break
    assert len(lines) == count, (name, len(lines))
    sources[name] = '\n'.join(lines) + '\n'
    (out / (name + '-original.cpp')).write_text(sources[name])

prefix = '#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\nconstexpr int max1 = 2048, max2 = 2048;\n'
for name in names:
    declarations = ''
    if name == 'suffix_array1':
        declarations = 'int len, lim, x[4101], y[4101], bin[4101], sa[4101], rk[4101], height[4101];\nchar s[4101];\n'
    if name == 'suffix_array2':
        declarations = 'int save_total_map;\n'
    body = sources[name]
    if name == 'manacher1':
        body = '#define main original_main\n' + body + '#undef main\n'
        driver = '''int main() {
    int cases;
    scanf("%d", &cases);
    while (cases--) {
        memset(pi, 0, sizeof(pi));
        memset(t, 0, sizeof(t));
        original_main();
    }
}
'''
    elif name == 'manacher2':
        driver = '''int main() {
    int cases;
    cin >> cases;
    while (cases--) {
        string s;
        cin >> s;
        string answer = Manacher(s);
        assert(s.find(answer) != string::npos);
        assert(equal(answer.begin(), answer.end(), answer.rbegin()));
        cout << answer.size() << '\\n';
    }
}
'''
    else:
        setup = 'cin >> len;\n        for (int i = 1; i <= len; i++) cin >> s[i];\n        Suffix_Array();' if name.endswith('1') else 'int len;\n        cin >> len >> save_total_map;\n        vector<int> a(len + 1);\n        for (int i = 1; i <= len; i++) cin >> a[i];\n        Suffix_Array(a.data(), len);'
        driver = '''int main() {
    int cases;
    cin >> cases;
    while (cases--) {
        memset(x, 0, sizeof(x));
        memset(y, 0, sizeof(y));
        memset(bin, 0, sizeof(bin));
        memset(height, 0, sizeof(height));
        memset(rk, 0, sizeof(rk));
        SETUP
        for (int i = 1; i <= len; i++) {
            cout << sa[i] - 1 << ' ' << rk[i] - 1 << ' ' << height[i] << ' ';
        }
        cout << '\\n';
    }
}
'''.replace('SETUP', setup)
    (out / (name + '.cpp')).write_text(prefix + declarations + body + driver)

rng = random.Random(1112)
strings = [''.join(s) for n in range(1, 8) for s in itertools.product('abc', repeat=n)]
strings += [''.join(rng.choices('abcdefghijklmnopqrstuvwxyz', k=rng.randrange(1, 100))) for _ in range(300)]
strings += ['a' * 1000, 'ab' * 500, 'z' * 1000]
def longest(s):
    answer = 0
    for center in range(2 * len(s) - 1):
        l = center // 2
        r = (center + 1) // 2
        while l >= 0 and r < len(s) and s[l] == s[r]:
            answer = max(answer, r - l + 1)
            l -= 1
            r += 1
    return answer

def suffix_truth(a, limit):
    sa = sorted(range(len(a)), key=lambda i: a[i:])
    rk = [0] * len(a)
    height = [0] * len(a)
    for k, i in enumerate(sa):
        rk[i] = k
        if k:
            j = sa[k - 1]
            h = 0
            while i + h < len(a) and j + h < len(a) and a[i + h] == a[j + h] and a[i + h] <= limit:
                h += 1
            height[k] = h
    return [v for i in range(len(a)) for v in (sa[i], rk[i], height[i])]

integer_cases = []
for n in range(1, 8):
    for a in itertools.product(range(1, min(n, 3) + 1), repeat=n):
        for limit in range(4):
            integer_cases.append((list(a), limit))
for _ in range(300):
    n = rng.randrange(1, 100)
    integer_cases.append(([rng.randrange(1, n + 1) for _ in range(n)], rng.randrange(n + 1)))
integer_cases += [([1] * 1000, 1), ([1, 2] * 500, 1), ([1, 2] * 500, 2)]
expected = {
    'manacher1': [[longest(s)] for s in strings],
    'suffix_array1': [suffix_truth(list(s), 'z') for s in strings],
    'suffix_array2': [suffix_truth(a, limit) for a, limit in integer_cases],
}
expected['manacher2'] = expected['manacher1']
inputs = {
    'manacher1': str(len(strings)) + '\n' + '\n'.join(strings) + '\n',
    'suffix_array1': str(len(strings)) + '\n' + ''.join(f'{len(s)} {s}\n' for s in strings),
    'suffix_array2': str(len(integer_cases)) + '\n' + ''.join(f'{len(a)} {limit}\n' + ' '.join(map(str, a)) + '\n' for a, limit in integer_cases),
}
inputs['manacher2'] = inputs['manacher1']
results = {}
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
for mode in ['normal', 'sanitizer']:
    flags = ['-std=c++20', '-O2']
    if mode == 'sanitizer':
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-D_GLIBCXX_ASSERTIONS']
    for name in names:
        exe = out / (name + '-' + mode)
        subprocess.run([CXX, *flags, str(out / (name + '.cpp')), '-o', str(exe)], check=True)
        p = subprocess.run([str(exe)], input=inputs[name], text=True, capture_output=True, env=env, timeout=120)
        assert p.returncode == 0 and not p.stderr, (name, mode, p.stderr[:2000])
        got = [list(map(int, line.split())) for line in p.stdout.splitlines()]
        assert len(got) == len(expected[name])
        for i, (a, b) in enumerate(zip(got, expected[name])):
            assert a == b, (name, i, a, b)
        results[name + '-' + mode] = len(got)
        print(name, mode, len(got), 'PASS', flush=True)
current_runs = {}
for mode in ['normal', 'sanitizer']:
    flags = ['-std=c++20', '-O2']
    if mode == 'sanitizer':
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-D_GLIBCXX_ASSERTIONS']
    for name in ['string_source_current', 'manacher', 'suffix_array']:
        exe = out / (name + '-' + mode)
        subprocess.run([CXX, *flags, str(root / 'tests' / (name + '.cpp')), '-o', str(exe)], check=True)
        data = inputs['suffix_array2'] if name == 'string_source_current' else ''
        p = subprocess.run([str(exe)], input=data, text=True, capture_output=True, env=env, timeout=120)
        assert p.returncode == 0 and not p.stderr, (name, mode, p.stderr[:2000])
        if name == 'string_source_current':
            assert [list(map(int, line.split())) for line in p.stdout.splitlines()] == expected['suffix_array2']
            current_runs[name + '-' + mode] = len(integer_cases)
        else:
            current_runs[name + '-' + mode] = p.stdout.strip()
        print(name, mode, 'PASS', flush=True)
failures = {}
for name, value, diagnostic in [('manacher1', '@', 'index -1 out of bounds'), ('manacher2', '$', '__pos <= size()')]:
    p = subprocess.run([str(out / (name + '-sanitizer'))], input='1\n' + value + '\n', text=True, capture_output=True, env=env)
    assert p.returncode != 0 and diagnostic in p.stderr
    failures[name] = {'input': value, 'diagnostic': diagnostic, 'scope': 'Outside tested lowercase domain; original is not arbitrary-byte safe'}
report = {'source_pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(), 'source_line_counts': dict(zip(names, counts)), 'source_sha256': {k: hashlib.sha256(v.encode()).hexdigest() for k, v in sources.items()}, 'runs': results, 'current_runs': current_runs, 'sentinel_counterexamples': failures, 'test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'current_header_sha256': hashlib.sha256((root / 'src/compact/string.hpp').read_bytes()).hexdigest(), 'scope': 'Unchanged source snippets; lowercase nonempty Manacher/SA1, positive codes <= n and separator-clipped SA2. Harness clears globals per case; repeated calls without clearing are not certified.', 'online': 'No new submission or AC'}
(root / 'verification/string-source-audit.json').write_text(json.dumps(report, indent=2) + '\n')
