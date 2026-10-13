"""Audit the still-pending pieces of the WIDA graph printout."""
import hashlib, json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-graph.md').read_bytes()
fix = root / 'tests/fixtures/wida_graphprint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.md').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
(fix / 'README.md').write_text(
    '# WIDA graph-printout fixture\n\n'
    'main.md is the exact CRLF blob `dbb3c24936d76887af097c274703c8e0bf2d0ab6` '
    'from hh2048/XCPC tree `cfdb12db6792eb2303798541fb5c760ed2bc618b`.\n\n'
    'Path: `02 - 打印稿模板汇总/03A - 图论.md`.\n\n'
    'The upstream GPL-3.0 license is preserved in LICENSE. This fixture is not '
    'relicensed under the root MIT license. See docs/WIDA-GRAPHPRINT.md.\n'
)
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'dbb3c24936d76887af097c274703c8e0bf2d0ab6'
text = blob.decode().replace('\r\n', '\n')
fences = [part.split('\n', 1)[1] for part in text.split('```')[1::2]]
planar, color, star, blossom, twosat, uniq = fences[4], fences[10], fences[11], fences[12], fences[26], fences[27]
out = root / 'build/wida-graphprint'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
head = '#include <bits/stdc++.h>\nusing namespace std;\n'
check = uniq.split('// 主函数中增加')[0].replace('// 结构体中增加\n', '')
sat = twosat.rstrip()[:-2] + check + '};\n'

def run(name, code, flags, input_text='', timeout=30):
    path = out / (name + '.cpp')
    path.write_text(head + code)
    exe = out / name
    compiled = subprocess.run([CXX, '-std=c++20', *flags, str(path), '-o', str(exe)], text=True, capture_output=True)
    if compiled.returncode != 0:
        compiled.stdout = ''
        return compiled
    try:
        return subprocess.run([str(exe)], input=input_text, text=True, capture_output=True, env=env, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        compiled.returncode = 124
        compiled.stdout = exc.stdout or ''
        compiled.stderr = exc.stderr or ''
        return compiled

color_main = '''
int main() {
    int n = 3;
    vector<vector<int>> ver(n + 1);
    ver[1] = {2, 3}; ver[2] = {1, 3}; ver[3] = {1, 2};
''' + color + '}\n'
star_main = '''
vector<int> a, siz(8), dis(8), d(8);
int n;
''' + star + '''
int main() {
    n = 3;
    Graph::add(1, 2); Graph::add(1, 3);
    Graph::dfs(1);
    if (siz[1] != 3 || dis[2] != 1 || dis[3] != 1 || (int)a.size() != 6) return 1;
    if (!Graph::topsort()) return 1;
    Graph::clear(3);
    Graph::add(1, 2); Graph::add(2, 1);
    if (Graph::topsort()) return 1;
    cout << "ok\\n";
}
'''
sat_main = sat + '''
int main() {
    TwoSat force(1);
    force.add(0, true, 0, true);
    if (!force.work() || !force.answer()[0] || !force.check(0, 1) || force.check(1, 0)) return 1;
    TwoSat bad(1);
    bad.add(0, true, 0, true);
    bad.add(0, false, 0, false);
    if (bad.work()) return 1;
    TwoSat either(2);
    either.add(0, true, 1, true);
    either.add(0, false, 1, true);
    if (!either.work()) return 1;
    auto show = [&](TwoSat& s, int i) {
        if (s.check(2 * i, 2 * i + 1)) return '1';
        if (s.check(2 * i + 1, 2 * i)) return '0';
        return '?';
    };
    if (show(either, 0) != '?' || show(either, 1) != '1') return 1;
    cout << "ok\\n";
}
'''
cases = [('tri', '3 3\n1 2\n2 3\n3 1\n', '1\n2 1 0 '),
         ('two', '4 2\n1 2\n3 4\n', '2\n2 1 4 3 '),
         ('stem', '4 4\n1 2\n2 3\n3 1\n3 4\n', '2\n2 1 4 3 ')]
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    painted = run('color-' + mode, color_main, flags)
    assert painted.returncode == 0 and painted.stdout == 'Yes\n'
    walked = run('star-' + mode, star_main, flags)
    assert walked.returncode == 0 and walked.stdout == 'ok\n'
    for name, inp, expect in cases:
        got = run('blossom-' + name + '-' + mode, blossom, flags, inp)
        assert got.returncode == 0 and got.stdout == expect, (name, got.returncode, got.stdout)
    logic = run('sat-' + mode, sat_main, flags)
    assert logic.returncode == 0 and logic.stdout == 'ok\n'
    print(mode, 'PASS')
fragment = run('planar', planar + 'int main(){return 0;}\n', ['-O2'])
assert fragment.returncode != 0
cycle = run('bfs-cycle', 'vector<int> a,siz(8),dis(8),d(8);\nint n=3;\n' + star + 'int main(){ Graph::add(1,2); Graph::add(2,3); Graph::add(3,2); Graph::bfs(1); }\n', ['-O2'], timeout=2)
assert cycle.returncode == 124
report = {
    'scope': 'A triangle is reported bipartite because the search never starts. Chain-forward DFS and topsort match after the missing arrays are supplied; BFS does not finish on a cycle. Blossom answers are 1, 2 and 2. Two-SAT accepts the checked formulas and the uniqueness scan prints ? 1. The planar fragment does not compile. No online AC.',
    'blob': 'dbb3c24936d76887af097c274703c8e0bf2d0ab6',
}
(root / 'verification/wida-graphprint.json').write_text(json.dumps(report, indent=2) + '\n')
print('bounds PASS')
