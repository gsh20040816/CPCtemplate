#!/usr/bin/env python3
"""P4735 suffix enumeration and large closed-form streams; no online AC claim."""
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from run_provenance import snapshot
from audit_copy_context import extract_components
from usage_examples import records
from compiler_config import CXX

def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    if not __debug__:raise RuntimeError('Python checks must stay enabled')
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='persistent-xor-app-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT);rng=random.Random(4735);cases=[]
    def add(name,initial,ops,expected=None,scope='statement-compatible numerical domain'):
        a=list(initial);want=[]
        if expected is None:
            for op in ops:
                if op[0]=='A':a.append(op[1])
                else:
                    _,l,r,x=op;ans=[]
                    for p in range(l-1,r):
                        value=x
                        for v in a[p:]:value^=v
                        ans.append(value)
                    want.append(max(ans))
        else:want=list(expected)
        data=(f'{len(initial)} {len(ops)}\n'+' '.join(map(str,initial))+'\n'+''.join(' '.join(map(str,op))+'\n' for op in ops)).encode()
        cases.append(dict(name=name,data=data,expected=want,scope=scope))
    add('zero-and-prefix',[0],[('Q',1,1,0),('A',0),('Q',1,2,7),('A',1),('Q',1,1,1),('Q',3,3,0)])
    add('prefix-above-element-bound',[8388608,8388607],[('Q',1,2,0),('Q',1,1,0),('Q',2,2,0),('A',10000000),('Q',1,3,9999999)])
    for k in range(100):
        initial=[rng.randrange(10000001) for _ in range(rng.randrange(1,15))];ops=[];n=len(initial)
        for j in range(80):
            if j%4==0:ops.append(('A',rng.randrange(10000001)));n+=1
            else:
                l=rng.randrange(1,n+1);r=rng.randrange(l,n+1)
                if j%5==0:l=1
                if j%7==0:r=n
                ops.append(('Q',l,r,rng.randrange(10000001)))
        add('random-'+str(k),initial,ops)
    add('uint64-query-extension',[1,8388608,8388607],[('Q',1,3,(1<<64)-1),('Q',1,1,1<<63),('A',1),('Q',2,4,(1<<63)+7)],scope='uint64 query extension; official page does not state a separate query-x bound')
    n=m=300000
    add('maximum-append-capacity',[0]*n,[('A',0)]*m,[])
    add('maximum-capacity-query',[0]*n,[('A',0)]*(m-1)+[('Q',1,n+m-1,10000000)],[10000000])
    ops=[('Q',1,n,i%10000001) for i in range(m)]
    add('maximum-query-count',[0]*n,ops,[op[3] for op in ops])
    ops=[('Q',1,n,i%10000001) for i in range(m)]
    add('alternating-suffixes',[1]*n,ops,[max(op[3],op[3]^1) for op in ops])
    row=next(r for r in records() if r['id']=='example-239')
    core=next(x['code'] for x in extract_components(json.loads((ROOT/'docs/catalog.json').read_text())) if x['symbol']=='PersistentXorTrie')
    prelude=''.join('#include <'+x+'>\n' for x in ['cassert','climits','cstdint','iostream','optional','stdexcept','vector'])+'using namespace std;\n'
    forms=[('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('bundle',row['program']),('copied',prelude+core+'\n'+row['snippet'])]
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler=Path(shutil.which(CXX) or CXX).resolve()
    report=dict(mode=mode,source_before_sha256=before,compiler=str(compiler),compiler_sha256=sha(compiler.read_bytes()),flags=flags,program_sha256=row['program_sha256'],cases=[],programs=[])
    for c in cases:
        (out/(c['name']+'.in')).write_bytes(c['data'])
        expected=(''.join(str(x)+'\n' for x in c['expected'])).encode();(out/(c['name']+'.expected')).write_bytes(expected)
        report['cases'].append(dict(name=c['name'],input_sha256=sha(c['data']),expected_sha256=sha(expected),queries=len(c['expected']),scope=c['scope']))
    for name,source in forms:
        cpp,exe=out/(name+'.cpp'),out/name;cpp.write_text(source)
        cmd=[CXX,*flags,str(cpp),'-o',str(exe)];subprocess.run(cmd,check=True,capture_output=True)
        entry=dict(name=name,compile_command=cmd,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()),runs=[])
        for c in cases:
            p=subprocess.run([str(exe)],input=c['data'],capture_output=True,env=env,timeout=180)
            assert p.returncode==0 and not p.stderr,(name,c['name'],p.returncode,p.stderr[-1000:])
            assert list(map(int,p.stdout.split()))==c['expected'],(name,c['name'])
            (out/(name+'-'+c['name']+'.out')).write_bytes(p.stdout)
            entry['runs'].append(dict(case=c['name'],output_sha256=sha(p.stdout),passed=True))
        report['programs'].append(entry)
    report.update(source_after_sha256=snapshot(ROOT),passed=True,scope='Constructed cases, not official samples or hidden data. Naive suffix XOR oracles, four maximum-scale closed forms and explicit uint64-query extension. No OJ AC, time-limit or memory-limit certification.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('P4735',mode,len(cases),'inputs x three forms PASS:',out/'report.json')
if __name__=='__main__':main()
