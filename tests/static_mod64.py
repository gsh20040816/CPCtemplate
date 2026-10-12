from pathlib import Path
import hashlib,json,os,subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
out=root/'build/static-mod64'
out.mkdir(exist_ok=True)
report={'scope':'Full uint64 fixed modulus, signed/unsigned construction, arithmetic, exact exponent and unit inverse; Boost cpp_int oracle; no online AC','runs':[]}
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
    exe=out/mode
    subprocess.run([CXX,'-std=c++20',*flags,'-I/opt/homebrew/include',str(root/'tests/static_mod64.cpp'),'-o',str(exe)],check=True)
    r=subprocess.run([str(exe)],text=True,capture_output=True,env=env,timeout=180)
    assert r.returncode==0 and not r.stderr,r.stderr
    report['runs'].append(dict(mode=mode,output=r.stdout.strip()))
    print(mode,r.stdout.strip(),flush=True)
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in ['src/compact/static_mod64.hpp','src/compact/mod64.hpp','tests/static_mod64.cpp','tests/static_mod64.py']}
(root/'verification/static-mod64.json').write_text(json.dumps(report,indent=2)+'\n')
