#!/usr/bin/env python3
"""Generate cross-book references for the competition/tools/language handbook."""
import json
from pathlib import Path
from taxonomy_layout import escape
root=Path(__file__).resolve().parents[1]
volumes=json.loads((root/'docs/volumes.json').read_text())
owner={s:v for v in volumes for s in v['entries']}
links=[('PBDS 配对堆：修改、合并与句柄','pheap'),('PBDS 有序树：排名与第 k 小','ost'),('GNU rope：序列与版本共享','rp'),('gp/cc 哈希表：整数键映射','gp_map'),('优先队列的最短路应用','Dijkstra'),('vector 与下标：树状数组','Fenwick'),('扩容与下标：可持久化数组','PersistentArray'),('比较次序：后缀数组','SuffixArray'),('数值精度约定：浮点几何','RealPlane'),('移动大数组：NTT 卷积','NttConvolution')]
intro=[r'\input{preamble.tex}']
for v in volumes:
 intro.append(r'\externaldocument[ext-'+v['id']+'-]{../build/pdf/volume-'+v['id']+'}[xcpc-'+v['id']+'.pdf]')
intro += [r'\begin{document}',r'\raggedbottom',r'\hypersetup{pageanchor=false}',r'\begin{titlepage}\centering\vspace*{35mm}',r'{\Huge\bfseries Infra\par}\vspace{15mm}',r'{\LARGE Morning Flower and Evening Oath\par}\vspace{15mm}',r'{\Large 比赛相关、工具软件、语言基础\par}\vfill',r'本册按 C++20 和当前模板使用方式整理；GNU 扩展与标准库明确区分。',r'\end{titlepage}\hypersetup{pageanchor=true}',r'\frontmatter\tableofcontents',r'\mainmatter',r'\input{infra-body.tex}',r'\chapter{分册跳转索引}\label{infra-links}',r'请将本册与其他 PDF 放在同一目录。下表页码是分册印刷页码；链接直接指向条目，部分浏览器内置 PDF 阅读器可能不支持跨文件跳转。',r'\begin{longtable}{p{80mm}p{65mm}}\toprule 内容 & 所属分册及页码\\\midrule\endhead']
records=[]
for title,symbol in links:
 v=owner[symbol];label='ext-'+v['id']+'-compact-'+symbol
 intro.append(escape(title)+' & '+escape(v['title'])+r'，第~\pageref{'+label+r'}~页\\')
 records.append(dict(symbol=symbol,volume=v['id'],file='xcpc-'+v['id']+'.pdf',label=label))
intro += [r'\bottomrule\end{longtable}',r'\backmatter\printindex',r'\end{document}']
(root/'docs/infra.tex').write_text('\n\n'.join(intro)+'\n')
(root/'docs/infra-links.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print('Infra generated with',len(records),'cross-book entries')
