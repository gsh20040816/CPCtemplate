"""Audit the self-contained pieces of the WIDA tree printout."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-tree.md').read_bytes()
fix = root / 'tests/fixtures/wida_treeprint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.md').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '40c98911328d95e41e3645a8f32ccb774c0cbd32'
text = blob.decode().replace('\r\n', '\n')
fences = [part.split('\n', 1)[1] for part in text.split('```')[1::2]]
dia, big, cent, hld, lift, weighted, cross, dsu = fences
assert 'return dep[root];' in dia and 'diam = d1[center] + up[center] + 1' in big
assert 'vis.resize(n);' in big and 'color[u]' in dsu and 'Flow' not in cent
out = root / 'build/wida-treeprint'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
bare = subprocess.run([CXX, '-std=c++20', '-x', 'c++', '-c', '-'], input=cent, text=True, capture_output=True)
assert bare.returncode != 0

def build(name, code, flags):
    path = out / (name + '.cpp')
    path.write_text('#include <bits/stdc++.h>\nusing namespace std;\n' + code)
    exe = out / name
    subprocess.run([CXX, '-std=c++20', *flags, str(path), '-o', str(exe)], check=True)
    return exe

dia_main = dia + r'''
int main() {
    Tree one(1);
    Tree edge(2); edge.add(1, 2);
    Tree path(4); path.add(1, 2); path.add(2, 3); path.add(3, 4);
    Tree star(4); star.add(1, 2); star.add(1, 3); star.add(1, 4);
    Tree forest(4); forest.add(1, 2); forest.add(3, 4);
    cout << one.getlen(1) << ' ' << edge.getlen(1) << ' ' << path.getlen(1) << ' '
         << star.getlen(2) << ' ' << forest.getlen(1) << ' ' << forest.getlen(3) << '\n';
}
'''
big_main = big + r'''
int main() {
    Tree path(4);
    path.add(1, 2, 1); path.add(2, 3, 1); path.add(3, 4, 1);
    path.dfs(1, 0); path.dfs1(1, 0); path.dfs2(1, 0); path.getCenter();
    Tree edge(2);
    edge.add(1, 2, 5);
    edge.dfs(1, 0); edge.dfs1(1, 0); edge.dfs2(1, 0); edge.getCenter();
    cout << path.center << ' ' << path.radius << ' ' << path.diam << ' '
         << edge.center << ' ' << edge.radius << ' ' << edge.diam << '\n';
}
'''
cog_main = big + r'''
int main() {
    Tree t(4);
    t.add(1, 2, 1); t.add(2, 3, 1); t.add(3, 4, 1);
    t.getCog();
    cout << t.cog << '\n';
}
'''
lca_main = hld + r'''
static pair<int, int> brute(const vector<int> &fa, int x, int y) {
    vector<int> px, py;
    for (int v = x; v; v = fa[v]) px.push_back(v);
    for (int v = y; v; v = fa[v]) py.push_back(v);
    int i = (int)px.size() - 1, j = (int)py.size() - 1, meet = px[i];
    while (i >= 0 && j >= 0 && px[i] == py[j]) { meet = px[i]; i--; j--; }
    return {meet, i + 1 + j + 1};
}
int main() {
    HLD t(6);
    vector<pair<int, int>> edges = {{1, 2}, {2, 3}, {3, 4}, {3, 5}, {5, 6}};
    vector<vector<int>> g(7);
    for (auto [x, y] : edges) { t.add(x, y); g[x].push_back(y); g[y].push_back(x); }
    vector<int> fa(7), seen(7), st = {1}; seen[1] = 1;
    for (int i = 0; i < (int)st.size(); i++) for (int y : g[st[i]]) if (!seen[y]) {
        seen[y] = 1; fa[y] = st[i]; st.push_back(y);
    }
    t.work(1);
    for (int x = 1; x <= 6; x++) for (int y = 1; y <= 6; y++) {
        auto [meet, edges] = brute(fa, x, y);
        if (t.lca(x, y) != meet || t.clac(x, y) != edges) return 1;
    }
    cout << "ok\n";
}
'''
lift_main = lift.replace('struct Tree', 'struct Lift', 1).replace('Tree(int n)', 'Lift(int n)', 1) + r'''
static pair<int, int> brute(const vector<int> &fa, int x, int y) {
    vector<int> px, py;
    for (int v = x; v; v = fa[v]) px.push_back(v);
    for (int v = y; v; v = fa[v]) py.push_back(v);
    int i = (int)px.size() - 1, j = (int)py.size() - 1, meet = px[i];
    while (i >= 0 && j >= 0 && px[i] == py[j]) { meet = px[i]; i--; j--; }
    return {meet, i + 1 + j + 1};
}
int main() {
    Lift t(4);
    t.add(1, 2); t.add(2, 3); t.add(3, 4);
    t.work(1);
    vector<int> fa = {0, 0, 1, 2, 3};
    for (int x = 1; x <= 4; x++) for (int y = 1; y <= 4; y++) {
        auto [meet, edges] = brute(fa, x, y);
        if (t.lca(x, y) != meet || t.clac(x, y) != edges) return 1;
    }
    cout << "ok\n";
}
'''
w_main = weighted.replace('struct Tree', 'struct WTree', 1).replace('Tree(int n)', 'WTree(int n)', 1) + r'''
int main() {
    WTree t(4);
    t.add(1, 2, 3); t.add(2, 3, 9); t.add(3, 4, 4);
    t.work(1);
    cout << t.clac(4, 2) << ' ' << t.query(4, 2) << ' ' << t.query(4, 1) << ' ' << t.query(2, 2) << '\n';
}
'''
cross_main = hld + r'''
HLD *cur;
int lca(int x, int y) { return cur->lca(x, y); }
int clac(int x, int y) { return cur->clac(x, y); }
#define dep (cur->dep)
''' + cross + r'''
#undef dep
int main() {
    HLD t(5);
    cur = &t;
    for (auto [x, y] : vector<pair<int, int>>{{1, 2}, {2, 3}, {3, 4}, {4, 5}}) t.add(x, y);
    t.work(1);
    auto nodes = [&](int x, int y) {
        int z = t.lca(x, y); set<int> s;
        for (int v = x; ; v = t.parent[v]) { s.insert(v); if (v == z) break; }
        for (int v = y; ; v = t.parent[v]) { s.insert(v); if (v == z) break; }
        return s;
    };
    auto count = [&](int x, int y, int X, int Y) {
        auto a = nodes(x, y), b = nodes(X, Y); int c = 0;
        for (int v : a) if (b.count(v)) c++;
        return c;
    };
    cout << intersection(1, 5, 2, 4) << ' ' << count(1, 5, 2, 4) << ' '
         << intersection(1, 2, 4, 5) << ' ' << count(1, 2, 4, 5) << '\n';
}
'''
dsu_main = 'using LL = long long;\nvector<int> color;\n' + dsu + r'''
int main() {
    color = {0, 1, 1, 2};
    HLD t(3);
    t.add(1, 2); t.add(1, 3);
    t.dfs1(1, 0); t.dfs2(1, 0, 1);
    cout << t.ans[1] << ' ' << t.ans[2] << ' ' << t.ans[3] << '\n';
}
'''
report = []
flags_list = [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]
for mode, flags in flags_list:
    assert subprocess.run([build('dia-' + mode, dia_main, flags)], text=True, capture_output=True, env=env, timeout=30, check=True).stdout == '0 1 3 2 1 1\n'
    assert subprocess.run([build('big-' + mode, big_main, flags)], text=True, capture_output=True, env=env, timeout=30, check=True).stdout == '2 2 4 1 5 6\n'
    assert subprocess.run([build('lca-' + mode, lca_main, flags)], text=True, capture_output=True, env=env, timeout=30, check=True).stdout == 'ok\n'
    assert subprocess.run([build('lift-' + mode, lift_main, flags)], text=True, capture_output=True, env=env, timeout=30, check=True).stdout == 'ok\n'
    assert subprocess.run([build('w-' + mode, w_main, flags)], text=True, capture_output=True, env=env, timeout=30, check=True).stdout == '2 9 9 0\n'
    assert subprocess.run([build('cross-' + mode, cross_main, flags)], text=True, capture_output=True, env=env, timeout=30, check=True).stdout == '3 3 0 0\n'
    assert subprocess.run([build('dsu-' + mode, dsu_main, flags)], text=True, capture_output=True, env=env, timeout=30, check=True).stdout == '1 1 2\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
cog = build('cog', cog_main, ['-O1', '-g', '-D_GLIBCXX_ASSERTIONS'])
bad = subprocess.run([cog], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'size()' in bad.stderr
report.append(dict(cog=bad.stderr.strip().splitlines()[-1]))
print('cog PASS', flush=True)
import json
(root / 'verification/wida-treeprint.json').write_text(json.dumps(dict(
    scope='Unweighted diameter lengths match. Weighted radius matches, but diam adds one. getCog sizes vis to n and the library assertion rejects vis[n]. HLD and binary LCA match parent walks. Weighted query returns the max edge, not the weight sum. Path intersection counts nodes. DSU-on-tree answers 1 1 2 after color and LL are supplied. The centroid snippet does not compile alone. No online AC.',
    blob='40c98911328d95e41e3645a8f32ccb774c0cbd32', runs=report), indent=2) + '\n')
