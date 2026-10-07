#!/usr/bin/env python3
"""Online arbitrary-state extension and offline Trie-edge SAM construction."""
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
    rng=random.Random(61391)
    data={'example-256':[], 'example-257':[], 'example-258':[], 'example-132':[]}
    def substrings(words):return set(s[i:j] for s in words for i in range(len(s)) for j in range(i+1,len(s)+1))
    for run in range(100):
        ops=[];words=[''];out=[]
        for i in range(rng.randrange(0,25)):
            p=rng.randrange(i+1);c=rng.choice('abcde');ops.append((p,c));words.append(words[p]+c);out.append(str(len(substrings(words))))
        inp=str(len(ops))+'\n'+''.join(f'{p} {c}\n' for p,c in ops)
        data['example-256'].append((f'random-{run}',inp,out))
        alpha=list('abcdefghijklmnopqrstuvwxyz');rng.shuffle(alpha);alpha=''.join(alpha)
        all=['']+sorted(substrings(words),key=lambda s:tuple(alpha.index(c) for c in s))
        ranks=list(range(1,len(all)+2))
        inp=f'{len(ops)} {len(ranks)}\n'+''.join(f'{p} {c}\n' for p,c in ops)+''.join(f'{alpha} {k}\n' for k in ranks)
        # Exact text preserves the empty-string result line.
        want=str(len(all))+'\n'+''.join((all[k-1] if k<=len(all) else '-1')+'\n' for k in ranks)
        data['example-257'].append((f'trie-{run}',inp,want))
    n=1600
    ops=[(i,'a') for i in range(n)]+[(i,'b') for i in range(n,-1,-1)]
    inp=str(len(ops))+'\n'+''.join(f'{p} {c}\n' for p,c in ops)
    data['example-256'].append(('descending-branches',inp,list(map(str,[*range(1,n+1),*([2*n+1]*(n+1))]))))
    n=250000
    inp=f'{n} 3\n'+''.join(f'{i} a\n' for i in range(n))+'abcdefghijklmnopqrstuvwxyz 1\nabcdefghijklmnopqrstuvwxyz 2\nabcdefghijklmnopqrstuvwxyz '+str(n+2)+'\n'
    data['example-257'].append(('long-trie-chain',inp,str(n+1)+'\n\na\n-1\n'))
    def docs_case(label,words,expected=None):
        if expected is None:
            ends={}
            for i,s in enumerate(words):
                for l in range(len(s)):
                    for r in range(l,len(s)):ends.setdefault(s[l:r+1],set()).add((i,r))
            expected=[len(ends),1+len({frozenset(x) for x in ends.values()})]
        inp=str(len(words))+'\n'+'\n'.join(words)+'\n'
        for key in ['example-258','example-132']:data[key].append((label,inp,list(map(str,expected))))
    docs_case('documented-official-sample-one',['aa','ab','bac','caa'],[10,10])
    docs_case('documented-official-sample-two',['a'],[1,2])
    docs_case('endpos-not-minimal-suffix-language',['ab','b'],[3,4])
    for i in range(160):
        words=[''.join(rng.choice('abc') for _ in range(rng.randrange(1,13))) for _ in range(rng.randrange(1,9))]
        docs_case(f'random-documents-{i}',words)
    n=1000000
    docs_case('million-chain',['a'*n],[n,n+1])
    docs_case('million-clone-heavy',['a'+'b'*(n-1)],[2*n-1,2*n-1])
    docs_case('two-alternating',['ab'*250000,'ba'*250000],[1000000,1000001])
    docs_case('400000-documents',['ab']*200000+['abc']*200000,[6,4])
    words=[format(i,'015b').translate(str.maketrans('01','ab')) for i in range(1<<15)]
    docs_case('complete-binary-trie',words,[(1<<16)-2,(1<<16)-1])
    return data


