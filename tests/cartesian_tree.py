from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
SAN='--sanitize' in sys.argv
MODE='sanitizer' if SAN else 'normal'
B=ROOT/'build/cartesian'/MODE
B.mkdir(parents=True,exist_ok=True)
flags=['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if SAN else ['-O2']
code=(ROOT/'src/compact/cartesian_tree.hpp').read_text().replace('#pragma once\n','')
def compile(src,exe,extra=[]):
 subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,*extra,str(src),'-o',str(exe)],check=True)
core={}
for form in ['header','ndebug','copied']:
 src=ROOT/'tests/cartesian_tree.cpp'
 if form=='copied':
  text=src.read_text().replace('#include "../src/compact/cartesian_tree.hpp"',code)
  src=B/'core.cpp';src.write_text(text)
 exe=B/('core-'+form);compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
 core[form]=subprocess.check_output([str(exe)],text=True,timeout=180).strip()
 print(MODE,form,core[form],flush=True)
r={'status':'pass','mode':MODE,'core':core,'oracle':'recursive leftmost interval argmin','online_status':'not submitted'}
(ROOT/('verification/cartesian-tree-'+MODE+'.json')).write_text(json.dumps(r,indent=2)+'\n')
import random
rng=random.Random(5854)
fixtures=[('5\n4 1 3 2 5\n', '19 21')]
for n in [1,2,5,20,100]:
 for repeat in range(10):
  a=list(range(1,n+1));rng.shuffle(a)
  left=[0]*n;right=[0]*n
  def build(l,r):
   if l==r:return 0
   m=min(range(l,r),key=lambda i:a[i])
   left[m]=build(l,m);right[m]=build(m+1,r)
   return m+1
  build(0,n)
  x=y=0
  for i in range(n):x^=(i+1)*(left[i]+1);y^=(i+1)*(right[i]+1)
  fixtures.append((str(n)+'\n'+' '.join(map(str,a))+'\n',f'{x} {y}'))
for form in ['header','ndebug','copied']:
 src=ROOT/'verify/luogu/P5854.compact.cpp'
 if form=='copied':
  src=B/'P5854.cpp'
  src.write_text((ROOT/'verify/luogu/P5854.compact.cpp').read_text().replace('#include "../../src/compact/cartesian_tree.hpp"',code))
 exe=B/('driver-'+form);compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
 for data,want in fixtures:
  assert subprocess.check_output([str(exe)],input=data,text=True,timeout=30).strip()==want
r['driver_cases']=len(fixtures)
r['official_samples']=1
r['driver_forms']=['header','ndebug','copied']
(ROOT/('verification/cartesian-tree-'+MODE+'.json')).write_text(json.dumps(r,indent=2)+'\n')
print(MODE,'driver PASS',flush=True)
