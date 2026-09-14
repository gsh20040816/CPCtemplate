#!/usr/bin/env python3
"""Inventory a pinned upstream checkout; discovered matches are not AC evidence."""
import argparse
import hashlib
import json
import re
import subprocess
import tomllib
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('checkout', type=Path)
args = ap.parse_args()
up = args.checkout.resolve()
commit = subprocess.check_output(['git', '-C', str(up), 'rev-parse', 'HEAD'], text=True).strip()
assert not subprocess.check_output(['git', '-C', str(up), 'status', '--porcelain'], text=True).strip(), 'Use a clean reference checkout'
base = 'https://github.com/yosupo06/library-checker-problems/blob/' + commit + '/'
categories = tomllib.loads((up / 'categories.toml').read_text())['categories']
category = {}
for group in categories:
    for pid in group['problems']:
        assert pid not in category
        category[pid] = group['name']
files = {}
for p in sorted(up.rglob('info.toml')):
    if p.relative_to(up).parts[0] == 'test':
        continue
    assert p.parent.name not in files
    files[p.parent.name] = p
assert not category.keys() - files.keys()
reviews = json.loads((root / 'docs/template-problem-reviews.json').read_text())
accepted = json.loads((root / 'verification/oj.json').read_text())
rows = []
for pid, p in sorted(files.items(), key=lambda x: (category.get(x[0], 'Unlisted'), x[0])):
    info = tomllib.loads(p.read_text())
    path = p.parent.relative_to(up)
    listed = pid in category
    excluded = category.get(pid) == 'Sample'
    drivers = []
    for d in sorted((root / 'verify/library_checker').rglob('*.compact.cpp')):
        urls = re.findall(r'https://judge\.yosupo\.jp/problem/([A-Za-z0-9_]+)', d.read_text())
        if pid in urls or (not urls and d.name == pid + '.compact.cpp'):
            drivers.append(str(d.relative_to(root)))
    linked_reviews = []
    for review in reviews:
        if f'https://judge.yosupo.jp/problem/{pid}' == review.get('url'):
            linked_reviews.append({'symbol': review['symbol'], 'statement_checked': review.get('statement_checked', False)})
    ac = [r['record'] for r in accepted if r['source_driver'] in drivers and r['verdict'] == 'Accepted' and 'judge.yosupo.jp/submission/' in r['record']]
    evidence = {}
    for name in ['info.toml', 'task.md', 'checker.cpp', 'verifier.cpp']:
        source = p.parent / name
        if source.exists():
            evidence[name] = dict(url=base + str(path / name), sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    rows.append(dict(id=pid, title=info['title'], category=category.get(pid, 'Unlisted'), listed_in_categories=listed,
        scope='excluded_sample' if excluded else 'included',
        exclusion_reason='Official Sample category; excluded by issue #1 reply.' if excluded else None,
        url=f'https://judge.yosupo.jp/problem/{pid}', upstream_path=str(path), timelimit_seconds=info['timelimit'],
        parameters=info.get('params', {}), generator_cases=sum(x['number'] for x in info.get('tests', [])),
        sources=evidence, candidate_drivers=drivers, linked_statement_reviews=linked_reviews,
        online_ac=ac, status='excluded_sample' if excluded else ('online_ac_scoped' if ac else 'pending_statement_adapter_and_online_validation'),
        ranking={'status':'not_checked','rank':None,'total':None}))
assert {d for r in rows for d in r['candidate_drivers']} == {str(d.relative_to(root)) for d in (root / 'verify/library_checker').rglob('*.compact.cpp')}, 'An existing Library Checker driver has no exact problem mapping'
report = dict(reference_repository='https://github.com/yosupo06/library-checker-problems', reference_commit=commit,
    categories_sha256=hashlib.sha256((up/'categories.toml').read_bytes()).hexdigest(),
    scope_note='All non-test info.toml entries are retained, including unlisted problems. Only official Sample entries are excluded. Metadata, existing drivers and matching review URLs do not confer implementation completeness or online acceptance. Unlisted problem URLs require deployment verification.',
    counts=dict(total=len(rows), listed=len(category), unlisted=len(rows)-len(category), included=sum(r['scope']=='included' for r in rows), excluded_sample=sum(r['scope']=='excluded_sample' for r in rows)), problems=rows)
(root/'docs/library-checker-inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
text = ['# Library Checker 逐题覆盖队列', '', f'固定官方仓库版本：[`{commit[:12]}`]({base[:-1]})。', '',
    '从所有非 test/ 的 info.toml 提取，核对 categories.toml，无分类缺失文件。未列入分类的题也保留，是否已部署需逐题核对。仅按用户要求排除官方 Sample 类；没有按实现难度缩小范围。', '',
    '这是逐题工作队列，不是已审题或 AC 清单。参数为上游原始元数据，完整输入条件仍需阅读题面和 verifier。候选驱动只按显式题目 URL 或精确文件名关联；其他 OJ 的同源题 AC 不冒充 Library Checker 在线 AC。', '',
    '| 分类 | 总数 | 纳入 |', '| --- | ---: | ---: |']
for name in list(dict.fromkeys(r['category'] for r in rows)):
    subset=[r for r in rows if r['category']==name]
    text.append(f"| {name} | {len(subset)} | {sum(r['scope']=='included' for r in subset)} |")
text += ['', '| 题目 | 分类 | 状态 | 候选驱动 |', '| --- | --- | --- | --- |']
for r in rows:
    status='排除：官方 Sample' if r['scope']=='excluded_sample' else '待逐题审题、适配与在线验证'
    if r['online_ac']:status='已有本库 Library Checker AC，接口范围仍须核对'
    if not r['listed_in_categories']:status+='；尚未列入分类'
    drivers='<br>'.join(f'[{Path(p).name}](../{p})' for p in r['candidate_drivers']) or '—'
    text.append(f"| [{r['title']}]({r['url']}) | {r['category']} | {status} | {drivers} |")
text += ['', '机器清单： [library-checker-inventory.json](library-checker-inventory.json)，包含参数、测试生成数量、题面/校验器摘要及固定版本链接。', '',
    '重建：`python3 tools/library_checker_inventory.py /path/to/clean/library-checker-problems`。更换上游版本时需审查增删；本工具不删除现有模板，也不自动迁移历史评测证据。']
(root/'docs/LIBRARY-CHECKER.md').write_text('\n'.join(text)+'\n')
print(json.dumps(report['counts']))
