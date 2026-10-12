from pathlib import Path
import hashlib,json,os,subprocess,time
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
out=root/'build/divide-segment-tree'
out.mkdir(parents=True,exist_ok=True)
paths=['src/compact/divide_segment_tree.hpp','tests/divide_segment_tree.cpp','tests/divide_segment_tree.py','tests/fixtures/wida_lazy/04.cpp']
report=dict(scope='Independent literal array, small exhaustive divisions, exact WIDA half with supplied all-active nonnegative Info/Tag, 500000 elements and 100000 uniform operation cycles. No online verdict; timings are local only.',runs=[])
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
 exe=out/mode
 subprocess.run([CXX,'-std=c++20',*flags,str(root/'tests/divide_segment_tree.cpp'),'-o',str(exe)],check=True)
 start=time.monotonic()
 r=subprocess.run([str(exe)],capture_output=True,text=True,env=env,timeout=300)
 elapsed=time.monotonic()-start
 assert r.returncode==0 and not r.stderr and 'PASS' in r.stdout,(mode,r.returncode,r.stdout,r.stderr)
 report['runs'].append(dict(mode=mode,stdout=r.stdout,elapsed_seconds=elapsed))
 print(mode,r.stdout.strip(),elapsed,flush=True)
assert report['files']=={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
(root/'verification/divide-segment-tree.json').write_text(json.dumps(report,indent=2)+'\n')
