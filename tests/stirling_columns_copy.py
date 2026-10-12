from pathlib import Path
import hashlib,json,os,subprocess,sys
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from audit_copy_context import extract_components,PRELUDE
entries={r['symbol']:r for r in extract_components(json.loads((root/'docs/catalog.json').read_text()))}
names=['ModInt','NttConvolution','FpsInverse','FpsFunctions','FpsPower','stirling_first_row','stirling_second_row','stirling_first_column','stirling_second_column']
test=(root/'tests/stirling_columns.cpp').read_text().splitlines()[2:]
src=root/'build/stirling-columns/copy.cpp'
src.write_text(PRELUDE+'\n'.join(entries[s]['code'] for s in names)+'\n'+'\n'.join(test))
results={}
for mode in ['normal','sanitizer']:
 flags=['-std=c++20','-O2']
 if mode=='sanitizer':flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
 exe=src.with_suffix('.'+mode)
 subprocess.run([CXX,*flags,str(src),'-o',str(exe)],check=True)
 p=subprocess.run([str(exe)],text=True,capture_output=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'),timeout=180)
 assert p.returncode==0 and not p.stderr,p.stderr
 results[mode]=p.stdout.strip();print(mode,p.stdout.strip(),flush=True)
(root/'verification/stirling-columns-copy.json').write_text(json.dumps(dict(components={s:entries[s]['code_sha256'] for s in names},runs=results),indent=2)+'\n')
