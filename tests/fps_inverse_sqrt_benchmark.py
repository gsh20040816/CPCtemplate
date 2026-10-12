from pathlib import Path
import hashlib,json,statistics,subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
exe=root/'build/wida-montgomery-poly/benchmark'
subprocess.run([CXX,'-std=c++20','-O2',str(root/'tests/fps_inverse_sqrt_benchmark.cpp'),'-o',str(exe)],check=True)
rows=[]
for n in [32768,131072]:
    runs=[]
    for repeat in range(3):
        for mode in (['original','composition'] if repeat%2==0 else ['composition','original']):
            seconds=float(subprocess.check_output([str(exe),str(n),mode],text=True,timeout=120))
            runs.append(dict(mode=mode,repeat=repeat,seconds=seconds))
    median={mode:statistics.median(r['seconds'] for r in runs if r['mode']==mode) for mode in ['original','composition']}
    rows.append(dict(n=n,runs=runs,median_seconds=median,ratio=median['composition']/median['original']))
report={'scope':'Local fresh-process first-call timing, geometric-series input with every coefficient independently certified. Does not cover original repeated-call defect, random workload or OJ timing.','compiler':subprocess.check_output([CXX,'--version'],text=True).splitlines()[0],'rows':rows}
paths=['tests/fps_inverse_sqrt_benchmark.cpp','tests/fps_inverse_sqrt_benchmark.py','tests/fixtures/wida_montgomery_poly/12C.cpp','src/compact/fps_sqrt.hpp','src/compact/fps_inverse.hpp','src/compact/ntt_convolution.hpp']
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
(root/'verification/fps-inverse-sqrt-performance.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(rows,indent=2),flush=True)
