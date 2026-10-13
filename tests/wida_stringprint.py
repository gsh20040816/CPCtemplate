"""Audit the self-contained pieces of the WIDA string printout."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-string.md').read_bytes()
fix = root / 'tests/fixtures/wida_stringprint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.md').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '0f160f11d0a3d00c5ec6c3e058824ae71b35e2bb'
text = blob.decode().replace('\r\n', '\n')
fences = [part.split('\n', 1)[1] for part in text.split('```')[1::2]]
kmp, zf, lcs, lcslong, doublehash, compress, mana, trie, trie01, sa, ac, pam, sam, seqt, seq = fences
out = root / 'build/wida-stringprint'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
head = '#include <bits/stdc++.h>\nusing namespace std;\n'

def run(name, code, flags, input_text=''):
    path = out / (name + '.cpp')
    path.write_text(head + code)
    exe = out / name
    compiled = subprocess.run([CXX, '-std=c++20', *flags, str(path), '-o', str(exe)], text=True, capture_output=True)
    if compiled.returncode != 0:
        compiled.stdout = ''
        return compiled
    return subprocess.run([str(exe)], input=input_text, text=True, capture_output=True, env=env, timeout=30)

zmod = r'''
template<int MOD> struct Zmod {
    int x;
    Zmod(long long v = 0) : x((int)(v % MOD)) { if (x < 0) x += MOD; }
    Zmod operator*(Zmod o) const { return 1LL * x * o.x % MOD; }
    Zmod operator+(Zmod o) const { int y = x + o.x; return y >= MOD ? y - MOD : y; }
    Zmod operator-(Zmod o) const { int y = x - o.x; return y < 0 ? y + MOD : y; }
    bool operator==(Zmod o) const { return x == o.x; }
    int val() const { return x; }
};
'''
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    kz = run('kz-' + mode, zf + r'''
int main() {
''' + kmp + r'''
    auto a = kmp("abc", "c");
    auto b = kmp("abc", "z");
    if (a != vector<int>{3} || !b.empty()) return 1;
    string s = "aaaa";
    auto z = zFunction(s);
    vector<int> expect(s.size());
    expect[0] = s.size();
    for (int i = 1; i < (int)s.size(); i++) while (i + expect[i] < (int)s.size() && s[expect[i]] == s[i + expect[i]]) expect[i]++;
    if (z != expect) return 1;
    cout << "ok\n";
}
''', flags)
    assert kz.returncode == 0 and kz.stdout == 'ok\n' and kz.stderr == ''
    small_bad = run('lcs-bad-' + mode, lcs, flags, '3 2 abc ac\n')
    assert small_bad.returncode != 0 and 'a + 1' in small_bad.stderr
    small_src = lcs.replace('cin >> n >> m >> a + 1 >> b + 1;', 'n = 3; m = 2; memcpy(a + 1, "abc", 3); memcpy(b + 1, "ac", 2);')
    small = run('lcs-' + mode, small_src, flags)
    assert small.returncode == 0 and small.stdout == '2\n'
    long = run('lcslong-' + mode, '#define maxn 100\n' + lcslong, flags, '3\n1 2 3\n3 2 1\n')
    assert long.returncode == 0 and long.stdout == '1\n'
    hs = run('hash-' + mode, zmod + doublehash + compress + r'''
int main() {
    init(8);
    String h("abc");
    auto ab = h.substring(0, 1);
    U expect1 = U('a') * base1 + U('b');
    V expect2 = V('a') * base2 + V('b');
    if (!(ab.first == expect1 && ab.second == expect2)) return 1;
    if (h.substring(0, 2).first == h.get().first) return 1;
    auto changed = h.modify(0, 'd');
    String dbc("dbc");
    if (!(changed.first == dbc.get().first && changed.second == dbc.get().second)) return 1;
    cout << compress({"ab", "bc"}) << '\n';
}
''', flags)
    assert hs.returncode == 0 and hs.stderr == '' and hs.stdout == 'abc\n'
    xortrie = trie01.replace('struct Trie', 'struct XorTrie', 1).replace('Trie(int n)', 'XorTrie(int n)', 1)
    tr = run('trie-' + mode, '#define N 200\nusing LL = long long;\n' + trie + xortrie + r'''
int main() {
    trie.init();
    trie.insert("ab"); trie.insert("abc");
    if (trie.query("ab") != 2 || trie.query("zz") != 0) return 1;
    XorTrie t(4);
    t.insert(1); t.insert(2); t.insert(3);
    if (t.query(0) != 3 || t.query(1) != 3) return 1;
    cout << "ok\n";
}
''', flags)
    assert tr.returncode == 0 and tr.stdout == 'ok\n'
    suffix = run('sa-' + mode, sa + r'''
int main() {
    SuffixArray a("banana");
    vector<int> expect_sa = {5, 3, 1, 0, 4, 2};
    vector<int> expect_lc = {1, 3, 0, 0, 2};
    if (a.sa != expect_sa || a.lc != expect_lc) return 1;
    cout << "ok\n";
}
''', flags)
    assert suffix.returncode == 0 and suffix.stdout == 'ok\n'
    acr = run('ac-' + mode, 'using LL = long long;\n' + ac + r'''
int main() {
    auto m = new ACAutomaton();
    memset(m, 0, sizeof(ACAutomaton));
    m->cntNodes = 1;
    m->insert("ab"); m->insert("bc"); m->build();
    if (m->query("abc") != 2 || m->query("abc") != 0) return 1;
    cout << "ok\n";
}
''', flags)
    assert acr.returncode == 0 and acr.stdout == 'ok\n'
    naive = seq.replace('struct SequenceAutomaton', 'struct NaiveSequence', 1).replace('SequenceAutomaton(vector<int> &in, int size)', 'NaiveSequence(vector<int> &in, int size)', 1)
    seqr = run('seq-' + mode, seqt + naive + r'''
int main() {
    vector<int> text = {1, 2, 1, 3};
    SequenceAutomaton<int> a(text);
    if (!a.contains(vector<int>{1, 1, 3}) || a.contains(vector<int>{1, 2, 2})) return 1;
    NaiveSequence b(text, 3);
    vector<int> missing = {3, 1};
    if (!b.contains(text) || b.contains(missing)) return 1;
    cout << "ok\n";
}
''', flags)
    assert seqr.returncode == 0 and seqr.stdout == 'ok\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
kmp_bad = run('kmp-bad', 'int main() {\n' + kmp + r'''
    auto a = kmp(string("aaa"), string("aa")); cout << a.size() << '\n';
}
''', ['-O1', '-g', '-D_GLIBCXX_ASSERTIONS'])
assert kmp_bad.returncode == 0 and kmp_bad.stdout == '2\n'
pamr = run('pam', pam + r'''
int main() {
    string s = "aba";
    auto p = new PalindromeAutomaton(s);
    int total = 0;
    for (int i = 0; i < (int)s.size(); i++) { p->insert(s[i], i); total += p->cnt[p->last]; }
    cout << total << ' ' << p->cntNodes - 1 << '\n';
}
''', ['-O2'])
assert pamr.returncode == 0 and pamr.stdout == '4 3\n'
samr = run('sam', sam + r'''
int main() {
    auto sam = new SuffixAutomaton();
    int p = 0;
    for (char c : string("ab")) p = sam->extend(p, c - 'a');
    cout << sam->cntNodes << ' ' << p << '\n';
}
''', ['-O2'])
assert samr.returncode == 0
report.append(dict(kmp='continues past a match', pam=pamr.stdout.strip(), sam=samr.stdout.strip()))
print('bounds PASS', flush=True)
import json
(root / 'verification/wida-stringprint.json').write_text(json.dumps(dict(
    scope='Safe KMP and the overlapping aaa/aa case return the checked positions. Z, both LCS programs, a local Zmod stand-in, trie, xor trie, suffix array, heap-allocated AC, and both subsequence automata match the checked cases. The original LCS reader does not compile. A local ACAutomaton overflows the stack. PAM reports 4 and 3 for aba. SAM.extend from 0 leaves cntNodes at 1. Manacher was not executed. No online AC.',
    blob='0f160f11d0a3d00c5ec6c3e058824ae71b35e2bb', runs=report), indent=2) + '\n')
