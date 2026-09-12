from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
P=167772161
for style in ['compact','classic']:
    for problem,first,limit in [('P5395',False,200000),('P5408',True,262143)]:
        path=root/f'build/submit/{problem}.{style}.cpp'
        subprocess.run(['python3','tools/bundle.py',f'verify/luogu/{problem}.{style}.cpp',str(path)],cwd=root,check=True)
        exe=root/f'build/{problem}.{style}'
        subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(path),'-o',str(exe)],check=True)
        for n in [1,2,3,7,16,17,31,32,33,100,limit]:
            values=list(map(int,subprocess.check_output([str(exe)],input=f'{n}\n',text=True).split()))
            assert len(values)==n+1 and all(0<=v<P for v in values)
            if n<=100:
                want=[1]
                for r in range(1,n+1):
                    want=[0]+[(want[k-1]+(r-1 if first else k)*(want[k] if k<r else 0))%P for k in range(1,r+1)]
                assert values==want,(problem,style,n)
            else:
                assert values[0]==0 and values[n]==1 and values[n-1]==n*(n-1)//2%P
                for x in [1,P-1,1234567]:
                    if first:
                        got=0
                        for v in reversed(values): got=(got*x+v)%P
                        want=1
                        for i in range(n): want=want*(x+i)%P
                    else:
                        got=0
                        falling=1
                        for k,v in enumerate(values):
                            got=(got+v*falling)%P
                            falling=falling*(x-k)%P
                        want=pow(x,n,P)
                    assert got==want,(problem,style,n,x)
        print(f'{problem} {style}: complete row drivers, DP and maximum-size polynomial identities PASS')
