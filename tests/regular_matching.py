"""Verify every returned matching independently; randomization affects time only."""
from pathlib import Path
import json, random, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
SAN='--sanitize' in sys.argv
MODE='sanitizer' if SAN else 'normal'
B=ROOT/'build/regular-matching'/MODE
B.mkdir(parents=True,exist_ok=True)
flags=['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if SAN else ['-O2']
header=(ROOT/'src/compact/regular_matching.hpp').read_text().replace('#pragma once\n','')
def compile(src,exe,extra=[]):
 subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,*extra,str(src),'-o',str(exe)],check=True)
cores={}
for kind in ['header','ndebug','copied']:
 src=ROOT/'tests/regular_matching.cpp'
 if kind=='copied':
  text=src.read_text().replace('#include "../src/compact/regular_matching.hpp"',header)
  src=B/'core-copy.cpp';src.write_text(text)
 exe=B/('core-'+kind);compile(src,exe,['-DNDEBUG'] if kind=='ndebug' else [])
 cores[kind]=subprocess.check_output([str(exe)],text=True,timeout=180).strip()
 print(MODE,kind,cores[kind],flush=True)
executables=[]
for kind in ['header','ndebug','copied']:
 src=ROOT/'verify/qoj/265.compact.cpp'
 if kind=='copied':
  text=src.read_text().replace('#include "../../src/compact/regular_matching.hpp"',header)
  src=B/'265.cpp';src.write_text(text)
 exe=B/kind;compile(src,exe,['-DNDEBUG'] if kind=='ndebug' else []);executables.append(exe)
def check(g):
 data=f'{len(g)} {len(g[0])}\n'+'\n'.join(' '.join(str(v+1) for v in row) for row in g)+'\n'
 for exe in executables:
  p=[int(x)-1 for x in subprocess.check_output([str(exe)],input=data,text=True,timeout=30).split()]
  assert sorted(p)==list(range(len(g)))
  assert all(v in g[u] for u,v in enumerate(p))
check([[2,3],[0,2],[1,1],[0,3]])
rng=random.Random(265)
for test in range(150):
 n=rng.randrange(1,100);d=rng.randrange(1,80)
 p=list(range(n));g=[[] for _ in range(n)]
 for j in range(d):
  rng.shuffle(p)
  for u in range(n):g[u].append(p[u])
 for row in g:rng.shuffle(row)
 check(g)
r={'status':'pass','mode':MODE,'core':cores,'driver_forms':['header','ndebug','copied'],'official_sample':1,'driver_random_cases':150,'oracle':'independent edge membership and permutation certificate; all input graphs constructed regular','online_status':'not submitted'}
(ROOT/('verification/regular-matching-'+MODE+'.json')).write_text(json.dumps(r,indent=2)+'\n')
