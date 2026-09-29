"""Full longest-palindrome and online decoded-PAM drivers, independent references."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(202609301)
mode = 'san' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
flags = ['-std=c++20', '-O2']
if mode == 'san':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
exes = {}
for problem in ['P3805', 'P5496']:
    exe = root / f'build/palindrome-{problem}-{mode}'
    subprocess.run([CXX, *flags, str(root / f'verify/luogu/{problem}.compact.cpp'), '-o', str(exe)], check=True)
    exes[problem] = exe


def run(problem, s, expected, ending='\n'):
    p = subprocess.run([str(exes[problem])], input=s + ending, text=True, capture_output=True, check=True, timeout=90)
    assert not p.stderr, p.stderr
    assert list(map(int, p.stdout.split())) == expected, (problem, s[:60], p.stdout[:200], expected[:20])


for _ in range(200):
    s = ''.join(rng.choice('abcz') for _ in range(rng.randint(1, 70)))
    longest = max(r - l for l in range(len(s)) for r in range(l + 1, len(s) + 1) if s[l:r] == s[l:r][::-1])
    run('P3805', s, [longest])
    plain = ''
    answer = []
    previous = 0
    for ch in s:
        plain += chr((ord(ch) - 97 + previous) % 26 + 97)
        previous = sum(plain[l:] == plain[l:][::-1] for l in range(len(plain)))
        answer.append(previous)
    run('P5496', s, answer, '\r\n')
print('P3805/P5496: each 200 independently reversed-substring oracles, PAM sequential decoding and CRLF input PASS', flush=True)
n = 11000000
run('P3805', 'a' * n, [n])
run('P3805', 'ab' * (n // 2), [n - 1])
# No equal adjacent characters and no repeated distance-two characters => no palindrome length >=2.
run('P3805', ('abc' * ((n + 2) // 3))[:n], [1])
print('P3805: 11000000 characters, equal, alternating and palindrome-free length>=2 closed forms PASS', flush=True)
n = 500000
# Encrypt chosen plaintext with its closed-form suffix counts; exercise online answer feedback.
encoded = ''.join(chr(97 + (-i) % 26) for i in range(n))
run('P5496', encoded, list(range(1, n + 1)), '\r')
encoded = ''.join(chr(97 + ((i % 2) - ((i + 1) // 2)) % 26) for i in range(n))
run('P5496', encoded, [(i + 2) // 2 for i in range(n)])
print('P5496: 500000 decoded equal/alternating characters, maximal distinct nodes and suffix counts PASS', flush=True)
