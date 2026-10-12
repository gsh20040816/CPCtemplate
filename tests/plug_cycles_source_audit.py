"""Extract the locked 213-line kuangbin source; compare complete drivers."""
from pathlib import Path
import hashlib
import json
import os
import random
import re
import subprocess
import time
import sys
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
build = root / 'build/plug-cycles/source'
build.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(root / 'tools'))
from audit_copy_context import extract_components
catalog = json.loads((root / 'docs/catalog.json').read_text())
mod = extract_components([r for r in catalog if r[1] == 'ModInt'])[0]['code']
core = (root / 'src/compact/plug_cycles.hpp').read_text().replace('#pragma once\n', '')
main = (root / 'verify/hdu/4285.compact.cpp').read_text().split('int main()', 1)[1]
minimal = root / 'build/plug-cycles/4285-minimal.cpp'
minimal.write_text(core + '\n' + mod + '\nint main()' + main)
assert minimal.read_bytes() == (root / 'verification/submitted/HDU4285.compact.cpp').read_bytes()
pdf = root / 'build/source-audit/kuangbin.pdf'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(pdf) == 'f1c90eae0c3fb309d58a14b050fe12b239efb474b033299a547b55646c2768ad'
s = pdf.with_suffix('.txt').read_text()
start = s.index(' 1   /*', s.index('     6.3.1 HDU 4285'))
end = s.index('     7     计算几何', start)
lines = []
for line in s[start:end].splitlines():
    m = re.match(r'\s*(\d+)\s*(.*)', line)
    if m:
        assert int(m[1]) == len(lines) + 1
        lines.append(m[2].replace('−', '-'))
    elif line.strip() and 'kuangbin' not in line:
        assert lines and line.startswith(' '), line
        lines[-1] += line.strip()
assert len(lines) == 213
source = build / 'original.cpp'
source.write_text('#include <bits/stdc++.h>\nusing namespace std;\n' + '\n'.join(lines) + '\n')
rng = random.Random(20261012)
cases = [(4,4,1,['**..','....','....','....']), (4,4,1,['....']*4)]
for _ in range(250):
    n, m = rng.randint(2,6), rng.randint(2,6)
    a = [''.join('.' if rng.randrange(100) < 70 else '*' for _ in range(m)) for _ in range(n)]
    for k in (0,1,2,3): cases.append((n,m,k,a))
for k in (1,2,6,18,36): cases.append((12,12,k,['.'*12]*12))
raw = str(len(cases))+'\n'+''.join(f'{n} {m} {k}\n'+'\n'.join(a)+'\n' for n,m,k,a in cases)
report = {'source_pdf_sha256':sha(pdf),'source_physical_pages':list(range(215,220)), 'numbered_lines':213, 'original_sha256':sha(source),'cases':len(cases),'runs':[], 'scope':'Upstream complete-program comparison; independent exhaustive oracle is in plug-cycles-local.json.'}
for mode in ('normal','sanitizer'):
    flags = ['-O2'] if mode=='normal' else ['-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all']
    results = []
    for name, path in [('original',source), ('driver',root/'verify/hdu/4285.compact.cpp'), ('minimal',root/'build/plug-cycles/4285-minimal.cpp')]:
        exe=build/(name+'-'+mode)
        compile_result=subprocess.run([CXX,'-std=c++20',*flags,str(path),'-o',str(exe)],check=True,capture_output=True,text=True)
        env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
        start=time.monotonic()
        p=subprocess.run([str(exe)],input=raw,capture_output=True,text=True,env=env,timeout=240)
        assert p.returncode==0 and not p.stderr,p.stderr
        values=[int(v) for v in p.stdout.split()]
        assert len(values)==len(cases)
        assert values[:2]==[2,6]
        results.append(values)
        report['runs'].append({'mode':mode,'form':name,'seconds':round(time.monotonic()-start,3),'output_sha256':hashlib.sha256(p.stdout.encode()).hexdigest(),'compile_diagnostic':compile_result.stderr.strip()})
        print(mode,name,len(values),'PASS',flush=True)
    assert results[0]==results[1]==results[2]
cmd = [CXX, '-std=c++20', '-Wformat=2', '-Werror=format', '-fsyntax-only', str(source)]
p = subprocess.run(cmd, capture_output=True, text=True)
assert p.returncode != 0 and 'char (*)[20]' in p.stderr
report['upstream_format_diagnostic'] = {'command': cmd, 'diagnostic': p.stderr}
(root/'verification/plug-cycles-source-audit.json').write_text(json.dumps(report,indent=2)+'\n')
