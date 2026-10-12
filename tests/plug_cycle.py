from pathlib import Path
import hashlib,json,subprocess,time
root=Path(__file__).resolve().parents[1]
build=root/'build/plug-cycle'
build.mkdir(parents=True,exist_ok=True)
header=root/'src/compact/plug_cycle.hpp'
test=root/'tests/plug_cycle.cpp'
copied=build/'copied.cpp'
copied.write_text(test.read_text().replace('#include "../src/compact/plug_cycle.hpp"',header.read_text().replace('#pragma once\n','')))
report={'status':'pass','source_sha256':hashlib.sha256(header.read_bytes()).hexdigest(),'checks':{}}
for mode in ['normal','sanitizer']:
    flags=['-O2'] if mode=='normal' else ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
    for form in ['header','ndebug','copied']:
        exe=build/(mode+'-'+form)
        subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-I/opt/homebrew/include',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(copied if form=='copied' else test),'-o',str(exe)],check=True)
        start=time.monotonic()
        output=subprocess.check_output([str(exe)],text=True,timeout=180).strip()
        report['checks'][mode+'-'+form]={'result':output,'seconds':round(time.monotonic()-start,3)}
        print(mode,form,output,flush=True)
(root/'verification/plug-cycle-local.json').write_text(json.dumps(report,indent=2)+'\n')
