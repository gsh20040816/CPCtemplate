from pathlib import Path
import hashlib
import json
import os
import statistics
import subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
out=root/'build/wida-z-audit'
report=dict(scope='Every coefficient independently checked against analytic series or modular-power evaluations. Internal timings include result conversion and evaluation construction, exclude input/oracle generation. No online AC or SOTA claim.',runs=[],benchmarks=[])
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
def run(exe,mode,op,impl,n):
    r=subprocess.run([str(exe),op,impl,str(n)],capture_output=True,text=True,env=env,timeout=1200)
    assert r.returncode==0 and not r.stderr,(mode,op,impl,n,r.returncode,r.stdout,r.stderr)
    count,digest,seconds,status=r.stdout.split()
    assert int(count)==n and status=='PASS'
    return dict(mode=mode,operation=op,implementation=impl,n=n,coefficient_digest=digest,seconds=float(seconds))
for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
    exe=out/('scale-'+mode)
    subprocess.run([CXX,'-std=c++20',*flags,str(root/'tests/wida_z_scale.cpp'),'-o',str(exe)],check=True)
    for op,n in [('inverse',1<<22),('log',1<<18),('exp',1<<18),('sqrt',1<<18),('eval',1<<14)]:
        for impl in ['original','current']:
            row=run(exe,mode,op,impl,n)
            report['runs'].append(row)
            print(mode,op,impl,n,'PASS',flush=True)
    if mode=='normal':
        for op,n in [('inverse',1<<17),('log',1<<17),('exp',1<<17),('sqrt',1<<17),('eval',1<<14)]:
            runs=[]
            for repeat in range(3):
                for impl in (['original','current'] if repeat%2==0 else ['current','original']):
                    runs.append(run(exe,mode,op,impl,n))
            medians={impl:statistics.median(r['seconds'] for r in runs if r['implementation']==impl) for impl in ['original','current']}
            report['benchmarks'].append(dict(operation=op,n=n,runs=runs,medians=medians,current_over_original=medians['current']/medians['original']))
            print('benchmark',op,medians,flush=True)
    (root/'verification/wida-z-scale-progress.json').write_text(json.dumps(report,indent=2)+'\n')
paths=['tests/wida_z_scale.cpp','tests/wida_z_scale.py','tests/fixtures/wida_poly_variants/12B.cpp','src/compact/fps_functions.hpp','src/compact/fps_power.hpp','src/compact/fps_sqrt.hpp','src/compact/fps_inverse.hpp','src/compact/multipoint_evaluation.hpp','src/compact/polynomial_division.hpp','src/compact/ntt_convolution.hpp','src/compact/number_theory.hpp']
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
(root/'verification/wida-z-scale.json').write_text(json.dumps(report,indent=2)+'\n')
(root/'verification/wida-z-scale-progress.json').unlink()
