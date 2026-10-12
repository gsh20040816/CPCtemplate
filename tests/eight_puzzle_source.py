"""Exhaustive independent packed-state oracle and full upstream application."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,time
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
build=root/'build/eight-puzzle';build.mkdir(exist_ok=True)
sys.path.insert(0,str(root/'tools'))
from usage_examples import expand
text=(root/'build/source-audit/kuangbin.txt').read_text().rsplit('     5.2.1 HDU1043 反向搜索',1)[1].split('     6     动态规划')[0]
lines=[]
for line in text.splitlines():
 m=re.match(r'^\s*(\d+)(?:\s+(.*))?$',line)
 if m:
  assert int(m[1])==len(lines)+1,(m[1],len(lines))
  lines.append(m[2] or '')
 elif lines and line.strip() and 'kuangbin' not in line:lines[-1]+=' '+line.strip()
assert len(lines)==89
# C++98 avoids collision between the old global move array and C++11 std::move.
original='#include <bits/stdc++.h>\nusing namespace std;\n'+'\n'.join(lines).replace('−','-')+'\n'
(build/'original.cpp').write_text(original)
driver=root/'verify/hdu/1043.compact.cpp'
expanded=expand(driver.read_text(),driver.parent,set())
(build/'expanded.cpp').write_text(expanded)
section=next(r for r in json.loads((root/'build/book-sections.json').read_text()) if r['symbol']=='EightPuzzle')
minimal='#include <bits/stdc++.h>\nusing namespace std;\n'+section['code']+'\n'+(root/'docs/usage/example-413.cpp').read_text()
(build/'minimal.cpp').write_text(minimal)
reports={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
 exe=build/('oracle-'+mode)
 subprocess.run([CXX,'-std=c++20',*flags,str(root/'tests/eight_puzzle.cpp'),'-o',str(exe)],check=True)
 p=subprocess.run([str(exe),str(build/'input.txt'),str(build/'depth.txt')],capture_output=True,text=True,check=True,timeout=180)
 assert not p.stderr,p.stderr
 histogram=list(map(int,p.stdout.split()));assert len(histogram)==32
 data=(build/'input.txt').read_text();depths=list(map(int,(build/'depth.txt').read_text().splitlines()))
 boards=[list(s.replace('x','0').split()) for s in data.splitlines()]
 for form in ['original','driver','expanded','minimal','ndebug']:
  src=build/'original.cpp' if form=='original' else driver if form=='driver' else build/'minimal.cpp' if form=='minimal' else build/'expanded.cpp'
  exe=build/(mode+'-'+form)
  subprocess.run([CXX,'-std=c++98' if form=='original' else '-std=c++20',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],check=True)
  start=time.monotonic()
  p=subprocess.run([str(exe)],input=data,capture_output=True,text=True,check=True,timeout=180)
  assert not p.stderr,p.stderr
  out=p.stdout.splitlines();assert len(out)==362880
  exceptions=[]
  for i,(path,depth,board) in enumerate(zip(out,depths,boards)):
   if depth<0:assert path=='unsolvable',(mode,form,i);continue
   if len(path)!=depth:
    assert form=='original' and depth==0 and len(path)==2,(mode,form,i,depth,path)
    exceptions.append(dict(board=board,path=path,expected=''))
   a=board.copy();z=a.index('0')
   for ch in path:
    dz={'u':-3,'d':3,'l':-1,'r':1}[ch];n=z+dz
    assert 0<=n<9 and abs(z//3-n//3)+abs(z%3-n%3)==1
    a[z],a[n]=a[n],a[z];z=n
   assert a==list('123456780'),(mode,form,i,path)
  assert len(exceptions)==(1 if form=='original' else 0)
  reports[mode+'-'+form]=dict(cases=len(out),seconds=round(time.monotonic()-start,3),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),stdout_sha256=hashlib.sha256(p.stdout.encode()).hexdigest(),upstream_shortest_path_exceptions=exceptions)
  print(mode,form,'362880 states PASS',exceptions,flush=True)
report=dict(status='pass',source_lines=89,source_pdf_sha256=hashlib.sha256((root/'build/source-audit/kuangbin.pdf').read_bytes()).hexdigest(),histogram=histogram,reachable=181440,unreachable=181440,max_distance=31,forms=reports,oracle='Independent 4-bit board encoding, undirected grid-edge BFS; permutation-rank bijection; inversion parity; replay every output move',source_language='Unmodified original compiled as C++98 to avoid global move/std::move ambiguity')
(root/'verification/eight-puzzle-local.json').write_text(json.dumps(report,indent=2)+'\n')
