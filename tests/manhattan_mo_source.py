"""Full source and independent probability/route checks for kuangbin 8.7."""
from pathlib import Path
import hashlib,json,math,random,re,resource,subprocess,sys,platform
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
build=root/'build/manhattan-mo'
build.mkdir(exist_ok=True)
if platform.system()!='Darwin':
 _,hard=resource.getrlimit(resource.RLIMIT_STACK)
 resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard!=-1 else 512<<20,hard))
sys.path.insert(0,str(root/'tools'))
from usage_examples import expand
text=(root/'build/source-audit/kuangbin.txt').read_text()
for variant,title,stop,total in [('block','8.7.1 分块','8.7.2 Manhattan MST',76),('mst','8.7.2 Manhattan MST 的 dfs 顺序求解','8.8 VIM 配置',176)]:
 part=text.rsplit(title,1)[1].split(stop)[0]
 lines=[]
 for line in part.splitlines():
  m=re.match(r'^\s*(\d+)(?:\s+(.*))?$',line)
  if m:
   assert int(m[1])==len(lines)+1,(variant,m[1],len(lines))
   lines.append(m[2] or '')
  elif lines and line.strip() and 'kuangbin' not in line:lines[-1]+=' '+line.strip()
 assert len(lines)==total,(variant,len(lines))
 (build/f'original-{variant}.cpp').write_text('#include <bits/stdc++.h>\nusing namespace std;\n'+'\n'.join(lines).replace('−','-')+'\n')
rng=random.Random(8702)
cases=[]
def case(a,q):
 data=f'{len(a)} {len(q)}\n'+' '.join(map(str,a))+'\n'+''.join(f'{l+1} {r}\n' for l,r in q)
 truth=[]
 for l,r in q:
  count={}
  for x in a[l:r]:count[x]=count.get(x,0)+1
  num=sum(c*(c-1)//2 for c in count.values());den=(r-l)*(r-l-1)//2
  g=math.gcd(num,den)
  truth.append(f'{num//g}/{den//g}' if num else '0/1')
 return data,truth
for n in range(2,10):
 for bits in range(1<<n):
  a=[1+(bits>>i&1) for i in range(n)]
  q=[(l,r) for l in range(n) for r in range(l+2,n+1)]
  cases.append(case(a,q))
for _ in range(120):
 n=rng.randint(2,50);a=[rng.randint(1,n) for _ in range(n)];q=[]
 for j in range(70):
  l=rng.randrange(n-1);q.append((l,rng.randint(l+2,n)))
 cases.append(case(a,q))
# Maximum official n,m; repeated known-answer intervals and a long MST chain.
for same in [False,True]:
 n=50000;a=[1]*n if same else list(range(1,n+1));q=[(0,r) for r in range(2,n+1)]+[(n-2,n)]
 data=f'{n} {len(q)}\n'+' '.join(map(str,a))+'\n'+''.join(f'{l+1} {r}\n' for l,r in q)
 cases.append((data,['1/1' if same else '0/1']*len(q)))
base_data=''.join(a for a,b in cases);base_truth=[v for a,b in cases for v in b]
extended=case([1,2,1],[(0,1),(1,2),(2,3),(0,3),(0,1)])
report={}
sections={r['symbol']:r['code'] for r in json.loads((root/'build/book-sections.json').read_text())}
# The new helper is read directly until generated book sections include it.
assert 'manhattan_order' in sections
for variant,names in [('block',['Mo']),('mst',['dsu','ManhattanMST','manhattan_order'])]:
 driver=root/f'verify/luogu/P1494.{variant}.cpp'
 (build/f'expanded-{variant}.cpp').write_text(expand(driver.read_text(),driver.parent,set()))
 pre='#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'
 (build/f'minimal-{variant}.cpp').write_text(pre+'\n'.join(sections[n] for n in names)+'\nint main()'+driver.read_text().split('int main()',1)[1])
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
 if platform.system()=='Darwin':flags+=['-Wl,-stack_size,0x20000000']
 for variant in ['block','mst']:
  for form in ['original','driver','expanded','minimal','ndebug']:
   src=root/f'verify/luogu/P1494.{variant}.cpp' if form=='driver' else build/f'{"minimal" if form=="ndebug" else form}-{variant}.cpp'
   exe=build/f'{mode}-{variant}-{form}'
   subprocess.run([CXX,'-std=c++20',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],check=True)
   data=base_data;truth=base_truth
   if form!='original':data+=extended[0];truth=truth+extended[1]
   p=subprocess.run([str(exe)],input=data,text=True,capture_output=True,timeout=240,check=True)
   assert not p.stderr,p.stderr
   assert p.stdout.splitlines()==truth,(mode,variant,form)
   report[f'{mode}-{variant}-{form}']=dict(queries=len(truth),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),status='pass')
   print(mode,variant,form,len(truth),'PASS',flush=True)
 # Route oracle is independent complete-graph Prim; recursive 50k-chain boundary.
 for form in ['header','ndebug']:
  exe=build/f'{mode}-route-{form}'
  subprocess.run([CXX,'-std=c++20',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(root/'tests/manhattan_order.cpp'),'-o',str(exe)],check=True)
  p=subprocess.run([str(exe)],text=True,capture_output=True,check=True,timeout=120)
  assert not p.stderr,p.stderr
  report[f'{mode}-route-{form}']=dict(status='pass',checks=3004)
  print(p.stdout.strip(),mode,form,flush=True)
(root/'verification/manhattan-mo-local.json').write_text(json.dumps(dict(status='pass',source_pdf_sha256=hashlib.sha256((root/'build/source-audit/kuangbin.pdf').read_bytes()).hexdigest(),physical_pages=list(range(260,267)),source_lines={'block':76,'mst':176},datasets=len(cases),forms=report),indent=2)+'\n')
