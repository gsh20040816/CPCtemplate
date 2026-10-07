#!/usr/bin/env python3
"""WIDA dominance and issue11 rectangle-sum adapters, with independent oracles."""
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from run_provenance import snapshot
from usage_examples import records
from compiler_config import CXX


def sha(x):
    return hashlib.sha256(x).hexdigest()


def dominance_cases():
    rng=random.Random(269)
    cases=[]
    for case in range(80):
        points=[]
        ops=[]
        want=[]
        for i in range(500):
            pool=[-2147483648,-1,0,1,2147483647]
            x,y=(rng.choice(pool),rng.choice(pool)) if case%3==0 else (rng.randrange(-40,41),rng.randrange(-40,41))
            if i%3:
                ops.append(f'1 {x} {y}')
                points.append((x,y))
            else:
                ops.append(f'2 {x} {y}')
                want.append(sum(a<=x and b<=y for a,b in points))
        cases.append((f'dominance-{case}',str(len(ops))+'\n'+'\n'.join(ops)+'\n',want))
    # Full signed-coordinate limits are API semantics, not P4148 inputs.
    ops=['2 2147483647 2147483647']
    for _ in range(100000):ops.append('1 -2147483648 -2147483648')
    ops+=['2 -2147483648 -2147483648','2 2147483647 2147483647']
    cases.append(('dominance-duplicates',str(len(ops))+'\n'+'\n'.join(ops)+'\n',[0,100000,100000]))
    return cases


def rectangle_cases():
    rng=random.Random(4148269)
    cases=[]
    def encode(name,n,ops,answers=None):
        lines=[str(n)]
        last=0
        points={}
        want=[]
        for op in ops:
            lines.append(str(op[0])+' '+' '.join(str(x^last) for x in op[1:]))
            if op[0]==1:
                _,x,y,w=op
                points[x,y]=points.get((x,y),0)+w
            else:
                _,x1,y1,x2,y2=op
                last=answers[len(want)] if answers is not None else sum(w for (x,y),w in points.items() if x1<=x<=x2 and y1<=y<=y2)
                want.append(last)
        lines.append('3')
        cases.append((name,'\n'.join(lines)+'\n',want))
    for case in range(60):
        ops=[(2,1,1,100,100)]
        for i in range(600):
            if i%3:
                ops.append((1,rng.randrange(1,101),rng.randrange(1,101),rng.randrange(1,1001)))
            else:
                x1,x2=sorted([rng.randrange(1,101),rng.randrange(1,101)])
                y1,y2=sorted([rng.randrange(1,101),rng.randrange(1,101)])
                ops.append((2,x1,y1,x2,y2))
        encode(f'xor-{case}',100,ops)
    ops=[]
    for i in range(1,100001):
        ops.extend([(1,i,i,1),(2,1,1,i,i)])
    encode('200000-online-ops',500000,ops,list(range(1,100001)))
    ops=[(1,i,500001-i,1) for i in range(1,199999)]
    ops.extend([(1,500000,500000,2147483647-199998),(2,1,1,500000,500000)])
    encode('199999-distinct-intmax',500000,ops,[2147483647])
    return cases


def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='kd-range-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT)
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],scope='Independent point-map, duplicate-count and XOR-stream oracles. Local only, not judge acceptance/resource measurement.')
    header=(ROOT/'src/compact/kd_tree_sum.hpp').read_text().replace('#pragma once\n','')
    probe=(ROOT/'tests/kd_tree_sum.cpp').read_text()
    probe='\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    probe=probe.replace('assert(', 'require(').replace('int main()','void run_cases()')
    prelude='#include <iostream>\n#include <stdexcept>\nvoid require(bool ok)\n{\n    if (!ok) throw std::runtime_error("ORACLE_REJECT");\n}\n'
    probe=prelude+probe+'''\nint main()
{
    try
    {
        run_cases();
        KDTreeSum<long long> s;
        s.add(-1, -1, 7);
        auto t = s;
        s = KDTreeSum<long long>();
        require(s.query(-1, -1, -1, -1) == 0);
        require(t.query(-1, -1, -1, -1) == 7);
        t.add(-1, -1, -7);
        require(t.query(-1, -1, -1, -1) == 0);
        require(t.a.size() == 2);
    }
    catch (const std::runtime_error &)
    {
        std::cout << "ORACLE_REJECT\\n";
    }
}
'''
    def compile(name,source,extra=()):
        cpp=out/(name+'.cpp');exe=out/name;cpp.write_text(source)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()),runs=[])
    for form,core in [('header','#include "'+str(ROOT/'src/compact/kd_tree_sum.hpp')+'"\n'),('copied',header)]:
        for release in [False,True]:
            name=form+('-ndebug' if release else '-assert')
            exe,entry=compile(name,core+'\n'+probe,['-DNDEBUG'] if release else [])
            start=time.monotonic();p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=300)
            assert p.returncode==0 and not p.stderr and b'PASS' in p.stdout and b'ORACLE_REJECT' not in p.stdout,(name,p.returncode,p.stdout,p.stderr[-1000:])
            entry.update(output_sha256=sha(p.stdout),result=p.stdout.decode().strip(),elapsed_seconds=time.monotonic()-start)
            report['programs'].append(entry);print(name,'PASS',flush=True)
    for name,old,new in [('overwrite-duplicate','a[p].value += delta;','a[p].value = delta;'),('open-upper-bound','a[p].high[d] < low[d]','a[p].high[d] <= low[d]'),('no-rebuild','if (4LL * heavy <= 3LL * a[p].size) return p;','if (heavy >= 0) return p;')]:
        assert header.count(old)==1
        exe,entry=compile(name,header.replace(old,new)+'\n'+probe,['-DNDEBUG'])
        p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=300)
        assert p.returncode==0 and not p.stderr and p.stdout==b'ORACLE_REJECT\n',(name,p.stdout,p.stderr[-1000:])
        entry.update(independent_oracle_rejected=True);report['mutants'].append(entry);print(name,'ORACLE_REJECT',flush=True)
    for example,cases in [('example-269',dominance_cases()),('example-114',rectangle_cases())]:
        row=next(r for r in records() if r['id']==example)
        prelude='#include <iostream>\n#include <climits>\n'
        for form,source in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('expanded',row['program']),('minimal-copy',prelude+header+'\n'+row['snippet'])]:
            exe,entry=compile(example+'-'+form,source)
            for name,inp,want in cases:
                start=time.monotonic();p=subprocess.run([str(exe)],input=inp.encode(),capture_output=True,env=env,timeout=180)
                assert p.returncode==0 and not p.stderr,(example,form,name,p.returncode,p.stderr[-1000:])
                assert list(map(int,p.stdout.split()))==want,(example,form,name)
                entry['runs'].append(dict(case=name,input_sha256=sha(inp.encode()),output_sha256=sha(p.stdout),elapsed_seconds=time.monotonic()-start,passed=True))
            report['programs'].append(entry);print(example,form,len(cases),'PASS',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT))
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('kd-range',mode,'PASS:',out/'report.json',flush=True)

if __name__=='__main__':main()
