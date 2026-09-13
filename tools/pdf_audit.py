#!/usr/bin/env python3
"""Check final-pass warnings and contiguous Arabic page destinations."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
reports = []
for key in ['template', 'strings', 'mathematics', 'data-structures', 'graphs', 'geometry', 'misc', 'infra']:
    path = root / ('output/pdf/infra.pdf' if key == 'infra' else f'output/pdf/xcpc-{key}.pdf')
    name = 'main' if key == 'template' else ('infra' if key == 'infra' else f'volume-{key}')
    log = (root / f'build/pdf/{name}.log').read_text()
    warnings = [s for s in log.splitlines() if any(w in s for w in ['Warning', 'Overfull', 'Underfull', 'Missing character'])]
    assert not warnings, (name, warnings)
    index = (root / f'build/pdf/{name}.ind').read_text()
    assert r'\item' in index, (name, 'Missing or empty algorithm index')
    dest = subprocess.check_output(['pdfinfo', '-dests', str(path)], text=True)
    rows = [(int(a), int(b)) for a, b in re.findall(r'^\s*(\d+) .*"page\.(\d+)"$', dest, re.M)]
    assert rows, name
    offset = rows[0][0] - 1
    assert all(a == b + offset for a, b in rows), name
    assert sorted(b for a, b in rows) == list(range(1, len(rows) + 1)), name
    reports.append(dict(file=str(path.relative_to(root)), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), main_pages=len(rows), offset=offset, warnings=warnings))
(root / 'verification/pdf-volumes.json').write_text(json.dumps(reports, indent=2) + '\n')
r = reports[0]
(root / 'verification/pdf-page-anchors.txt').write_text(
    f"PDF SHA256: {r['sha256']}\n{r['main_pages']} Arabic page anchors form a contiguous sequence and map to physical page n+{r['offset']}.\npage.1 points to physical page {r['offset'] + 1}, not the title page.\n")
print('PASS: eight PDFs, final logs without warnings; Arabic page destinations contiguous')
