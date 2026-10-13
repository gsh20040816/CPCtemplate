"""Check whether WIDA maintainL/maintainR can be instantiated."""
import subprocess
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
src = (root / 'tests/fixtures/wida_lazy/04.cpp').read_text()
tree = src.split('struct Tag', 1)[0]
out = root / 'build/wida-maintain'
out.mkdir(parents=True, exist_ok=True)
head = '#include <bits/stdc++.h>\nusing namespace std;\nconstexpr int inf = 1000000000;\n'
plain = head + tree + r'''
struct Tag { int x = 0; void apply(const Tag&) & {} };
struct Info {
    int x = 0;
    void apply(const Tag&) & {}
};
Info operator+(const Info&, const Info& b) { return b; }
int main() {
    LazySegmentTree<Info, Tag> t(2);
    t.maintainL();
}
'''
rich = head + tree + r'''
struct Tag { int x = 0; void apply(const Tag&) & {} };
struct Info {
    int difl = 0, difr = 0;
    int maxlowl = -inf, maxlowr = -inf, max = -inf, maxl = -1, maxr = -1, x = 0;
    void apply(const Tag&) & {}
    friend Info operator+(Info a, Info b) {
        Info c;
        c.max = std::max(a.max, b.max);
        c.maxl = a.max >= b.max ? a.maxl : b.maxl;
        c.maxr = a.max >= b.max ? a.maxr : b.maxr;
        return c;
    }
};
int main() {
    vector<Info> a(2);
    a[0].maxlowl = 5; a[0].maxlowr = 8;
    a[1].maxlowl = 1; a[1].maxlowr = 9;
    LazySegmentTree<Info, Tag> t(a);
    t.maintainL();
    cout << t.info[2].max << ' ' << t.info[2].maxl << ' ' << t.info[2].maxlowl << '\n';
    cout << t.info[3].max << ' ' << t.info[3].maxl << '\n';
    LazySegmentTree<Info, Tag> u(a);
    u.maintainR();
    cout << u.info[3].max << ' ' << u.info[3].maxlowr << '\n';
}
'''

def run(name, code, flags):
    path = out / (name + '.cpp')
    path.write_text(code)
    exe = out / name
    compiled = subprocess.run([CXX, '-std=c++20', *flags, str(path), '-o', str(exe)], text=True, capture_output=True)
    if compiled.returncode != 0:
        compiled.stdout = ''
        return compiled
    return subprocess.run([str(exe)], text=True, capture_output=True, timeout=30)

for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    bad = run('plain-' + mode, plain, flags)
    assert bad.returncode != 0 and 'difl' in bad.stderr
    got = run('rich-' + mode, rich, flags)
    assert got.returncode == 0 and got.stdout == '5 0 -1000000000\n1 1\n1 -1000000000\n', (got.returncode, got.stdout, got.stderr[-400:])
    print(mode, 'PASS')
print('bounds PASS')
