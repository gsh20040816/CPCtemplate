"""After official generate.py and tests/rectangle_sum.py, check pinned official cases locally."""
from pathlib import Path
import hashlib,json,subprocess,time
root=Path(__file__).resolve().parents[1]; ref=root/'build/library-checker-reference'; p=ref/'data_structure/rectangle_sum'; out=root/'build/offline-rectangle'
assert subprocess.check_output(['git','-C',str(ref),'rev-parse','HEAD'],text=True).strip() == 'e64660561a995c357cdc61ddee1bde68b80528db'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
rows=[]
for inp in sorted((p/'in').glob('*.in')):
    dst=out/(inp.stem+'.out'); ans=p/'out'/(inp.stem+'.out')
    with inp.open('rb') as i,dst.open('wb') as o:
        start=time.perf_counter(); subprocess.run([str(out/'normal')],stdin=i,stdout=o,check=True,timeout=10); elapsed=time.perf_counter()-start
    run=subprocess.run([str(p/'checker'),str(inp),str(dst),str(ans)],capture_output=True,text=True)
    assert run.returncode==0,run.stderr
    rows.append(dict(case=inp.stem,input_sha256=sha(inp),answer_sha256=sha(ans),output_sha256=sha(dst),elapsed_seconds=round(elapsed,4),verdict='local_checker_accepted',checker_message=run.stderr.strip()))
wrong=out/'wrong.out'; wrong.write_text('-1\n')
run=subprocess.run([str(p/'checker'),str(inp),str(wrong),str(ans)],capture_output=True,text=True)
assert run.returncode!=0
report=dict(problem='rectangle_sum',scope='Local official generated tests; no online verdict or controlled speed ranking',reference_commit=subprocess.check_output(['git','-C',str(ref),'rev-parse','HEAD'],text=True).strip(),metadata_sha256=sha(p/'info.toml'),checker_source_sha256=sha(p/'checker.cpp'),bundle_sha256=sha(out/'submission.cpp'),cases=rows,negative_control=dict(exit_code=run.returncode,message=run.stderr.strip()))
(root/'verification/offline-rectangle-official.json').write_text(json.dumps(report,indent=2)+'\n')
print(len(rows),'official cases PASS; max seconds',max(r['elapsed_seconds'] for r in rows))
