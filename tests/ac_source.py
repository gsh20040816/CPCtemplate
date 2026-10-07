#!/usr/bin/env python3
"""Audit existing AC semantics and presence adapter with literal oracles."""
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import resource
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
    data={'example-70':[], 'example-262':[]}
    rng=random.Random(5357)
    for i in range(180):
        patterns=[''.join(rng.choice('abc') for _ in range(rng.randrange(1,12))) for _ in range(rng.randrange(1,30))]
        if i%3==0:patterns+=patterns[:5]
        text=''.join(rng.choice('abcd') for _ in range(rng.randrange(1,150)))
        counts=[sum(text.startswith(p,j) for j in range(len(text))) for p in patterns]
        raw=str(len(patterns))+'\n'+'\n'.join(patterns)+'\n'+text+'\n'
        data['example-70'].append((f'random-{i}',raw,counts))
        data['example-262'].append((f'random-{i}',raw,[sum(c>0 for c in counts)]))
    for example,n,length in [('example-70',200000,2000000),('example-262',1000000,1000000)]:
        def add(label,patterns,text,counts):
            raw=str(len(patterns))+'\n'+'\n'.join(patterns)+'\n'+text+'\n'
            data[example].append((label,raw,counts if example=='example-70' else [sum(c>0 for c in counts)]))
        add('max-chain',['a'*n],'a'*length,[length-n+1])
        add('max-duplicate-patterns',['a']*n,'a'*length,[length]*n)
        add('no-match-chain',['a'*n],'b'*length,[0])
        patterns=['a'*i for i in range(1,632)]
        add('nested-suffix-matches',patterns,'a'*length,[length-len(p)+1 for p in patterns])
        add('duplicate-and-absent',['ab','ab','ba','a','c'],'ababab',[3,3,2,3,0])
    return data


def main():
    if not __debug__:raise RuntimeError('Python checks must stay enabled')
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='ac-source-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT)
    parts=extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))
    def component(s):return next(x['code'] for x in parts if x['symbol']==s)
    symbols=['AhoCorasick']
    core='\n'.join(component(s) for s in symbols)
    prelude=''.join('#include <'+s+'>\n' for s in ['algorithm','array','cassert','climits','iostream','map','numeric','optional','queue','random','set','stdexcept','string','utility','vector'])+'using namespace std;\n'
    probe=(ROOT/'tests/ac_source_probe.cpp').read_text()
    copied=prelude+core+'\n'+'\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    # Native recursion is preserved; match the contest's memory-sized stack.
    if platform.system()=='Darwin':flags+=['-Wl,-stack_size,0x20000000']
    else:
        _,hard=resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard!=-1 else 512<<20,hard))
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler=Path(shutil.which(CXX) or CXX).resolve()
    report=dict(mode=mode,source_before_sha256=before,compiler=str(compiler),compiler_sha256=sha(compiler.read_bytes()),flags=flags,programs=[],mutants=[],applications=[])
    def compile(name,source,extra=()):
        cpp,exe=out/(name+'.cpp'),out/name;cpp.write_text(source)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()))
    reference=None
    for form,source in [('header','#include "'+str(ROOT/'tests/ac_source_probe.cpp')+'"\n'),('copied',copied)]:
        for nd in [False,True]:
            name=form+('-ndebug' if nd else '-assert')
            exe,entry=compile(name,source,['-DNDEBUG'] if nd else [])
            p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=600)
            assert p.returncode==0 and not p.stderr and p.stdout.startswith(b'PASS '),(name,p.returncode,p.stdout,p.stderr[-1000:])
            if reference is None:reference=p.stdout
            assert p.stdout==reference
            entry.update(result=p.stdout.decode().strip(),output_sha256=sha(p.stdout))
            report['programs'].append(entry);print(name,entry['result'],flush=True)
    mutations=[
        ('no-root-queue','if (v) q.push(v);','if (false) q.push(v);'),
        ('wrong-failure-parent','a[v].fail = a[a[u].fail].go[c];','a[v].fail = 0;'),
        ('lose-fallback-transition','a[u].go[c] = a[a[u].fail].go[c];','a[u].go[c] = 0;'),
        ('omit-text-visit','++ans[u];','ans[u] += 0;'),
        ('omit-failure-aggregation','ans[a[order[i]].fail] += ans[order[i]];','ans[a[order[i]].fail] += 0;'),
    ]
    for name,old,new in mutations:
        assert copied.count(old)==1,(name,copied.count(old))
        exe,entry=compile(name,copied.replace(old,new),['-DNDEBUG'])
        p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=600)
        assert p.returncode==0 and not p.stderr and p.stdout==b'ORACLE_REJECT\n',(name,p.returncode,p.stdout,p.stderr[-1000:])
        entry.update(independent_oracle_rejected=True,output_sha256=sha(p.stdout));report['mutants'].append(entry)
        print(name,'rejected',flush=True)
    data=datasets()
    for example,cases in data.items():
        row=next(r for r in records() if r['id']==example)
        own='\n'.join(component(s) for s in row['requires'])
        for form,source in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('bundle',row['program']),('minimal-copy',prelude+own+'\n'+row['snippet'])]:
            name=example+'-'+form;exe,entry=compile(name,source);entry['runs']=[]
            for label,inp,want in cases:
                raw=inp.encode();p=subprocess.run([str(exe)],input=raw,capture_output=True,env=env,timeout=180)
                assert p.returncode==0 and not p.stderr,(name,label,p.returncode,p.stderr[-1000:])
                assert p.stdout.split()==[str(x).encode() for x in want],(name,label,p.stdout[:200])
                entry['runs'].append(dict(case=label,input_sha256=sha(raw),output_sha256=sha(p.stdout),passed=True))
            report['applications'].append(entry);print(name,len(cases),'inputs PASS',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT),complete_input_counts={k:len(v) for k,v in data.items()},scope='Independent prefix-trie and longest-suffix transition/failure oracles; literal substring occurrence counts and duplicate pattern IDs; empty text/set, resets, copies and repeated queries. Four core forms and five semantic mutants. Three complete P5357/P3808 forms with maximal valid sizes. Local only, no online AC/rank or full-library rerun.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('ac-source',mode,'PASS:',out/'report.json',flush=True)

if __name__=='__main__':main()
