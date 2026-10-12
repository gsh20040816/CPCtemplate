from compiler_config import CXX
from pathlib import Path
import subprocess,json,hashlib,time
root=Path(__file__).resolve().parents[1];build=root/'build/weighted-blossom';build.mkdir(exist_ok=True)
header=(root/'src/compact/weighted_blossom.hpp').read_text()
body=header.split('// BEGIN WeightedBlossom\n')[1].split('// END WeightedBlossom')[0]
driver=(root/'tests/weighted_blossom.cpp').read_text().split('\n',1)[1]
# Only the implementation has NDEBUG; oracle assertions remain active.
(build/'ndebug.cpp').write_text('#define NDEBUG\n#include "../../src/compact/weighted_blossom.hpp"\n#undef NDEBUG\n#include <cassert>\n'+driver)
(build/'copied.cpp').write_text('#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'+body+driver)
reports={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
 for form in ['header','ndebug','copied']:
  src=root/'tests/weighted_blossom.cpp' if form=='header' else build/(form+'.cpp');exe=build/(mode+'-'+form)
  subprocess.run([CXX,'-std=c++20',*flags,str(src),'-o',str(exe)],check=True)
  start=time.monotonic();r=subprocess.run([str(exe)],text=True,capture_output=True,check=True,timeout=180)
  assert not r.stderr,r.stderr
  reports[mode+'-'+form]=dict(status='pass',result=r.stdout.strip(),seconds=round(time.monotonic()-start,3));print(mode,form,r.stdout.strip(),flush=True)
(root/'verification/weighted-blossom-local.json').write_text(json.dumps(dict(status='pass',source_sha256=hashlib.sha256(header.encode()).hexdigest(),oracle='Independent subset DP; optimum weight/cardinality and complete witness checks and independent LP dual certificates; exhaustive four-vertex weights, all five-vertex simple graphs, random n<=12, LL extremes, repeat solve and add after solve',forms=reports),indent=2)+'\n')
