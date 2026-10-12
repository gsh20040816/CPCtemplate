from pathlib import Path
import hashlib,json,statistics,subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
exe=root/'build/montgomery/benchmark'
subprocess.run([CXX,'-std=c++20','-O2',str(root/'tests/montgomery_benchmark.cpp'),'-o',str(exe)],check=True)
runs=[]
for repeat in range(3):
    for mode in (['ordinary','montgomery'] if repeat%2==0 else ['montgomery','ordinary']):
        result=subprocess.check_output([str(exe),'10000000',mode],text=True).split()
        runs.append(dict(repeat=repeat,mode=mode,checksum=int(result[0]),seconds=float(result[1])))
assert len({r['checksum'] for r in runs})==1
med={mode:statistics.median(r['seconds'] for r in runs if r['mode']==mode) for mode in ['ordinary','montgomery']}
report=dict(scope='Local dependent multiply-add chain, constant modulus 998244353, C++20 O2; no OJ or universal performance claim',iterations=10000000,runs=runs,median_seconds=med,ratio=med['montgomery']/med['ordinary'],compiler=subprocess.check_output([CXX,'--version'],text=True).splitlines()[0])
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in ['src/compact/montgomery_modint.hpp','tests/montgomery_benchmark.cpp','tests/montgomery_benchmark.py']}
(root/'verification/montgomery-performance.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
