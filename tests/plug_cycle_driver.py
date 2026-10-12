from pathlib import Path
import subprocess,json,hashlib,time
root=Path(__file__).resolve().parents[1]
build=root/'build/plug-cycle'
build.mkdir(parents=True,exist_ok=True)
header=root/'src/compact/plug_cycle.hpp'
driver=root/'verify/luogu/P5056.compact.cpp'
source=build/'P5056.cpp'
source.write_text(driver.read_text().replace('#include "../../src/compact/plug_cycle.hpp"',header.read_text().replace('#pragma once\n','')))
# OEIS A003763, undirected Hamilton cycles on 2n x 2n grid points.
known=[1,6,1072,4638576,467260456608,1076226888605605706,56126499620491437281263608]
cases=[]
for k,want in enumerate(known,1):
    n=2*k
    cases.append((f'{n} {n}\n'+('.'*n+'\n')*n,str(want)))
cases += [('2 2\n**\n**\n','0'),('2 5\n..*..\n..*..\n','0'),('3 3\n...\n.*.\n...\n','1'),('3 4\n..**\n..**\n****\n','1')]
report={'status':'pass','oracle':'https://oeis.org/A003763','known_full_squares':list(range(2,15,2)),'boundary_cases':4,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'forms':{}}
for mode in ['normal','sanitizer']:
    flags=['-O2'] if mode=='normal' else ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
    for form in ['header','ndebug','copied']:
        exe=build/('driver-'+mode+'-'+form)
        subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-I/opt/homebrew/include',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(source if form=='copied' else driver),'-o',str(exe)],check=True)
        timings=[]
        for data,want in cases:
            start=time.monotonic()
            assert subprocess.check_output([str(exe)],input=data,text=True,timeout=120).strip()==want
            timings.append(round(time.monotonic()-start,3))
        report['forms'][mode+'-'+form]={'status':'pass','wall_seconds':timings}
        print(mode,form,'PASS',flush=True)
(root/'verification/plug-cycle-driver.json').write_text(json.dumps(report,indent=2)+'\n')
