"""Independent frequency counts for P2709, plus full-size known answers."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import random
import subprocess

root = Path(__file__).resolve().parents[1]
build = root / 'build/ordinary-mo'
build.mkdir(parents=True, exist_ok=True)
header = root / 'src/compact/ordinary_mo.hpp'
driver = root / 'verify/luogu/P2709.compact.cpp'
source = build / 'P2709.cpp'
source.write_text(driver.read_text().replace('#include "../../src/compact/ordinary_mo.hpp"', header.read_text().replace('#pragma once\n', '')))
cases = [('6 4 3\n1 3 2 1 1 3\n1 4\n2 6\n3 5\n5 6\n', '6 9 5 2')]
rng = random.Random(2709)
for test in range(100):
    n = rng.randint(1, 80)
    k = rng.randint(1, n)
    a = [rng.randint(1, k) for _ in range(n)]
    queries = []
    answers = []
    for i in range(100):
        l, r = sorted([rng.randint(1, n), rng.randint(1, n)])
        queries.append(f'{l} {r}')
        answers.append(str(sum(x*x for x in Counter(a[l-1:r]).values())))
    cases.append((f'{n} 100 {k}\n' + ' '.join(map(str,a)) + '\n' + '\n'.join(queries) + '\n', ' '.join(answers)))
# All equal and all distinct have independent closed-form answers, including >2^31.
large = []
n = 100000
queries = [(1,n)] + [tuple(sorted([rng.randint(1,n),rng.randint(1,n)])) for _ in range(n-1)]
for equal in [True, False]:
    a = [1] * n if equal else list(range(1,n+1))
    data = f'{n} {n} {n}\n' + ' '.join(map(str,a)) + '\n' + '\n'.join(f'{l} {r}' for l,r in queries) + '\n'
    want = [str((r-l+1)**(2 if equal else 1)) for l,r in queries]
    large.append((data,want))
report = {'status':'pass','official_samples':1,'random_cases':100,'large_cases':2,'large_n_m':100000,'forms':{},'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
for mode in ['normal','sanitizer']:
    flags = ['-O2'] if mode == 'normal' else ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
    for form in ['header','ndebug','copied']:
        exe = build / ('driver-'+mode+'-'+form)
        subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(source if form=='copied' else driver),'-o',str(exe)],check=True)
        for data,want in cases:
            assert subprocess.check_output([str(exe)],input=data,text=True,timeout=30).split()==want.split()
        for data,want in large:
            assert subprocess.check_output([str(exe)],input=data,text=True,timeout=120).split()==want
        report['forms'][mode+'-'+form]='pass'
        print(mode,form,'PASS',flush=True)
(root/'verification/ordinary-mo-driver.json').write_text(json.dumps(report,indent=2)+'\n')
