# Morning Flower and Evening Oath — XCPC Template

同济大学队伍 **Morning Flower and Evening Oath** 的个性化模板库。

**建设中，尚未达到完整覆盖或全部 OJ 验证要求。** 不把参考目录、原版代码、仅编译通过的模板标记为已完成。

## 范围

1. kuangbin 2018 ACM 模板的完整目录。
2. WIDA XCPC 在线模板、打印稿及补充模板。
3. 2023–2025 中国 ICPC/CCPC 赛题使用的缺项，追加已公开的 2026 场次。
4. OI Wiki 有价值的数学：数论、组合、代数、多项式、概率与数值算法。

目标是贴近队伍码风、封装后易抄写、覆盖赛事常用算法。每个算法只保留有独立价值的一份实现，简单算法并入所属家族的头文件，单题解法不作为模板收录；删减原则见 [编写优先级](docs/PRIORITIES.md)，删除与替代关系见 [issue #21 记录](docs/ISSUE-21.md) 与 [issue21-removed.json](docs/issue21-removed.json)。

完整来源条目见 [coverage.csv](docs/coverage.csv)，来源见 [SOURCES.md](docs/SOURCES.md)，中国赛站的逐题需求与缺口见 [赛题审计](docs/CONTESTS.md)。原始目录中的重复实现与旧版本须逐项注明替代关系，不能静默遗漏。

## 码风

- `src/compact/`：基于队伍实际提交，`vector`、小写短名、清晰分行；目录名不表示压缩代码。
- 不为统一接口添加代理层；简单条目以函数或轻量 struct 写在家族头文件中。

[码风证据](docs/STYLE.md)。共享队号不能直接推断每份代码的个人作者。

## 验证

按队内要求停用 GitHub 自动 CI；验证脚本保留供本地按需运行。

```sh
python3 tools/book.py
python3 tools/volumes.py
tools/test.sh
SANITIZE=1 tools/test.sh
```

前两步生成文档集成检查所需的分册 TeX，不需要安装 LaTeX；新克隆后也要执行。
需要 GCC、C++20、Boost（独立精确几何参考）及 Python mpmath（高精度数值参考）。每份可提交代码与测试及打印代码同源。

- [OJ 记录与实际受测接口](verification/oj.json)：保留原始提交源码和 SHA256，不把同文件未调用模块算作通过评测；已删除模板的记录在 [源码对照](verification/oj-source-audit.json) 中标为 retired。
- [待评测队列](verification/pending-oj.md)：尚未提交、网站错误与未完成验证的接口。
- 使用示例：每个模板最多印一份模板题用法；应用题与接口演示驱动只作为本地测试，见 [使用示例覆盖表](docs/USAGE-COVERAGE.md)。

## 构建

运行 `tools/build_pdf.sh`（需要 XeLaTeX、latexmk），生成 `output/pdf/` 下的总册、六本分册（字符串、数学、数据结构、图论、计算几何、杂项）与 Infra 册，见 [分册说明](docs/VOLUMES.md)。

当前有 103 个分类知识节（数学 71、图论 16、计算几何 1、数据结构 9、杂项 3、字符串 3），按固定 OI Wiki 导航纳入总册和所属分册，映射见 [知识分类](docs/KNOWLEDGE-TAXONOMY.md)；不把这些节数当作完整知识体系的覆盖比例。PDF 中的知识节只保留公式、适用条件和复杂度；推导、反例与验证范围见 [知识节完整说明](docs/KNOWLEDGE-DETAILS.md)，由 `python3 tools/knowledge_markdown.py` 从 `docs/knowledge-full/` 生成。
