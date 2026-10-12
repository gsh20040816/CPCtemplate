#!/usr/bin/env python3
"""Reconcile archived public AX rows with counts; never infer missing records."""
from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parents[1]
report = []
for pid in ('4656', '4742'):
    base = root / 'verification' / ('hdu' + pid)
    evidence = base.with_name(base.name + '-all-ac-pages.txt')
    data_path = base.with_name(base.name + '-all-ac.json')
    data = json.loads(data_path.read_text())
    rows = []
    pages = evidence.read_text().split('\n\nPAGE\n\n')
    for page in pages:
        assert 'Description: Realtime Status' in page
        for block in re.split(r'\n\s*\d+ row\n', page):
            if '文本 Accepted' not in block or 'showproblem.php?pid=' + pid not in block:
                continue
            def match(pattern):
                result = re.search(pattern, block)
                assert result, pattern
                return result[1]
            rows.append(dict(run_id=int(match(r'文本 (\d{5,})\n')),
                date=match(r'文本 (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)'),
                time_ms=int(match(r'文本 (\d+)MS')),
                memory_k=int(match(r'文本 (\d+)K')),
                bytes=int(match(r'(?:文本|link) (\d+)\s*B')),
                language=match(r'文本 (G\+\+|C\+\+|GCC|Java|C|Pascal)\n'),
                user=match(r'link ([^\n]+), Value: acm.hdu.edu.cn/userstatus')))
    assert rows == data['rows']
    assert len(pages) == data['pages']
    assert len(rows) == len({r['run_id'] for r in rows}) == data['visible_unique_records']
    assert all(a['run_id'] > b['run_id'] for a, b in zip(rows, rows[1:]))
    times = [r['time_ms'] for r in rows]
    assert sum(t < data['current_time_ms'] for t in times) + 1 == data['rank_in_visible_records']
    assert times.count(data['current_time_ms']) == data['ties']
    ordered = sorted(rows, key=lambda r: (r['time_ms'], r['run_id']))
    assert ordered[0] == data['fastest_visible']
    assert data['visible_percentile_index'] == len(rows) // 100
    assert ordered[len(rows) // 100 - 1] == data['visible_percentile_record']
    hashes = {}
    for suffix in ('-best-before-ax.txt', '-best-after-ax.txt'):
        path = base.with_name(base.name + suffix)
        text = path.read_text()
        found = re.search(r'文本 Accepted\n[\s\S]*?link (\d+), Value: acm.hdu.edu.cn/status.php\?pid=' + pid + '&status=5', text)
        assert found and int(found[1]) == data['official_accepted_count']
        hashes[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert data['all_accepted_verified'] == (len(rows) == data['official_accepted_count'])
    assert data['official_accepted_count'] - len(rows) == (0 if pid == '4656' else 4)
    hashes[str(evidence.relative_to(root))] = hashlib.sha256(evidence.read_bytes()).hexdigest()
    hashes[str(data_path.relative_to(root))] = hashlib.sha256(data_path.read_bytes()).hexdigest()
    report.append(dict(problem=pid, pages=len(pages), unique_rows=len(rows), missing=data['official_accepted_count']-len(rows), sha256=hashes))
    print(pid, 'archived rows/count/rank PASS; complete:', data['all_accepted_verified'])
(root / 'verification/hdu-ranking-evidence.json').write_text(json.dumps(report, indent=2) + '\n')
