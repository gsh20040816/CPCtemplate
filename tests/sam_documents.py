#!/usr/bin/env python3
"""Independent document-frequency oracles, semantic mutants and complete programs."""
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
    data={'example-259':[], 'example-260':[]}
    def app(label, words, k, want=None):
        if want is None:
            counts={}
            for s in words:
                seen={s[l:r] for l in range(len(s)) for r in range(l+1,len(s)+1)}
                for t in seen:counts[t]=counts.get(t,0)+1
            want=[sum(counts[s[l:r]]>=k for l in range(len(s)) for r in range(l+1,len(s)+1)) for s in words]
        data['example-259'].append((label,f'{len(words)} {k}\n'+'\n'.join(words)+'\n',want))
    app('official-one',['abc','a','ab'],1,[6,1,3])
    app('official-two',['rubik','furik','abab','baba','aaabbbababa','abababababa','zero'],4,[1,0,9,9,21,30,0])
    rng=random.Random(204)
    for i in range(180):
        words=[''.join(rng.choice('abc') for _ in range(rng.randrange(1,13))) for _ in range(rng.randrange(1,9))]
        if i%4==0:words += words[:2]
        for k in [1,rng.randrange(1,len(words)+1),len(words),len(words)+1]:app(f'random-{i}-k{k}',words,k)
        queries=[''.join(rng.choice('abcd') for _ in range(rng.randrange(1,15))) for _ in range(15)]
        queries+=sorted({s[l:r] for s in words for l in range(len(s)) for r in range(l+1,len(s)+1)})
        raw=f'{len(words)} {len(queries)}\n'+'\n'.join(words+queries)+'\n'
        data['example-260'].append((f'patterns-{i}',raw,[sum(t in s for s in words) for t in queries]))
    data['example-260'].append(('empty-collection','0 2\na\nabc\n',[0,0]))
    n=100000
    app('max-single-chain',['a'*n],1,[n*(n+1)//2])
    app('max-k-beyond-docs',['a'*n],n,[0])
    app('max-clone-heavy',['a'+'b'*(n-1)],1,[n*(n+1)//2])
    m=n//2
    app('max-duplicate-long-chain',['a'*m]*2,2,[m*(m+1)//2]*2)
    app('max-two-disjoint',['a'*m,'b'*m],2,[0,0])
    m=33333
    app('max-short-document-limits',['a'*(2*m),'a'*m],2,[m*(m+1)//2+m*m,m*(m+1)//2])
    app('max-many-documents',['a']*n,n,[1]*n)
    app('max-half-documents',['a']*(n//2)+['b']*(n//2),n//2+1,[0]*n)
    # Complete binary words: each length-l substring is present in an enumerated
    # number of documents; independent literal membership oracle, not SAM.
    words=[format(i,'012b').translate(str.maketrans('01','ab')) for i in range(1<<12)]
    frequency={}
    for s in words:
        for t in {s[l:r] for l in range(12) for r in range(l+1,13)}:frequency[t]=frequency.get(t,0)+1
    k=1000
    want=[sum(frequency[s[l:r]]>=k for l in range(12) for r in range(l+1,13)) for s in words]
    app('broad-binary-trie',words,k,want)
    data['example-260'].append(('long-patterns','2 4\n'+'a'*50000+'\n'+'a'*49999+'b\na\n'+'a'*50000+'\nb\n'+'a'*50001+'\n',[2,1,1,0]))
    return data


def main():
    if not __debug__:raise RuntimeError('Python checks must stay enabled')
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='sam-documents-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT)
    parts=extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))
    def component(s):return next(x['code'] for x in parts if x['symbol']==s)
    symbols=['GeneralSAM','OnlineSAM','SuffixAutomaton','SAMLex','Fenwick','SAMDocuments']
    core='\n'.join(component(s) for s in symbols)
    prelude=''.join('#include <'+s+'>\n' for s in ['algorithm','array','cassert','climits','iostream','map','numeric','optional','queue','random','set','stdexcept','string','utility','vector'])+'using namespace std;\n'
    probe=(ROOT/'tests/sam_documents_probe.cpp').read_text()
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
    for form,source in [('header','#include "'+str(ROOT/'tests/sam_documents_probe.cpp')+'"\n'),('copied',copied)]:
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
        ('merge-document-identities','tag[p].push_back(id);','tag[p].push_back(0);'),
        ('count-occurrences-not-documents','if (last[id]) bit.add(last[id], -1);','if (false) bit.add(last[id], -1);'),
        ('prefix-not-subtree','cnt[u] = bit.query(l, timer);','cnt[u] = bit.sum(timer);'),
        ('skip-child-markers','for (int v : g[u]) self(self, v);','for (int v : g[u]) if (false) self(self, v);'),
        ('strict-threshold','if (cnt[u] >= k) best[u] = sam.a[u].len;','if (cnt[u] > k) best[u] = sam.a[u].len;'),
        ('lose-suffix-inheritance','best[v] = best[u];','best[v] = 0;'),
        ('ignore-empty-documents','cnt[0] = s.size();','cnt[0] = 0;'),
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
    report.update(passed=True,source_after_sha256=snapshot(ROOT),complete_input_counts={k:len(v) for k,v in data.items()},scope='Independent literal per-document substring sets, all small triples, random permutations, document duplicates and empties, every state and all thresholds, SAMLex document weights, unchanged source SAM and copies. GeneralSAM/OnlineSAM/single SAM; recursive depth100000 and 64-bit totals. Four core forms, seven semantic mutants and three complete forms per usage. Local only: no online AC/rank or full-library claim.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('sam-documents',mode,'PASS:',out/'report.json',flush=True)

if __name__=='__main__':main()
