from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
out=root/'build/wida-mint-poly'
out.mkdir(parents=True,exist_ok=True)
p=root/'tests/fixtures/wida_poly_variants/12D-mint.cpp'
b=p.read_bytes()
assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()=='f2063c0206f44f664a04090a48f9dea4c3054879'
report=dict(scope='Exact WIDA12D MInt source Poly interfaces against independent coefficient recurrences/Horner and current components. Scoped local checks, no original application or online AC.',runs=[])
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
    exe=out/mode
    subprocess.run([CXX,'-std=c++20',*flags,str(root/'tests/wida_mint_poly.cpp'),'-o',str(exe)],check=True)
    for task in (['small','large','parameters','modular','counterexamples','singleton','shift-min','large-mod-add'] if mode=='sanitizer' else ['small','large','parameters','modular','counterexamples','singleton']):
        r=subprocess.run([str(exe),task],capture_output=True,text=True,env=env,timeout=600)
        if task=='large-mod-add':
            assert r.returncode!=0 and 'signed integer overflow' in r.stderr,(task,r)
        elif task=='shift-min':
            assert r.returncode!=0 and 'cannot be represented in type' in r.stderr,(task,r)
        elif task=='singleton' and mode=='sanitizer':
            assert r.returncode!=0 and 'shift exponent -1 is negative' in r.stderr,(task,r)
        else:
            assert r.returncode==0 and not r.stderr,(mode,task,r.returncode,r.stdout,r.stderr)
        report['runs'].append(dict(mode=mode,task=task,stdout=r.stdout,stderr=r.stderr,returncode=r.returncode))
        print(mode,task,r.stdout.strip() or ('expected UB' if r.returncode else 'PASS'),flush=True)
paths=['tests/wida_mint_poly.cpp','tests/wida_mint_poly.py','tests/fixtures/wida_poly_variants/12D-mint.cpp','src/compact/fps_functions.hpp','src/compact/fps_power.hpp','src/compact/fps_sqrt.hpp','src/compact/fps_inverse.hpp','src/compact/multipoint_evaluation.hpp','src/compact/polynomial_division.hpp','src/compact/ntt_convolution.hpp','src/compact/number_theory.hpp','src/compact/convolution_mod.hpp']
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
(root/'verification/wida-mint-poly.json').write_text(json.dumps(report,indent=2)+'\n')
