"""Audit the executable pieces of the WIDA number-theory conclusions printout."""
import hashlib, json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-ntb.md').read_bytes()
fix = root / 'tests/fixtures/wida_ntbprint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.md').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
(fix / 'README.md').write_text(
    '# WIDA number-theory conclusions fixture\n\n'
    'main.md is the exact CRLF blob `2897b4bbfeab4548fd8fecc101f425c9e397fa97` '
    'from hh2048/XCPC tree `cfdb12db6792eb2303798541fb5c760ed2bc618b`.\n\n'
    'Path: `02 - 打印稿模板汇总/05B - 数论常见结论及例题.md`.\n\n'
    'The upstream GPL-3.0 license is preserved in LICENSE. This fixture is not '
    'relicensed under the root MIT license. See docs/WIDA-NTBPRINT.md.\n'
)
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '2897b4bbfeab4548fd8fecc101f425c9e397fa97'
text = blob.decode().replace('\r\n', '\n')
codes = [part.split('```', 1)[0] for part in text.split('```c++')[1:]]
ball, harmonic, powers, clac = codes
assert 'YangHuiTriangle' in ball and 'log(n)' in harmonic and 'popcountll' in powers and 'clac' in clac
out = root / 'build/wida-ntbprint'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
head = '#include <bits/stdc++.h>\nusing namespace std;\nusing i64 = long long;\n'

def run(name, code, flags, input_text=''):
    path = out / (name + '.cpp')
    path.write_text(head + code)
    exe = out / name
    compiled = subprocess.run([CXX, '-std=c++20', *flags, str(path), '-o', str(exe)], text=True, capture_output=True)
    if compiled.returncode != 0:
        compiled.stdout = ''
        return compiled
    return subprocess.run([str(exe)], input=input_text, text=True, capture_output=True, env=env, timeout=30)

ready = ball.replace(
    'int Task = 1;',
    'YangHuiTriangle(); Stirling2(); GeneratingFunction(); Fac(10);\n        int Task = 1;',
    1,
)
queries = '\n'.join([
    '8',
    '1 4 2',
    '3 4 2',
    '4 2 3',
    '6 5 3',
    '9 4 2',
    '10 3 2',
    '11 2 5',
    '12 3 2',
]) + '\n'
expect = '3\n2\n6\n6\n7\n8\n20\n6\n'
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    got = run('balls-' + mode, ready, flags, queries)
    assert got.returncode == 0 and got.stdout == expect, (got.returncode, got.stdout, got.stderr[-400:])
    split = run('pow-' + mode, powers, flags, '9 4\n')
    assert split.returncode == 0 and split.stdout == 'YES\n1 2 2 4 ', (split.stdout, split.stderr[-200:])
    refused = run('pow-no-' + mode, powers, flags, '3 1\n')
    assert refused.stdout == 'NO\n'
    approx = run('harm-' + mode, 'int main(){ int n=10; double h=0; for(int i=1;i<=n;i++) h+=1.0/i; double a=' + harmonic + '; if (abs(a-h) > 1e-2) return 1; cout<<"ok\\n"; }\n', flags)
    assert approx.returncode == 0 and approx.stdout == 'ok\n'
    print(mode, 'PASS')
raw = run('balls-raw', ball, ['-O1', '-g', '-fsanitize=address,undefined'], '1\n1 4 2\n')
assert raw.returncode != 0
narrow = ball.replace('int Task = 1;', 'Stirling2(10); return 0;\n        int Task = 1;', 1)
assert run('stir-narrow', narrow, ['-O1', '-g', '-fsanitize=address,undefined']).returncode != 0
fac_default = ball.replace('int Task = 1;', 'Fac(); return 0;\n        int Task = 1;', 1)
assert run('fac-default', fac_default, ['-O1', '-g', '-fsanitize=address,undefined']).returncode != 0
assert run('clac', clac + '\nint main(){return 0;}\n', ['-O2']).returncode != 0
report = {
    'scope': 'After the four initializers are called, with Fac limited to 10, the checked ball-box answers are 3 2 6 6 7 8 20 6. The printed main does not call them. Stirling2(10) writes past its table. The default Fac(30) overflows signed long long. 9 as four powers of two prints 1 2 2 4. The inclusion function does not compile. The harmonic expression is within 0.01 of H_10. No online AC.',
    'blob': '2897b4bbfeab4548fd8fecc101f425c9e397fa97',
}
(root / 'verification/wida-ntbprint.json').write_text(json.dumps(report, indent=2) + '\n')
print('bounds PASS')
