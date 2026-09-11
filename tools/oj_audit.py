#!/usr/bin/env python3
"""Compare current bundled drivers with archived accepted submissions.
A formatting-normalized check is only a scoped source comparison, not a new AC.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
formatter = os.environ.get('CLANG_FORMAT', 'clang-format')
rows = json.loads((root / 'verification/oj.json').read_text())
report = []

def digest(data):
    return hashlib.sha256(data).hexdigest()

def normalize(text):
    result = subprocess.run([formatter, '--style=LLVM'], input=text, text=True,
                            capture_output=True, check=True).stdout
    return '\n'.join(line for line in result.splitlines() if line.strip())

def component(text, name):
    match = re.search(r'(?:template[^\n]*\n)?(?:template[^\n]* )?struct '
                      + re.escape(name) + r'\b.*?^};', text, re.S | re.M)
    if not match:
        raise ValueError('Missing tested component: ' + name)
    return match[0]

for row in rows:
    archived = (root / row['submitted_source']).read_bytes()
    if digest(archived) != row['submitted_sha256']:
        raise ValueError('Archive hash mismatch: ' + row['submitted_source'])
    with tempfile.NamedTemporaryFile(suffix='.cpp') as tmp:
        subprocess.run(['python3', str(root / 'tools/bundle.py'),
                        str(root / row['source_driver']), tmp.name], check=True)
        current = Path(tmp.name).read_bytes()
    entry = dict(problem=row['problem'], style=row['style'], record=row['record'],
                 current_sha256=digest(current), submitted_sha256=digest(archived),
                 exact_bundle_match=current == archived)
    if current != archived and row['problem'] == 'Luogu P3376':
        name = 'Dinic' if row['style'] == 'compact' else 'Network_Flow'
        old = archived.decode()
        new = current.decode()
        entry['compared_component'] = name
        entry['component_matches_after_formatting'] = (
            normalize(component(old, name)) == normalize(component(new, name)))
        # These two archived drivers follow the final top-level class definition.
        entry['driver_tail_matches_after_formatting'] = (
            normalize(old[old.rfind('\n};') + 3:]) ==
            normalize(new[new.rfind('\n};') + 3:]))
        entry['note'] = ('Current bundle additionally includes unused circulation '
                         'code; its correctness is not established by P3376 AC.')
    report.append(entry)
(root / 'verification/oj-source-audit.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('Audited', len(report), 'accepted snapshots; inspect scoped mismatches in report')
