"""Reject four semantic faults using the independently generated oracle corpus."""
from pathlib import Path
import json,subprocess,sys
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
b=root/'build/circle-coverage'
v=json.loads((b/'cases.json').read_text())
pairs=[(c,e) for c,e in zip(v['cases'],v['expected']) if len(c)<30]
text=str(len(pairs))+'\n'+''.join(str(len(c))+'\n'+''.join(' '.join(map(str,q))+'\n' for q in c) for c,e in pairs)
source=(b/'copied.cpp').read_text()
changes={
 'duplicates-all-contained':('(s > r || j < i)','true'),
 'descending-difference':('for (int k = 1; k <= size; k++)','for (int k = size; k >= 1; k--)'),
 'absolute-arc':('R y = value - error[count];','R y = abs(value) - error[count];'),
 'missing-wrap':('events.push_back({l + tau, 1});','events.push_back({l + tau, 0});')}
report={}
for name,(old,new) in changes.items():
 assert source.count(old)==1
 p=b/(name+'.cpp');p.write_text(source.replace(old,new));exe=b/name
 subprocess.run([CXX,'-std=c++20','-O2',str(p),'-o',str(exe)],check=True)
 lines=subprocess.check_output([str(exe)],input=text,text=True).splitlines()
 bad=[]
 for i,((c,e),line) in enumerate(zip(pairs,lines)):
  if any(abs(float(x)-float(y))/(1+abs(float(y)))>1e-9 for x,y in zip(line.split(),e)):bad.append(i)
 assert bad,name
 report[name]={'status':'rejected','failed_cases':len(bad),'first_case':pairs[bad[0]][0]}
 print(name,len(bad),'rejected',flush=True)
(root/'verification/circle-coverage-mutants.json').write_text(json.dumps(report,indent=2)+'\n')
