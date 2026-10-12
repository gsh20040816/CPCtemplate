from pathlib import Path
import hashlib,json,math,os,random,subprocess,sys
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from usage_examples import records
row=next(r for r in records() if r['id']=='example-449')
assert (root/row['snippet_file']).read_text()==row['snippet']
out=root/'build/static-mod64'
p=(1<<64)-1
rng=random.Random(449)
cases=[(a,b,k) for a in [-(1<<63),-1,0,1,(1<<63)-1] for b in [0,1,2,3,1<<63,p-1,p] for k in [0,1,p-1,p]]
cases += [(rng.randrange(-(1<<63),1<<63),rng.randrange(1<<64),rng.randrange(1<<64)) for _ in range(4000)]
data=str(len(cases))+'\n'+''.join(f'{a} {b} {k}\n' for a,b,k in cases)
expected=[(a%p,b%p,(a+b)%p,(a-b)%p,a*b%p,pow(a,k,p),pow(b,-1,p) if math.gcd(b,p)==1 else -1) for a,b,k in cases]
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
report={'scope':'Exact printed and header API programs at UINT64_MAX composite modulus; Python integer arithmetic, modular pow and inverse','runs':[]}
for form,source in [('header','#include "'+str(root/row['driver'])+'"\n'),('printed',row['program'])]:
    cpp=out/('protocol-'+form+'.cpp');cpp.write_text(source)
    for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
        exe=out/(form+'-'+mode)
        subprocess.run([CXX,'-std=c++20',*flags,str(cpp),'-o',str(exe)],check=True)
        r=subprocess.run([str(exe)],input=data,text=True,capture_output=True,env=env,timeout=90)
        assert r.returncode==0 and not r.stderr,r.stderr
        assert [tuple(map(int,line.split())) for line in r.stdout.splitlines()]==expected
        report['runs'].append(dict(form=form,mode=mode,cases=len(cases),source_sha256=hashlib.sha256(source.encode()).hexdigest()))
        print(form,mode,len(cases),'Python checks PASS',flush=True)
(root/'verification/static-mod64-protocols.json').write_text(json.dumps(report,indent=2)+'\n')
