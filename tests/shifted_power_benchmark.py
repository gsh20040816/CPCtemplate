from pathlib import Path
import hashlib
import json
import statistics
import subprocess
import sys
import time
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from usage_examples import records
out=root/'build/wida-mul-audit'
row=next(r for r in records() if r['id']=='example-454')
programs={'current':row['program'],'original':'''#include <bits/stdc++.h>
#include <cassert>
using i64 = long long;
#include "'''+str(root/'tests/fixtures/wida_poly_variants/12D-mint.cpp')+'''"
int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    auto f = get(n, m);
    for (int i = 0; i <= n; i++)
        std::cout << f[i] << "\\n "[i != n];
}
'''}
for name,code in programs.items():
    p=out/f'benchmark-{name}.cpp'
    p.write_text(code)
    subprocess.run([CXX,'-std=c++20','-O2','-DNDEBUG',str(p),'-o',str(out/f'benchmark-{name}')],check=True)
report=dict(scope='Three alternating process wall-time rounds including IO. Exact WIDA get and current printed program. Outputs compared between implementations; independent correctness is in separate receipts. Not SOTA or online ranking.',cases=[])
for n,m in [(32768,1),(32768,1000000000),(131072,1000000000)]:
    runs=[]
    answer=None
    for turn in range(3):
        for name in (['original','current'] if turn%2==0 else ['current','original']):
            start=time.monotonic()
            r=subprocess.run([str(out/f'benchmark-{name}')],input=f'{n} {m}\n',text=True,capture_output=True,check=True,timeout=120)
            elapsed=time.monotonic()-start
            assert not r.stderr
            digest=hashlib.sha256(r.stdout.encode()).hexdigest()
            if answer is None:answer=digest
            assert digest==answer,(n,m,name)
            runs.append(dict(round=turn,implementation=name,seconds=elapsed,output_sha256=digest))
    medians={name:statistics.median(r['seconds'] for r in runs if r['implementation']==name) for name in programs}
    report['cases'].append(dict(n=n,m=m,runs=runs,medians=medians,current_over_original=medians['current']/medians['original']))
    print(n,m,medians,flush=True)
report['programs_sha256']={name:hashlib.sha256(code.encode()).hexdigest() for name,code in programs.items()}
(root/'verification/shifted-power-performance.json').write_text(json.dumps(report,indent=2)+'\n')
