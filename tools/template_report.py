#!/usr/bin/env python3
"""Render reviewed mappings; candidate inventory remains separate."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def ac_status(row, root):
    if row.get('ac'):
        return f"[记录]({row['ac']})"
    if row.get('implementation') in ['missing', 'planned_extension']:
        return '待实现'
    if row.get('driver') and (root / row['driver']).is_file():
        return '待在线 AC'
    # Missing registration is not evidence that no implementation was written.
    return '驱动登记待核验；AC 待核验'


def source_links(sources):
    entries = sources.values() if isinstance(sources, dict) else sources
    urls = [entry['url'] if isinstance(entry, dict) else entry for entry in entries]
    if not all(isinstance(url, str) and url.startswith(('https://', 'http://')) for url in urls):
        raise ValueError('Statement references must provide actual HTTP(S) URLs')
    return '，'.join(f'[来源 {i+1}]({url})' for i, url in enumerate(urls))


def render(rows, root=ROOT):
    lines = ['# 已核对的模板题入口', '',
             '本表记录已核对的题面或来源模型与适配约定；原题面不可访问的记录明确标注，不能视为题面核验完成。AC、接口覆盖与速度榜分别记录；历史 AC 不自动证明当前源码或未受测接口，空白项不表示完成。完整候选和上游缺项见 [候选清单](template-problems.json)，执行依据为 [issue #1](ISSUE-1.md)。', '',
             '| 算法 | 模板题 | 边界 | 已登记 AC | 速度榜 |', '|---|---|---|---|---|']
    for row in rows:
        rank = row['ranking']; text = '待核验'
        if rank.get('rank') is not None:
            text = f"{rank['rank']} out of {rank['total']}（{rank.get('scope','')}）"
        bound = row['limits'].replace('|', '\\|')
        name = row['symbol']
        if row.get('api') and '::' not in row['api']:
            name += '::' + row['api']
        lines.append(f"| `{name}` | [{row['problem']}]({row['url']}) | {bound} | {ac_status(row, root)} | {text} |")
    lines += ['', '## 适配与证据范围', '']
    for row in rows:
        lines += [f"### {row['problem']} / {row['symbol']}", '', row['classification'], '',
                  row.get('adapter', ''), '', row['remaining'], '']
        if row.get('statement_sources'):
            lines += ['原始题面与参数：' + source_links(row['statement_sources']), '']
    lines += ['## 榜单口径', '',
              'QOJ statistics 的“最快”表会合并同一用户的提交，不能把榜单行号配上全体满分提交数。已核对同一用户三条 AC 的反例，详见 ranking-audits.json。用户要求的所有提交速度排名需另行枚举或找到可靠筛选接口；没有核验前保持待查。读取时间、相邻排名与并列用时范围必须随排名一起保存。', '']
    return '\n'.join(lines)


def main():
    rows = json.loads((ROOT / 'docs/template-problem-reviews.json').read_text())
    (ROOT / 'docs/TEMPLATE-PROBLEMS.md').write_text(render(rows))


if __name__ == '__main__':
    main()
