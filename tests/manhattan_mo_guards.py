"""Check source singleton failure, active-set invariants and rejected mutants."""
from pathlib import Path
import json,subprocess,random,math
from compiler_config import CXX
root=Path(__file__).resolve().parents[1];b=root/'build/manhattan-mo'
rng=random.Random(871);data='';truth=[]
for n in range(1,36):
 a=[rng.randint(1,n) for _ in range(n)]
 q=[(l,r) for l in range(n) for r in range(l+1,n+1)];rng.shuffle(q)
 data+=f'{n} {len(q)}\n'+' '.join(map(str,a))+'\n'+''.join(f'{l+1} {r}\n' for l,r in q)
 for l,r in q:
  num=sum(a[i]==a[j] for i in range(l,r) for j in range(i+1,r));den=(r-l)*(r-l-1)//2;g=math.gcd(num,den)
  truth.append(f'{num//g}/{den//g}' if num else '0/1')
report={}
for v in ['block','mst']:
 p=subprocess.run([str(b/f'sanitizer-{v}-original')],input='1 1\n1\n1 1\n',text=True,capture_output=True)
 assert 'division by zero' in p.stderr,(v,p.stderr)
 report['source-singleton-'+v]='division by zero reproduced'
 s=(b/f'minimal-{v}.cpp').read_text()
 s=s.replace('        long long sum = 0;','        vector<int> live(n);\n        long long sum = 0;')
 s=s.replace('            sum += cnt[a[i]];','            if (i < 0 || i >= n || live[i]++) abort();\n            sum += cnt[a[i]];')
 s=s.replace('            cnt[a[i]]--;','            if (i < 0 || i >= n || !live[i]--) abort();\n            cnt[a[i]]--;')
 check='''            for (int j = 0; j < n; j++)
                if (live[j] != (ql <= j && j < qr)) abort();
'''
 if v=='mst':s=s.replace('            save(id, r - l);',check+'            save(id, r - l);')
 else:s=s.replace('            save(id, mo.q[id].r - mo.q[id].l);','            int ql = mo.q[id].l, qr = mo.q[id].r;\n'+check+'            save(id, qr - ql);')
 p=b/f'guard-{v}.cpp';p.write_text(s);exe=b/f'guard-{v}'
 subprocess.run([CXX,'-std=c++20','-O2',str(p),'-o',str(exe)],check=True)
 out=subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True)
 assert out.stdout.splitlines()==truth
 report['active-set-'+v]=dict(queries=len(truth),status='pass')
 s=(b/f'minimal-{v}.cpp').read_text()
 for name,bad in [('singleton',s.replace('if (sum == 0)','if (false)')),('denominator',s.replace('len * (len - 1) / 2','len * len / 2'))]:
  p=b/f'mutant-{v}-{name}.cpp';p.write_text(bad);exe=p.with_suffix('')
  subprocess.run([CXX,'-std=c++20','-O2',str(p),'-o',str(exe)],check=True)
  out=subprocess.run([str(exe)],input=data,text=True,capture_output=True)
  assert out.returncode or out.stdout.splitlines()!=truth
  report['mutant-'+v+'-'+name]='rejected'
(root/'verification/manhattan-mo-guards.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
