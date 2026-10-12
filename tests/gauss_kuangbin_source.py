"""Full kuangbin 2.10: original applications versus independent existing oracles."""
from pathlib import Path
import ast,hashlib,json,random,re,runpy,subprocess,sys,time
from compiler_config import CXX
root=Path(__file__).resolve().parents[1];build=root/'build/gauss-kuangbin';build.mkdir(exist_ok=True)
sys.path.insert(0,str(root/'tools'))
from usage_examples import expand
text=(root/'build/source-audit/kuangbin.txt').read_text()
segments={1681:text.rsplit('2.10.1 一类开关问题，对 2 取模的 01 方程组',1)[1].split('2.10.2 解同余方程组')[0],2947:text.rsplit('2.10.2 解同余方程组',1)[1].split('2.11   整数拆分')[0]}
for pid,total in [(1681,125),(2947,101)]:
 lines=[]
 for line in segments[pid].splitlines():
  m=re.match(r'^\s*(\d+)(?:\s+(.*))?$',line)
  if m:
   assert int(m[1])==len(lines)+1,(pid,m[1],len(lines))
   lines.append(m[2] or '')
  elif lines and line.strip() and 'kuangbin' not in line:lines[-1]+=' '+line.strip()
 assert len(lines)==total,(pid,len(lines))
 src='#include <bits/stdc++.h>\nusing namespace std;\n'+'\n'.join(lines).replace('−','-').replace('␣',' ')+'\n'
 (build/f'original-{pid}.cpp').write_text(src)
# Reuse reviewed independent weekday / assignment and rank-certificate fixtures.
# This also runs the existing driver once; no reference is obtained from its output.
widget=runpy.run_path(str(root/'tests/widget_factory_application.py'))
widget_data=widget['data'];widget_truth=widget['expected']
# Load just the two pure oracle functions, without running unrelated MST tests.
module=ast.parse((root/'tests/mst_switch_applications.py').read_text())
helpers=ast.Module(body=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name in ['direct_table','chase']],type_ignores=[])
scope={};exec(compile(helpers,'switch-oracles','exec'),scope)
rng=random.Random(2101681);boards=[]
for n in range(1,4):
 table=scope['direct_table'](n)
 for board in range(1<<(n*n)):
  answer=str(table[board]) if board in table else 'inf'
  assert scope['chase'](n,board)==answer
  boards.append((n,board,answer))
for n in range(4,16):
 for board in [0,(1<<(n*n))-1]+[rng.getrandbits(n*n) for _ in range(4)]:boards.append((n,board,scope['chase'](n,board)))
for _ in range(20):
 n=15;board=rng.getrandbits(n*n);boards.append((n,board,scope['chase'](n,board)))
switch_batches=[]
for start in range(0,len(boards),20):
 batch=boards[start:start+20]
 data=str(len(batch))+'\n'
 for n,b,_ in batch:data+=str(n)+'\n'+''.join(''.join('w' if b>>(i*n+j)&1 else 'y' for j in range(n))+'\n' for i in range(n))
 switch_batches.append((data,[v for n,b,v in batch]))
sections={r['symbol']:r['code'] for r in json.loads((root/'build/book-sections.json').read_text())}
deps=json.loads((root/'docs/template-dependencies.json').read_text())
def closure(name,seen):
 if name in seen:return ''
 seen.add(name)
 return ''.join(closure(d,seen) for d in deps[name])+sections[name]+'\n'
prelude='#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'
for pid,symbol in [(1681,'GaussXor'),(2947,'GaussMod')]:
 driver=root/f'verify/poj/{pid}.compact.cpp'
 snippet=driver.read_text().split('int main()',1)[1]
 (build/f'expanded-{pid}.cpp').write_text(expand(driver.read_text(),driver.parent,set()))
 (build/f'minimal-{pid}.cpp').write_text(prelude+closure(symbol,set())+'int main()'+snippet)

report={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
 for pid in [1681,2947]:
  batches=switch_batches if pid==1681 else [(widget_data,widget_truth)]
  for form in ['original','driver','expanded','minimal','ndebug']:
   src=root/f'verify/poj/{pid}.compact.cpp' if form=='driver' else build/f'{"minimal" if form=="ndebug" else form}-{pid}.cpp'
   exe=build/f'{mode}-{pid}-{form}'
   subprocess.run([CXX,'-std=c++20',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],check=True)
   outputs=[];start=time.monotonic()
   for data,truth in batches:
    p=subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True,timeout=120)
    assert not p.stderr,p.stderr
    assert p.stdout.splitlines()==truth,(mode,pid,form,[(a,b) for a,b in zip(p.stdout.splitlines(),truth) if a!=b][:3])
    outputs+=p.stdout.splitlines()
   report[f'{mode}-{pid}-{form}']=dict(cases=len(outputs),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),output_sha256=hashlib.sha256('\n'.join(outputs).encode()).hexdigest(),seconds=round(time.monotonic()-start,3))
   print(mode,pid,form,len(outputs),'PASS',flush=True)
(root/'verification/gauss-kuangbin-source.json').write_text(json.dumps(dict(status='pass',source_lines={'1681':125,'2947':101},physical_pages=[39,40,41,42,43],source_pdf_sha256=hashlib.sha256((root/'build/source-audit/kuangbin.pdf').read_bytes()).hexdigest(),normalization='numbering, page headers, wrapped lines, Unicode minus and visible space glyph, standard headers only',forms=report,oracles='Physical press subsets + first-row chasing; enumeration of assignments3..9, all weekdays and repeated coefficients, rank-preserving dense300x300 construction'),indent=2)+'\n')
