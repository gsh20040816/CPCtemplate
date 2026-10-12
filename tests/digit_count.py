from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[1]
build=root/'build/digit-count'
build.mkdir(parents=True, exist_ok=True)
header=root/'src/compact/digit_count.hpp'
test=root/'tests/digit_count.cpp'
copied=build/'copied.cpp'
copied.write_text(test.read_text().replace('#include "../src/compact/digit_count.hpp"',header.read_text().replace('#pragma once\n','')))
report={'status':'pass','source_sha256':hashlib.sha256(header.read_bytes()).hexdigest(),'checks':{}}
for mode in ['normal','sanitizer']:
    flags=['-O2'] if mode=='normal' else ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
    for form in ['header','copied']:
        exe=build/(mode+'-'+form)
        subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,str(copied if form=='copied' else test),'-o',str(exe)],check=True)
        report['checks'][mode+'-'+form]=subprocess.check_output([str(exe)],text=True,timeout=120).strip()
        print(mode,form,'PASS',flush=True)
(root/'verification/digit-count-local.json').write_text(json.dumps(report,indent=2)+'\n')
