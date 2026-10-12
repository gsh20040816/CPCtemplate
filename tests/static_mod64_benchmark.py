from pathlib import Path
import hashlib,json,statistics,subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
exe=root/'build/static-mod64/benchmark'
subprocess.run([CXX,'-std=c++20','-O2',str(root/'tests/static_mod64_benchmark.cpp'),'-o',str(exe)],check=True)
runs=[]
for repeat in range(3):
    for mode in (['ordinary','wrapped'] if repeat%2==0 else ['wrapped','ordinary']):
        result=subprocess.check_output([str(exe),'3000000',mode],text=True).split()
        runs.append(dict(repeat=repeat,mode=mode,checksum=int(result[0]),seconds=float(result[1])))
assert len({r['checksum'] for r in runs})==1
med={mode:statistics.median(r['seconds'] for r in runs if r['mode']==mode) for mode in ['ordinary','wrapped']}
report=dict(scope='Local dependent multiply-add chain, constant modulus 18446744073709551557, C++20 O2; no OJ or universal performance claim',iterations=3000000,runs=runs,median_seconds=med,ratio=med['wrapped']/med['ordinary'],compiler=subprocess.check_output([CXX,'--version'],text=True).splitlines()[0])
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in ['src/compact/static_mod64.hpp','src/compact/mod64.hpp','tests/static_mod64_benchmark.cpp','tests/static_mod64_benchmark.py']}
(root/'verification/static-mod64-performance.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
