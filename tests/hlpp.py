import hashlib
import json
import os
import random
import subprocess
import sys
from pathlib import Path
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from usage_examples import records
from audit_copy_context import candidate, extract_components
san = '--sanitize' in sys.argv
mode = 'sanitizer' if san else 'normal'
work = root / 'build/hlpp' / mode
work.mkdir(parents=True, exist_ok=True)
flags = ['-std=c++20', '-O1' if san else '-O2']
if san:
    flags += ['-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
rows = [r for r in records() if r['id'] in ['example-383','example-384']]
row = rows[0]
components = {r['symbol']: r for r in extract_components(json.loads((root / 'docs/catalog.json').read_text()))}
copy = candidate(row, ['HLPP'], components)['program']
(root / 'build/hlpp/P4722.cpp').write_text(copy)
commands = []
def compile(src, exe, extra=()):
    cmd = [CXX, *flags, *extra, str(src), '-o', str(exe)]
    commands.append(cmd)
    subprocess.run(cmd, check=True, capture_output=True, text=True)
def run(exe, data=''):
    p = subprocess.run([str(exe)], input=data, text=True, capture_output=True, env=env, timeout=120)
    assert p.returncode == 0, p.stderr
    return p.stdout
core_source = (root / 'tests/hlpp.cpp').read_text().replace('#include "../src/compact/hlpp.hpp"', copy.split('int main()')[0])
core = {}
for form in ['header', 'ndebug', 'copied']:
    src = root / 'tests/hlpp.cpp'
    exe = work / ('core-' + form)
    if form == 'copied':
        src = exe.with_suffix('.cpp')
        src.write_text(core_source)
    compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
    core[form] = run(exe).strip()
    print(mode, form, core[form], flush=True)
def parse(data):
    a = list(map(int,data.split()))
    n,m,s,t = a[:4]
    edges = list(zip(a[4::3],a[5::3],a[6::3]))
    return n,m,s,t,edges

def brute(n,s,t,edges):
    return min(sum(c for u,v,c in edges if mask>>(u-1)&1 and not mask>>(v-1)&1) for mask in range(1<<n) if mask>>(s-1)&1 and not mask>>(t-1)&1)

cases = [('7 14 1 7\n1 2 5\n1 3 6\n1 4 5\n2 3 2\n2 5 3\n3 2 2\n3 4 3\n3 5 3\n3 6 7\n4 6 5\n5 6 1\n6 5 1\n5 7 8\n6 7 7\n',14),('10 16 1 2\n1 3 2\n1 4 2\n5 2 2\n6 2 2\n3 5 1\n3 6 1\n4 5 1\n4 6 1\n1 7 2147483647\n9 2 2147483647\n7 8 2147483647\n10 9 2147483647\n8 5 2\n8 6 2\n3 10 2\n4 10 2\n',8),('2 1 1 2\n1 2 9223372036854775807\n',9223372036854775807)]
rng = random.Random(4722)
for trial in range(150):
    n = rng.randrange(2,9)
    s,t = rng.sample(range(1,n+1),2)
    edges = [(rng.randrange(1,n+1),rng.randrange(1,n+1),rng.randrange(1000)) for _ in range(rng.randrange(45))]
    data = f'{n} {len(edges)} {s} {t}\n' + ''.join(f'{u} {v} {c}\n' for u,v,c in edges)
    cases.append((data,brute(n,s,t,edges)))
# Independent source/sink cuts and explicit paths prove these maximum-scale cases.
for shape in ['dense','dead','chain']:
    n = 1200
    edges = []
    if shape == 'chain':
        edges = [(i,i+1,17) for i in range(1,n)]
        want = 17
    else:
        edges = [(1,i,10**9) for i in range(2,n)]
        if shape == 'dense': edges += [(i,n,1) for i in range(2,n)]
        want = n-2 if shape == 'dense' else 0
    while len(edges) < 120000:
        u,v = rng.sample(range(2,n),2)
        edges.append((u,v,10**9))
    cases.append((f'{n} {len(edges)} 1 {n}\n'+''.join(f'{u} {v} {c}\n' for u,v,c in edges),want))
usage = {}
for row in rows:
    forms = {}
    for form in ['header','ndebug','expanded','copied']:
        src = root / row['driver']
        exe = work / (row['id']+'-'+form)
        if form in ['expanded','copied']:
            src = exe.with_suffix('.cpp')
            src.write_text(row['program'] if form == 'expanded' else candidate(row,['HLPP'],components)['program'])
        compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
        for data,want in cases:
            out = run(exe,data).split()
            assert int(out[0]) == want
            if row['id']=='example-384':
                n,m,s,t,edges = parse(data)
                assert len(out) == m+2
                fs = list(map(int,out[1:-1]))
                cut = list(map(int,out[-1]))
                assert len(cut)==n and cut[s-1]==1 and cut[t-1]==0
                net=[0]*(n+1)
                for (u,v,c),f in zip(edges,fs):
                    assert 0<=f<=c
                    net[u]-=f
                    net[v]+=f
                assert all(net[u] == (-want if u==s else want if u==t else 0) for u in range(1,n+1))
                assert sum(c for u,v,c in edges if cut[u-1] and not cut[v-1]) == want
        forms[form]=len(cases)
        print(mode,row['id'],form,'PASS',flush=True)
    usage[row['id']]=dict(program_sha256=row['program_sha256'],forms=forms)
mutants={}
if not san:
    for name,old,new in [('reverse-residual','e[id ^ 1].cap += f;','e[id ^ 1].cap += 0;'),('stranded-excess','u == s || u == t || !ex[u]','u == s || u == t || !ex[u] || h[u] >= n'),('flow-plan','e[id].initial - e[id].cap','e[id].cap')]:
        assert old in core_source
        src=work/('mutant-'+name+'.cpp')
        exe=src.with_suffix('')
        src.write_text(core_source.replace(old,new))
        compile(src,exe,['-D_GLIBCXX_ASSERTIONS'])
        try:
            p=subprocess.run([str(exe)],capture_output=True,timeout=15)
            assert p.returncode!=0,name
            mutants[name]='detected'
        except subprocess.TimeoutExpired:
            mutants[name]='detected by termination timeout'
files=['src/compact/hlpp.hpp','tests/hlpp.cpp','tests/hlpp.py']+[r['driver'] for r in rows]
report=dict(status='pass',mode=mode,commands=commands,core=core,usage=usage,mutants=mutants,source_sha256={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files},scope='Independent cut enumeration plus capacity/conservation/min-cut witness checks; two official samples, max n/m dense/stranded/chain construction; OJ/ranking evidence separate.')
(root/f'verification/hlpp-{mode}.json').write_text(json.dumps(report,indent=2)+'\n')
