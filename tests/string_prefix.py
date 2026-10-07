#!/usr/bin/env python3
"""Historical labels and independent multiset vectors, with ownership audits."""
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
    rng=random.Random(5410)
    data=[]
    def direct(s,t):
        p=[]
        for i in range(len(s)):
            k=0
            while i+k<len(s) and k<len(t) and s[i+k]==t[k]:k+=1
            p.append(k)
        return p
    def checksum(a):
        ans=0
        for i,x in enumerate(a,1):ans^=i*(x+1)
        return ans
    for case in range(150):
        s=''.join(rng.choice('abc') for _ in range(rng.randrange(1,100)))
        t=''.join(rng.choice('abc') for _ in range(rng.randrange(1,90)))
        data.append((f'random-{case}',s+'\n'+t+'\n',[checksum(direct(t,t)),checksum(direct(s,t))]))
    n=20000000
    # Closed-form LCPs, independent of the Z recurrence.
    z=checksum(range(n,0,-1))
    zero=checksum([0]*n)
    data.append(('maximum-equal','a'*n+'\n'+'a'*n+'\n',[z,z]))
    data.append(('maximum-disjoint','b'*n+'\n'+'a'*n+'\n',[z,zero]))
    periodic=checksum(n-i if i%2==0 else 0 for i in range(n))
    shifted=checksum(n-i if i%2 else 0 for i in range(n))
    data.append(('maximum-periodic','ba'*(n//2)+'\n'+'ab'*(n//2)+'\n',[periodic,shifted]))
    data.append(('short-text-long-pattern','a\n'+'a'*n+'\n',[z,2]))
    data.append(('long-text-short-pattern','a'*n+'\na\n',[2,checksum([1]*n)]))
    return data


def main():
    if not __debug__:
        raise RuntimeError('Python checks must stay enabled')
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    out = Path(tempfile.mkdtemp(prefix='string-prefix-' + mode + '-', dir=ROOT / 'build'))
    before = snapshot(ROOT)
    probe = (ROOT / 'tests/string_prefix_probe.cpp').read_text()
    parts = extract_components(json.loads((ROOT / 'docs/catalog.json').read_text()))
    core = '\n'.join(next(x['code'] for x in parts if x['symbol'] == s) for s in ['prefix_function','kmp_match','z_function','manacher','exkmp'])
    prelude = ''.join('#include <'+s+'>\n' for s in ['algorithm','cassert','climits','iostream','numeric','random','stdexcept','utility','vector','string'])+'using namespace std;\n'
    copied = prelude+core+'\n'+probe.replace('#include "../src/compact/exkmp.hpp"','')
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
    for form,source in [('header','#include "'+str(ROOT/'tests/string_prefix_probe.cpp')+'"\n'),('copied',copied)]:
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
        ('text-is-pattern','auto z = z_function(t);','auto z = z_function(s);'),
        ('omit-pattern-bound','p[i] < m && p[i] < n - i','p[i] < m - 1 && p[i] < n - i'),
        ('wrong-z-reuse','z[i - l]','z[0]'),
        ('wrong-return-order','return {move(z), move(p)};','return {move(p), move(z)};'),
        ('omit-overlap','j = p[j - 1];\n        }','j = 0;\n        }'),
        ('wrong-z-zero','if (n) a[0] = n;','if (n) a[0] = 0;'),
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
    for example in ['example-250']:
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
    report.update(passed=True,source_after_sha256=snapshot(ROOT),complete_input_counts={'P5410':len(data)},scope='Independent prefix/border/period, palindrome-substring and two-string direct-LCP oracles. Empty, zero/high byte, unequal lengths, overlap, periodic strings, million-character formulas; header/copied assert/NDEBUG; seven semantic mutants; three complete P5410 forms including20-million-character maximum lengths. Not official samples, online AC, rankings, full-library runtime or LeakSanitizer.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('string-prefix',mode,'PASS:',out/'report.json',flush=True)

if __name__=='__main__':
    main()
