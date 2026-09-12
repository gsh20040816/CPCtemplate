#!/usr/bin/env python3
"""Seed issue #1's review queue without conferring template or ranking verification."""
from pathlib import Path
import csv,json,re
root=Path(__file__).resolve().parents[1]
cat=json.loads((root/'docs/catalog.json').read_text())
records=json.loads((root/'verification/oj.json').read_text())
qoj={'SuffixAutomaton':217,'IntegerGeometry':218,'NumberTheory':249,'prefix_function':464,'kmp_match':464,'berlekamp_massey':547,'MinCostFlow':602,'NttConvolution':618,'z_function':786,'manacher':787,'PalindromicTree':801,'Arborescence':904,'TarjanSCC':906,'SuffixArray':956,'Lowlink':995,'TwoSAT':997,'LinkCutTree':21529,'CentroidPairs':21959,'BostanMori':146}
drivers=list((root/'verify').rglob('*.compact.cpp'))
rows=[]
for file,name,title,contract in cat:
    candidates=[]
    for driver in drivers:
        text=driver.read_text()
        if not re.search(r'\b'+re.escape(name)+r'\b',text):continue
        rel=str(driver.relative_to(root));pid=driver.name.split('.')[0];judge=driver.parent.name
        url={'luogu':f'https://www.luogu.com.cn/problem/{pid}','qoj':f'https://qoj.ac/problem/{pid}','cses':f'https://cses.fi/problemset/task/{pid}','library_checker':f'https://judge.yosupo.jp/problem/{pid}'}.get(judge,'')
        ac=[r['record'] for r in records if r['style']=='compact' and r['source_driver']==rel and r['verdict']=='Accepted']
        candidates.append(dict(driver=rel,url=url,existing_ac=ac,review='candidate: audit full statement and exclude competition applications'))
    rows.append(dict(symbol=name,title=title,source=f'src/compact/{file}.hpp',status='needs_template_problem_review',candidate_drivers=candidates,qoj_tag_candidate=f'https://qoj.ac/problem/{qoj[name]}' if name in qoj else None,ranking=dict(status='not_checked',rank=None,total=None,checked_at=None,scope=None)))
upstream=list(csv.DictReader((root/'docs/coverage.csv').open()))
missing=[{k:r[k] for k in ['source','source_path','page','topic']} for r in upstream if r['status']=='pending']
data=dict(issue='https://github.com/gsh20040816/CPCtemplate/issues/1',note='Candidates only. A template tag or an existing application AC does not prove a noncompetition template, complete API coverage, or a fastest-submission rank.',qoj_tag_source='https://qoj.ac/problems?tag=%E6%A8%A1%E6%9D%BF%E9%A2%98',algorithms=rows,unresolved_upstream_topics=missing)
(root/'docs/template-problems.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(len(rows),'implemented algorithm entries;',len(missing),'upstream topics still require deduplication and mapping')
