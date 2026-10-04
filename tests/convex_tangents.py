#!/usr/bin/env python3
"""Exact support-line and nearest-contact oracle for convex polygon tangents."""
import hashlib
import itertools
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
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def hull(a):
    a=sorted(set(a));l=[];u=[]
    for p in a:
        while len(l)>1 and cross(l[-2],l[-1],p)<=0:l.pop()
        l.append(p)
    for p in a[::-1]:
        while len(u)>1 and cross(u[-2],u[-1],p)<=0:u.pop()
        u.append(p)
    return l[:-1]+u[:-1]
def oracle(p,q):
    n=len(p)
    if all(cross(p[i],p[(i+1)%n],q)>=0 for i in range(n)):return (-1,-1)
    def pick(sign):
        ids=[i for i,v in enumerate(p) if all(sign*cross(q,v,w)>=0 for w in p)]
        return min(ids,key=lambda i:(p[i][0]-q[0])**2+(p[i][1]-q[1])**2)
    return (pick(-1),pick(1))
def payload(p,queries):
    return (f'{len(p)} {len(queries)}\n'+''.join(f'{x} {y}\n' for x,y in p)+''.join(f'{x} {y}\n' for x,y in queries)).encode()
def cases():
    rng=random.Random(20261004);items=[]
    def add(name,p,q,want=None):
        p=list(p);q=list(q);n=len(p)
        assert n>=3 and all(cross(p[i-1],p[i],p[(i+1)%n])>0 for i in range(n))
        assert all(abs(x)<=10**12 and abs(y)<=10**12 for x,y in p+q)
        if want is None:want=[oracle(p,x) for x in q]
        items.append(dict(name=name,p=p,queries=q,expected=list(want)))
    grid=list(itertools.product(range(3),repeat=2));polys=set()
    for mask in range(1<<9):
        p=hull([x for i,x in enumerate(grid) if mask>>i&1])
        if len(p)>=3:polys.add(tuple(p))
    for k,p in enumerate(sorted(polys)):
        for s in range(len(p)):add(f'grid-{k}-{s}',p[s:]+p[:s],itertools.product(range(-4,5),repeat=2))
    for k in range(400):
        p=hull([(rng.randrange(-30,31),rng.randrange(-30,31)) for _ in range(15)])
        if len(p)<3:continue
        q=[(rng.randrange(-70,71),rng.randrange(-70,71)) for _ in range(20)]+p
        for i,v in enumerate(p):
            w=p[(i+1)%len(p)]
            q.extend([(2*v[0]-w[0],2*v[1]-w[1]),(2*w[0]-v[0],2*w[1]-v[1])])
        for v in p[1:]:q.extend([(2*p[0][0]-v[0],2*p[0][1]-v[1]),(2*v[0]-p[0][0],2*v[1]-p[0][1])])
        s=rng.randrange(len(p));p=p[s:]+p[:s];add('random-'+str(k),p,q)
        if k<40:
            add('reflect-'+str(k),[(x,-y) for x,y in p[::-1]],[(x,-y) for x,y in q])
            scale=10**9;dx=10**11;dy=-10**11
            add('large-transform-'+str(k),[(x*scale+dx,y*scale+dy) for x,y in p],[(x*scale+dx,y*scale+dy) for x,y in q])
    B=10**12
    add('extreme-square',[(-B+1,-B+1),(B-1,-B+1),(B-1,B-1),(-B+1,B-1)],itertools.product([-B,-B+1,0,B-1,B],repeat=2))
    p=[(0,0),(B,1),(B-1,1)];q=[(0,0),(B,1),(B-1,1),(0,1),(0,-1),(-B,0),(B,0),(B,2),(-B,-1)]
    for s in range(3):add('determinant-one-'+str(s),p[s:]+p[:s],q)
    add('no-queries',[(0,0),(1,0),(0,1)],[])
    n=100000;p=[(i,i*i) for i in range(n-1)]+[(-1,n*n)]
    q=[];want=[]
    for i in range(25000):
        q.extend([(0,-B+i),(-B+i,0),(B-i,0),(0,B-i)])
        want.extend([(n-1,n-2),(n-1,0),(0,n-1),(n-2,n-1)])
    for s in [0,12345,n-1]:
        rot=p[s:]+p[:s];ans=[((a-s)%n,(b-s)%n) for a,b in want]
        # Full support-line certificates on each directional family's endpoints.
        for i in [0,1,2,3,len(q)-4,len(q)-3,len(q)-2,len(q)-1]:
            a,b=ans[i]
            assert all((j==a or cross(q[i],rot[a],v)<0) and (j==b or cross(q[i],rot[b],v)>0) for j,v in enumerate(rot))
        add('large-parabola-'+str(s),rot,q,ans)
    return items

