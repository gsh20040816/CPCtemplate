from pathlib import Path
import subprocess, random, time
root=Path(__file__).resolve().parents[1]
rng=random.Random(61577)
for style in ['compact']:
    for problem,p,limit in [('P4717',998244353,17),('P6097',1000000009,20)]:
        source=root/f'build/submit/{problem}.{style}.cpp'
        subprocess.run(['python3','tools/bundle.py',f'verify/luogu/{problem}.{style}.cpp',str(source)],cwd=root,check=True)
        exe=root/f'build/{problem}.{style}'
        subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(source),'-o',str(exe)],check=True)
        def run(m,a,b):
            data=f'{m}\n'+' '.join(map(str,a))+'\n'+' '.join(map(str,b))+'\n'
            return [list(map(int,line.split())) for line in subprocess.check_output([str(exe)],input=data,text=True).splitlines()]
        for t in range(50):
            m=rng.randrange(1,7)
            n=1<<m
            a=[rng.randrange(p) for _ in range(n)]
            b=[rng.randrange(p) for _ in range(n)]
            ops=['|','&','^'] if problem=='P4717' else ['s']
            want=[]
            for op in ops:
                row=[0]*n
                for i in range(n):
                    for j in range(n):
                        if op=='s' and i&j: continue
                        k=i|j if op in ['|','s'] else i&j if op=='&' else i^j
                        row[k]=(row[k]+a[i]*b[j])%p
                want.append(row)
            assert run(m,a,b)==want,(style,problem,t)
        m=limit
        n=1<<m
        a=[pow(123,i.bit_count(),p) for i in range(n)]
        b=[pow(456,i.bit_count(),p) for i in range(n)]
        start=time.monotonic()
        values=run(m,a,b)
        elapsed=time.monotonic()-start
        expected=[]
        for op in (['|','&','^'] if problem=='P4717' else ['s']):
            row=[]
            for k in range(m+1):
                if op=='|': v=pow(123+456+123*456,k,p)
                elif op=='&': v=pow(123*456,k,p)*pow(1+123+456,m-k,p)%p
                elif op=='^': v=pow(123+456,k,p)*pow(1+123*456,m-k,p)%p
                else: v=pow(123+456,k,p)
                row.append(v)
            expected.append(row)
        assert len(values)==len(expected)
        for row,want in zip(values,expected):
            assert len(row)==n
            assert all(v==want[i.bit_count()] for i,v in enumerate(row))
        print(f'{problem} {style}: 50 pair-enumeration cases and full {m}-bit tensor identity PASS; large driver wall time {elapsed:.3f}s',flush=True)
