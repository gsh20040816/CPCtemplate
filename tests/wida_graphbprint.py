"""Audit the executable pieces of the WIDA graph-conclusions printout."""
import hashlib, json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-graphb.md').read_bytes()
fix = root / 'tests/fixtures/wida_graphbprint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.md').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
(fix / 'README.md').write_text(
    '# WIDA graph-conclusions fixture\n\n'
    'main.md is the exact CRLF blob `aa934fd18fc4616b802f3473276cb69a6a3095bb` '
    'from hh2048/XCPC tree `cfdb12db6792eb2303798541fb5c760ed2bc618b`.\n\n'
    'Path: `02 - 打印稿模板汇总/03B - 图论常见结论及例题.md`.\n\n'
    'The upstream GPL-3.0 license is preserved in LICENSE. This fixture is not '
    'relicensed under the root MIT license. See docs/WIDA-GRAPHBPRINT.md.\n'
)
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'aa934fd18fc4616b802f3473276cb69a6a3095bb'
text = blob.decode().replace('\r\n', '\n')
codes = [part.split('```', 1)[0] for part in text.split('```c++')[1:]]
def pick(needle):
    found = [c for c in codes if needle in c]
    assert len(found) == 1, (needle, len(found))
    return found[0]
pair = pick('k - val[y]')
second = pick('num[e][0]')
tri = pick('cout << fa << " " << x << " " << y')
weighted = pick('a[k][i]')
flody = pick('flody')
bfs = pick('dis[x] + dis[y] + 1')
simple = pick('(ans - m) / 2')
anycycle = pick('二元环需删去')
dircount = pick('ans++')
dirout = pick('rotate(E.begin()')
undout = pick('ans1.push_back')
planar = pick('Impossible')
out = root / 'build/wida-graphbprint'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
head = '#include <bits/stdc++.h>\nusing namespace std;\nusing LL = long long;\n'

def run(name, code, flags, input_text=''):
    path = out / (name + '.cpp')
    path.write_text(head + code)
    exe = out / name
    compiled = subprocess.run([CXX, '-std=c++20', *flags, str(path), '-o', str(exe)], text=True, capture_output=True)
    if compiled.returncode != 0:
        compiled.stdout = ''
        return compiled
    return subprocess.run([str(exe)], input=input_text, text=True, capture_output=True, env=env, timeout=30)

