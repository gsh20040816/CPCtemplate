#!/usr/bin/env python3
"""Inventory archived submissions without conflating timing scopes or benchmark ranks."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIMING = ('time_ms', 'time_display', 'total_time_ms', 'max_case_time_ms',
          'max_case_time_display', 'displayed_total_time', 'test_times_ms', 'test_ms')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def observations(root):
    paths = [root / 'verification/oj.json', *sorted((root / 'verification').glob('*-online.json'))]
    for path in paths:
        data = json.loads(path.read_text())
        if isinstance(data, list):
            rows = data
        elif isinstance(data.get('record'), dict):
            row = dict(data['record'])
            for key in TIMING:
                if key in data:
                    row[key] = data[key]
            if 'testpoints' in data:
                row['test_times_ms'] = [p['time_ms'] for p in data['testpoints']]
            rows = [row]
        elif isinstance(data.get('record'), str) and data.get('problem'):
            rows = [data]
        else:
            raise ValueError(f'Unsupported online evidence schema: {path}')
        for row in rows:
            yield path, row


def build(root):
    entries = {}
    inputs = {}
    for path, row in observations(root):
        rel = str(path.relative_to(root))
        inputs[rel] = digest(path)
        url = row.get('record')
        archive = row.get('submitted_source', row.get('source'))
        sha = row.get('submitted_sha256', row.get('sha256'))
        if archive:
            if not sha or digest(root / archive) != sha:
                raise ValueError(f'Archive hash mismatch: {archive}')
        key = url or ('no-record:' + str(archive))
        entry = entries.setdefault(key, dict(record=url, problem=row['problem'],
            sources=[], observations=[], statuses=[], styles=[], algorithms=[],
            maximum_case_ms=None, sum_of_case_ms=None, reported_total_ms=None,
            benchmark_status='not_checked', benchmark=None, ratio=None))
        if archive:
            source = dict(path=archive, sha256=sha)
            if source not in entry['sources']:
                entry['sources'].append(source)
        for target, value in [('statuses', row.get('verdict', row.get('status'))),
                              ('styles', row.get('style')), ('algorithms', row.get('algorithm'))]:
            if value and value not in entry[target]:
                entry[target].append(value)
        values = {k: row[k] for k in TIMING if k in row}
        entry['observations'].append(dict(evidence=rel, timing=values,
            language=row.get('language'), note=row.get('note', row.get('scope', ''))))
        cases = row.get('test_times_ms', row.get('test_ms'))
        if cases is not None:
            assert cases and all(isinstance(t, (int, float)) and t >= 0 for t in cases)
        if cases and row.get('max_case_time_ms') is not None and max(cases) != row['max_case_time_ms']:
            raise ValueError(f'Conflicting maximum_case_ms within observation: {key}')
        metrics = {'maximum_case_ms': max(cases) if cases else row.get('max_case_time_ms'),
                   'sum_of_case_ms': sum(cases) if cases else None,
                   'reported_total_ms': row.get('total_time_ms')}
        for metric, value in metrics.items():
            if value is None:
                continue
            old = entry[metric]
            if old is not None and old != value:
                raise ValueError(f'Conflicting {metric}: {key}: {old}, {value}')
            entry[metric] = value
    review_path = root / 'docs/template-problem-reviews.json'
    inputs[str(review_path.relative_to(root))] = digest(review_path)
    for review in json.loads(review_path.read_text()):
        if review.get('ac') and review['ac'] not in entries:
            raise ValueError('Reviewed AC missing archived runtime observation: ' + review['ac'])
    # Multiple historical observations are retained; a pending state never turns into AC here.
    rows = sorted(entries.values(), key=lambda r: (r['problem'], r['record'] or ''))
    return dict(scope='Archived central ledger plus batch online receipts, cross-checked against reviewed AC URLs. Not a crawl of complete account history or proof of benchmark completion.',
                inputs_sha256=inputs, entries=rows,
                counts=dict(entries=len(rows), with_record=sum(bool(r['record']) for r in rows),
                    accepted=sum('Accepted' in r['statuses'] for r in rows),
                    known_case_max=sum(r['maximum_case_ms'] is not None for r in rows),
                    benchmarks_verified=0))


def render(data):
    lines = ['# 已归档提交的运行时间', '',
             '对应 [issue #16](https://github.com/gsh20040816/CPCtemplate/issues/16)。本表合并中央登记与批次线上回执，并逐项绑定提交源码哈希；覆盖已归档记录，不声称已遍历整个账号的所有历史提交。退役 classic 只作为历史记录保留，不重新维护第二套码风。', '',
             '旧 `time_ms` 字段的含义不一致，原样列入“原始登记”，不能直接与单点或总计比较。只有逐测试点列表或明确字段支持的值才进入相应列；显示为秒的舍入总时长不转换为精确毫秒。等待评测和拒绝提交不算 AC。', '',
             '已审查的候选及差距见 [P4980 核查](RUNTIME-P4980.md)。候选未满足排名覆盖核验条件，仍不计入正式 SOTA。', '',
             '基准全部待核验：需记录同题、语言/优化、计时口径、测评时间、全体通过提交数量与所选名次，并检查基准源码；排除打表等取巧提交。若改用同算法基准，须说明原因。按用户去重的最快榜不是全体通过提交排名。基准未知时不计算倍数，也不据此宣布性能达标。', '',
             f"当前 {data['counts']['entries']} 项，{data['counts']['accepted']} 条 AC；{data['counts']['known_case_max']} 项有明确最慢单点，0 项已完成 SOTA 核验。", '',
             '| 题目/记录 | 状态、码风 | 原始登记 | 最慢单点 ms | 逐点合计 ms | 明确登记总计 ms | SOTA |',
             '|---|---|---|---:|---:|---:|---|']
    show = lambda v: '—' if v is None else str(v)
    for row in data['entries']:
        raw = []
        for obs in row['observations']:
            for key in ('time_ms', 'time_display', 'displayed_total_time', 'max_case_time_display'):
                if key in obs['timing']:
                    value = f'{key}={obs["timing"][key]}'
                    if value not in raw:
                        raw.append(value)
        name = f"[{row['problem']}]({row['record']})" if row['record'] else row['problem'] + '（无记录）'
        state = ', '.join(row['statuses'] + row['styles'])
        lines.append('| ' + ' | '.join([name, state, '; '.join(raw) or '—',
            show(row['maximum_case_ms']), show(row['sum_of_case_ms']), show(row['reported_total_ms']), '待核验']) + ' |')
    lines += ['', '逐条证据路径、源码哈希、编译语言与原始计时字段见 [机器可读清单](../verification/online-runtimes.json)。本表可由 `python3 tools/online_runtimes.py` 重建。', '']
    return '\n'.join(lines)


def main():
    result = build(ROOT)
    (ROOT / 'verification/online-runtimes.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    (ROOT / 'docs/ONLINE-RUNTIMES.md').write_text(render(result))
    print(result['counts'])


if __name__ == '__main__':
    main()
