#!/usr/bin/env python3
"""Audit a pinned OI Wiki navigation snapshot and explicit template mappings."""
import hashlib
import json
import re
from pathlib import Path
root = Path(__file__).resolve().parents[1]
source = root/'docs/references/oi-wiki-mkdocs.yml'
text = source.read_text()
nav = text.split('\nnav:\n', 1)[1].split('\n# Theme', 1)[0]
stack = []
leaves = []
for number, line in enumerate(nav.splitlines(), 1):
    if not line.strip() or line.lstrip().startswith('#'):
        continue
    match = re.fullmatch(r'( +)- (.*?):\s*(.*?)\s*', line)
    assert match, (number, line)
    indent, title, path = len(match[1]), match[2], match[3]
    while stack and stack[-1][0] >= indent:
        stack.pop()
    assert not stack or indent == stack[-1][0]+2, line
    labels = [x[1] for x in stack]+[title]
    if path:
        assert path.endswith('.md'), path
        leaves.append(dict(path=path, hierarchy=labels, order=len(leaves)))
    else:
        stack.append((indent, title))
by_path = {r['path']: r for r in leaves}
assert len(by_path) == len(leaves)
mapping = json.loads((root/'docs/oi-template-map.json').read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest() == mapping['reference_source_sha256'], 'Pinned navigation snapshot changed'
catalog = {r[1]:r for r in json.loads((root/'docs/catalog.json').read_text())}
assert set(mapping['templates']) == set(catalog), (set(catalog)-mapping['templates'].keys(),mapping['templates'].keys()-set(catalog))
for symbol, entry in mapping['templates'].items():
    assert entry['primary'] in by_path, (symbol, entry)
    assert entry['relation'] in ['direct', 'application', 'composite', 'related']
    assert entry['note'] or entry['relation']=='direct'
    for page in entry.get('additional', []):
        assert page in by_path, (symbol,page)
    entry['hierarchy'] = by_path[entry['primary']]['hierarchy']
    entry['order'] = by_path[entry['primary']]['order']
result = dict(reference_commit=mapping['reference_commit'],source_url='https://github.com/OI-wiki/OI-wiki/blob/'+mapping['reference_commit']+'/mkdocs.yml',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),navigation=leaves,templates=mapping['templates'])
(root/'docs/oi-taxonomy.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
lines=['# OI Wiki 分类映射', '', '固定官方导航来源：['+mapping['reference_commit'][:12]+']('+result['source_url']+')。', '', 'issue #7 指定的 oi-wiki.com 未能通过网页工具访问；此处明确采用 OI Wiki 官方仓库，不声称已核验该域名与官方导航相同。', '', '此表驱动 PDF 的导航层级；复合条目的内部拆分与相关挂靠仍待处理。direct 表示直接知识点，application 表示应用，composite 表示一个代码条目横跨多个页面，related 表示仅有相关挂靠，需进一步处理。分类不代表上游整页内容已实现或验证。', '', '| 模板 | 上游完整层级 | 关系 | 处理说明 |', '| --- | --- | --- | --- |']
for symbol, entry in sorted(mapping['templates'].items(),key=lambda p:(p[1]['order'],p[0])):
    labels=' → '.join(entry['hierarchy']).replace('|','\\|')
    lines.append('| '+symbol+' | '+labels+' | '+entry['relation']+' | '+entry['note'].replace('|','\\|')+' |')
(root/'docs/OI-TAXONOMY.md').write_text('\n'.join(lines)+'\n')
print(f'{len(leaves)} navigation pages; {len(catalog)} templates mapped; navigation layout active; composite/related refinements remain')
