from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
out=root/'build/wida-raw-poly'
out.mkdir(parents=True,exist_ok=True)
report=dict(scope='Exact 12A raw-int polynomial: ordinary source numerical observations are not defined-behavior proof because sanitizer reproduces UB in constant/log/exp. Current replacement is checked independently in both modes.',runs=[])
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
    exe=out/mode
    subprocess.run([CXX,'-std=c++20',*flags,str(root/'tests/wida_raw_poly.cpp'),'-o',str(exe)],check=True)
    tasks=['current','source'] if mode=='normal' else ['current','source-safe','source-constant','source-log','source-exp']
    for task in tasks:
        r=subprocess.run([str(exe),task],capture_output=True,text=True,env=env,timeout=300)
        if task in ['source-constant','source-log','source-exp']:
            assert r.returncode!=0 and 'shift exponent -1 is negative' in r.stderr,(task,r.returncode,r.stdout,r.stderr)
        else:
            assert r.returncode==0 and not r.stderr and 'PASS' in r.stdout,(task,r.returncode,r.stdout,r.stderr)
        report['runs'].append(dict(mode=mode,task=task,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        print(mode,task,r.stdout.strip() or 'expected source UB',flush=True)
paths=['tests/wida_raw_poly.cpp','tests/wida_raw_poly.py','tests/fixtures/wida_poly_variants/12A.cpp','src/compact/fps_functions.hpp','src/compact/fps_sqrt.hpp','src/compact/fps_inverse.hpp','src/compact/multipoint_evaluation.hpp','src/compact/polynomial_division.hpp','src/compact/ntt_convolution.hpp','src/compact/number_theory.hpp']
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
(root/'verification/wida-raw-poly.json').write_text(json.dumps(report,indent=2)+'\n')
