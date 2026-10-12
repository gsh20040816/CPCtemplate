from pathlib import Path
import hashlib,json,os,subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1];out=root/'build/wida-balanced';out.mkdir(exist_ok=True)
results={}
for mode in ['normal','sanitizer']:
 flags=['-std=c++20','-O2']
 if mode=='sanitizer':flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
 exe=out/('sequence-max-'+mode)
 subprocess.run([CXX,*flags,str(root/'tests/sequence_max_treap.cpp'),'-o',str(exe)],check=True)
 p=subprocess.run([str(exe)],text=True,capture_output=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'),timeout=180)
 assert p.returncode==0 and not p.stderr,p.stderr
 results[mode]=p.stdout.strip();print(mode,p.stdout.strip(),flush=True)
files=['src/compact/sequence_max_treap.hpp','tests/sequence_max_treap.cpp','tests/sequence_max_treap.py']
(root/'verification/sequence-max-treap.json').write_text(json.dumps(dict(runs=results,files={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files}),indent=2)+'\n')
