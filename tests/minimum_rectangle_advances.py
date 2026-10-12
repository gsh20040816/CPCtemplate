"""Instrument the actual implementation to check amortized pointer work."""
from pathlib import Path
import json,subprocess,math
from compiler_config import CXX
b=Path('build/minimum-rectangle')
s=(b/'copied.cpp').read_text().replace('pair<RealPlane::R, array<RealPlane::Point, 4>> minimum_rectangle','long long advances = 0;\npair<RealPlane::R, array<RealPlane::Point, 4>> minimum_rectangle').replace('steps++;','steps++;\n                advances++;').replace('auto [area, box] = minimum_rectangle(p);','advances = 0;\n        auto [area, box] = minimum_rectangle(p);\n        if (advances > 6LL * n + 6) abort();')
(b/'counted.cpp').write_text(s)
subprocess.run([CXX,'-std=c++20','-O2',str(b/'counted.cpp'),'-o',str(b/'counted')],check=True)
v=json.loads((b/'cases.json').read_text());cases=v['cases'];n=50000
cases.append([(math.cos(2*math.pi*i/n),math.sin(2*math.pi*i/n)) for i in range(n)])
s=str(len(cases))+'\n'+''.join(str(len(p))+'\n'+''.join(f'{x} {y}\n' for x,y in p) for p in cases)
subprocess.run([str(b/'counted')],input=s,text=True,stdout=subprocess.DEVNULL,check=True,timeout=20)
print('caliper advance bound',len(cases),'PASS')
Path('verification/minimum-rectangle-advances.json').write_text(json.dumps(dict(status='pass',cases=len(cases),bound='three pointers combined <=6*n+6; instrumented production source; includes 50000 regular polygon'),indent=2)+'\n')
