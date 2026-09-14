#!/usr/bin/env python3
"""Record every heading in the user attachment; titles alone never prove coverage."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('pdf', type=Path)
args = ap.parse_args()
path = root / 'docs/issue11-inventory.json'
prior = json.loads(path.read_text()) if path.exists() else {}
sha = hashlib.sha256(args.pdf.read_bytes()).hexdigest()
if prior:
    assert sha == prior['pdf_sha256'], 'Attachment changed; review before replacing scope'
text = subprocess.check_output(['pdftotext', '-layout', str(args.pdf), '-'], text=True)
pages = text.split('\f')
if not pages[-1].strip():
    pages.pop()
old = {r['section']: r for r in prior.get('entries', [])}
norm = lambda s: re.sub(r'\s+', '', s)
rows = []
for page in pages[:3]:
    for line in page.splitlines():
        m = re.match(r'^\s*(\d+(?:\.\d+)*)\s+(.+?)\s+(\d+)\s*$', line)
        if not m:
            continue
        section, title, number = m.groups()
        title = re.sub(r'(?:\s*\.\s*){2,}$', '', title).strip()
        target = norm(section + title)
        hits = [i for i, body in enumerate(pages[3:], 4)
                if any(norm(s).startswith(target) for s in body.splitlines())]
        assert hits, (section, title)
        row = dict(section=section, title=title, toc_page=int(number),
                   physical_page=hits[0], level=section.count('.'),
                   status='pending_content_review', candidate_symbols=[])
        for key in ['status', 'candidate_symbols', 'review']:
            if key in old.get(section, {}):
                row[key] = old[section][key]
        rows.append(row)
assert len(rows) == 88 and sum(r['level'] == 1 for r in rows) == 55
assert len({r['section'] for r in rows}) == len(rows)
data = dict(issue='https://github.com/gsh20040816/CPCtemplate/issues/11',
            url='https://github.com/user-attachments/files/32176902/default.pdf',
            pdf_sha256=sha, pdf_bytes=args.pdf.stat().st_size, pdf_pages=len(pages),
            scope_note='All 88 chapter/topic/variant headings retained, including 55 main topics. Physical start pages matched against body headings, not copied from stale TOC numbers. No coverage is inferred from titles.',
            entries=rows)
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
lines = ['# Issue 11 附件核对清单', '',
         f'附件共 {len(pages)} 页、55 个主要主题，连同章节和变体共 88 个目录项。PDF SHA-256：`{sha}`。', '',
         '目录页码与实际 PDF 页码分别保留；正文标题已用于定位起始页。标题相同只产生候选，不等于实现或验证完成。', '',
         '| 节号 | 标题 | 原目录页 | PDF 实际页 | 状态 |', '|---|---|---:|---:|---|']
for r in rows:
    lines.append(f"| {r['section']} | {r['title']} | {r['toc_page']} | {r['physical_page']} | {r['status']} |")
lines += ['', '来源为 issue #11 用户提供附件；完整 PDF 留在本地 build 中，仓库仅登记来源、摘要与覆盖状态。',
          '三元环、左偏树、Johnson 已独立实现并本地验证，在线待补；其余目录按上表状态继续核对，不排除任何主题或变体。']
(root / 'docs/ISSUE-11.md').write_text('\n'.join(lines) + '\n')
print('Issue 11:', len(rows), 'headings, 55 primary topics,', len(pages), 'PDF pages')
