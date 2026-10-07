#!/usr/bin/env python3
"""Signed AC aggregation and dynamic rebuild, independent literal and online oracles."""
import hashlib
import json
import os
from pathlib import Path
import random
import selectors
import shutil
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from run_provenance import snapshot
from audit_copy_context import extract_components
from usage_examples import records
from compiler_config import CXX


def sha(data):
    return hashlib.sha256(data).hexdigest()


def datasets():
    rng = random.Random(710263)
    data = []
    for case in range(120):
        active, used, ops, want = set(), set(), [], []
        for step in range(100):
            kind = rng.randrange(3)
            if kind == 0:
                s = ''.join(rng.choice('abc') for _ in range(rng.randrange(1, 9)))
                if s in used:
                    continue
                used.add(s)
                active.add(s)
                ops.append((1, s))
            elif kind == 1 and active:
                s = rng.choice(sorted(active))
                active.remove(s)
                ops.append((2, s))
            else:
                s = ''.join(rng.choice('abcd') for _ in range(rng.randrange(1, 80)))
                ops.append((3, s))
                want.append(sum(s.startswith(p, j) for p in active for j in range(len(s))))
        data.append((f'random-{case}', ops, want))
    data.append(('official-1', [(1,'abc'),(3,'abcabc'),(2,'abc'),(1,'aba'),(3,'abababc')], [2,2]))
    data.append(('official-2', [(1,'abc'),(1,'bcd'),(1,'abcd'),(3,'abcd'),(2,'abcd'),(3,'abcd'),(2,'bcd'),(3,'abcd'),(2,'abc'),(3,'abcd')], [3,2,1,0]))
    data.append(('maximum-operations', [(3,'a')]*300000, [0]*300000))
    data.append(('maximum-chain', [(1,'a'*149999),(3,'a'*150001)], [3]))
    ps=['a'*i for i in range(1,501)]
    length=300000-sum(map(len,ps))
    data.append(('nested-wide-answer',[(1,p) for p in ps]+[(3,'a'*length)], [sum(length-len(p)+1 for p in ps)]))
    ps=[]
    for x in range(32769):
        s=''
        for _ in range(4):
            s+=chr(97+x%26)
            x//=26
        ps.append('z'+s)
    text='z'*100000
    expected=sum(text.startswith(p,j) for p in ['zzzzz'] if p in ps for j in range(len(text)))
    data.append(('many-carries',[(1,p) for p in ps]+[(3,text)], [expected]))
    for label,ops,want in data:
        assert len(ops)<=300000 and sum(len(s) for _,s in ops)<=300000,label
        seen,active=set(),set()
        for t,s in ops:
            assert s and s.isascii() and s.islower()
            if t==1:
                assert s not in seen
                seen.add(s)
                active.add(s)
            elif t==2:
                assert s in active
                active.remove(s)
        assert sum(t==3 for t,_ in ops)==len(want)
    return data


