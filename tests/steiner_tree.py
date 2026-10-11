from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
SAN='--sanitize' in sys.argv
MODE='sanitizer' if SAN else 'normal'
B=ROOT/'build/steiner'/MODE
B.mkdir(parents=True,exist_ok=True)
flags=['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if SAN else ['-O2']
code=(ROOT/'src/compact/steiner_tree.hpp').read_text().replace('#pragma once\n','')
def compile(src,exe,extra=[]):
 subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,*extra,str(src),'-o',str(exe)],check=True)
core={}
for form in ['header','ndebug','copied']:
 src=ROOT/'tests/steiner_tree.cpp'
 if form=='copied':
  text=src.read_text().replace('#include "../src/compact/steiner_tree.hpp"',code)
  src=B/'core.cpp';src.write_text(text)
 exe=B/('core-'+form);compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
 core[form]=subprocess.check_output([str(exe)],text=True,timeout=180).strip()
 print(MODE,form,core[form],flush=True)
r={'status':'pass','mode':MODE,'core':core,'oracle':'independent edge-subset enumeration and returned edge witness','online_status':'not submitted'}
(ROOT/('verification/steiner-tree-'+MODE+'.json')).write_text(json.dumps(r,indent=2)+'\n')
# The official numeric sample was not available in the retrieved statement.
# These are authored driver fixtures, not claimed as official samples.
fixtures = [
 ('3 3 2\n1 2 4\n2 3 7\n1 3 20\n1 3\n', '11'),
 ('4 4 3\n1 2 3\n2 3 2\n2 4 5\n1 4 100\n1 3 4\n', '10'),
 ('2 3 2\n1 1 0\n1 2 8\n1 2 2\n1 2\n', '2'),
 ('3 1 2\n1 2 3\n1 3\n', '-1'),
]
for form in ['header','ndebug','copied']:
 src=ROOT/'verify/luogu/P6192.compact.cpp'
 if form=='copied':
  src=B/'P6192.cpp'
  src.write_text((ROOT/'verify/luogu/P6192.compact.cpp').read_text().replace('#include "../../src/compact/steiner_tree.hpp"',code))
 exe=B/('driver-'+form)
 compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
 for data,want in fixtures:
  out=subprocess.check_output([str(exe)],input=data,text=True,timeout=30).strip()
  assert out==want,(form,out,want)
r['driver_forms']=['header','ndebug','copied']
r['authored_driver_cases']=len(fixtures)
(ROOT/('verification/steiner-tree-'+MODE+'.json')).write_text(json.dumps(r,indent=2)+'\n')
print(MODE,'driver PASS',flush=True)
