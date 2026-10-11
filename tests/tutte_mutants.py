from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[1]
b=root/'build/tutte/mutants';b.mkdir(parents=True,exist_ok=True)
s=(root/'src/compact/tutte.hpp').read_text()
t=(root/'tests/tutte.cpp').read_text().replace('#include "../src/compact/tutte.hpp"','#include "mutant.hpp"')
(b/'test.cpp').write_text(t)
mutants={'geometric-zero':('geometric(n + 1);','geometric(n + 1, 1);'), 'mobius-sign':('value -= f[(size_t)(s ^ bit) * width + j];','value += f[(size_t)(s ^ bit) * width + j];'), 'component-sum':('answer = answer * connected(g) % mod;','answer = (answer + connected(g)) % mod;')}
r={}
for name,(old,new) in mutants.items():
 assert old in s
 (b/'mutant.hpp').write_text(s.replace(old,new))
 subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(b/'test.cpp'),'-o',str(b/'test')],check=True)
 p=subprocess.run([str(b/'test')],capture_output=True,timeout=30)
 assert p.returncode!=0,name
 r[name]='detected by independent edge-subset definition'
 print(name,r[name],flush=True)
(root/'verification/tutte-mutants.json').write_text(json.dumps(r,indent=2)+'\n')
