"""Negative controls against the same independent moment and plane oracle."""
from pathlib import Path
import subprocess,json
path=Path(__file__).with_name('hull3d_metrics.py')
exec(path.read_text().split('reports = {}')[0])
original=(build/'copied.cpp').read_text()
mutations={
 'wrong_total':('total += 4 * v;', 'total += 3 * v;'),
 'missing_anchor':('mass[0] += v;', 'mass[0] += 0;'),
 'vertex_mean':('(long double)mass[i] * (p[k] - base[k])', '(long double)total / h.p.size() * (p[k] - base[k])'),
 'wrong_distance_sign':('auto d = -Hull::orient', 'auto d = Hull::orient'),
 'incomplete_coplanarity':('for (int u : h.faces[i])', 'for (int u : vector<int>{h.faces[i][0]})'),
}
report={}
for name,(a,b) in mutations.items():
 assert original.count(a)==1,(name,original.count(a))
 src=build/('mutation-'+name+'.cpp');src.write_text(original.replace(a,b))
 exe=src.with_suffix('')
 subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(src),'-o',str(exe)],check=True)
 result=subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True,timeout=30)
 try:check(result.stdout)
 except AssertionError as e:report[name]={'rejected':True,'first_mismatch':str(e)[:300]}
 else:raise AssertionError('Surviving mutation '+name)
 print(name,'rejected',flush=True)
(root/'verification/hull3d-metrics-mutations.json').write_text(json.dumps(report,indent=2)+'\n')
