"""Ensure the independent active-set oracle catches contract regressions."""
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
(root/'build/ordinary-mo').mkdir(parents=True, exist_ok=True)
header = (root/'src/compact/mo.hpp').read_text().replace('#pragma once\n','')
test = (root/'tests/ordinary_mo.cpp').read_text()
mutants = {
    'missing_left_expansion': ('while (l > a.l) add(--l);', 'while (l > a.l) --l;'),
    'missing_cleanup': ('while (l < r) del(l++);', ''),
    'wrong_query_id': ('ans(a.id);', 'ans(0);'),
}
report = {}
for name,(old,new) in mutants.items():
    assert old in header
    source=root/'build/ordinary-mo'/('mutant-'+name+'.cpp')
    source.write_text(test.replace('#include "../src/compact/mo.hpp"',header.replace(old,new)))
    exe=source.with_suffix('')
    subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(source),'-o',str(exe)],check=True)
    p=subprocess.run([str(exe)],capture_output=True,timeout=30)
    assert p.returncode != 0,name
    report[name]={'detected':True,'returncode':p.returncode}
(root/'verification/ordinary-mo-mutants.json').write_text(json.dumps(report,indent=2)+'\n')
print('3 mutants detected')
