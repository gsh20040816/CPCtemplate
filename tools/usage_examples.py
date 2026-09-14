#!/usr/bin/env python3
"""Generate usage-only listings and track coverage independently of algorithm AC."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def expand(text, base, seen):
    result = []
    for line in text.splitlines():
        m = re.fullmatch(r'\s*#include "([^"]+)"\s*', line)
        if m:
            path = (base / m[1]).resolve()
            assert path.is_relative_to(ROOT), path
            if path not in seen:
                seen.add(path)
                result.append(expand(path.read_text(), path.parent, seen))
        elif line.strip() != '#pragma once':
            result.append(line)
    return '\n'.join(result) + '\n'

def records():
    rows = json.loads((ROOT / 'docs/usage-examples.json').read_text())
    for row in rows:
        source = ROOT / row['driver']
        text = source.read_text()
        m = re.search(r'(?m)^int main\(\)', text)
        assert m, row
        start = m.start()
        if row.get('configuration_functions'):
            marker = '// BEGIN USAGE\n'
            assert text.count(marker) == 1
            start = text.index(marker) + len(marker)
            assert start < m.start()
            config = text[start:m.start()]
            names = re.findall(r'(?m)^\w+\s+(\w+)\([^;\n]*\)\s*\n\{', config)
            assert names == row['configuration_functions'], 'Configuration callback list changed'
        prefix, snippet = text[:start], text[start:]
        assert all(not line.strip() or line.startswith('#include') or line.startswith('using namespace') or line.lstrip().startswith('//')
                   for line in prefix.splitlines()), 'Usage depends on non-include prefix: ' + row['id']
        assert '#include' not in snippet
        # Explicitly registered local input records may contain fields, not methods.
        helpers = list(re.finditer(r'\bstruct\s+(\w+)\s*\{([^{}]*)\}\s*;', snippet))
        declared = re.findall(r'\bstruct\s+(\w+)\s*\{', snippet)
        assert declared == [h[1] for h in helpers] == row.get('helper_types', [])
        for helper in helpers:
            assert re.fullmatch(r'\s*(?:(?:char|int|long long)\s+\w+(?:\s*,\s*\w+)*\s*;\s*)+', helper[2]), 'Input records may only declare primitive fields'
        row['snippet'] = snippet
        row['snippet_file'] = 'docs/usage/' + row['id'] + '.cpp'
        row['program'] = '#include <bits/stdc++.h>\nusing namespace std;\n' + expand(prefix, source.parent, set()) + snippet
        row['program_sha256'] = hashlib.sha256(row['program'].encode()).hexdigest()
    return rows

def generate():
    rows = records()
    catalog = json.loads((ROOT / 'docs/catalog.json').read_text())
    symbols = {r[1] for r in catalog}
    assert len({r['id'] for r in rows}) == len(rows)
    assert all(r['symbol'] in symbols and set(r['requires']) <= symbols for r in rows)
    proof_path = ROOT / 'verification/usage-examples.json'
    proof = json.loads(proof_path.read_text()) if proof_path.exists() else {}
    for row in rows:
        path = ROOT / row['snippet_file']
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(row['snippet'])
    coverage = []
    for _, symbol, title, _ in catalog:
        matches = [r for r in rows if r['symbol'] == symbol]
        verified = any(r.get('kind', 'template') == 'template' for r in matches) and all(proof.get(r['id'], {}).get('program_sha256') == r['program_sha256']
                    and proof[r['id']].get('modes') == ['normal', 'sanitizer'] for r in matches)
        coverage.append(dict(symbol=symbol, title=title, examples=[r['id'] for r in matches],
                             status='locally_checked_example' if verified else 'generated_unverified' if matches else 'pending_example'))
    (ROOT / 'docs/usage-coverage.json').write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + '\n')
    text = ['# 模板题使用示例覆盖', '',
            '每个条目需要最简题意、所需模板和使用代码；代码只含必要配置与 main 调用部分，不重复算法。',
            '示例与现有完整驱动共用源文件；模板依赖展开后的源码哈希改变时，原执行记录不再视为当前验证。示例执行通过不等于在线 AC。', '',
            '| 模板 | 示例 | 状态 |', '|---|---|---|']
    kind_by_id = {r['id']: r.get('kind', 'template') for r in rows}
    for row in coverage:
        links = []
        for e in row['examples']:
            label = e + ('（应用补充）' if kind_by_id[e] == 'application' else '')
            links.append('[' + label + '](usage/' + e + '.cpp)')
        text.append(f"| {row['symbol']} | {', '.join(links) or '待补'} | {row['status']} |")
    (ROOT / 'docs/USAGE-COVERAGE.md').write_text('\n'.join(text) + '\n')
    print('Usage:', sum(r['status'] == 'locally_checked_example' for r in coverage), '/', len(coverage), 'templates locally checked;', len(rows), 'examples')
    return rows

if __name__ == '__main__':
    generate()
