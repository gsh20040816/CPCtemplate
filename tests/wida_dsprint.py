"""Audit the self-contained pieces of the WIDA data-structure printout."""
import hashlib, json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-ds.md').read_bytes()
fix = root / 'tests/fixtures/wida_dsprint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.md').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
(fix / 'README.md').write_text(
    '# WIDA data-structure printout fixture\n\n'
    'main.md is the exact CRLF blob `8dbb0e73c1a81acf14fb8d143b06b088a1762749` '
    'from hh2048/XCPC tree `cfdb12db6792eb2303798541fb5c760ed2bc618b`.\n\n'
    'Path: `02 - 打印稿模板汇总/08 - 数据结构.md`.\n\n'
    'The upstream GPL-3.0 license is preserved in LICENSE. This fixture is not '
    'relicensed under the root MIT license. See docs/WIDA-DSPRINT.md.\n'
)
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '8dbb0e73c1a81acf14fb8d143b06b088a1762749'
text = blob.decode().replace('\r\n', '\n')
fences = []
pos = 0
while True:
    a = text.find('```', pos)
    if a < 0:
        break
    b = text.find('\n', a)
    c = text.find('```', b + 1)
    fences.append(text[b + 1:c])
    pos = c + 3
dsu, bit, bit2, bitmax, inv, rank, *rest = fences
segt = fences[8]
simple, comp = fences[14], fences[15]
mo = fences[18]
frac, st = fences[21], fences[24]
pbds, vec, odt = fences[27], fences[28], fences[30]
out = root / 'build/wida-dsprint'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
head = '#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\nusing i64 = long long;\nusing LL = long long;\n'

def run(name, code, flags, input_text=''):
    path = out / (name + '.cpp')
    path.write_text(head + code)
    exe = out / name
    compiled = subprocess.run([CXX, '-std=c++20', *flags, str(path), '-o', str(exe)], text=True, capture_output=True)
    if compiled.returncode != 0:
        compiled.stdout = ''
        return compiled
    return subprocess.run([str(exe)], input=input_text, text=True, capture_output=True, env=env, timeout=30)

body = dsu + bit + 'using Sum = BIT;\n' + bit2.replace('struct BIT', 'struct Range', 1).replace('BIT(', 'Range(', 1) + bitmax.replace('struct BIT', 'struct MaxBIT', 1).replace('BIT(', 'MaxBIT(', 1) + r'''
int main() {
    DSU d(3);
    if (!d.merge(1, 2) || d.size(1) != 2 || d.E(1) != 1 || d.F(1)) return 1;
    if (d.merge(1, 1) || !d.F(1) || d.E(1) != 2) return 1;
    Sum s(3);
    s.add(1, 3); s.add(3, 4);
    if (s.rangeAsk(1, 3) != 7) return 1;
    Range g(3);
    g.rangeAdd(1, 3, 5);
    if (g.rangeSum(2, 3) != 10) return 1;
    MaxBIT m(3);
    m.modify(1, 4); m.modify(2, 9);
    if (m.rangeMax(1, 2) != 9) return 1;
    cout << "ok\n";
}
'''
rank_code = rank.replace('const int N = 10000000;', 'const int N = 16;') + '\n'
simple_code = r'''
int main() {
    vector<int> alls = {3, 1, 3};
''' + simple + r'''
    cout << get(1) << ' ' << get(3) << "\n";
}
'''
comp_code = comp + r'''
int main() {
    Compress h;
    h.add(3, 1, 3);
    h.init();
    cout << h[1] << ' ' << h[3] << ' ' << h.Get(0) << ' ' << h.count(2) << "\n";
}
'''
st_code = st + r'''
int main() {
    ST t(4);
    t.in1 = t.in2 = {0, 5, 1, 4, 2};
    t.init();
    cout << t.getMax(2, 4) << ' ' << t.getMin(1, 3) << "\n";
}
'''
frac_code = frac + r'''
int main() {
    Frac<int> a(1, 2);
    cout << (a < Frac<int>(2, 3)) << "\n";
}
'''
frac_add = frac + 'int main(){ Frac<int> a(1,2), b(1,3); cout << (a+b); }\n'
segt_code = segt + r'''
int main() {
    Segt<long long> s(vector<int>{0, 1, 2, 3});
    cout << s.ask(1, 3) << ' ' << s.rmq(1, 3) << "\n";
    s.modify(1, 3, 5);
    cout << s.ask(1, 1) << "\n";
}
'''
odt_code = odt + r'''
int main() {
    ODT t;
    t.s.insert({1, 5, 1});
    t.assign(2, 3, 7);
    cout << t.kth(1, 5, 3) << "\n";
}
'''
vec_code = 'int main() {\n' + vec + '}\n'
pbds_code = pbds.replace('int n; cin >> n;', 'int main() {\n    int n; cin >> n;', 1) + '}\n'
mo_code = mo
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    assert run('base-' + mode, body, flags).stdout == 'ok\n'
    assert run('simple-' + mode, simple_code, flags).stdout == '0 1\n'
    assert run('comp-' + mode, comp_code, flags).stdout == '1 2 1 0\n'
    assert run('st-' + mode, st_code, flags).stdout == '4 1\n'
    assert run('frac-' + mode, frac_code, flags).stdout == '1\n'
    assert run('segt-' + mode, segt_code, flags).stdout == '6 1\n4\n'
    assert run('odt-' + mode, odt_code, flags).returncode != 0
    assert run('vec-' + mode, vec_code, flags, '4\n1 3\n1 1\n3 3\n4 1\n').stdout == '2\n1\n'
    assert run('pbds-' + mode, pbds_code, flags, '3\n1 3\n1 1\n3 3\n').stdout == '2\n'
    assert run('mo-' + mode, mo_code, flags, '2\n1 2\n1\n1 1\n').stdout == '0\n'
    got = run('rank-' + mode, rank_code, flags, '4\n1 3\n1 5\n3 5\n4 1\n')
    assert got.returncode == 0 and got.stdout == '2\n3\n', (got.returncode, got.stdout, got.stderr[-250:])
    print(mode, 'PASS')
assert run('inv', inv + '\nint main(){return 0;}\n', ['-O2']).returncode != 0
assert run('pbds-raw', pbds, ['-O2']).returncode != 0
assert run('frac-add', frac_add, ['-O2']).returncode != 0
report = {
    'scope': 'DSU, both sum BITs and the max BIT match. Compression, ST, fraction comparison, ODT, vector order statistics and pbds match the checked queries. Fraction addition does not compile. ODT assign crashes because split(r + 1) is invalidated by split(l). The inversion BIT does not compile. Ordinary MoTeam add and delete are empty, so the answer stays 0. After a full-range add of 5, a leaf reads 4 rather than 6. No online AC.',
    'blob': '8dbb0e73c1a81acf14fb8d143b06b088a1762749',
}
(root / 'verification/wida-dsprint.json').write_text(json.dumps(report, indent=2) + '\n')
print('bounds PASS')
