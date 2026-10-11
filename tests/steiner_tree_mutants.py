from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[1]
b=root/'build/steiner/mutants';b.mkdir(parents=True,exist_ok=True)
s=(root/'src/compact/steiner_tree.hpp').read_text()
t=(root/'tests/steiner_tree.cpp').read_text().replace('#include "../src/compact/steiner_tree.hpp"','#include "mutant.hpp"')
(b/'test.cpp').write_text(t)
mutants={'missing-merge':('if (sub > other) continue;', 'continue;'), 'wrong-cost':('distance + edges[id].w;', 'distance + edges[id].w + 1;'), 'missing-witness':('used[id] = 1;', 'used[id] = 0;')}
r={}
for name,(old,new) in mutants.items():
 assert old in s
 (b/'mutant.hpp').write_text(s.replace(old,new))
 subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(b/'test.cpp'),'-o',str(b/'test')],check=True)
 p=subprocess.run([str(b/'test')],capture_output=True,timeout=30)
 assert p.returncode!=0,name
 r[name]='detected by independent edge-subset definition'
 print(name,r[name],flush=True)
(root/'verification/steiner-tree-mutants.json').write_text(json.dumps(r,indent=2)+'\n')
