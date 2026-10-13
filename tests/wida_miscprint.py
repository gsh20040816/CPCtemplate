"""Audit the small executable pieces of the WIDA miscellaneous printout."""
import hashlib, json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-misc.md').read_bytes()
fix = root / 'tests/fixtures/wida_miscprint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.md').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
(fix / 'README.md').write_text(
    '# WIDA miscellaneous-printout fixture\n\n'
    'main.md is the exact CRLF blob `85b94a25b993c8938d736a43e4d022c2483cb2d0` '
    'from hh2048/XCPC tree `cfdb12db6792eb2303798541fb5c760ed2bc618b`.\n\n'
    'Path: `02 - 打印稿模板汇总/14 - 杂类.md`.\n\n'
    'The upstream GPL-3.0 license is preserved in LICENSE. This fixture is not '
    'relicensed under the root MIT license. See docs/WIDA-MISCPRINT.md.\n'
)
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '85b94a25b993c8938d736a43e4d022c2483cb2d0'
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
dfs, bits, poker, base, pack, multi = fences[1], fences[2], fences[3], fences[4], fences[5], fences[6]
hada, magic, lis, lis2 = fences[8], fences[9], fences[10], fences[11]
line, jos, jos2, week, window = fences[14], fences[15], fences[16], fences[17], fences[18]
out = root / 'build/wida-miscprint'
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

choose = '1 2 3\n'
hada_code = 'int main(){\n' + hada + r'''
    for (int i = 0; i < N; i++) {
        for (int j = i + 1; j < N; j++) {
            int dot = 0;
            for (int k = 0; k < N; k++) {
                int u = ans[i][k] ? 1 : -1, v = ans[j][k] ? 1 : -1;
                dot += u * v;
            }
            if (dot) return 1;
        }
    }
    cout << "ok\n";
}
'''
magic_code = 'int main(){\n' + magic + r'''
    int s = n * (n * n + 1) / 2;
    vector<int> seen(n * n + 1);
    for (int i = 1; i <= n; i++) {
        int row = 0, col = 0;
        for (int j = 1; j <= n; j++) {
            row += ans[i][j]; col += ans[j][i];
            if (seen[ans[i][j]]++) return 1;
        }
        if (row != s || col != s) return 1;
    }
    cout << "ok\n";
}
'''
lis_code = r'''
int main() {
    int n; cin >> n;
''' + lis + '}\n'
lis2_code = 'int main(){\n    int n; cin >> n;\n' + lis2 + '}\n'
jos_code = '#define repeat(i,a,b) for (int i = (a); i < (b); i++)\n' + jos + jos2 + r'''
int main() {
    if (jos(5, 2) != 3) return 1;
    cout << "ok\n";
}
'''
# The second jos overwrites the first. Test them under different names.
jos_linear = '#define repeat(i,a,b) for (int i = (a); i < (b); i++)\n' + jos + r'''
int main() { cout << jos(5, 2) << "\n"; }
'''
jos_fast = jos2 + r'''
int main() { cout << jos(5, 2) << "\n"; }
'''
week_code = week + 'int main(){ cout << week(2000, 1, 1) << "\\n"; }\n'
window_code = '#define IOS() ios::sync_with_stdio(false); cin.tie(0)\n#define MAX 20\n' + window
line_code = 'int main(){\n' + line + '}\n'
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    assert run('dfs-' + mode, 'int main(){\n' + dfs + '}\n', flags, '3 2\n' + choose).stdout == '3\n4\n5\n'
    assert run('bit-' + mode, 'int main(){\n' + bits + '}\n', flags, '3 2\n' + choose).stdout == '3\n4\n5\n'
    assert run('hada-' + mode, hada_code, flags, '2\n').stdout == 'ok\n'
    assert run('magic-' + mode, magic_code, flags, '3\n').stdout == 'ok\n'
    assert run('lis-' + mode, lis_code, flags, '4\n1 2 2 3\n').stdout == '4\n'
    assert run('lis2-' + mode, lis2_code, flags, '2\n1 1\n2 2\n').stdout == '2\n1 2 '
    assert run('jos-' + mode, jos_linear, flags).stdout == '2\n'
    assert run('jos2-' + mode, jos_fast, flags).stdout == '2\n'
    assert run('week-' + mode, week_code, flags).stdout == '6\n'
    assert run('win-' + mode, window_code, flags, '4 2\n1 3 2 4\n').stdout == '3\n3\n4\n'
    assert run('line-' + mode, line_code, flags, '1 2 3\n').stdout == '100\n200\n300\n'
    print(mode, 'PASS')
assert run('jos-raw', jos + 'int main(){return 0;}\n', ['-O2']).returncode != 0
report = {
    'scope': 'Choosing two of 1 2 3 prints 3 4 5. The order-2 Hadamard rows are orthogonal and the order-3 magic square uses 1..9 with line sum 15. Nondecreasing LIS of 1 2 2 3 has length 4. Both Josephus formulas give 2 for n=5,k=2 after repeat is defined; the printed linear version does not compile. 2000-01-01 returns weekday 6. The window maximums are 3 3 4. No online AC.',
    'blob': '85b94a25b993c8938d736a43e4d022c2483cb2d0',
}
(root / 'verification/wida-miscprint.json').write_text(json.dumps(report, indent=2) + '\n')
print('bounds PASS')
