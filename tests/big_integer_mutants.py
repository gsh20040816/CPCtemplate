from pathlib import Path
import subprocess,json
from compiler_config import CXX
root=Path(__file__).resolve().parents[1];b=root/'build/bigint';s=(b/'copied.cpp').read_text()
changes={
 'lost_quotient_sign':('q.sign = sign * (b < 0 ? -1 : 1);','q.sign = 1;'),
 'lost_product_carry':('c.d[i + b.d.size()] = carry;','c.d[i + b.d.size()] = 0;'),
 'wrong_borrow':('c.d[i] = v + borrow * base;','c.d[i] = v;'),
 'negative_zero':('if (d.empty())\n            sign = 1;','if (d.empty())\n            sign = -1;')}
text=(b/'cases.in').read_text();want=(b/'expected.txt').read_text();report={}
for name,(a,c) in changes.items():
 assert s.count(a)==1
 f=b/(name+'.cpp');f.write_text(s.replace(a,c));exe=b/name
 subprocess.run([CXX,'-std=c++20','-O2',str(f),'-o',str(exe)],check=True)
 r=subprocess.run([str(exe)],input=text,text=True,capture_output=True,timeout=90)
 assert r.returncode!=0 or r.stdout!=want,name
 report[name]={'detected':True,'exit_code':r.returncode}
(root/'verification/big-integer-mutants.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
