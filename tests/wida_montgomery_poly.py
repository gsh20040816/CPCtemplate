from pathlib import Path
import hashlib,json,os,subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
out=root/'build/wida-montgomery-poly'
raw=(root/'tests/fixtures/wida_montgomery_poly/12C.cpp').read_bytes()
blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
assert blob=='2fc05cbaebfde127ea5437a97ff27b4f7c6033fd'
report={'scope':'Exact12C at modulus998244353 and nonempty polynomials with up to255 coefficients; independent naive recurrences and existing replacement composition. Not full-scale/other moduli/source application coverage.','source_blob':blob,'runs':[]}
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
    exe=out/mode
    subprocess.run([CXX,'-std=c++20',*flags,str(root/'tests/wida_montgomery_poly.cpp'),'-o',str(exe)],check=True)
    r=subprocess.run([str(exe)],text=True,capture_output=True,env=env,timeout=180)
    assert r.returncode==0 and not r.stderr,r.stderr or r.stdout
    report['runs'].append(dict(mode=mode,output=r.stdout.strip()))
    print(mode,r.stdout.strip(),flush=True)
    r=subprocess.run([str(exe),'minimal'],text=True,capture_output=True,env=env,timeout=180)
    assert r.returncode==0 and not r.stderr,r.stderr or r.stdout
    report['runs'].append(dict(mode=mode,test='repeated-square-root-minimal',output=r.stdout.strip()))
    print(mode,'minimal',r.stdout.strip(),flush=True)
paths=['tests/wida_montgomery_poly.cpp','tests/wida_montgomery_poly.py','tests/fixtures/wida_montgomery_poly/12C.cpp','src/compact/fps_functions.hpp','src/compact/fps_inverse.hpp','src/compact/fps_power.hpp','src/compact/fps_sqrt.hpp','src/compact/polynomial_division.hpp','src/compact/ntt_convolution.hpp','src/compact/number_theory.hpp','src/compact/modular_sqrt.hpp']
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
(root/'verification/wida-montgomery-poly.json').write_text(json.dumps(report,indent=2)+'\n')
