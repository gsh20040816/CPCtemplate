from pathlib import Path
import hashlib
import json
import statistics
import subprocess
import time
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
out = root/'build/bivariate/official'
initial = json.loads((root/'verification/bivariate-initial.json').read_text())
(out/'initial.cpp').write_text(initial['printed_program'])
subprocess.run([CXX,'-std=c++20','-O2','-DNDEBUG',str(out/'initial.cpp'),'-o',str(out/'initial')],check=True)
hashes = json.loads((out/'hash.json').read_text())
rows = []
for name in ['maxDegX','randomSquare','degX10','degY100','square']:
    label = name+'_00'
    data = subprocess.check_output([str(out/('gen-'+name)),'0'])
    assert hashlib.sha256(data).hexdigest() == hashes[label+'.in']
    runs = []
    for repeat in range(3):
        order = ['initial','normal','reference']
        if repeat%2:
            order.reverse()
        for mode in order:
            start = time.monotonic()
            result = subprocess.check_output([str(out/mode)],input=data,timeout=120)
            elapsed = time.monotonic()-start
            assert hashlib.sha256(result).hexdigest() == hashes[label+'.out'],(label,mode)
            runs.append(dict(mode=mode,repeat=repeat,seconds=elapsed))
    medians = {mode:statistics.median(r['seconds'] for r in runs if r['mode']==mode) for mode in order}
    rows.append(dict(label=label,dimensions=data.splitlines()[0].decode(),input_sha256=hashes[label+'.in'],runs=runs,medians=medians,after_over_before=medians['normal']/medians['initial'],after_over_reference=medians['normal']/medians['reference']))
    print(label,rows[-1],flush=True)
report = dict(scope='Local same-machine GCC16 O2 subprocess wall time including I/O, three alternating rounds. Official reference is an easy comparison, not fastest/SOTA or an online verdict. Run after correctness jobs finish.',compiler=subprocess.check_output([CXX,'--version'],text=True).splitlines()[0],rows=rows)
report['programs'] = {name:hashlib.sha256((out/path).read_bytes()).hexdigest() for name,path in [('initial','initial.cpp'),('normal','printed.cpp'),('reference','sol/correct.cpp')]}
report['script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(root/'verification/bivariate-performance.json').write_text(json.dumps(report,indent=2)+'\n')
