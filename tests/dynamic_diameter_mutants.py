from pathlib import Path
import subprocess,json
root=Path.cwd()
s=(root/'src/compact/dynamic_diameter.hpp').read_text()
t=(root/'tests/dynamic_diameter.cpp').read_text().replace('#include "../src/compact/dynamic_diameter.hpp"','#include "mutant.hpp"')
b=root/'build/dynamic-diameter'
(b/'mutant-test.cpp').write_text(t)
mutants={'missing-return-visit':('                d.push_back(depth);','                // omit return visit'), 'wrong-lazy-sign':('t[x].left -= delta;','t[x].left += delta;'), 'missing-cross-term':('a.left + b.high, a.high + b.right','a.left + b.high, 0LL')}
result={}
for name,(old,new) in mutants.items():
 assert old in s
 (b/'mutant.hpp').write_text(s.replace(old,new))
 subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(b/'mutant-test.cpp'),'-o',str(b/'mutant')],check=True)
 r=subprocess.run([str(b/'mutant')],capture_output=True,timeout=30)
 assert r.returncode != 0,name
 result[name]='detected'
 print(name,'detected',flush=True)
(root/'verification/dynamic-diameter-mutants.json').write_text(json.dumps(result,indent=2)+'\n')