def online(exe, env):
    ops=[(1,'a'),(3,'aaa'),(1,'aa'),(3,'aaa'),(2,'a'),(3,'aaa'),(2,'aa'),(3,'aaa')]
    answers=iter([3,5,2,0])
    p=subprocess.Popen([str(exe)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,bufsize=0)
    sel=selectors.DefaultSelector()
    sel.register(p.stdout,selectors.EVENT_READ)
    try:
        p.stdin.write(f'{len(ops)}\n'.encode())
        for t,s in ops:
            p.stdin.write(f'{t} {s}\n'.encode())
            if t==3:
                assert sel.select(10),'answer not flushed before next input'
                assert p.stdout.readline()==f'{next(answers)}\n'.encode()
        p.stdin.close()
        assert p.wait(timeout=10)==0 and p.stderr.read()==b''
    finally:
        sel.close()
        if p.poll() is None:
            p.kill()
            p.wait()


def main():
    if not __debug__:
        raise RuntimeError('Python checks must stay enabled')
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='ac-weighted-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT)
    parts=extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))
    symbols=['AhoCorasick','ACWeighted','DynamicAC']
    core='\n'.join(next(p['code'] for p in parts if p['symbol']==s) for s in symbols)
    prelude=''.join('#include <'+s+'>\n' for s in ['array','cassert','iostream','iomanip','queue','random','stdexcept','string','utility','vector'])+'using namespace std;\n'
    probe=(ROOT/'tests/ac_weighted_probe.cpp').read_text()
    copied=prelude+core+'\n'+'\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler=Path(shutil.which(CXX) or CXX).resolve()
    report=dict(mode=mode,source_before_sha256=before,compiler=str(compiler),compiler_sha256=sha(compiler.read_bytes()),programs=[],mutants=[],applications=[])
    def compile(name,source,extra=()):
        cpp,exe=out/(name+'.cpp'),out/name
        cpp.write_text(source)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()))
    reference=None
    for form,source in [('header','#include "'+str(ROOT/'tests/ac_weighted_probe.cpp')+'"\n'),('copied',copied)]:
        for nd in [False,True]:
            exe,entry=compile(form+('-ndebug' if nd else '-assert'),source,['-DNDEBUG'] if nd else [])
            p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=300)
            assert p.returncode==0 and not p.stderr and p.stdout.startswith(b'PASS '),(entry,p.stdout,p.stderr[-1000:])
            if reference is None:reference=p.stdout
            assert p.stdout==reference
            entry['result']=p.stdout.decode().strip()
            report['programs'].append(entry)
            print(entry['name'],entry['result'],flush=True)
    mutations=[('lose-duplicate','sum[u] += w;','sum[u] = w;'),('omit-failure','sum[u] += sum[ac.a[u].fail];','sum[u] += 0;'),('omit-empty-boundary','long long ans = sum[0];','long long ans = 0;'),('lose-negative','ends.push_back({u, w});','ends.push_back({u, w < 0 ? 0 : w});'),('lose-merged-records','cur.push_back(move(p));','(void)p;'),('omit-group-query','ans += ac[k].query(s);','ans += 0;')]
    for name,old,new in mutations:
        assert copied.count(old)==1,(name,copied.count(old))
        exe,entry=compile(name,copied.replace(old,new),['-DNDEBUG'])
        p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=300)
        assert p.returncode==0 and not p.stderr and p.stdout==b'ORACLE_REJECT\n',(name,p.stdout,p.stderr[-1000:])
        report['mutants'].append(entry)
        print(name,'oracle rejection PASS',flush=True)
    rows={r['id']:r for r in records()}
    data=datasets()
    for example in ['example-263','example-264']:
        row=rows[example]
        chosen=symbols if example=='example-264' else symbols[:2]
        listing=prelude+'\n'.join(next(p['code'] for p in parts if p['symbol']==s) for s in chosen)+'\n'+row['snippet']
        for form,source in [('expanded',row['program']),('listing',listing),('listing-ndebug',listing)]:
            exe,entry=compile(example+'-'+form,source,['-DNDEBUG'] if form.endswith('ndebug') else [])
            entry['runs']=[]
            if example=='example-264':
                online(exe,env)
                entry['online_flush_checked']=True
                inputs=[(label,str(len(ops))+'\n'+''.join(f'{t} {s}\n' for t,s in ops),want) for label,ops,want in data]
            else:
                inputs=[]
                rng=random.Random(263)
                for i in range(160):
                    ps=[(''.join(rng.choice('abc') for _ in range(rng.randrange(7))),rng.randrange(-100,101)) for _ in range(rng.randrange(20))]
                    ts=[''.join(rng.choice('abc') for _ in range(rng.randrange(40))) for _ in range(10)]
                    want=[sum(w for p,w in ps for j in range(len(t)+1) if t.startswith(p,j)) for t in ts]
                    raw=f'{len(ps)} {len(ts)}\n'+''.join(f'"{p}" {w}\n' for p,w in ps)+''.join(f'"{t}"\n' for t in ts)
                    inputs.append((f'random-{i}',raw,want))
            for label,raw,want in inputs:
                p=subprocess.run([str(exe)],input=raw.encode(),capture_output=True,env=env,timeout=180)
                assert p.returncode==0 and not p.stderr,(example,label,p.stderr[-1000:])
                assert p.stdout.split()==[str(x).encode() for x in want],(example,label,p.stdout[:200],want[:20])
                entry['runs'].append(dict(case=label,input_sha256=sha(raw.encode()),output_sha256=sha(p.stdout)))
            report['applications'].append(entry)
            print(entry['name'],len(inputs),'inputs PASS',flush=True)
    # A buffered answer must fail the incremental input protocol.
    exe,entry=compile('missing-flush',rows['example-264']['program'].replace('<< endl;',"<< '\\n';"))
    try:
        online(exe,env)
    except AssertionError as e:
        assert str(e)=='answer not flushed before next input'
        report['protocol_mutant']='missing flush rejected by withheld next input'
    else:
        raise AssertionError('missing flush mutant accepted')
    report.update(passed=True,source_after_sha256=snapshot(ROOT),scope='Local independent signed occurrence oracles, per-state suffix weights, carries, copies/reset, empty pattern semantics, wide totals; formal legal CF710F maximum inputs and incremental flushed protocol. No online AC/rank.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('ac-weighted',mode,'PASS:',out/'report.json',flush=True)

if __name__=='__main__':
    main()
