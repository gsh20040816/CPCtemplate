from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
out=root/'build/wida-matrix'
report=dict(scope='Independent bit-matrix application, composition/repeated application and analytic uint64 powers; exact source operator and rotation/AND/OR reader comparisons. No original problem protocol or online AC.',runs=[])
b=(root/'tests/fixtures/wida_matrix/matrix.cpp').read_bytes()
assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()=='5f16c4a7f59a95446ac34c183fcb6c75b21cfcec'
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
    exe=out/mode
    subprocess.run([CXX,'-std=c++20',*flags,str(root/'tests/xor_affine64.cpp'),'-o',str(exe)],check=True)
    r=subprocess.run([str(exe)],capture_output=True,text=True,env=env,timeout=300)
    assert r.returncode==0 and not r.stderr and 'PASS' in r.stdout,(mode,r.returncode,r.stdout,r.stderr)
    report['runs'].append(dict(mode=mode,stdout=r.stdout))
    print(mode,r.stdout.strip(),flush=True)
paths=['tests/xor_affine64.cpp','tests/xor_affine64.py','tests/fixtures/wida_matrix/matrix.cpp','src/compact/xor_affine64.hpp']
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
(root/'verification/xor-affine64.json').write_text(json.dumps(report,indent=2)+'\n')
