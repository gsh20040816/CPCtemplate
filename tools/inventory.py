#!/usr/bin/env python3
"""Refresh upstream inventory from local reference checkouts; never marks code verified."""
import csv,re,argparse
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--wida',type=Path,required=True); p.add_argument('--kuangbin-text',type=Path,required=True)
a=p.parse_args(); rows=[]
for f in sorted(a.wida.rglob('*')):
    if not f.is_file() or '.git' in f.parts: continue
    rel=f.relative_to(a.wida).as_posix()
    if not rel.startswith(('01 -','02 -','03 -')): continue
    if f.suffix in ('.cpp','.h'):
        rows.append(['WIDA',rel,'',f.stem,'pending','','',''])
    elif f.suffix=='.md' and f.name!='README.md':
        for line in f.read_text().splitlines():
            m=re.match(r'^(#{3,6})\s+(.+)',line)
            if m: rows.append(['WIDA',rel,'',m[2],'pending','','',''])
s=a.kuangbin_text.read_text().split('1 字符串处理\n1.1 KMP\n1 /*')[0]
for line in s.splitlines():
    m=re.match(r'^(\d+(?:\.\d+)+)\s+(.+?)\s+\.\s*\.\s*.*?\s(\d+)\s*$',line)
    if m: rows.append(['kuangbin','ACM template (2018)',m[3],m[1]+' '+m[2],'pending','','',''])
out=Path('docs/coverage.csv')
if out.exists():
    old={tuple(r[:4]):r for r in list(csv.reader(out.open()))[1:]}
    rows=[old.get(tuple(r[:4]),r) for r in rows]
with out.open('w') as f:
    w=csv.writer(f,lineterminator='\n'); w.writerow(['source','source_path','page','topic','status','compact','classic','verification']); w.writerows([[x.strip() for x in row] for row in rows])
print(len(rows),'source entries inventoried')
