#!/usr/bin/env python3
"""Local ablation on fixed P4980-domain cases; never an OJ SOTA claim."""
from pathlib import Path
import hashlib,json,platform,random,statistics,subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
exe=root/'build/runtime-audit/polya-runtime'
subprocess.run([CXX,'-std=c++20','-O2',str(root/'tests/polya_runtime.cpp'),'-o',str(exe)],check=True)
rng=random.Random(4980)
sets={'prime_repeat':[999999937]*1000,'mixed':[rng.randrange(1,10**9+1) for _ in range(1000)],'many_divisors':[735134400,698377680,963460800,831600000]*250}
small=list(range(1,81))
want=[sum(n**__import__('math').gcd(n,k) for k in range(n))//n%1000000007 for n in small]
for mode in range(4):
 r=subprocess.run([str(exe),str(mode)],input='\n'.join(map(str,small)),text=True,capture_output=True,check=True)
 assert list(map(int,r.stdout.split()))==want
results={}
for name,ns in sets.items():
 data='\n'.join(map(str,ns))+'\n'
 samples={m:[] for m in range(4)};outputs={}
 for trial in range(5):
  order=list(range(4));rng.shuffle(order)
  for mode in order:
   r=subprocess.run([str(exe),str(mode)],input=data,text=True,capture_output=True,check=True)
   samples[mode].append(float(r.stderr));outputs[mode]=r.stdout
 assert len(set(outputs.values()))==1
 results[name]=dict(input_sha256=hashlib.sha256(data.encode()).hexdigest(),count=len(ns),milliseconds=samples,median_ms={m:statistics.median(v) for m,v in samples.items()},output_sha256=hashlib.sha256(outputs[0].encode()).hexdigest())
report=dict(scope='Local chrono wall-time incl sieve+factor+count; excludes input/output. Four variants, five shuffled runs. Same outputs on test sets; exact rotation formula for n<=80. Compiler/platform differ from OJ; no speed rank or performance guarantee.',modes=['existing general implementation','prime sieve factorization, still scans divisors','prime sieve plus recursive divisor/phi enumeration, same general modular division','same enumeration, fixed prime inverse and 64-bit products; narrower P4980 domain'],platform=platform.platform(),compiler=subprocess.check_output([CXX,'--version'],text=True).splitlines()[0],flags=['-std=c++20','-O2'],source_sha256={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in ['tests/polya_runtime.cpp','tests/polya_runtime.py','src/compact/polya.hpp']},results=results)
(root/'verification/polya-runtime-local.json').write_text(json.dumps(report,indent=2)+'\n')
for name,r in results.items():print(name,r['median_ms'])
