#!/usr/bin/env python3
"""Independent all-pairs tree-distance oracle, including forced-online decoding."""
from pathlib import Path
import json, random, subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
B = ROOT / 'build/dynamic-diameter'
B.mkdir(parents=True, exist_ok=True)
SAN = '--sanitize' in sys.argv
flags = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if SAN else ['-O2']
compiler = '/opt/homebrew/bin/g++-16'
header = (ROOT / 'src/compact/dynamic_diameter.hpp').read_text()
source = (ROOT / 'verify/loj/3163.compact.cpp').read_text()
expanded = source.replace('#include "../../src/compact/dynamic_diameter.hpp"', header)
(B / '3163.cpp').write_text(expanded)
executables = []
for kind, src, extra in [('header', ROOT / 'verify/loj/3163.compact.cpp', []), ('ndebug', ROOT / 'verify/loj/3163.compact.cpp', ['-DNDEBUG']), ('expanded', B / '3163.cpp', [])]:
    exe = B / (kind + ('-san' if SAN else ''))
    subprocess.run([compiler, '-std=c++20', *flags, *extra, str(src), '-o', str(exe)], check=True)
    executables.append(exe)
def run(data, expected):
    for exe in executables:
        out = subprocess.run([str(exe)], input=data, text=True, capture_output=True, timeout=30, check=True).stdout.split()
        assert list(map(int, out)) == expected, (exe, data, out, expected)
run('4 3 2000\n1 2 100\n2 3 1000\n2 4 1000\n2 1030\n1 1020\n1 890\n', [2030,2080,2050])
run('10 10 10000\n1 9 1241\n5 6 1630\n10 5 1630\n2 6 853\n10 1 511\n5 3 760\n8 3 1076\n4 10 1483\n7 10 40\n8 2051\n5 6294\n5 4168\n7 1861\n0 5244\n6 5156\n3 3001\n8 5267\n5 3102\n8 3623\n', [6164,7812,8385,6737,6738,7205,6641,7062,6581,5155])
rng = random.Random(3163)
for case in range(150):
    n = rng.randrange(2, 30)
    w = rng.choice([1, 2, 100, 20000000000000])
    es = [[u, rng.randrange(u), rng.randrange(w)] for u in range(1, n)]
    rng.shuffle(es)
    lines = [f'{n} 60 {w}'] + [f'{u+1} {v+1} {c}' for u,v,c in es]
    ans = []
    last = 0
    for q in range(60):
        d, e = rng.randrange(n-1), rng.randrange(w)
        lines.append(f'{d} {e}')
        es[(d + last) % (n-1)][2] = (e + last) % w
        g = [[] for _ in range(n)]
        for u,v,c in es:
            g[u].append((v,c))
            g[v].append((u,c))
        def distances(u, parent, dist):
            return max([dist] + [distances(v,u,dist+c) for v,c in g[u] if v != parent])
        last = max(distances(u,-1,0) for u in range(n))
        ans.append(last)
    run('\n'.join(lines)+'\n', ans)
report = {'status':'pass', 'mode':'sanitizer' if SAN else 'normal', 'drivers':['header','ndebug','expanded'], 'official_samples':2, 'random_forced_online_cases':150, 'queries_per_random_case':60, 'oracle':'independent all-pairs recursive distance enumeration', 'online_status':'not submitted'}
(ROOT / ('verification/dynamic-diameter-driver-' + report['mode'] + '.json')).write_text(json.dumps(report,indent=2)+'\n')
print(report)
