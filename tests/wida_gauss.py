from pathlib import Path
import hashlib,json,os,subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
out=root/'build/wida-gauss'
out.mkdir(parents=True,exist_ok=True)
report=dict(scope='Exact WIDA old gauss: exhaustive small-field entire solution sets, safe invertible source systems, diagonally dominant floating systems, zero-pivot and singular-source counterexamples, constructed polynomial division. No source application or online AC.',runs=[])
b=(root/'tests/fixtures/wida_gauss/gauss.cpp').read_bytes()
assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()=='f45eaa851860a615f3ad9801df134bea93ec898a'
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
    exe=out/mode
    subprocess.run([CXX,'-std=c++20',*flags,str(root/'tests/wida_gauss.cpp'),'-o',str(exe)],check=True)
    for task in (['normal'] if mode=='normal' else ['normal','singular']):
        r=subprocess.run([str(exe),task],capture_output=True,text=True,env=env,timeout=300)
        if task=='singular':assert r.returncode!=0 and 'heap-buffer-overflow' in r.stderr,(r.returncode,r.stderr)
        else:assert r.returncode==0 and not r.stderr and 'PASS' in r.stdout,(mode,r.returncode,r.stdout,r.stderr)
        report['runs'].append(dict(mode=mode,task=task,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        print(mode,task,r.stdout.strip() or 'expected source out-of-bounds',flush=True)
paths=['tests/wida_gauss.cpp','tests/wida_gauss.py','tests/fixtures/wida_gauss/gauss.cpp','src/compact/gauss_mod.hpp','src/compact/gauss_real.hpp','src/compact/polynomial_division.hpp','src/compact/fps_inverse.hpp','src/compact/ntt_convolution.hpp','src/compact/number_theory.hpp']
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
(root/'verification/wida-gauss.json').write_text(json.dumps(report,indent=2)+'\n')
