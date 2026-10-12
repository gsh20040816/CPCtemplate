from pathlib import Path
from fractions import Fraction
import hashlib
import json
import os
import random
import subprocess
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'build/fraction'
out.mkdir(parents=True, exist_ok=True)
rng = random.Random(1572)
lo, hi = -(1 << 63), (1 << 63) - 1
cases, expected = [], []
def fits(x):
    return lo <= x.numerator <= hi and x.denominator <= hi
def add(wide,n,d,op,m,e):
    a,b = Fraction(n,d), Fraction(m,e)
    if op == 'cmp':
        result=' '.join(str(int(x)) for x in [a<b,a>b,a==b,a<=b,a>=b,a!=b])
    else:
        if op.startswith('self'):
            b=a
            action=op[-1]
        else:
            action=op
        if action == '/' and not b:
            return
        c = {'+':lambda:a+b,'-':lambda:a-b,'*':lambda:a*b,'/':lambda:a/b,'neg':lambda:-a,'norm':lambda:a}[action]()
        if not wide and not fits(c):
            return
        result=f'{c.numerator} {c.denominator} {c}'
    if not wide and (not fits(a) or not fits(b)):
        return
    cases.append(f'{wide} {n} {d} {op} {m} {e}')
    expected.append(result)
ops=['+','-','*','/','self+','self-','self*','self/','neg','norm','cmp']
for i in range(5000):
    wide = i % 2
    size = 10**rng.randrange(1,200) if wide else hi
    n,m = (rng.randrange(-size,size+1) for _ in range(2))
    d,e = (rng.randrange(1,size+1)*rng.choice([-1,1]) for _ in range(2))
    for op in ops:
        add(wide,n,d,op,m,e)
for n in [lo,lo+1,-1,0,1,hi-1,hi]:
    for d in [lo,-hi,-2,-1,1,2,hi]:
        for m,e in [(lo,hi),(hi,hi-1),(n,d),(0,1),(1,2),(-1,2)]:
            for op in ops:
                add(0,n,d,op,m,e)
report={'scope':'Independent Python Fraction exact oracle, signed64 extremes, up to 199 decimal digits, all six comparisons and self operations. No online verdict.','cases_per_mode':len(cases),'runs':[]}
flags=['-std=c++20','-Wall','-Wextra']
if Path('/opt/homebrew/include/boost').exists():
    flags+=['-I/opt/homebrew/include']
data=str(len(cases))+'\n'+'\n'.join(cases)+'\n'
for mode, options in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
    env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    results={}
    for name in ['fraction','fraction_protocol']:
        exe=out/(name+'-'+mode)
        command=[CXX,*flags,*options,str(ROOT/'tests'/(name+'.cpp')),'-o',str(exe)]
        subprocess.run(command,check=True)
        run=subprocess.run([str(exe)],input=data if name.endswith('protocol') else '',capture_output=True,text=True,env=env,timeout=180)
        assert run.returncode==0 and not run.stderr,run.stderr
        if name.endswith('protocol'):
            assert run.stdout.splitlines()==expected,next(((a,b) for a,b in zip(run.stdout.splitlines(),expected) if a!=b), 'length mismatch')
            results[name]=f'{len(cases)} exact Python Fraction cases PASS'
        else:
            results[name]=run.stdout.strip()
        print(mode,name,results[name],flush=True)
    report['runs'].append({'mode':mode,'results':results})
report['files']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['src/compact/fraction.hpp','tests/fraction.cpp','tests/fraction_protocol.cpp','tests/fraction.py','tests/fixtures/wida_fraction/Frac.cpp']}
(ROOT/'verification/fraction.json').write_text(json.dumps(report,indent=2)+'\n')
