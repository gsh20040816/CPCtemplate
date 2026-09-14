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
        prefix, snippet = text[:m.start()], text[m.start():]
        assert all(not line.strip() or line.startswith('#include') or line.startswith('using namespace')
                   for line in prefix.splitlines()), 'Usage depends on non-include prefix: ' + row['id']
        assert '#include' not in snippet and not re.search(r'\bstruct\s+\w+\s*\{', snippet)
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
        verified = bool(matches) and all(proof.get(r['id'], {}).get('program_sha256') == r['program_sha256']
                    and proof[r['id']].get('modes') == ['normal', 'sanitizer'] for r in matches)
        coverage.append(dict(symbol=symbol, title=title, examples=[r['id'] for r in matches],
                             status='locally_checked_example' if verified else 'generated_unverified' if matches else 'pending_example'))
    (ROOT / 'docs/usage-coverage.json').write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + '\n')
    text = ['# 模板题使用示例覆盖', '',
            '每个条目需要最简题意、所需模板和使用代码；代码仅含 main 调用部分，不重复算法。',
            '示例与现有完整驱动共用源文件；模板依赖展开后的源码哈希改变时，原执行记录不再视为当前验证。示例执行通过不等于在线 AC。', '',
            '| 模板 | 示例 | 状态 |', '|---|---|---|']
    for row in coverage:
        text.append(f"| {row['symbol']} | {', '.join('[' + e + '](usage/' + e + '.cpp)' for e in row['examples']) or '待补'} | {row['status']} |")
    (ROOT / 'docs/USAGE-COVERAGE.md').write_text('\n'.join(text) + '\n')
    print('Usage:', sum(r['status'] == 'locally_checked_example' for r in coverage), '/', len(coverage), 'templates locally checked;', len(rows), 'examples')
    return rows

if __name__ == '__main__':
    generate()
