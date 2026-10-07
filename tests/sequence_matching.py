#!/usr/bin/env python3
"""Order-isomorphic matching and generic palindrome independent oracles."""
import hashlib
import json
import os
from pathlib import Path
import random
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
    rng=random.Random(6080)
    data=[]
    def direct(s,t):
        return [i+1 for i in range(len(s)-len(t)+1) if all(
            (s[i+j]<s[i+k])==(t[j]<t[k]) and (s[i+j]==s[i+k])==(t[j]==t[k])
            for j in range(len(t)) for k in range(j))]
    def add(label,s,t,want=None):
        if want is None:want=direct(s,t)
        inp=f'{len(s)} {len(t)} 25\n'+' '.join(map(str,s))+'\n'+' '.join(map(str,t))+'\n'
        data.append((label,inp,[len(want),*want]))
    add('statement-illustration',[5,6,2,10,10,7,3,2,9],[1,4,4,3,2,1])
    for i in range(200):
        s=[rng.randrange(1,26) for _ in range(rng.randrange(1,70))]
        t=[rng.randrange(1,26) for _ in range(rng.randrange(1,20))]
        if i%2==0 and len(s)>=len(t):t=s[:len(t)]
        add('random-'+str(i),s,t)
    n,m=100000,25000
    add('maximum-equal',[1]*n,[25]*m,list(range(1,n-m+2)))
    add('maximum-periodic',[1,25]*(n//2),[2,3]*(m//2),list(range(1,n-m+2,2)))
    add('maximum-no-match',[1]*n,[1,2]*(m//2),[])
    add('pattern-longer',[1],[1]*m,[])
    add('one-element-pattern',[1]*n,[25],list(range(1,n+1)))
    return data


def main():
    if not __debug__:
        raise RuntimeError('Python checks must stay enabled')
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    out = Path(tempfile.mkdtemp(prefix='sequence-matching-' + mode + '-', dir=ROOT / 'build'))
    before = snapshot(ROOT)
    probe = (ROOT / 'tests/sequence_matching_probe.cpp').read_text()
    parts = extract_components(json.loads((ROOT / 'docs/catalog.json').read_text()))
    core = '\n'.join(next(x['code'] for x in parts if x['symbol'] == s) for s in ['order_match','manacher'])
    prelude = ''.join('#include <'+s+'>\n' for s in ['algorithm','cassert','climits','iostream','numeric','random','stdexcept','utility','vector','string','map','iterator'])+'using namespace std;\n'
    copied = prelude+core+'\n'+probe.replace('#include "../src/compact/order_match.hpp"','').replace('#include "../src/compact/string.hpp"','')
    flags = ['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env = os.environ.copy()
    if mode=='sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler=Path(shutil.which(CXX) or CXX).resolve()
    report=dict(mode=mode,source_before_sha256=before,compiler=str(compiler),compiler_sha256=sha(compiler.read_bytes()),flags=flags,programs=[],mutants=[],applications=[])
    def compile(name,source,extra=()):
        cpp,exe=out/(name+'.cpp'),out/name
        cpp.write_text(source)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()))
    reference=None
    for form,source in [('header','#include "'+str(ROOT/'tests/sequence_matching_probe.cpp')+'"\n'),('copied',copied)]:
        for nd in [False,True]:
            name=form+('-ndebug' if nd else '-assert')
            exe,entry=compile(name,source,['-DNDEBUG'] if nd else [])
            p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=600)
            assert p.returncode==0 and not p.stderr and p.stdout.startswith(b'PASS '),(name,p.returncode,p.stdout,p.stderr[-1000:])
            if reference is None:reference=p.stdout
            assert reference==p.stdout
            entry.update(result=p.stdout.decode().strip(),output_sha256=sha(p.stdout))
            report['programs'].append(entry)
            print(name,entry['result'],flush=True)
    mutations=[
        ('omit-equality','return a[i] == a[start + eq[j]];','return true;'),
        ('non-strict-lower','a[i] <= a[start + lo[j]]','a[i] < a[start + lo[j]]'),
        ('non-strict-upper','a[i] >= a[start + hi[j]]','a[i] > a[start + hi[j]]'),
        ('wrong-predecessor','lo[j] = prev(it)->second;','lo[j] = last.begin()->second;'),
        ('omit-overlap','j = p[j - 1];\n        }','j = 0;\n        }'),
        ('wrong-failure','p[i] = j;','p[i] = 0;'),
        ('omit-even-radius','even[i] = k--;','even[i] = 0;\n        k--;'),
    ]
    for name,old,new in mutations:
        assert copied.count(old)==1,(name,copied.count(old))
        exe,entry=compile(name,copied.replace(old,new),['-DNDEBUG'])
        p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=600)
        assert p.returncode==0 and not p.stderr and p.stdout==b'ORACLE_REJECT\n',(name,p.returncode,p.stdout,p.stderr[-1000:])
        entry.update(independent_oracle_rejected=True,output_sha256=sha(p.stdout))
        report['mutants'].append(entry)
        print(name,'rejected',flush=True)
    data=datasets()
    for example in ['example-251']:
        row=next(r for r in records() if r['id']==example)
        own='\n'.join(next(x['code'] for x in parts if x['symbol']==symbol) for symbol in row['requires'])
        for form,source in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('bundle',row['program']),('minimal-copy',prelude+own+'\n'+row['snippet'])]:
            name=example+'-'+form
            exe,entry=compile(name,source)
            entry['runs']=[]
            for label,inp,want in data:
                raw=inp.encode()
                p=subprocess.run([str(exe)],input=raw,capture_output=True,env=env,timeout=180)
                assert p.returncode==0 and not p.stderr,(name,label,p.returncode,p.stderr[-1000:])
                assert p.stdout.split()==[str(x).encode() for x in want],(name,label,p.stdout[:200])
                entry['runs'].append(dict(case=label,input_sha256=sha(raw),output_sha256=sha(p.stdout),passed=True))
            report['applications'].append(entry)
            print(name,len(data),'inputs PASS',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT),complete_input_counts={'P6080':len(data)},scope='Pairwise order/equality oracle and substring mirror palindrome oracle. Exhaustive duplicate-heavy sequences, signed64 extremes, empty text/sequence, overlap, million-element closed forms. Four core forms and three complete P6080 application forms. Seven semantic mutants. Not online AC, ranking, formal-template coverage or whole-library audit.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('sequence-matching',mode,'PASS:',out/'report.json',flush=True)

if __name__=='__main__':
    main()
