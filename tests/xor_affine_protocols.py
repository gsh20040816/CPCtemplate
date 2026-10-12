from pathlib import Path
import hashlib,json,os,random,subprocess,sys
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from usage_examples import records
out=root/'build/wida-matrix'
rng=random.Random(457)
mask=(1<<64)-1
cases={'example-456':[],'example-457':[]}
def apply(col,bias,x):
    result=bias
    for i in range(64):
        if (x>>i)&1:result^=col[i]
    return result
for trial in range(80):
    bias=rng.getrandbits(64)
    col=[rng.getrandbits(64) for _ in range(64)]
    queries=[];truth=[]
    for _ in range(4):
        x=rng.getrandbits(64);k=rng.randrange(12);y=x
        for _ in range(k):y=apply(col,bias,y)
        queries.append(f'{x} {k}\n');truth.append(y)
    data=str(bias)+'\n'+' '.join(map(str,col))+'\n4\n'+''.join(queries)
    cases['example-456'].append((data,truth))
    ops=[(rng.randrange(64),rng.randrange(2),rng.getrandbits(64)) for _ in range(trial%15)]
    constant=rng.getrandbits(64);x=rng.getrandbits(64);k=rng.randrange(12);y=x
    for _ in range(k):
        z=constant
        for s,o,a in ops:
            rotated=((y<<s)|(y>>(64-s)))&mask
            z^=(rotated|a) if o==0 else (rotated&a)
        y=z
    data=str(len(ops))+'\n'+''.join(f'{s} {o} {a}\n' for s,o,a in ops)+f'{constant} {x} {k}\n'
    cases['example-457'].append((data,[y]))
for k in [0,1,2,mask]:
    x=mask;bias=0x123456789abcdef0
    data=str(bias)+'\n'+' '.join(str(1<<i) for i in range(64))+f'\n1\n{x} {k}\n'
    truth=x^(bias if k%2 else 0)
    cases['example-456'].append((data,[truth]))
    cases['example-457'].append((f'1\n0 1 {mask}\n{bias} {x} {k}\n',[truth]))
report=dict(scope='Exact printed/header drivers with independent Python repeated bit/rotation expressions and analytic uint64 toggle powers. No online AC.',runs=[])
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for row in records():
    if row['id'] not in cases:continue
    for form in ['header','printed']:
        source=root/row['driver'] if form=='header' else out/(row['id']+'.cpp')
        if form=='printed':source.write_text(row['program'])
        for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
            exe=out/f"{row['id']}-{form}-{mode}"
            subprocess.run([CXX,'-std=c++20',*flags,str(source),'-o',str(exe)],check=True)
            for data,expected in cases[row['id']]:
                r=subprocess.run([str(exe)],input=data,text=True,capture_output=True,env=env,timeout=30)
                assert r.returncode==0 and not r.stderr and list(map(int,r.stdout.split()))==expected,(row['id'],mode,data[:80],r.stdout,r.stderr)
            report['runs'].append(dict(id=row['id'],form=form,mode=mode,cases=len(cases[row['id']]),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),program_sha256=row['program_sha256']))
            print(row['id'],form,mode,'PASS',flush=True)
(root/'verification/xor-affine-protocols.json').write_text(json.dumps(report,indent=2)+'\n')
