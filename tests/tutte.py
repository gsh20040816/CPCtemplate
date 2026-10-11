from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
SAN='--sanitize' in sys.argv
MODE='sanitizer' if SAN else 'normal'
B=ROOT/'build/tutte'/MODE
B.mkdir(parents=True,exist_ok=True)
flags=['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if SAN else ['-O2']
code=(ROOT/'src/compact/tutte.hpp').read_text().replace('#pragma once\n','')
def compile(src,exe,extra=[]):
 subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,*extra,str(src),'-o',str(exe)],check=True)
core={}
for form in ['header','ndebug','copied']:
 src=ROOT/'tests/tutte.cpp'
 if form=='copied':
  text=src.read_text().replace('#include "../src/compact/tutte.hpp"',code)
  src=B/'core.cpp';src.write_text(text)
 exe=B/('core-'+form);compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
 core[form]=subprocess.check_output([str(exe)],text=True,timeout=180).strip()
 print(MODE,form,core[form],flush=True)
sample='5\n0 1 1 0 1\n1 0 0 1 1\n1 0 0 1 1\n0 1 1 0 0\n1 1 1 0 0\n'
for form in ['header','ndebug','copied']:
 src=ROOT/'verify/qoj/45.compact.cpp'
 if form=='copied':
  text=src.read_text().replace('#include "../../src/compact/tutte.hpp"',code)
  src=B/'45.cpp';src.write_text(text)
 exe=B/('driver-'+form);compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
 for x,y,w in [(0,1,6),(0,2,24),(1,0,10),(1,1,24),(1,2,52),(2,0,60),(2,1,86)]:
  out=subprocess.check_output([str(exe)],input=sample+f'{x} {y}\n',text=True,timeout=30)
  assert int(out)==w
r={'status':'pass','mode':MODE,'core':core,'driver_forms':['header','ndebug','copied'],'official_driver_evaluations':7,'online_status':'not submitted'}
(ROOT/('verification/tutte-'+MODE+'.json')).write_text(json.dumps(r,indent=2)+'\n')
