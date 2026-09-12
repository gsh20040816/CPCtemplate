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
    if row['style'] == 'classic':
        report.append(dict(problem=row['problem'], style=row['style'], record=row['record'],
                           submitted_sha256=digest(archived), retired=True,
                           scope_note='Historical AC archive only; static style retired from the current library.'))
        continue
    with tempfile.NamedTemporaryFile(suffix='.cpp') as tmp:
        subprocess.run(['python3', str(root / 'tools/bundle.py'),
                        str(root / row['source_driver']), tmp.name], check=True)
        current = Path(tmp.name).read_bytes()
    entry = dict(problem=row['problem'], style=row['style'], record=row['record'],
                 current_sha256=digest(current), submitted_sha256=digest(archived),
                 exact_bundle_match=current == archived)
    entry['format_only_bundle_match'] = current != archived and normalize(current.decode()) == normalize(archived.decode())
    name = None
    note = None
    if row['problem'] == 'Luogu P3376':
        name = 'Dinic' if row['style'] == 'compact' else 'Network_Flow'
        note = 'Current bundle includes unused circulation code, not verified by P3376.'
    elif row['problem'] == 'Luogu P3369' and row.get('algorithm') == 'OrderedTreap':
        name = 'OrderedTreap' if row['style'] == 'compact' else 'Ordered_Treap'
        note = 'Sequence Treap shares this header but is not called by the P3369 driver.'
    if current != archived and name is not None:
        old = archived.decode()
        new = current.decode()
        entry['compared_component'] = name
        entry['component_matches_after_formatting'] = (
            normalize(component(old, name)) == normalize(component(new, name)))
        # These known drivers follow the final top-level class definition.
        entry['driver_tail_matches_after_formatting'] = (
            normalize(old[old.rfind('\n};') + 3:]) ==
            normalize(new[new.rfind('\n};') + 3:]))
        entry['note'] = note
    if current != archived and row['problem'] in {'Luogu P1495', 'Luogu P4777', 'Luogu P6091', 'Luogu P4195'}:
        # These reviewed drivers do not instantiate the factorial-table class.
        unused = 'Binomial' if row['style'] == 'compact' else 'Combination'
        old = archived.decode()
        new = current.decode()
        old_rest = old.replace(component(old, unused), '', 1)
        new_rest = new.replace(component(new, unused), '', 1)
        entry['excluded_unused_component'] = unused
        entry['remaining_bundle_matches_after_formatting'] = normalize(old_rest) == normalize(new_rest)
        entry['scope_note'] = 'Only the uninstantiated factorial table is excluded; this does not validate its new APIs or confer a new AC.'
    if current != archived and row['problem'] == 'Luogu P5395':
        name = 'stirling_first_row' if row['style'] == 'compact' else 'Stirling_First_Row'
        pattern = r'// BEGIN ' + name + r'.*?// END ' + name
        old = re.sub(pattern, '', archived.decode(), flags=re.S)
        new = re.sub(pattern, '', current.decode(), flags=re.S)
        entry['excluded_unused_component'] = name
        entry['remaining_bundle_matches_after_formatting'] = normalize(old) == normalize(new)
        entry['scope_note'] = 'P5395 calls second-kind rows only; changing the unused first-kind function does not invalidate the unchanged tested API or validate the new first-kind implementation.'
    report.append(entry)
(root / 'verification/oj-source-audit.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('Audited', len(report), 'accepted snapshots; inspect scoped mismatches in report')

# Keep the actionable queue in sync while preserving historical UI notes below it.
pending_path = root / 'verification/pending-oj.md'
heading = '## 已解决的提交异常'
pending_text = pending_path.read_text()
if heading not in pending_text:
    raise ValueError('Missing pending queue history heading')
history = heading + pending_text.split(heading, 1)[1]
accepted_drivers = {row['source_driver'] for row in rows if row['verdict'] == 'Accepted'}
drivers = sorted(str(p.relative_to(root)) for p in (root / 'verify').rglob('*.cpp'))
queue = [p for p in drivers if p not in accepted_drivers]
pending_path.write_text(
    '# 待在线评测\n\n'
    '以下提交驱动尚无本库的新 AC 记录；列表由当前 verify/ 与 oj.json 对照生成。\n\n'
    + ''.join(f'- `{p}`\n' for p in queue) + '\n' + history)
