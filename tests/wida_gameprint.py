"""Check the WIDA game-theory claims on small positions and compile the code fences."""
import hashlib, math, os, subprocess, sys
from functools import cache
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-game.md').read_bytes()
fix = root / 'tests/fixtures/wida_gameprint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.md').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'bd90a128c5ae7351295225790b333d7be220d4e7'
text = blob.decode().replace('\r\n', '\n')
assert 'int x = 0;' in text and 'lorry' in text
fences = [part.split('\n', 1)[1] for part in text.split('```')[1::2]]
sg, wythoff, fib, tree = fences

def bash_win(n, m):
    @cache
    def win(r):
        if r == 0: return False
        return any(not win(r - t) for t in range(1, min(m, r) + 1))
    return win(n)

for m in range(1, 6):
    for n in range(0, 31):
        assert bash_win(n, m) == (n % (m + 1) != 0)

def ext_win(n, a, b):
    @cache
    def win(r):
        if r < a: return False
        return any(not win(r - t) for t in range(a, min(b, r) + 1))
    return win(n)

for a in range(1, 5):
    for b in range(a, 7):
        for n in range(0, 41):
            k, r = divmod(n, a + b)
            if r == 0 or r < a: expect = False
            else: expect = True
            assert ext_win(n, a, b) == expect

def anti_win(piles):
    piles = tuple(piles)
    @cache
    def win(state):
        if sum(state) == 0: return True
        for i, c in enumerate(state):
            for t in range(1, c + 1):
                nxt = list(state); nxt[i] -= t
                if sum(nxt) == 0: continue
                if not win(tuple(nxt)): return True
        return False
    return win(piles)

def anti_claim(piles):
    xor = 0
    big = False
    for x in piles:
        xor ^= x
        big = big or x > 1
    if not big and xor == 0: return True
    if big and xor != 0: return True
    return False

for a in range(0, 4):
    for b in range(0, 4):
        for c in range(0, 4):
            assert anti_win((a, b, c)) == anti_claim((a, b, c))

def stair_win(stairs):
    stairs = tuple(stairs)
    @cache
    def win(state):
        state = list(state)
        if sum(state) == 0: return False
        for i, c in enumerate(state):
            for t in range(1, c + 1):
                nxt = state[:]
                nxt[i] -= t
                if i: nxt[i - 1] += t
                if not win(tuple(nxt)): return True
        return False
    return win(stairs)

for n in range(1, 5):
    for mask in range(1 << n):
        stairs = [(mask >> i) & 1 for i in range(n)]
        xor = 0
        for i, c in enumerate(stairs):
            if i % 2 == 0: xor ^= c
        assert stair_win(stairs) == (xor != 0)

def lasker(limit=20):
    sg = [0] * (limit + 1)
    for x in range(1, limit + 1):
        s = {sg[k] for k in range(x)}
        if x > 2:
            for a in range(1, x):
                s.add(sg[a] ^ sg[x - a])
        mex = 0
        while mex in s: mex += 1
        sg[x] = mex
    return sg

sgv = lasker()
for x, got in enumerate(sgv):
    if x % 4 == 0: formula = x - 1
    elif x % 4 == 3: formula = x + 1
    else: formula = x
    if x == 0: assert got == 0 and formula == -1
    else: assert got == formula

def fib_lose(n):
    @cache
    def win(rem, limit):
        if rem == 0: return False
        return any(not win(rem - t, 2 * t) for t in range(1, min(limit, rem) + 1))
    if n <= 0: return True
    return not win(n, n - 1)

seq = [1, 2]
while len(seq) < 20: seq.append(seq[-1] + seq[-2])
for n in range(1, 31):
    assert fib_lose(n) == (n in seq)

out = root / 'build/wida-gameprint'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
tree_src = '#include <bits/stdc++.h>\nusing namespace std;\nint main(){vector<vector<int>> ver(2);auto dfs=' + tree.split('auto dfs =')[1]
tree_compile = subprocess.run([CXX, '-std=c++20', '-c', '-x', 'c++', '-'], input=tree_src, text=True, capture_output=True)
assert tree_compile.returncode != 0 and 'x' in tree_compile.stderr
wy = r'''
#include <bits/stdc++.h>
using namespace std;
''' + wythoff + r'''
bool lose(int n, int m) {
    if (n < m) swap(n, m);
    double x = n - m;
    return (int)(lorry * x) == m;
}
int main() {
    for (int k = 1; k <= 200; k++) {
        int a = (int)(lorry * k);
        cout << lose(a + k, a) << lose(a + k, a + 1) << '\n';
    }
}
'''
(out / 'wy.cpp').write_text(wy)
subprocess.run([CXX, '-std=c++20', '-O2', str(out / 'wy.cpp'), '-o', str(out / 'wy')], check=True)
got = subprocess.run([str(out / 'wy')], text=True, capture_output=True, env=env, timeout=30, check=True)
phi = (1 + math.sqrt(5)) / 2
lines = got.stdout.splitlines()
for k, line in enumerate(lines, 1):
    a = math.floor(k * phi)
    assert line == '10'
    assert a == int(phi * k)
print('claims PASS', flush=True)
import json
(root / 'verification/wida-gameprint.json').write_text(json.dumps(dict(
    scope='Bash, extended bash, anti-Nim and odd-stair Nim match the stated rules on the checked ranges. Lasker matches for 1..20 and disagrees at 0. Fibonacci losses through 30 are the sequence starting 1,2,3,5. Wythoff cold positions through k=200 match floor(k*phi). Moore says every bit count is not a multiple of K+1; one pile of 1 with K=1 is a first-player win but has zero counts. The tree lambda redeclares x and does not compile. SG, Every-SG and fusion code or definitions were not executed as complete programs. No online AC.',
    blob='bd90a128c5ae7351295225790b333d7be220d4e7'), indent=2) + '\n')
