# Morning Flower and Evening Oath — XCPC Template

同济大学队伍 **Morning Flower and Evening Oath** 的个性化模板库。

**建设中，尚未达到完整覆盖或全部 OJ 验证要求。** 不把参考目录、原版代码、仅编译通过的模板标记为已完成。

后续按[编写优先级](docs/PRIORITIES.md)补齐高频且易错的模板，以平衡树、Tarjan 等为难度参照；已完成高级模板保留。

执行顺序见 [issue #1 计划](docs/ISSUE-1.md)，已审题入口见 [模板题表](docs/TEMPLATE-PROBLEMS.md)，完整候选见 [映射清单](docs/template-problems.json)。

## 范围

1. kuangbin 2018 ACM 模板的完整目录。
2. WIDA XCPC 在线模板、打印稿及补充模板。
3. 2023–2025 中国 ICPC/CCPC 赛题使用的缺项，追加已公开的 2026 场次。
4. OI Wiki 有价值的数学：数论、组合、代数、多项式、概率与数值算法。

完整来源条目见 [coverage.csv](docs/coverage.csv)，来源见 [SOURCES.md](docs/SOURCES.md)。中国赛站的逐题需求与缺口另见 [赛题审计](docs/CONTESTS.md)。原始目录中的重复实现与旧版本须逐项注明替代关系，不能静默遗漏。

## 码风

- `src/compact/`：基于队伍实际提交，`vector`、小写短名、清晰分行；目录名不表示压缩代码。

[码风证据](docs/STYLE.md)。共享队号不能直接推断每份代码的个人作者。

只保留 `src/compact/` 的 vector 实现。历史静态版已从当前源码与驱动中移除；历史 AC 快照仍保留原样。

## 验证

```sh
tools/test.sh
SANITIZE=1 tools/test.sh
```

需要 GCC、C++20 和 Boost（用于独立精确几何参考）。每份可提交代码与测试及打印代码同源。

- [OJ 记录与实际受测接口](verification/oj.json)：保留原始提交源码和 SHA256，不把同文件未调用模块算作通过评测。
- [当前源码与 AC 快照对照](verification/oj-source-audit.json)：完整文件相同或受测结构的排版归一化比对结果。
- [待评测队列](verification/pending-oj.md)：尚未提交、网站错误与未完成验证的接口。

覆盖表中的 `pending` 表示对应项尚未完成迁移和验证；当前仍未达到完整覆盖要求。

## LaTeX

运行 `tools/build_pdf.sh`（需要 XeLaTeX、latexmk）。[当前 PDF](output/pdf/xcpc-template.pdf) 含 vector 版源码、目录、接口索引与数学速查；为建设稿。

所有模板以赛时快速抄写为先：一行一条语句，展开函数体，按算法需要选择函数或轻量 struct。见 [码风规范](docs/STYLE.md)。
