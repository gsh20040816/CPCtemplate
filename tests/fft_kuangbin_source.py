"""Complete kuangbin FFT source extraction and independent application tests."""
from pathlib import Path
from itertools import combinations, combinations_with_replacement
import re,random,json,hashlib,subprocess,sys,time
root=Path(__file__).resolve().parents[1]
build=root/'build/fft-kuangbin';build.mkdir(exist_ok=True)
sys.path.insert(0,str(root/'tools'))
from usage_examples import expand
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
text=(root/'build/source-audit/kuangbin.txt').read_text().rsplit('     2.9 FFT',1)[1].split('    2.10   高斯消元法')[0]
lines=[]
for line in text.splitlines():
 m=re.match(r'^\s*(\d+)(?:\s+(.*))?$',line)
 if m:
  assert int(m[1])==len(lines)+1,(m[1],len(lines))
  lines.append(m[2] or '')
 elif lines and line.strip() and 'kuangbin' not in line:lines[-1]+=' '+line.strip()
assert len(lines)==156
lines=[s.replace('−','-') for s in lines]
prelude='#include <bits/stdc++.h>\nusing namespace std;\n'
source={1402:prelude+'\n'.join(lines[:100])+'\n',4609:prelude+'\n'.join(lines[:62]+lines[101:])+'\n'}
for pid in source:(build/f'original-{pid}.cpp').write_text(source[pid])
rng=random.Random(14024609)
products=[('1','2'),('1000','2'),('0','0'),('000','000009'),('9','9')]
for k in range(180):
 products.append(tuple(''.join(str(rng.randrange(10)) for _ in range(rng.randrange(1,401))) for j in range(2)))
products += [('9'*50000,'9'*50000),('1'+'0'*49999,'9'*50000),('9'*50000,'9'),('0','9'*50000),('1234567890'*5000,'9876543210'*5000)]
signed=[('-0','+0'),('-000123','+00456'),('-999','-999'),('+001','-1000')]
for k in range(100):signed.append(tuple(str(rng.randrange(-10**100,10**100)) for j in range(2)))
def multiplication_data(cases):return ''.join(a+' '+b+'\n' for a,b in cases)
def multiplication_truth(cases):return [str(int(a)*int(b)) for a,b in cases]
triangles=[[1,3,3,4],[2,3,3,4]]
for n in range(3,9):triangles.extend(map(list,combinations_with_replacement(range(1,6),n)))
for k in range(160):triangles.append([rng.randrange(1,101) for _ in range(rng.randrange(3,31))])
def brute(a):
 good=sum(x+y>z for triple in combinations(a,3) for x,y,z in [sorted(triple)])
 return good/(len(a)*(len(a)-1)*(len(a)-2)//6)
tri_truth=[brute(a) for a in triangles]
# Maximum frequency and maximum transform length; closed forms, not FFT oracles.
for a,want in [([100000]*100000,1),([1]*99999+[100000],(99997/100000)),([1]*50000+[100000]*50000,None),([1,1,2],0),([1,2,3],0)]:
 if want is None:
  n=100000;k=50000
  choose=lambda n:n*(n-1)*(n-2)//6
  bad=k*(k-1)//2*k
  want=(choose(n)-bad)/choose(n)
 triangles.append(a);tri_truth.append(want)
triangle_data=str(len(triangles))+'\n'+''.join(str(len(a))+'\n'+' '.join(map(str,a))+'\n' for a in triangles)
# The total test count exceeds the official single-file T bound; batch at <=100 below.
def run(exe,data,timeout=90):
 p=subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True,timeout=timeout)
 assert not p.stderr,p.stderr
 return p.stdout.splitlines()
reports={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
 for pid in [1402,4609]:
  for form in ['original','driver','expanded','ndebug']:
   driver=root/f'verify/hdu/{pid}.compact.cpp'
   if form=='expanded':
    src=build/f'expanded-{pid}.cpp';src.write_text(expand(driver.read_text(),driver.parent,set()))
   else:src=build/f'original-{pid}.cpp' if form=='original' else driver
   exe=build/f'{mode}-{pid}-{form}'
   subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],check=True)
   start=time.monotonic()
   if pid==1402:
    cases=products if form=='original' else products+signed
    out=run(exe,multiplication_data(cases));assert out==multiplication_truth(cases),(mode,form,'product')
    count=len(cases)
   else:
    out=[]
    for i in range(0,len(triangles),100):
     batch=triangles[i:i+100]
     data=str(len(batch))+'\n'+''.join(str(len(a))+'\n'+' '.join(map(str,a))+'\n' for a in batch)
     out += run(exe,data)
    assert len(out)==len(tri_truth)
    for i,(v,w) in enumerate(zip(out,tri_truth)):assert abs(float(v)-w)<5.1e-8,(mode,form,i,v,w)
    count=len(triangles)
   reports[f'{mode}-{pid}-{form}']={'cases':count,'seconds':round(time.monotonic()-start,3)}
   print(mode,pid,form,count,'PASS',flush=True)
report={'status':'pass','source_numbered_lines':156,'printed_pages':[34,37],'physical_pages':[36,39],'normalization':'Unicode minus, numbered-line wraps, common62-lineFFT prepended to second application, standard headers only','source_pdf_sha256':hashlib.sha256((root/'build/source-audit/kuangbin.pdf').read_bytes()).hexdigest(),'original_sha256':{str(k):hashlib.sha256(v.encode()).hexdigest() for k,v in source.items()},'source_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'src/compact/fft.hpp',root/'src/compact/convolution_fft.hpp',root/'verify/hdu/1402.compact.cpp',root/'verify/hdu/4609.compact.cpp']},'forms':reports}
(root/'verification/fft-kuangbin-local.json').write_text(json.dumps(report,indent=2)+'\n')
