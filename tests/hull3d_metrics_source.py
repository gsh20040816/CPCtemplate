from pathlib import Path
import re,subprocess,json,hashlib,random
root=Path.cwd();b=root/'build/hull3d-metrics'
s=(root/'build/source-audit/kuangbin.txt').read_text().rsplit('     7.4.1 HDU4273',1)[1].split('   8     其他')[0]
lines=[]
for line in s.splitlines():
 m=re.match(r'^\s*(\d+)(?:\s+(.*))?$',line)
 if m:
  assert int(m[1])==len(lines)+1,(m[1],len(lines))
  lines.append(m[2] or "")
 elif lines and line.strip() and 'kuangbin' not in line and 'HDU 4273' not in line:
  lines[-1]+=' '+line.strip()
assert len(lines)==246
original='#include <bits/stdc++.h>\nusing namespace std;\n'+'\n'.join(lines).replace('−','-')+'\n'
(b/'original.cpp').write_text(original)
rng=random.Random(4273)
sample=[[(0,0,0),(1,0,0),(0,1,0),(0,0,1)],[(x,y,z) for x in (0,2) for y in (0,2) for z in (0,2)]]
cases=sample[:]
# Moment-curve vertices are all extreme; moderate coordinates avoid upstream eps failures.
for k in range(100):
 vals=rng.sample(range(-15,16),rng.randrange(4,20))
 shift=[rng.randrange(-5000,5001) for _ in range(3)]
 cases.append([tuple(v+t for v,t in zip((i,i*i,i*i*i),shift)) for i in vals])
text=''.join(str(len(p))+'\n'+''.join(' '.join(map(str,q))+'\n' for q in p) for p in cases)
(b/'official-domain.txt').write_text(text)
report={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
 results=[]
 for form,source in [('original',b/'original.cpp'),('driver',root/'verify/hdu/4273.compact.cpp'),('minimal',b/'4273.cpp')]:
  exe=b/(mode+'-4273-'+form)
  subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,str(source),'-o',str(exe)],check=True)
  r=subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True,timeout=30)
  assert not r.stderr,r.stderr
  out=r.stdout.splitlines();assert len(out)==len(cases)
  assert out[:2]==['0.144','1.000']
  results.append(out)
 assert results[0]==results[1]==results[2],mode
 report[mode]={'cases':len(cases),'original_driver_minimal_equal':True}
 print(mode,'102 EOF cases PASS',flush=True)
(root/'verification/hull3d-metrics-source.json').write_text(json.dumps({'status':'pass','printed_pages':[243,248],'physical_pages':[245,250],'numbered_lines':246,'original_sha256':hashlib.sha256(original.encode()).hexdigest(),'pdf_sha256':hashlib.sha256((root/'build/source-audit/kuangbin.pdf').read_bytes()).hexdigest(),'normalization':'Unicode minus, wrapped numbered lines, standard includes only','tests':report},indent=2)+'\n')
