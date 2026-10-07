#!/usr/bin/env python3
"""Weighted SAM paths and LCS with independent explicit substring oracles."""
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
    rng=random.Random(3975)
    data={'example-253':[], 'example-254':[], 'example-255':[]}
    def words(s):return [s[i:j] for i in range(len(s)) for j in range(i+1,len(s)+1)]
    for i in range(160):
        s=''.join(rng.choice('abcde') for _ in range(rng.randrange(1,24)))
        mode=i%2
        all=words(s)
        all=sorted(all if mode else set(all))
        k=rng.randrange(1,len(all)+3)
        data['example-253'].append((f'random-{i}',s+f'\n{mode} {k}\n',[all[k-1] if k<=len(all) else '-1']))
        t=''.join(rng.choice('abcdf') for _ in range(rng.randrange(0,28)))
        best=max([0]+[len(x) for x in set(all) if x in t])
        data['example-254'].append((f'random-{i}',s+'\n'+t+'\n',[str(best)]))
    n=500000
    for mode,k in [(0,1),(0,n),(0,n+1),(1,n),(1,n+1),(1,1000000000)]:
        if mode:
            left,length=k,1
            while left>n-length+1:left-=n-length+1;length+=1
            want='a'*length
        else:want='a'*k if k<=n else '-1'
        data['example-253'].append((f'maximum-repeat-{mode}-{k}','a'*n+f'\n{mode} {k}\n',[want]))
    # a followed by b's creates almost2n SAM states, unlike a constant word.
    for mode,k in [(0,n),(0,2*n-1),(1,n+1),(1,1000000000)]:
        if mode:
            left,length=k-n,1
            while left>n-length:left-=n-length;length+=1
            want='b'*length
        else:want='a'+'b'*(n-1) if k==n else 'b'*(n-1)
        data['example-253'].append((f'maximum-clones-{mode}-{k}','a'+'b'*(n-1)+f'\n{mode} {k}\n',[want]))
    for label,s,t,want in [('empty-first','','abc',0),('empty-second','abc','',0),('both-empty','','',0),('equal','ab'*125000,'ab'*125000,250000),('shifted','ab'*125000,'ba'*125000,249999),('disjoint','a'*250000,'b'*250000,0)]:
        data['example-254'].append((label,s+'\n'+t+'\n',[str(want)]))
    for i in range(100):
        docs=[''.join(rng.choice('abc') for _ in range(rng.randrange(1,10))) for _ in range(rng.randrange(0,6))]
        alphabet=list('abcdefghijklmnopqrstuvwxyz');rng.shuffle(alphabet);alphabet=''.join(alphabet)
        all=set(w for s in docs for w in words(s))
        sorted_words=sorted(all,key=lambda s:tuple(alphabet.index(c) for c in s))
        k=rng.randrange(1,len(all)+3)
        t=''.join(rng.choice('abcd') for _ in range(rng.randrange(1,18)))
        length=max([0]+[len(w) for w in all if w in t]);start=min([t.index(w) for w in all if len(w)==length and w in t],default=0)
        inp=str(len(docs))+'\n'+'\n'.join(docs)+'\n'+alphabet+f' {k} '+t+'\n'
        want=[sorted_words[k-1] if k<=len(all) else '-1',str(start),str(length)]
        data['example-255'].append((f'general-{i}',inp,want))
    return data


def main():
    if not __debug__:
        raise RuntimeError('Python checks must stay enabled')
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    out = Path(tempfile.mkdtemp(prefix='sam-queries-' + mode + '-', dir=ROOT / 'build'))
    before = snapshot(ROOT)
    probe = (ROOT / 'tests/sam_queries_probe.cpp').read_text()
    parts = extract_components(json.loads((ROOT / 'docs/catalog.json').read_text()))
    core = '\n'.join(next(x['code'] for x in parts if x['symbol'] == s) for s in ['SuffixAutomaton','GeneralSAM','SAMLex','sam_lcs'])
    prelude = ''.join('#include <'+s+'>\n' for s in ['algorithm','cassert','climits','iostream','numeric','random','stdexcept','utility','vector','string','map','iterator','array','queue','optional','set'])+'using namespace std;\n'
    copied = prelude+core+'\n'+probe.replace('#include "../src/compact/string.hpp"','').replace('#include "../src/compact/general_sam.hpp"','').replace('#include "../src/compact/sam_queries.hpp"','')
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
    for form,source in [('header','#include "'+str(ROOT/'tests/sam_queries_probe.cpp')+'"\n'),('copied',copied)]:
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
        ('count-empty-word','weight[0] = 0;','weight[0] = 1;'),
        ('ignore-multiplicity','sum = weight;','sum.assign(n, 1);'),
        ('wrong-rank-boundary','if (k > sum[v])','if (k >= sum[v])'),
        ('wrong-letter-order','for (char c : alphabet)','for (char c : string(alphabet.rbegin(), alphabet.rend()))'),
        ('wrong-saturation','LLONG_MAX - sum[u]','max(0LL, LLONG_MAX / 2 - sum[u])'),
        ('wrong-lcs-fallback','length = sam.a[p].len;','length = 0;'),
        ('wrong-tie-position','if (length > ans.second)','if (length >= ans.second)'),
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
    for example in data:
        row=next(r for r in records() if r['id']==example)
        own='\n'.join(next(x['code'] for x in parts if x['symbol']==symbol) for symbol in row['requires'])
        for form,source in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('bundle',row['program']),('minimal-copy',prelude+own+'\n'+row['snippet'])]:
            name=example+'-'+form
            exe,entry=compile(name,source)
            entry['runs']=[]
            for label,inp,want in data[example]:
                raw=inp.encode()
                p=subprocess.run([str(exe)],input=raw,capture_output=True,env=env,timeout=180)
                assert p.returncode==0 and not p.stderr,(name,label,p.returncode,p.stderr[-1000:])
                assert p.stdout.split()==[str(x).encode() for x in want],(name,label,p.stdout[:200])
                entry['runs'].append(dict(case=label,input_sha256=sha(raw),output_sha256=sha(p.stdout),passed=True))
            report['applications'].append(entry)
            print(name,len(data[example]),'inputs PASS',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT),complete_input_counts={k:len(v) for k,v in data.items()},scope='Explicit substring set/multiset enumeration, custom weights with int128 totals, arbitrary alphabet permutations, generalized document union, LCS substring oracle, empty inputs and500000/250000-character closed forms. Four core forms; three complete forms per usage253/254/255. Seven semantic mutants. Local only; not online AC/rank or whole-library audit.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('sam-queries',mode,'PASS:',out/'report.json',flush=True)

if __name__=='__main__':
    main()
