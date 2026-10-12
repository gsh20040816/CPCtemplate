"""Source inverse normalization witness and application negative controls."""
from pathlib import Path
import subprocess,json,cmath,math,random
root=Path(__file__).resolve().parents[1];b=root/'build/fft-kuangbin'
original=(b/'original-1402.cpp').read_text().split('const int MAXN')[0]
probe=original+'\n#include "'+str(root/'src/compact/fft.hpp')+'"\n'+r'''
int main()
{
    int n;
    cout << setprecision(18);
    while (cin >> n)
    {
        vector<Complex> a(n);
        for (auto &z : a) cin >> z.x >> z.y;
        for (int sign : {1, -1})
        {
            auto v = a;
            fft(v.data(), n, sign);
            for (auto z : v) cout << z.x << ' ' << z.y << ' ';
            cout << '\n';
        }
        ComplexFFT current(n);
        for (bool inverse : {false, true})
        {
            vector<ComplexFFT::C> v(n);
            for (int i = 0; i < n; i++) v[i] = {a[i].x, a[i].y};
            current.transform(v, inverse);
            for (auto z : v) cout << z.real() << ' ' << z.imag() << ' ';
            cout << '\n';
        }
    }
}
'''
(b/'source-transform.cpp').write_text(probe)
rng=random.Random(62);cases=[]
for n in [1,2,4,8,16,32,64]:
 cases.extend([[complex(rng.randrange(-9,10),rng.randrange(-9,10)) for _ in range(n)] for k in range(8)])
cases.append([1j,0j])
data=''.join(str(len(a))+'\n'+''.join(f'{z.real} {z.imag}\n' for z in a) for a in cases)
reports={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
 exe=b/f'source-transform-{mode}'
 subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,str(b/'source-transform.cpp'),'-o',str(exe)],check=True)
 p=subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True)
 assert not p.stderr
 rows=iter(p.stdout.splitlines())
 for a in cases:
  n=len(a)
  for kind in range(4):
   row=list(map(float,next(rows).split()));out=[complex(*row[i:i+2]) for i in range(0,len(row),2)]
   sign=-1 if kind in [0,3] else 1
   want=[sum(z*cmath.exp(sign*2j*math.pi*j*k/n) for j,z in enumerate(a)) for k in range(n)]
   if kind==1:want=[complex(z.real/n,z.imag) for z in want]
   if kind==3:want=[z/n for z in want]
   assert all(abs(u-v)<1e-8 for u,v in zip(out,want)),(kind,n,out,want)
 reports[mode]={'cases':len(cases),'original_inverse_scales_real_only':True,'current_scales_both':True,'opposite_forward_sign':True}
# Mutants use current complete expanded applications and inputs with hand-verifiable answers.
mutations={
 'missing_self_pair':(4609,'for (int v : a) count[2 * v]--;','', '1\n3\n1 1 2\n','0.0000000'),
 'ordered_pairs':(4609,'for (auto &v : count) v /= 2;','', '1\n3\n1 1 2\n','0.0000000'),
 'strict_prefix':(4609,'good -= count[v];','good -= count[v - 1];', '1\n3\n1 1 2\n','0.0000000'),
 'cyclic_alias':(4609,'while (size <= 2 * m)','while (size <= m)', '1\n3\n3 3 3\n','1.0000000'),
 'missing_carry':(1402,'c[i + 1] += c[i] / 10;','', '99 99\n','9801'),
 'negative_zero':(1402,'negative && c.back() != 0','negative', '-0 7\n','0'),
}
for name,(pid,a,c,data,want) in mutations.items():
 s=(b/f'expanded-{pid}.cpp').read_text();assert s.count(a)==1
 src=b/('mutant-'+name+'.cpp');src.write_text(s.replace(a,c));exe=src.with_suffix('')
 subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(src),'-o',str(exe)],check=True)
 p=subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True)
 assert p.stdout.strip()!=want,name
 reports[name]={'rejected':True,'expected':want,'observed':p.stdout.strip()}
 print(name,'rejected',flush=True)
(root/'verification/fft-kuangbin-negative-controls.json').write_text(json.dumps(reports,indent=2)+'\n')
