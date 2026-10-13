"""Audit the checkable snippets in the WIDA STL printout."""
import hashlib, json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-stl.md').read_bytes()
fix = root / 'tests/fixtures/wida_stlprint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.md').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
(fix / 'README.md').write_text(
    '# WIDA STL-printout fixture\n\n'
    'main.md is the exact CRLF blob `13987c4c523997325bba88a0f9888aefac06808a` '
    'from hh2048/XCPC tree `cfdb12db6792eb2303798541fb5c760ed2bc618b`.\n\n'
    'Path: `02 - 打印稿模板汇总/12 - STL与库函数.md`.\n\n'
    'The upstream GPL-3.0 license is preserved in LICENSE. This fixture is not '
    'relicensed under the root MIT license. See docs/WIDA-STLPRINT.md.\n'
)
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '13987c4c523997325bba88a0f9888aefac06808a'
text = blob.decode().replace('\r\n', '\n')
out = root / 'build/wida-stlprint'
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

checks = r'''
int main() {
    int a[] = {1, 2, 2, 4};
    if (lower_bound(a, a + 4, 2) - a != 1) return 1;
    if (upper_bound(a, a + 4, 2) - lower_bound(a, a + 4, 2) != 2) return 1;
    if (!binary_search(a, a + 4, 4) || binary_search(a, a + 4, 3)) return 1;
    int b[4];
    iota(b, b + 4, 3);
    if (b[0] != 3 || b[3] != 6) return 1;
    vector<int> v = {2, 2, 1, 1};
    sort(v.begin(), v.end());
    v.erase(unique(v.begin(), v.end()), v.end());
    if (v != vector<int>({1, 2})) return 1;
    if (__builtin_popcount(15) != 4 || __builtin_ffs(8) != 4 || __builtin_ffs(26) != 2) return 1;
    if (__builtin_ctz(8) != 3 || bit_width(9u) != 4 || bit_width(26u) != 5) return 1;
    if (stoi("1010", nullptr, 2) != 10 || stoi("c", nullptr, 16) != 12) return 1;
    if (stoi("0x3f3f3f3f", nullptr, 0) != 1061109567) return 1;
    if (atoi("   12") != 12 || atoi("-12abc") != -12 || atoi("abc12") != 0) return 1;
    if (!is_sorted(a, a + 4) || accumulate(a, a + 4, 1) != 10) return 1;
    vector<int> p = {1, 2, 3};
    int perms = 0;
    do perms++; while (next_permutation(p.begin(), p.end()));
    if (perms != 6) return 1;
    bitset<8> x("11101001"), y("11101000");
    if ((x ^ y).to_ullong() != 1 || x.count() != 5) return 1;
    string shown = to_string(12.12);
    if (shown.find("12.12") != 0) return 1;
    cout << shown << "\n";
}
'''
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    got = run('lib-' + mode, checks, flags)
    assert got.returncode == 0 and got.stdout.startswith('12.12'), (got.returncode, got.stdout, got.stderr[-300:])
    print(mode, 'PASS')
bad = {
    'itoa': 'int main(){ char s[16]; itoa(12, s, 2); }\n',
    'tuple': 'int main(){ tuple<string,int,int> Student = {"Wida", 23, 45000); }\n',
    'deque': 'int main(){ deque<int> d; d.pop_front(1); }\n',
    'setname': 'int main(){ set<int> s; s.lower_cound(1); }\n',
    'hash': 'int main(){ pair<int,int> p; auto x = p.fi; }\n',
}
for name, code in bad.items():
    assert run(name, code, ['-O2']).returncode != 0
report = {
    'scope': 'The checked lower_bound, unique, bit functions, stoi, atoi, permutations and bitset values match. to_string(12.12) starts with 12.12. itoa, the tuple brace, deque pop_front(x), lower_cound and p.fi do not compile. No online AC.',
    'blob': '13987c4c523997325bba88a0f9888aefac06808a',
}
(root / 'verification/wida-stlprint.json').write_text(json.dumps(report, indent=2) + '\n')
print('bounds PASS')
