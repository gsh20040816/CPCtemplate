from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
out=root/'build/wida-z-audit'
report=dict(scope='Exact 12D MInt BM and rational coefficient source; exhaustive short prime-field sequences checked by independent Gaussian consistency/minimal order; direct coefficient recurrence; uint64 Fibonacci fast doubling. No online AC.',runs=[])
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
    exe=out/('recurrence-'+mode)
    subprocess.run([CXX,'-std=c++20',*flags,str(root/'tests/wida_mint_recurrence.cpp'),'-o',str(exe)],check=True)
    tasks=['normal','constant-denominator']
    if mode=='sanitizer':tasks.append('short-numerator')
    for task in tasks:
        r=subprocess.run([str(exe),task],capture_output=True,text=True,env=env,timeout=600)
        if task=='short-numerator':
            assert r.returncode!=0 and 'heap-buffer-overflow' in r.stderr,(r.returncode,r.stderr)
        else:
            assert r.returncode==0 and not r.stderr and 'PASS' in r.stdout,(mode,task,r.returncode,r.stdout,r.stderr)
        report['runs'].append(dict(mode=mode,task=task,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        print(mode,task,r.stdout.strip() or 'expected source buffer-overflow',flush=True)
paths=['tests/wida_mint_recurrence.cpp','tests/wida_mint_recurrence.py','tests/fixtures/wida_poly_variants/12D-mint.cpp','src/compact/recurrence.hpp','src/compact/bostan_mori.hpp','src/compact/ntt_convolution.hpp','src/compact/number_theory.hpp']
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
(root/'verification/wida-mint-recurrence.json').write_text(json.dumps(report,indent=2)+'\n')
