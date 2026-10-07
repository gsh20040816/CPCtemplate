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
    data={'example-265':[], 'example-266':[]}
    rng=random.Random(266)
    for i in range(160):
        ps=[''.join(rng.choice('ABC') for _ in range(rng.randrange(8))) for _ in range(rng.randrange(1,16))]
        ts=[''.join(rng.choice('ABCD') for _ in range(rng.randrange(30))) for _ in range(6)]
        counts=[sum(t.startswith(p,j) for j in range(len(t)+1)) for t in ts for p in ps]
        raw=f'{len(ps)} {len(ts)} A\n'+'\n'.join('"'+s+'"' for s in ps+ts)+'\n'
        data['example-266'].append((f'random-{i}',raw,counts))
        off=-2147483648 if i%2 else 2147483622
        raw=f'{len(ps)} {len(ts)} {off}\n'+'\n'.join(str(len(s))+' '+ ' '.join(str(ord(c)-65+off) for c in s) for s in ps+ts)+'\n'
        data['example-265'].append((f'random-{i}',raw,list(map(len,ps))+counts))
    return data


def main():
    if not __debug__:raise RuntimeError('Python checks must stay enabled')
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='ac-indexed-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT)
    parts=extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))
    def component(s):return next(x['code'] for x in parts if x['symbol']==s)
    symbols=['AhoCorasick']
    core='\n'.join(component(s) for s in symbols)
    prelude=''.join('#include <'+s+'>\n' for s in ['algorithm','array','cassert','climits','iomanip','iostream','map','numeric','optional','queue','random','set','stdexcept','string','utility','vector'])+'using namespace std;\n'
    probe=(ROOT/'tests/ac_indexed_probe.cpp').read_text()
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
    for form,source in [('header','#include "'+str(ROOT/'tests/ac_indexed_probe.cpp')+'"\n'),('copied',copied)]:
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
        ('depth-stuck','a[v].len = a[u].len + 1;','a[v].len = a[u].len;'),
        ('missing-empty-boundary','ans[0] = 1;','ans[0] = 0;'),
        ('ignore-offset','long long c = (long long)ch - offset;','long long c = ((long long)ch - offset + 1) % 26;'),
        ('wrong-failure-parent','a[v].fail = a[a[u].fail].go[c];','a[v].fail = 0;'),
    ]
    for name,old,new in mutations:
        assert copied.count(old)==(2 if name=='ignore-offset' else 1),(name,copied.count(old))
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
    report.update(passed=True,source_after_sha256=snapshot(ROOT),complete_input_counts={k:len(v) for k,v in data.items()},scope='Independent integer-prefix/longest-suffix oracles, depth and empty-boundary counts, signed extreme offsets, character offsets, copies/reset and million-node chain. Four forms and four mutants; three full forms per new API. Local only, no online AC/rank or full-library rerun.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('ac-indexed',mode,'PASS:',out/'report.json',flush=True)

if __name__=='__main__':main()
