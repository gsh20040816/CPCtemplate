#!/usr/bin/env python3
"""Local dense-tie stress: forces visits through already matched zero-slack columns."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'build/assignment-spectrum/stress'
out.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
paths=['src/compact/assignment_spectrum.hpp','verify/luogu/P6577.spectrum.compact.cpp','tests/assignment_spectrum_stress.py']
snapshot={p:sha((ROOT/p).read_bytes()) for p in paths}
report=[]
for mode in ('normal','sanitizer'):
    exe=out/mode
    flags=['-std=c++20','-O2'] if mode=='normal' else ['-std=c++20','-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer']
    command=[CXX,*flags,str(ROOT/paths[1]),'-o',str(exe)]
    subprocess.run(command,check=True,capture_output=True)
    for kind in ('equal','separable'):
        n=500
        value=lambda x,y: -19980731 if kind=='equal' else x+y-500
        data=f'{n} {n*n}\n'+''.join(f'{x+1} {y+1} {value(x,y)}\n' for x in range(n) for y in range(n))
        start=time.monotonic()
        proc=subprocess.run([str(exe)],input=data,text=True,capture_output=True,timeout=90,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})
        elapsed=time.monotonic()-start
        assert proc.returncode==0,proc.stderr
        result=list(map(int,proc.stdout.split()))
        expected=-19980731*n if kind=='equal' else -n
        assert len(result)==n+1 and result[0]==expected
        assert sorted(result[1:])==list(range(1,n+1))
        assert sum(value(x-1,y) for y,x in enumerate(result[1:]))==expected
        report.append(dict(mode=mode,kind=kind,n=n,edges=n*n,seconds=round(elapsed,3),input_sha256=sha(data.encode()),output_sha256=sha(proc.stdout.encode()),binary_sha256=sha(exe.read_bytes()),command=command))
        print(mode,kind,round(elapsed,3),'seconds PASS',flush=True)
assert snapshot=={p:sha((ROOT/p).read_bytes()) for p in paths}
(ROOT/'verification/assignment-spectrum-stress.json').write_text(json.dumps(dict(snapshot=snapshot,results=report,scope='Local dense tied weights only; wall time includes process/input/output, not OJ performance or ranking.'),indent=2)+'\n')