def main():
    if not __debug__:raise RuntimeError('Oracle assertions must stay enabled')
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='convex-tangents-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT);items=cases()
    data=(str(len(items))+'\n').encode()+b''.join(payload(c['p'],c['queries']) for c in items)
    expected=json.dumps([dict(name=c['name'],expected=c['expected']) for c in items],separators=(',',':')).encode()
    (out/'cases.in').write_bytes(data);(out/'expected.json').write_bytes(expected)
    comps={x['symbol']:x['code'] for x in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    core=comps['IntegerPlane']+'\n'+comps['convex_tangents_i64']
    prelude=''.join('#include <'+x+'>\n' for x in ['cassert','climits','cstdint','iostream','optional','tuple','utility','vector'])+'using namespace std;\n'
    probe=(ROOT/'tests/convex_tangents_probe.cpp').read_text()
    copied=prelude+core+'\n'+probe.replace('#include "../src/compact/convex_tangents_i64.hpp"','')
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler=Path(shutil.which(CXX) or CXX).resolve()
    report=dict(mode=mode,source_before_sha256=before,compiler=str(compiler),compiler_sha256=sha(compiler.read_bytes()),flags=flags,input_sha256=sha(data),expected_sha256=sha(expected),polygons=len(items),queries=sum(len(c['queries']) for c in items),programs=[],mutants=[],applications=[])
    def check(output,selected):
        lines=iter(output.decode().splitlines())
        for c in selected:
            for a,b in c['expected']:assert list(map(int,next(lines).split()))==[a,b,1],c['name']
            assert next(lines)=='UNCHANGED 1',c['name']
        assert next(lines,None) is None
    def compile(name,text,extra=[]):
        cpp,exe=out/(name+'.cpp'),out/name;cpp.write_text(text);cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        subprocess.run(cmd,check=True,capture_output=True)
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()))
    for form,text in [('header','#include "'+str(ROOT/'tests/convex_tangents_probe.cpp')+'"\n'),('copied',copied)]:
        for nd in [False,True]:
            exe,entry=compile(form+('-ndebug' if nd else '-assert'),text,['-DNDEBUG'] if nd else [])
            run=subprocess.run([str(exe)],input=data,capture_output=True,env=env,timeout=600)
            assert run.returncode==0 and not run.stderr,(entry['name'],run.returncode,run.stderr[-1000:]);check(run.stdout,items)
            (out/(entry['name']+'.out')).write_bytes(run.stdout);entry['output_sha256']=sha(run.stdout);report['programs'].append(entry)
    small=items[:35]+[c for c in items if c['name'].startswith('determinant') or c['name']=='extreme-square']
    bad=(str(len(small))+'\n').encode()+b''.join(payload(c['p'],c['queries']) for c in small)
    mutations=[('nonstrict-visible','q) < 0;','q) <= 0;'),('reverse-fan','dir * G::cross','G::cross'),('swap-tangents','pair{boundary(h, v), boundary(v, h)}','pair{boundary(v, h), boundary(h, v)}'),('wrong-left-contact','boundary(v, h)}','(boundary(v, h) + n - 1) % n}'),('accept-interior','if (!visible(v)) return nullopt;','if (false) return nullopt;')]
    for name,old,new in mutations:
        assert copied.count(old)==1,(name,copied.count(old));exe,entry=compile(name,copied.replace(old,new),['-DNDEBUG'])
        run=subprocess.run([str(exe)],input=bad,capture_output=True,env=env,timeout=180)
        assert run.returncode==0 and not run.stderr,(name,run.returncode,run.stderr[-1000:])
        rejected=False
        try:check(run.stdout,small)
        except (AssertionError,ValueError,StopIteration):rejected=True
        assert rejected,name
        (out/(name+'.out')).write_bytes(run.stdout);entry.update(output_sha256=sha(run.stdout),independent_checker_rejected=True);report['mutants'].append(entry)
    row=next(r for r in records() if r['id']=='example-240')
    selected=items[::max(1,len(items)//35)]+[c for c in items if c['name'].startswith(('determinant','large-parabola')) or c['name'] in ['no-queries','extreme-square']]
    selected=list({c['name']:c for c in selected}.values());report['application_case_count']=len(selected)
    for name,text in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('bundle',row['program']),('minimal-copy',prelude+core+'\n'+row['snippet'])]:
        exe,entry=compile(name,text);entry['runs']=[]
        for c in selected:
            inp=payload(c['p'],c['queries']);run=subprocess.run([str(exe)],input=inp,capture_output=True,env=env,timeout=180)
            assert run.returncode==0 and not run.stderr,(name,c['name'],run.returncode,run.stderr[-1000:])
            assert list(map(int,run.stdout.split()))==[v for ans in c['expected'] for v in ans],(name,c['name'])
            (out/(name+'-'+c['name']+'.out')).write_bytes(run.stdout)
            entry['runs'].append(dict(case=c['name'],input_sha256=sha(inp),output_sha256=sha(run.stdout),passed=True))
        report['applications'].append(entry)
    report.update(source_after_sha256=snapshot(ROOT),passed=True,scope='Strict CCW n>=3, |coordinates|<=1e12; exact support-line oracle, nearest contact and large closed forms. API demonstration only; no OJ AC, whole Chengdu I, non-strict polygons, full-suite or leak claim.')
    assert before==report['source_after_sha256'];(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Convex tangents',mode,report['polygons'],'polygons',report['queries'],'queries per form;',len(selected),'API inputs x3 PASS:',out/'report.json')
if __name__=='__main__':main()
