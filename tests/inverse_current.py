"""Current vector inverse cores, independent certificates in both build modes."""
from compiler_config import CXX
from pathlib import Path
import subprocess,json,hashlib
reports=[]
for name in ['batch_inverse','inverse_table','batch_units','dynamic_modint']:
 source=Path('tests/'+name+'.cpp')
 for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
  exe='build/inverse-core-'+name+'-'+mode
  subprocess.run([CXX,'-std=c++20',*flags,str(source),'-o',exe],check=True)
  result=subprocess.run([exe],capture_output=True,text=True,check=True,timeout=60)
  assert not result.stderr,result.stderr
  reports.append(dict(test=str(source),mode=mode,flags=flags,test_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),stdout=result.stdout,new_online_ac=False))
  print(name,mode,result.stdout.strip(),flush=True)
Path('verification/inverse-current-core.json').write_text(json.dumps(reports,indent=2)+'\n')
