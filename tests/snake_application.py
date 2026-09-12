from pathlib import Path
import os,subprocess
root=Path(__file__).resolve().parents[1]
cases=[('2 2 4\n1 1\n1 2\n2 2\n2 1\n..\n..\n',14),('4 5 5\n3 5\n3 4\n3 3\n3 2\n4 2\n'+('.....\n'*4),293),('5 5 3\n1 2\n1 1\n2 1\n.....\n.###.\n.#.#.\n.###.\n.....\n',407)]
k=3000
cases.append((f'1 {k} {k}\n'+''.join(f'1 {i+1}\n' for i in range(k))+'.'*k+'\n',sum((k+j-2)**2 for j in range(1,k))))
n=m=3000
# Independent closed-form sum of (row + column)^2 over the reachable rectangle.
def squares(n,m):
    return (m*n*(n-1)*(2*n-1)//6+n*m*(m-1)*(2*m-1)//6+2*(n*(n-1)//2)*(m*(m-1)//2))%(1<<64)
cases.append((f'{n} {m} 1\n1 1\n'+('.'*m+'\n')*n,squares(n,m)))
cases.append((f'{n} {m} 1\n1 1\n'+('.'*1499+'#'+'.'*1500+'\n')*n,squares(n,1499)))
for style in ['compact','classic']:
    source=root/f'build/submit/QOJ8236.{style}.cpp'
    exe=root/f'build/QOJ8236.{style}'
    subprocess.run(['python3','tools/bundle.py',f'verify/qoj/8236.{style}.cpp',str(source)],check=True)
    flags=['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if os.getenv('CPC_SANITIZE')=='1' else ['-O2']
    subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,str(source),'-o',str(exe)],check=True)
    for data,want in cases:
        got=int(subprocess.check_output([str(exe)],input=data,text=True))
        assert got==want,(style,got,want)
    print(f'QOJ8236 {style}: official samples, full snake chain, 3000-square open/barrier grids PASS',flush=True)
