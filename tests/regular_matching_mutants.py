from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[1]
b=root/'build/regular-matching/mutants';b.mkdir(parents=True,exist_ok=True)
s=(root/'src/compact/regular_matching.hpp').read_text()
t=(root/'tests/regular_matching.cpp').read_text().replace('#include "../src/compact/regular_matching.hpp"','#include "mutant.hpp"')
(b/'test.cpp').write_text(t)
mutants={'stale-right-mate':('right[v] = x;','// omit right mate update'), 'forward-flip':('for (int i = (int)path.size() - 1; i >= 0; i--)','for (int i = 0; i < (int)path.size(); i++)'), 'stale-loop-position':('pos[path.back()] = -1;','// omit removed position reset')}
r={}
for name,(old,new) in mutants.items():
 assert old in s
 (b/'mutant.hpp').write_text(s.replace(old,new))
 subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(b/'test.cpp'),'-o',str(b/'test')],check=True)
 try:
  p=subprocess.run([str(b/'test')],capture_output=True,timeout=10)
  assert p.returncode!=0,name
  r[name]='detected by nonzero exit'
 except subprocess.TimeoutExpired:
  r[name]='detected by timeout'
 print(name,r[name],flush=True)
(root/'verification/regular-matching-mutants.json').write_text(json.dumps(r,indent=2)+'\n')
