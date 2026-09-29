"""P6139 full driver: independent document/end-position classes, not another SAM."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
mode = 'san' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
flags = ['-std=c++20', '-O2'] if mode == 'normal' else ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
source = root / f'build/P6139-{mode}.cpp'
exe = source.with_suffix('')
subprocess.run(['python3', str(root/'tools/bundle.py'), str(root/'verify/luogu/P6139.compact.cpp'), str(source)], check=True)
subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)


def run(words, expected=None):
    if expected is None:
        ends = {}
        for i, s in enumerate(words):
            for l in range(len(s)):
                for r in range(l, len(s)):
                    ends.setdefault(s[l:r+1], set()).add((i, r))
        expected = [len(ends), 1 + len({frozenset(x) for x in ends.values()})]
    p = subprocess.run([str(exe)], input=str(len(words))+'\n'+'\n'.join(words)+'\n', text=True, capture_output=True, check=True, timeout=90)
    assert not p.stderr, p.stderr
    assert list(map(int, p.stdout.split())) == expected, (words[:5], p.stdout, expected)


# Both official samples, plus the simplest suffix-language/endpos counterexample.
run(['aa', 'ab', 'bac', 'caa'], [10, 10])
run(['a'], [1, 2])
run(['ab', 'b'], [3, 4])
run(['b', 'ab', 'b'], [3, 4])
rng = random.Random(613927)
for _ in range(300):
    words = [''.join(rng.choice('abcxyz') for _ in range(rng.randint(1, 22))) for _ in range(rng.randint(1, 12))]
    run(words)
    rng.shuffle(words)
    run(words)
print('P6139: official samples and 600 independent endpos/count cases including insertion permutations PASS', flush=True)
n = 1000000
run(['a'*n], [n, n+1])
run(['a'+'b'*(n-1)], [2*n-1, 2*n-1])
# Each of the two alternating words of every length has a distinct endpos set.
h = n//2
run(['ab'*(h//2), 'ba'*(h//2)], [2*h, 2*h+1])
run(['ab']*200000 + ['abc']*200000, [6, 4])
print('P6139: million-character chain/clone-heavy input, two half-million alternating words, 400000 documents/1000000 chars PASS', flush=True)
# All binary words of length 15: all shorter binary words occur; no endpos classes merge.
words = [format(i, '015b').translate(str.maketrans('01', 'ab')) for i in range(1<<15)]
run(words, [(1<<16)-2, (1<<16)-1])
print('P6139: complete depth-15 binary trie (32768 documents, 491520 chars) PASS', flush=True)
