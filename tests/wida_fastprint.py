"""Audit the compilable pieces of the WIDA constant-optimization printout."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-fast.md').read_bytes()
fix = root / 'tests/fixtures/wida_fastprint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.md').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'f78e56d873d9b1297f19c70b658a2ac5a1556a6d'
text = blob.decode().replace('\r\n', '\n')
fences = [part.split('\n', 1)[1] for part in text.split('```')[1::2]]
gcd, prime, miller, rho, mont, hlpp, fio = fences
assert 'struct Montgomery {} M(10);' in rho and 'bool isprime(i64 n) {}' in rho
assert 'LL gcd' in gcd and 'h[i] += dis' not in hlpp
out = root / 'build/wida-fastprint'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
bare = subprocess.run([CXX, '-std=c++20', '-x', 'c++', '-c', '-'], input=rho, text=True, capture_output=True)
assert bare.returncode != 0

def build(name, code, flags):
    path = out / (name + '.cpp')
    path.write_text('#include <bits/stdc++.h>\nusing namespace std;\n' + code)
    exe = out / name
    subprocess.run([CXX, '-std=c++20', *flags, str(path), '-o', str(exe)], check=True)
    return exe

gcd_main = 'using LL = long long;\n' + gcd + r'''
int main() {
    for (LL a = 0; a <= 200; a++) for (LL b = 0; b <= 200; b++)
        if (gcd(a, b) != std::gcd(a, b)) return 1;
    cout << gcd(0, 0) << ' ' << gcd(-4, 6) << '\n';
}
'''
prime_main = prime + r'''
static bool trial(int n) {
    if (n < 2) return false;
    for (int i = 2; 1LL * i * i <= n; i++) if (n % i == 0) return false;
    return true;
}
int main() {
    for (int n = 0; n <= 5000; n++) if (is_prime(n) != trial(n)) return 1;
    cout << "ok\n";
}
'''
mont_main = 'using i64 = long long;\n' + mont + r'''
int main() {
    const u64 M = 1000000007;
    Montgomery g(M);
    for (u64 a = 0; a < 50; a++) for (u64 b = 0; b < 50; b++) {
        if (g.mul(a, b) != a * b % M) return 1;
        if (g.add(a, b) != (a + b) % M) return 1;
        if (g.sub(a, b) != (a + M - b) % M) return 1;
        if (b && g.div(a, b) != a * [](u64 x){ u64 r=1, p=M-2; while(p){ if(p&1) r=r*x%M; x=x*x%M; p>>=1;} return r; }(b) % M) return 1;
    }
    if (g.pow(2, 10) != 1024) return 1;
    cout << "ok\n";
}
'''
mill_main = 'using i64 = long long;\n' + miller + r'''
static bool trial(i64 n) {
    if (n < 2) return false;
    for (i64 i = 2; i * i <= n; i++) if (n % i == 0) return false;
    return true;
}
int main() {
    for (int n = 0; n <= 3000; n++) if (isprime(n) != trial(n)) {
        cout << "bad " << n << '\n';
        return 1;
    }
    cout << isprime(1000000007) << ' ' << isprime(1000000009) << ' ' << isprime(4) << '\n';
}
'''
hlpp_main = hlpp + r'''
static long long ek(int n, const vector<tuple<int, int, int>> &edges, int s, int t) {
    struct E { int to, rev, cap; };
    vector<E> e; vector<vector<int>> g(n + 1);
    auto add = [&](int u, int v, int c) {
        g[u].push_back((int)e.size()); e.push_back({v, (int)e.size() + 1, c});
        g[v].push_back((int)e.size()); e.push_back({u, (int)e.size() - 1, 0});
    };
    for (auto [u, v, c] : edges) add(u, v, c);
    long long flow = 0;
    while (true) {
        vector<int> pre(n + 1, -1); queue<int> q; q.push(s); pre[s] = -2;
        while (!q.empty()) {
            int u = q.front(); q.pop();
            for (int id : g[u]) if (e[id].cap && pre[e[id].to] == -1) { pre[e[id].to] = id; q.push(e[id].to); }
        }
        if (pre[t] == -1) break;
        int aug = INT_MAX;
        for (int v = t; v != s; v = e[e[pre[v]].rev].to) aug = min(aug, e[pre[v]].cap);
        for (int v = t; v != s; v = e[e[pre[v]].rev].to) { e[pre[v]].cap -= aug; e[e[pre[v]].rev].cap += aug; }
        flow += aug;
    }
    return flow;
}
int main() {
    vector<tuple<int, vector<tuple<int, int, int>>, int, int>> graphs = {
        {2, {{1, 2, 5}}, 1, 2}, {2, {}, 1, 2},
        {4, {{1, 2, 10}, {1, 3, 10}, {2, 3, 1}, {2, 4, 10}, {3, 4, 10}}, 1, 4},
    };
    for (auto [n, edges, s, t] : graphs) {
        PushRelabel<long long> g(n);
        for (auto [u, v, c] : edges) g.addedge(u, v, c);
        if (g.work(s, t) != ek(n, edges, s, t)) return 1;
    }
    cout << "ok\n";
}
'''
fio_main = fio + r'''
int main(int argc, char **argv) {
    if (argc > 1) { int a; Cin(a); return 0; }
    int a, b, c; Cin(a, b, c);
    Cout(a); putchar(' '); Cout(b); putchar(' '); Cout(c);
}
'''
def build(name, code, flags):
    path = out / (name + '.cpp')
    path.write_text('#include <bits/stdc++.h>\nusing namespace std;\n' + code)
    exe = out / name
    subprocess.run([CXX, '-std=c++20', *flags, str(path), '-o', str(exe)], check=True)
    return exe

report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    g = subprocess.run([build('gcd-' + mode, gcd_main, flags)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert g.stderr == '' and g.stdout == '0 2\n'
    assert subprocess.run([build('prime-' + mode, prime_main, flags)], text=True, capture_output=True, env=env, timeout=30, check=True).stdout == 'ok\n'
    assert subprocess.run([build('mont-' + mode, mont_main, flags)], text=True, capture_output=True, env=env, timeout=30, check=True).stdout == 'ok\n'
    m = subprocess.run([build('mill-' + mode, mill_main, flags)], text=True, capture_output=True, env=env, timeout=60, check=True)
    assert m.stderr == '' and m.stdout == '1 1 0\n'
    assert subprocess.run([build('hlpp-' + mode, hlpp_main, flags)], text=True, capture_output=True, env=env, timeout=30, check=True).stdout == 'ok\n'
    fio_exe = build('fio-' + mode, fio_main, flags)
    got = subprocess.run([fio_exe], input='  -12 0 34x', text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == '-12 0 34'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
proc = subprocess.Popen([str(out / 'fio-normal'), 'empty'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
try:
    proc.communicate(timeout=2)
    finished = True
except subprocess.TimeoutExpired:
    proc.kill(); proc.communicate(); finished = False
assert not finished
ub = build('fio-min', fio + 'int main() { Cout(INT_MIN); }\n', ['-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined'])
bad = subprocess.run([ub], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'negation' in bad.stderr
report.append(dict(empty='did not finish', minimum=bad.stderr.strip().splitlines()[-1]))
print('bounds PASS', flush=True)
import json
(root / 'verification/wida-fastprint.json').write_text(json.dumps(dict(
    scope='Binary gcd matches std::gcd on 0..200, and gcd(-4,6) is 2. is_prime matches trial through 5000. Montgomery add, sub, mul, div and pow match mod 1000000007 on 0..49. Miller-Rabin matches through 3000 and accepts the two 1e9 primes. HLPP matches Edmonds-Karp on three graphs. The Pollard-Rho fence is a stub and does not compile. Cin reads -12 0 34; empty input does not finish; Cout(INT_MIN) negates the minimum. No online AC.',
    blob='f78e56d873d9b1297f19c70b658a2ac5a1556a6d', runs=report), indent=2) + '\n')
