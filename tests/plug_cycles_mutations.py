"""Ensure the independent enumeration rejects specific transfer defects."""
from pathlib import Path
import json
import os
import subprocess
from compiler_config import CXX

root=Path(__file__).resolve().parents[1]
build=root/'build/plug-cycles'
core=(root/'src/compact/plug_cycles.hpp').read_text().replace('#pragma once\n','')
probe=(root/'tests/plug_cycles.cpp').read_text().replace('#include "../src/compact/plug_cycles.hpp"','CORE').replace('#include "../src/compact/plug_cycle.hpp"','#include "'+str(root/'src/compact/plug_cycle.hpp')+'"')
mutations=[('allow-nesting','nested || parity == 0','true'),('lose-cycle-count','add(c + 1)','add(c)'),('lose-row-shift','s << 4','s'),('lose-merge','if (v == y) v = x;','if (v == y) v = y;')]
report=[]
for name,old,new in mutations:
    assert old in core
    path=build/('mutant-'+name+'.cpp')
    path.write_text(probe.replace('CORE',core.replace(old,new)))
    exe=path.with_suffix('')
    subprocess.run([CXX,'-std=c++20','-O2','-I/opt/homebrew/include',str(path),'-o',str(exe)],check=True)
    p=subprocess.run([str(exe)],capture_output=True,text=True,timeout=30)
    assert p.returncode!=0 and 'expected' in p.stderr,(name,p.stderr)
    report.append({'mutation':name,'rejected':True,'counterexample':p.stderr.strip()})
    print(name,'REJECTED',flush=True)
(root/'verification/plug-cycles-mutations.json').write_text(json.dumps(report,indent=2)+'\n')
