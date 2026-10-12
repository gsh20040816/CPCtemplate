from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
out = root/'build/wida-mul-audit'
out.mkdir(parents=True, exist_ok=True)
p = root/'tests/fixtures/wida_poly_variants/12D-mint.cpp'
b = p.read_bytes()
assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest() == 'f2063c0206f44f664a04090a48f9dea4c3054879'
report = dict(scope='Independent binomial expansion; exact original get(n,m); full uint64 boundaries and periodicity; maximum supported degree analytic binomial coefficients. Local only.', runs=[])
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
for mode, flags in [('normal',['-O2','-DNDEBUG']), ('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
    exe = out/('shifted-'+mode)
    subprocess.run([CXX,'-std=c++20',*flags,str(root/'tests/shifted_power_sum.cpp'),'-o',str(exe)],check=True)
    for args in [[],['capacity']]:
        r = subprocess.run([str(exe),*args],capture_output=True,text=True,env=env,timeout=600)
        assert r.returncode == 0 and not r.stderr and 'PASS' in r.stdout,(mode,args,r.returncode,r.stdout,r.stderr)
        report['runs'].append(dict(mode=mode,args=args,stdout=r.stdout))
        print(mode,args,r.stdout.strip(),flush=True)
paths = ['tests/shifted_power_sum.cpp','tests/shifted_power_sum.py','tests/fixtures/wida_poly_variants/12D-mint.cpp','src/compact/shifted_power_sum.hpp','src/compact/fps_inverse.hpp','src/compact/ntt_convolution.hpp','src/compact/number_theory.hpp']
report['files'] = {p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
(root/'verification/shifted-power-sum.json').write_text(json.dumps(report,indent=2)+'\n')
