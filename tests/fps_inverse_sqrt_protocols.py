from pathlib import Path
import hashlib,json,os,random,subprocess,sys
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from usage_examples import records
row=next(r for r in records() if r['id']=='example-450')
assert (root/row['snippet_file']).read_text()==row['snippet']
out=root/'build/wida-montgomery-poly'
p=998244353
rng=random.Random(450)
cases=[]
def add(r):
    n=len(r)
    a=[0]*n
    for i,x in enumerate(r):
        for j in range(n-i):a[i+j]=(a[i+j]+x*r[j])%p
    iv=[pow(r[0],-1,p)]+[0]*(n-1)
    for i in range(1,n):iv[i]=-sum(r[j]*iv[i-j] for j in range(1,i+1))*iv[0]%p
    a=[x-p if i%3==0 else x for i,x in enumerate(a)]
    cases.append((a,iv))
for n in [1,2,3,7,8,9,31,32,33,63,64,65,127,128,129,255,256,257,512,513]:
    for _ in range(3):add([rng.randrange(1,1000000)]+[rng.randrange(p) for _ in range(n-1)])
for _ in range(140):
    n=rng.randrange(1,81)
    add([1]+[rng.randrange(p) for _ in range(n-1)])
for _ in range(4):cases.append(([1,2],[1,p-1]))
assert pow(3,(p-1)//2,p)==p-1
for a in [[0],[0,0],[0,1],[0,0,1],[3],[3,1]]:cases.append((a,[-1]))
data=str(len(cases))+'\n'+''.join(str(len(a))+'\n'+' '.join(map(str,a))+'\n' for a,_ in cases)
expected=[b for _,b in cases]
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
report={'scope':'Exact printed/header programs; independent quadratic construction and coefficientwise inverse; repeated calls and nonunit/nonresidue rejection. No online AC','runs':[]}
for form,source in [('header','#include "'+str(root/row['driver'])+'"\n'),('printed',row['program'])]:
    cpp=out/('inverse-sqrt-'+form+'.cpp');cpp.write_text(source)
    for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
        exe=out/('inverse-sqrt-'+form+'-'+mode)
        subprocess.run([CXX,'-std=c++20',*flags,str(cpp),'-o',str(exe)],check=True)
        r=subprocess.run([str(exe)],input=data,text=True,capture_output=True,env=env,timeout=90)
        assert r.returncode==0 and not r.stderr,r.stderr
        assert [list(map(int,line.split())) for line in r.stdout.splitlines()]==expected
        report['runs'].append(dict(form=form,mode=mode,cases=len(cases),source_sha256=hashlib.sha256(source.encode()).hexdigest()))
        print(form,mode,len(cases),'Python inverse square root checks PASS',flush=True)
(root/'verification/fps-inverse-sqrt-protocols.json').write_text(json.dumps(report,indent=2)+'\n')