pair_code = r'''
int main() {
    int n = 4, k = 4;
    vector<vector<int>> ver(n + 1);
    ver[1] = {2}; ver[2] = {1, 3}; ver[3] = {2, 4}; ver[4] = {3};
''' + pair + '}\n'
tree_code = r'''
const int N = 20;
const LL MAX18 = (LL)4e18;
#define FOR(i, a, b) for (int i = (a); i <= (b); i++)
void add(LL x, LL y);
''' + pick('point[x] += max') + r'''
void add(LL x, LL y) { ver[++tot] = y; nex[tot] = head[x]; head[x] = tot; }
int main() {
    string in = "2\n1 10\n1 2 3\n";
    stringstream ss(in);
    cin.rdbuf(ss.rdbuf());
    Solve();
}
'''
zstub = r'''
struct Z { long long x; Z(long long v = 0) : x(v) {} Z& operator+=(Z o) { x += o.x; return *this; } long long val() const { return x; } };
using PIII = tuple<int, int, int>;
const int INF = 1e9;
'''
flody_code = r'''
const int N = 8;
int dis[N][N], val[N][N];
''' + flody + r'''
int main() {
    int n = 3;
    for (int i = 1; i <= n; i++) for (int j = 1; j <= n; j++) dis[i][j] = i == j ? 0 : 1000;
    dis[1][2] = dis[2][1] = dis[2][3] = dis[3][2] = dis[3][1] = dis[1][3] = 1;
    cout << flody(n) << "\n";
}
'''
bfs_code = r'''
int main() {
    int n = 3, ans = 1000;
    vector<vector<int>> ver(n + 1);
    int dis[8], fa[8];
    ver[1] = {2, 3}; ver[2] = {1, 3}; ver[3] = {1, 2};
''' + bfs + '}\n'
simple_code = "int main() {\n" + simple + "}\n"
dir_code = r'''
int main() {
    int n = 3;
    vector<vector<int>> ver(n + 1);
    ver[1] = {2}; ver[2] = {3}; ver[3] = {1};
''' + dircount + '}\n'
self_code = r'''
int main() {
    int n = 1;
    vector<vector<int>> ver(n + 1);
    ver[1] = {1};
''' + dircount + '}\n'
miss_code = r'''
int main() {
    int n = 4;
    vector<vector<int>> ver(n + 1);
    ver[2] = {3}; ver[3] = {4}; ver[4] = {2};
''' + anycycle + '}\n'
twosat = r'''
struct TwoSat {
    int n; vector<vector<int>> e; vector<bool> ans;
    TwoSat(int n) : n(n), e(2 * n), ans(n) {}
    void add(int u, bool f, int v, bool g) { e[2 * u + !f].push_back(2 * v + g); e[2 * v + !g].push_back(2 * u + f); }
    bool work() {
        vector<int> id(2 * n, -1), dfn(2 * n, -1), low(2 * n, -1), stk; int now = 0, cnt = 0;
        auto tarjan = [&](auto self, int u) -> void {
            stk.push_back(u); dfn[u] = low[u] = now++;
            for (auto v : e[u]) if (dfn[v] == -1) { self(self, v); low[u] = min(low[u], low[v]); } else if (id[v] == -1) low[u] = min(low[u], dfn[v]);
            if (dfn[u] == low[u]) { int v; do { v = stk.back(); stk.pop_back(); id[v] = cnt; } while (v != u); ++cnt; }
        };
        for (int i = 0; i < 2 * n; i++) if (dfn[i] == -1) tarjan(tarjan, i);
        for (int i = 0; i < n; i++) { if (id[2 * i] == id[2 * i + 1]) return false; ans[i] = id[2 * i] > id[2 * i + 1]; }
        return true;
    }
    vector<bool> answer() { return ans; }
};
'''
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    assert run('pair-' + mode, pair_code, flags).stdout == '4\n'
    assert run('tree-' + mode, tree_code, flags).stdout == '14\n'
    arrays = 'int ver[M], ne[M], h[N], edge[M], tot;\n'
    second_fixed = second.replace(arrays, '', 1).replace('void Clear()', arrays + 'void Clear()', 1)
    got = run('second-' + mode, zstub + second_fixed + 'int main(){Solve();}\n', flags, '3 3 1 2\n1 2\n1 3\n3 2\n')
    assert got.returncode == 0 and got.stdout == '2\n', (got.returncode, got.stdout, got.stderr[-300:])
    assert run('floyd-' + mode, flody_code, flags).stdout == '3\n'
    weighted_code = r'''
int main() {
    int n = 3; const int mod = 1000000007;
    LL a[4][4] = {}, dis[4][4], cnt[4][4] = {};
    for (int i = 1; i <= 3; i++) for (int j = 1; j <= 3; j++) dis[i][j] = i == j ? 0 : (LL)1e15;
    a[1][2] = a[2][3] = a[3][1] = dis[1][2] = dis[2][3] = dis[3][1] = 1;
    cnt[1][2] = cnt[2][3] = cnt[3][1] = 1;
''' + weighted + r'''
    cout << Min << ' ' << ans << "\n";
}
'''
    assert run('weighted-' + mode, weighted_code, flags).stdout == '3 1\n'
    assert run('bfs-' + mode, bfs_code, flags).stdout == '3'
    assert run('simple-' + mode, simple_code, flags, '3 3\n1 2\n2 3\n3 1\n').stdout == '1\n'
    assert run('dircount-' + mode, dir_code, flags).stdout == '1\n'
    assert run('self-' + mode, self_code, flags).stdout == '1\n'
    assert run('miss-' + mode, miss_code, flags).stdout == ''
    cyc = run('und-' + mode, undout, flags, '3 3\n1 2\n2 3\n3 1\n')
    assert cyc.returncode == 0 and cyc.stdout.splitlines()[0] == '3'
    none = run('none-' + mode, undout, flags, '3 2\n1 2\n2 3\n')
    assert none.stdout == '-1\n'
    loop = run('loop-' + mode, dirout, flags, '1 1\n1 1\n')
    assert loop.returncode == 0 and loop.stdout.splitlines()[0] == '1'
    cross = run('cross-' + mode, twosat + planar, flags, '4 2\n1 3\n2 4\n')
    assert cross.returncode == 0 and set(cross.stdout.split()) == {'in', 'out'}
    nest = run('nest-' + mode, twosat + planar, flags, '4 2\n1 4\n2 3\n')
    assert nest.stdout == 'in in \n' or nest.stdout.split() == ['in', 'in']
    print(mode, 'PASS')
order = run('second-order', zstub + second + 'int main(){Solve();}\n', ['-O2'])
assert order.returncode != 0 and 'tot' in order.stderr
tri_bad = run('tri', "int main() {\n" + tri + "}\n", ['-O1', '-g', '-fsanitize=address,undefined'], '3\n010\n001\n100\n')
assert tri_bad.returncode != 0 and 'ERROR' in tri_bad.stderr
hit = run('hit', r'''
int main() {
    int n = 3;
    vector<vector<int>> ver(n + 1);
    ver[1] = {2, 3}; ver[2] = {1, 3}; ver[3] = {1, 2};
''' + anycycle + '}\n', ['-O2'])
assert hit.returncode == 0 and hit.stdout.splitlines()[0] == '3'
report = {
    'scope': 'Path pairing gives 4 when k is the vertex count. The negative-weight tree gives 14. Second-shortest counting gives 2 after the arrays are moved up. Weighted and unweighted minimum cycles on a triangle are 3, and the simple-cycle counter gives 1. Directed back-edge counting gives 1. The any-cycle search misses a component that does not contain vertex 1. The directed triangle printer does not survive ASan. Crossing chords receive different sides. No online AC.',
    'blob': 'aa934fd18fc4616b802f3473276cb69a6a3095bb',
}
(root / 'verification/wida-graphbprint.json').write_text(json.dumps(report, indent=2) + '\n')
print('bounds PASS')
