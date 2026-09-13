#!/usr/bin/env python3
"""Build category books from the same source-linked sections as the omnibus."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
rows = json.loads((root / 'build/book-sections.json').read_text())
from taxonomy_layout import TAX, render
# The top-level categories come from the pinned navigation, not source modules.
groups = {'strings': ('字符串', ''),
          'mathematics': ('数学', ''), 'data-structures': ('数据结构', ''),
          'graphs': ('图论', ''), 'geometry': ('计算几何', ''), 'misc': ('杂项', '')}
owner = {title: key for key, (title, _) in groups.items()}
for r in rows:
    r['volume'] = owner[TAX[r['symbol']]['hierarchy'][0]]
by_name = {r['symbol']: r for r in rows}
assert len(by_name) == len(rows)
notes = {k: [] for k in groups}
parts = re.split(r'(?=\\section\{)', (root / 'docs/mathematics.tex').read_text())[1:]
for part in parts:
    title = part.split('\n', 1)[0]
    if 'ACL 的组合约定' in title:
        # General ACL comparison stays in the omnibus, not every category.
        continue
    key = 'mathematics'
    if '数值算法与几何' in title:
        key = 'geometry'
    elif any(x in title for x in ['可持久化区间', '杭州 2023 K', '带修莫队', '并查集模板题']):
        key = 'data-structures'
    elif '非负权树' in title:
        key = 'graphs'
    elif any(x in title for x in ['函数图', '杭州 2023 H', '杭州 2023 G', 'SCC 模板题']):
        key = 'graphs'
    if '带修莫队' in title:
        key = 'misc'
    notes[key].append(part)
notes['geometry'].append((root / 'docs/geometry-notes.tex').read_text())

manifest = []
for key, (title, _) in groups.items():
    primary = [r for r in rows if r['volume'] == key]
    included = {r['symbol'] for r in primary}
    knowledge = '\n'.join(notes[key])
    # Exact catalog identifiers conservatively include dependencies mentioned in
    # code/comments or interface notes; close transitively before emitting labels.
    pending = knowledge + '\n' + '\n'.join(r['code'] + r['latex'] for r in primary)
    while True:
        tokens = set(re.findall(r'\b[A-Za-z_]\w*\b', pending))
        added = (tokens & by_name.keys()) - included
        if not added:
            break
        included.update(added)
        pending = '\n'.join(by_name[n]['code'] + by_name[n]['latex'] for n in added)
    dependencies = [r for r in rows if r['symbol'] in included and r not in primary]
    body = [r'\input{preamble.tex}', r'\begin{document}', r'\raggedbottom',
            r'\hypersetup{pageanchor=false}', r'\begin{titlepage}\centering\vspace*{35mm}',
            r'{\Huge\bfseries ' + title + r'\par}\vspace{15mm}',
            r'{\LARGE Morning Flower and Evening Oath\par}\vspace{15mm}',
            r'{\Large XCPC vector 模板分册\par}\vfill',
            r'建设稿：验证状态与适用边界见各条目及仓库 verification/。',
            r'\end{titlepage}\hypersetup{pageanchor=true}', r'\frontmatter\tableofcontents',
            r'\chapter{使用约定}',
            r'C++20，默认包含 bits/stdc++.h 与 cassert，并使用 std 命名空间。下标、区间及数值范围以各条目说明为准。DFS 保持递归，需满足题目栈空间条件。',
            r'本册主目录沿用 OI Wiki 官方导航的大、中、小层级，各页下列本库实现。PBDS 与 GNU rope 按队内约定纳入平衡树。组合条目与相关挂靠仍见仓库分类审计。跨类引用的已收录组件附在依赖部分；源头文件中的依赖仍须一并检查。',
            r'本册尚非全量完成稿；传统版评测仅为历史档案，当前只维护 vector 代码。', r'\mainmatter']
    def emit(entries):
        body.append(render(entries))
    emit(primary)
    if knowledge.strip():
        body += [r'\chapter{配套知识与验证范围}', knowledge]
    if dependencies:
        body.append(r'\appendix')
        body.append(r'\part{跨类依赖}')
        emit(dependencies)
    body += [r'\backmatter\printindex', r'\end{document}']
    source = '\n\n'.join(body) + '\n'
    labels = set(re.findall(r'\\label\{([^}]+)\}', source))
    refs = set(re.findall(r'\\(?:page)?ref\{([^}]+)\}', source))
    assert not refs - labels, (key, refs - labels)
    (root / f'docs/volume-{key}.tex').write_text(source)
    manifest.append(dict(id=key, title=title, entries=[r['symbol'] for r in primary], dependencies=[r['symbol'] for r in dependencies]))
assert sum(len(v['entries']) for v in manifest) == len(rows)
(root / 'docs/volumes.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print('Generated six category volumes with user-requested PBDS placement; each template has one primary category')
