"""Pinned Library Checker fixed-k cases; must generate official data first."""
from pathlib import Path
import hashlib,json,os,subprocess,time
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
ref=root/'build/library-checker-reference'
out=root/'build/stirling-columns'
assert subprocess.check_output(['git','-C',str(ref),'rev-parse','HEAD'],text=True).strip()=='e64660561a995c357cdc61ddee1bde68b80528db'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reports=[]
for kind in ['first','second']:
 problem=f'stirling_number_of_the_{kind}_kind_fixed_k'
 p=ref/'enumerative_combinatorics'/problem
 driver=f'verify/library_checker/{problem}.compact.cpp'
 source=out/(kind+'.cpp')
 subprocess.run(['python3','tools/bundle.py',driver,str(source)],cwd=root,check=True)
 for mode in ['normal','sanitizer']:
  flags=['-std=c++20','-O2']
  if mode=='sanitizer':flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
  exe=out/(kind+'-'+mode)
  subprocess.run([CXX,*flags,str(source),'-o',str(exe)],check=True)
  cases=[]
  for inp in sorted((p/'in').glob('*.in')):
   dst=out/(kind+'-'+mode+'-'+inp.stem+'.out');ans=p/'out'/(inp.stem+'.out')
   with inp.open('rb') as i,dst.open('wb') as o:
    start=time.perf_counter()
    run=subprocess.run([str(exe)],stdin=i,stdout=o,stderr=subprocess.PIPE,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'),timeout=180)
    elapsed=time.perf_counter()-start
   assert run.returncode==0 and not run.stderr,run.stderr
   check=subprocess.run([str(p/'checker'),str(inp),str(dst),str(ans)],capture_output=True,text=True)
   assert check.returncode==0,check.stderr
   cases.append(dict(case=inp.stem,input_sha256=sha(inp),answer_sha256=sha(ans),output_sha256=sha(dst),elapsed_seconds=round(elapsed,4),verdict='local_checker_accepted'))
  assert len(cases)==14,len(cases)
  wrong=out/'wrong.out';wrong.write_text('-1\n')
  check=subprocess.run([str(p/'checker'),str(inp),str(wrong),str(ans)],capture_output=True,text=True)
  assert check.returncode!=0
  reports.append(dict(problem=problem,mode=mode,driver=driver,bundle_sha256=sha(source),reference_commit='e64660561a995c357cdc61ddee1bde68b80528db',metadata_sha256=sha(p/'info.toml'),checker_sha256=sha(p/'checker.cpp'),flags=flags,cases=cases,negative_control=check.stderr.strip()))
  print(kind,mode,len(cases),'official cases PASS; maximum seconds',max(r['elapsed_seconds'] for r in cases),flush=True)
(root/'verification/stirling-columns-official.json').write_text(json.dumps(dict(scope='Official generated tests locally accepted, not online AC; sanitizer time is diagnostic only',reports=reports),indent=2)+'\n')