def main():
    if not __debug__:
        raise RuntimeError('Python checks must stay enabled')
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    out = Path(tempfile.mkdtemp(prefix='sam-build-' + mode + '-', dir=ROOT / 'build'))
    before = snapshot(ROOT)
    probe = (ROOT / 'tests/sam_build_probe.cpp').read_text()
    parts = extract_components(json.loads((ROOT / 'docs/catalog.json').read_text()))
    core = '\n'.join(next(x['code'] for x in parts if x['symbol'] == s) for s in ['OnlineSAM','GeneralSAM','SAMLex','sam_lcs'])
    prelude = ''.join('#include <'+s+'>\n' for s in ['algorithm','cassert','climits','iostream','numeric','random','stdexcept','utility','vector','string','map','iterator','array','queue','optional','set'])+'using namespace std;\n'
    copied = prelude+core+'\n'+probe.replace('#include "../src/compact/online_sam.hpp"','').replace('#include "../src/compact/general_sam.hpp"','').replace('#include "../src/compact/sam_queries.hpp"','')
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
    for form,source in [('header','#include "'+str(ROOT/'tests/sam_build_probe.cpp')+'"\n'),('copied',copied)]:
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
        ('skip-existing-edge-clone','if (a[q].len == a[p].len + 1) return q;','if (true) return q;'),
        ('wrong-clone-length','copy.len = a[p].len + 1;\n            a.push_back(copy);','copy.len = a[p].len;\n            a.push_back(copy);'),
        ('wrong-old-suffix-link','a[q].link = clone;','a[q].link = 0;'),
        ('wrong-new-suffix-link','a[cur].link = parent;','a[cur].link = 0;'),
        ('wrong-incremental-total','total += a[cur].len - a[parent].len;','total += a[cur].len - a[parent].len - 1;'),
        ('wrong-trie-return','return a[p].go[c];','return p;'),
        ('reset-every-character',"for (char ch : s) p = add(p, ch - 'a');","for (char ch : s) p = add(0, ch - 'a');"),
    ]
    for name,old,new in mutations:
        assert copied.count(old)==1,(name,copied.count(old))
        exe,entry=compile(name,copied.replace(old,new),['-DNDEBUG'])
        p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=600)
        assert p.returncode==0 and not p.stderr and p.stdout==b'ORACLE_REJECT\n',(name,p.returncode,p.stdout,p.stderr[-1000:])
        entry.update(independent_oracle_rejected=True,output_sha256=sha(p.stdout))
        report['mutants'].append(entry)
        print(name,'rejected',flush=True)
    online=next(x['code'] for x in parts if x['symbol']=='OnlineSAM')
    measured=online.replace('a[p].go[c] = clone;', 'redirects++;\n                a[p].go[c] = clone;')
    instrument=prelude+'long long redirects = 0;\n'+measured+"""
int main()
{
    int n;
    cin >> n;
    OnlineSAM sam;
    vector<int> state(n + 1);
    for (int i = 1; i <= n; i++) state[i] = sam.extend(state[i - 1], 0);
    for (int i = n; i >= 0; i--) sam.extend(state[i], 1);
    cout << redirects << ' ' << sam.total << '\\n';
}
"""
    exe,entry=compile('redirect-count',instrument)
    entry['runs']=[]
    for n in [200,400,800,1600]:
        p=subprocess.run([str(exe)],input=str(n).encode(),capture_output=True,env=env,timeout=120)
        assert p.returncode==0 and not p.stderr
        assert list(map(int,p.stdout.split()))==[n*(n+1)//2,2*n+1]
        entry['runs'].append(dict(chain_length=n,operations=2*n+1,redirects=n*(n+1)//2,output_sha256=sha(p.stdout)))
    report['quadratic_redirect_witness']=entry
    print('descending-branch exact redirect counts PASS',flush=True)
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
                assert (p.stdout.decode()==want if isinstance(want,str) else p.stdout.split()==[str(x).encode() for x in want]),(name,label,p.stdout[:200])
                entry['runs'].append(dict(case=label,input_sha256=sha(raw),output_sha256=sha(p.stdout),passed=True))
            report['applications'].append(entry)
            print(name,len(data[example]),'inputs PASS',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT),complete_input_counts={k:len(v) for k,v in data.items()},scope='Independent substring/endpos classes after each arbitrary-parent insertion; stable longest-state handles, direct Trie edges and whole-string insertions, accepted-language DFS, weighted-query integration, cloned-state parents and250000-character formulas. Four core forms; three complete forms for usages256/257/258/132. Seven semantic mutants. Local only; no online AC/rank or full-library claim.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('sam-build',mode,'PASS:',out/'report.json',flush=True)

if __name__=='__main__':
    main()
