"""Negative controls for the all-state route and rank checker."""
from pathlib import Path
import json,subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1];build=root/'build/eight-puzzle'
source=(root/'src/compact/eight_puzzle.hpp').read_text().replace('#pragma once\n','')
harness=(root/'tests/eight_puzzle.cpp').read_text().replace('#include "../src/compact/eight_puzzle.hpp"',source)
changes={
 'direction-not-inverted':('string inverse = "durl";','string inverse = "udlr";'),
 'rank-base':('id = id * (9 - i) + smaller;','id = id * 8 + smaller;'),
 'unreachable-as-empty-solution':('return {false, ""};','return {true, ""};'),
 'horizontal-wrap':('if (r < 0 || r >= 3 || c < 0 || c >= 3) continue;','if (r * 3 + c < 0 || r * 3 + c >= 9) continue;')}
rows={}
for name,(old,new) in changes.items():
 assert harness.count(old)==1
 p=build/(name+'.cpp');p.write_text(harness.replace(old,new));exe=p.with_suffix('')
 subprocess.run([CXX,'-std=c++20','-O1','-fsanitize=address,undefined','-fno-sanitize-recover=all',str(p),'-o',str(exe)],check=True)
 result=subprocess.run([str(exe)],capture_output=True,text=True,timeout=30)
 assert result.returncode,name
 rows[name]=dict(rejected=True,returncode=result.returncode,diagnostic=result.stderr[:500])
 print(name,'rejected',flush=True)
(root/'verification/eight-puzzle-negative-controls.json').write_text(json.dumps(rows,indent=2)+'\n')
