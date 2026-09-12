#!/usr/bin/env python3
"""Render reviewed mappings; candidate inventory remains separate."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'docs/template-problem-reviews.json').read_text())
lines=['# 已核对的模板题入口','',
'本表仅收录已经阅读题面与适配约定的映射。AC、接口覆盖与速度榜分别记录；空白项不表示完成。完整候选和上游缺项见 [候选清单](template-problems.json)，执行依据为 [issue #1](ISSUE-1.md)。','',
'| 算法 | 模板题 | 边界 | 当前 AC | 速度榜 |','|---|---|---|---|---|']
for r in rows:
    rank=r['ranking'];txt='待核验'
    if rank.get('rank') is not None:txt=f"{rank['rank']} out of {rank['total']}（{rank.get('scope','')}）"
    ac=f"[记录]({r['ac']})" if r.get('ac') else '待提交'
    bound=r['limits'].replace('|','\\|')
    lines.append(f"| `{r['symbol']}` | [{r['problem']}]({r['url']}) | {bound} | {ac} | {txt} |")
lines+=['','## 适配与证据范围','']
for r in rows:
    lines += [f"### {r['problem']} / {r['symbol']}",'',r['classification'],'',r.get('adapter',''),'',r['remaining'],'']
lines+=['## 榜单口径','',
'QOJ statistics 的“最快”表会合并同一用户的提交，不能把榜单行号配上全体满分提交数。已核对同一用户三条 AC 的反例，详见 ranking-audits.json。用户要求的所有提交速度排名需另行枚举或找到可靠筛选接口；没有核验前保持待查。读取时间、相邻排名与并列用时范围必须随排名一起保存。','']
(root/'docs/TEMPLATE-PROBLEMS.md').write_text('\n'.join(lines))
