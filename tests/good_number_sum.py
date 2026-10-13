from pathlib import Path
import hashlib,json,os,subprocess,time
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
out=root/'build/good-number-sum'
out.mkdir(parents=True,exist_ok=True)
report=dict(scope='Independent exhaustive adjacent-substring sums and randomized literal integer oracle, moduli 1/7/2^61-1 force collisions. No online AC.',runs=[])
paths=['tests/good_number_sum.cpp','tests/good_number_sum.py','src/compact/good_number_sum.hpp','src/compact/exkmp.hpp','src/compact/string.hpp']
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
 exe=out/mode
 subprocess.run([CXX,'-std=c++20',*flags,str(root/'tests/good_number_sum.cpp'),'-o',str(exe)],check=True)
 start=time.monotonic()
 p=subprocess.run([str(exe)],text=True,capture_output=True,env=env,timeout=300)
 assert p.returncode==0 and not p.stderr and 'PASS' in p.stdout,(mode,p.returncode,p.stdout,p.stderr)
 report['runs'].append(dict(mode=mode,stdout=p.stdout,elapsed_seconds=time.monotonic()-start))
 print(mode,p.stdout.strip(),flush=True)
(root/'verification/good-number-sum.json').write_text(json.dumps(report,indent=2)+'\n')
