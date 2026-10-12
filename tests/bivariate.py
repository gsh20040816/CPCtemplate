from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
rows = []
for mode, flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
    exe = root/'build/bivariate'/mode
    subprocess.run([CXX,'-std=c++20',*flags,str(root/'tests/bivariate.cpp'),'-o',str(exe)],check=True)
    r = subprocess.run([str(exe)],text=True,capture_output=True,timeout=300,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
    assert r.returncode == 0 and not r.stderr,(r.returncode,r.stdout,r.stderr)
    print(mode,r.stdout,flush=True)
    rows.append(dict(mode=mode,flags=flags,output=r.stdout))
paths = ['src/compact/ntt_2d.hpp','src/compact/bivariate_inverse.hpp','src/compact/ntt_convolution.hpp','src/compact/fps_inverse.hpp','src/compact/number_theory.hpp','tests/bivariate.cpp','tests/bivariate.py']
(root/'verification/bivariate-core.json').write_text(json.dumps(dict(scope='Independent local 2D DFT, four-loop convolution and triangular coefficient inverse; no online AC',runs=rows,files={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}),indent=2)+'\n')
