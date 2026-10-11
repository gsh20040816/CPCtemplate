from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[1]
b=root/'build/cartesian/mutants';b.mkdir(parents=True,exist_ok=True)
s=(root/'src/compact/cartesian_tree.hpp').read_text()
t=(root/'tests/cartesian_tree.cpp').read_text().replace('#include "../src/compact/cartesian_tree.hpp"','#include "mutant.hpp"')
(b/'test.cpp').write_text(t)
mutants={'wrong-tie':('a[i] < a[st.back()]','a[i] <= a[st.back()]'), 'lost-left':('tree.left[i] = last;', 'tree.left[i] = -1;'), 'wrong-root':('tree.root = st.front();', 'tree.root = st.back();')}
r={}
for name,(old,new) in mutants.items():
 assert old in s
 (b/'mutant.hpp').write_text(s.replace(old,new))
 subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(b/'test.cpp'),'-o',str(b/'test')],check=True)
 p=subprocess.run([str(b/'test')],capture_output=True,timeout=30)
 assert p.returncode!=0,name
 r[name]='detected by independent recursive argmin tree'
 print(name,r[name],flush=True)
(root/'verification/cartesian-tree-mutants.json').write_text(json.dumps(r,indent=2)+'\n')
