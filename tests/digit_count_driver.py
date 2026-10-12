from pathlib import Path
import random,subprocess,json,hashlib
root=Path(__file__).resolve().parents[1]
build=root/'build/digit-count'
build.mkdir(parents=True,exist_ok=True)
header=root/'src/compact/digit_count.hpp'
driver=root/'verify/luogu/P2602.compact.cpp'
source=build/'P2602.cpp'
source.write_text(driver.read_text().replace('#include "../../src/compact/digit_count.hpp"',header.read_text().replace('#pragma once\n','')))
rng=random.Random(2602)
cases=[]
for a,b in [(1,1),(1,10),(99,101),(10**12,10**12)]+[(a:=rng.randint(1,10000),a+rng.randint(0,300)) for _ in range(100)]:
    want=[0]*10
    for n in range(a,b+1):
        for d in str(n):want[int(d)]+=1
    cases.append((f'{a} {b}\n',list(map(str,want))))
# 1..10^12: each nonzero digit occurs 12*10^11 times in 0..10^12-1;
# remove padded leading zeros, then append the endpoint 10^12.
z=12*10**11-sum(10**i for i in range(12))+12
cases.append(('1 1000000000000\n',list(map(str,[z,12*10**11+1]+[12*10**11]*8))))
report={'status':'pass','cases':len(cases),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'forms':{}}
for mode in ['normal','sanitizer']:
    flags=['-O2'] if mode=='normal' else ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
    for form in ['header','copied']:
        exe=build/('driver-'+mode+'-'+form)
        subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,str(source if form=='copied' else driver),'-o',str(exe)],check=True)
        for data,want in cases:
            assert subprocess.check_output([str(exe)],input=data,text=True,timeout=10).split()==want,(data,want)
        report['forms'][mode+'-'+form]='pass'
        print(mode,form,'PASS',flush=True)
(root/'verification/digit-count-driver.json').write_text(json.dumps(report,indent=2)+'\n')
