"""Audit the executable pieces of the WIDA dynamic-programming printout."""
import hashlib, json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-dp.md').read_bytes()
fix = root / 'tests/fixtures/wida_dpprint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.md').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
(fix / 'README.md').write_text(
    '# WIDA DP-printout fixture\n\n'
    'main.md is the exact CRLF blob `92e5005479645a57705dfbb367463b890fd4eab1` '
    'from hh2048/XCPC tree `cfdb12db6792eb2303798541fb5c760ed2bc618b`.\n\n'
    'Path: `02 - 打印稿模板汇总/09 - 动态规划.md`.\n\n'
    'The upstream GPL-3.0 license is preserved in LICENSE. This fixture is not '
    'relicensed under the root MIT license. See docs/WIDA-DPPRINT.md.\n'
)
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '92e5005479645a57705dfbb367463b890fd4eab1'
text = blob.decode().replace('\r\n', '\n')
codes = [part.split('```', 1)[0] for part in text.split('```c++')[1:]]
def pick(needle):
    found = [c for c in codes if needle in c]
    assert len(found) == 1, needle
    return found[0]
zero_one = pick('dp[i - 1][j - w[i]]')
zero_one_1d = pick('当前装第')
complete = pick('k * w[i] <= j')
complete_1d = pick('j = w[i]; j <= W')
multi = pick('j - k * w[i] < 0')
binary = pick('%lld%lld%lld')
mono = pick('memcpy')
mix = pick('s == -1')
two_cost = pick('k >= m')
group = pick('scanf("%d", &s[i])')
tree = pick('g[p]')
count = pick('cnt[i] = 1')
plan = pick('ans.push_back')
digit = pick('zero')
king = pick('st[')
hello = pick('helloworld')
bracket = pick('maxn')
ban = pick('pre==6')
out = root / 'build/wida-dpprint'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')

def run(name, code, flags, input_text=''):
    path = out / (name + '.cpp')
    path.write_text(code)
    exe = out / name
    compiled = subprocess.run([CXX, '-std=c++20', *flags, str(path), '-o', str(exe)], text=True, capture_output=True)
    if compiled.returncode != 0:
        compiled.stdout = ''
        return compiled
    return subprocess.run([str(exe)], input=input_text, text=True, capture_output=True, env=env, timeout=30)

loops = r'''
#include <bits/stdc++.h>
using namespace std;
int main() {
    int n = 2, W = 3, w[3] = {0, 1, 2}, v[3] = {0, 1, 3};
    int dp2[3][4] = {};
    int dp[4] = {};
''' + zero_one.replace('dp[', 'dp2[') + zero_one_1d + r'''
    if (dp2[2][3] != 4 || dp[3] != 4) return 1;
    int c2[3][6] = {}, c[6] = {};
    n = 1; W = 5; w[1] = 2; v[1] = 3;
''' + complete.replace('dp[', 'c2[') + complete_1d.replace('dp[', 'c[') + r'''
    if (c2[1][5] != 6 || c[5] != 6) return 1;
    int md[6] = {}, s[3] = {0, 2};
    n = 1; W = 5; w[1] = 2; v[1] = 3; s[1] = 2;
''' + multi.replace('dp[', 'md[') + '}\n' + r'''
    if (md[5] != 6) return 1;
    cout << "ok\n";
}
'''
two = r'''
#include <bits/stdc++.h>
using namespace std;
int main() {
    int n = 1, W = 5, M = 4, w = 2, m = 3, v = 7, dp[6][5] = {};
''' + two_cost + r'''
    cout << dp[2][3] << "\n";
}
'''
binary_code = r'''
#include <bits/stdc++.h>
using namespace std;
int main() {
    long long n = 1, W = 5, x, y, s, t, num = 0, w[30] = {}, v[30] = {}, dp[30] = {};
''' + binary + r'''
    cout << dp[W] << "\n";
}
'''
plan_code = '#include <bits/stdc++.h>\nusing namespace std;\n' + plan
digit_code = '#include <bits/stdc++.h>\nusing namespace std;\nusing LL = long long;\n' + digit + 'int main(){ cout << solve(20, 1) << " " << solve(10, 1) << "\\n"; }\n'
ban_code = '#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n' + ban
bracket_code = bracket
expect_ban = sum('4' not in str(i) and '62' not in str(i) for i in range(1, 21))
assert expect_ban == 18
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    got = run('loops-' + mode, loops, flags)
    assert got.returncode == 0 and got.stdout == 'ok\n', (got.returncode, got.stdout, got.stderr[-400:])
    assert run('cost-' + mode, two, flags).stdout == '7\n'
    assert run('bin-' + mode, binary_code, flags, '2 3 2\n').stdout == '6\n'
    assert run('mono-' + mode, mono, flags, '1 5\n2 3 2\n').stdout == '6\n'
    assert run('mix-' + mode, mix, flags, '2 5\n2 3 -1\n2 1 0\n').stdout == '4\n'
    assert run('group-' + mode, group, flags, '1 3\n2\n1 1\n1 1\n').stdout == '1\n'
    assert run('tree-' + mode, tree, flags, '2 3\n1 1 -1\n1 5 1\n').stdout == '6\n'
    assert run('count-' + mode, count, flags, '2 1\n1 1\n1 1\n').stdout == '2\n'
    assert run('count-gap-' + mode, count, flags, '2 2\n1 5\n2 1\n').stdout == '1\n'
    assert run('plan-' + mode, plan_code, flags, '1\n2 3\n1 1\n2 3\n').stdout == '2\n1 2 \n'
    assert run('digit-' + mode, digit_code, flags).stdout == '12 2\n'
    assert run('king-' + mode, king, flags, '2 1\n').stdout == '4\n'
    assert run('king0-' + mode, king, flags, '2 0\n').stdout == '1\n'
    assert run('king2-' + mode, king, flags, '2 2\n').stdout == '0\n'
    assert run('hello-' + mode, hello, flags, 'HelloWorld\n').stdout == '1\n'
    assert run('ban-' + mode, ban_code, flags, '1\n1 20\n').stdout == '18\n'
    print(mode, 'PASS')
broken = run('multi-broken', '#include <bits/stdc++.h>\nusing namespace std;\nint main(){\n' + multi + '\n}\n', ['-O2'])
assert broken.returncode != 0
bad_bracket = run('bracket', bracket_code, ['-O1', '-g', '-fsanitize=address,undefined'], '()')
assert bad_bracket.returncode != 0 and 'index -1' in bad_bracket.stderr
report = {
    'scope': 'The checked knapsack loops, monotone queue, mixture, group, tree, counts, reconstruction, digit DP, kings, helloworld and the 4/62 counter match. The first multiple-knapsack loop does not compile. Bracket matching reads dp[-1]. No online AC.',
    'blob': '92e5005479645a57705dfbb367463b890fd4eab1',
}
(root / 'verification/wida-dpprint.json').write_text(json.dumps(report, indent=2) + '\n')
print('bounds PASS')
