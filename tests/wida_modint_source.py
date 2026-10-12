from pathlib import Path
import hashlib,json,os,subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
out=root/'build/wida-modint'
out.mkdir(exist_ok=True)
raw=(root/'tests/fixtures/wida_mod_reduction/07E.cpp').read_bytes()
blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
assert blob=='c5af9ebd28047a3c6bd7023cbe26150761c8e86b'
report={'scope':'07E fixed32 safe-domain arithmetic, invGcd, floating64 portability and full-uint64 addition counterexample. Original applications not read; no online AC.','blob':blob,'runs':[]}
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined,float-cast-overflow'])]:
    exe=out/mode
    subprocess.run([CXX,'-std=c++20',*flags,str(root/'tests/wida_modint_source.cpp'),'-o',str(exe)],check=True)
    r=subprocess.run([str(exe)],text=True,capture_output=True,env=env,timeout=180)
    assert r.returncode==0 and not r.stderr,r.stderr
    report['runs'].append(dict(mode=mode,output=r.stdout.strip()))
    print(mode,r.stdout,flush=True)
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in ['src/compact/mod64.hpp','tests/wida_modint_source.cpp','tests/wida_modint_source.py','tests/fixtures/wida_mod_reduction/07E.cpp']}
(root/'verification/wida-modint-source.json').write_text(json.dumps(report,indent=2)+'\n')
