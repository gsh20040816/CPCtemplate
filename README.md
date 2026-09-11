# Morning Flower and Evening Oath — XCPC Template

同济大学队伍 **Morning Flower and Evening Oath** 的个性化模板库。

**建设中，尚未达到完整覆盖或全部 OJ 验证要求。** 不把参考目录、原版代码、仅编译通过的模板标记为已完成。

后续按[编写优先级](docs/PRIORITIES.md)补齐高频且易错的模板，以平衡树、Tarjan 等为难度参照；已完成高级模板保留。

## 范围

1. kuangbin 2018 ACM 模板的完整目录。
2. WIDA XCPC 在线模板、打印稿及补充模板。
3. 2023–2025 中国 ICPC/CCPC 赛题使用的缺项，追加已公开的 2026 场次。
4. OI Wiki 有价值的数学：数论、组合、代数、多项式、概率与数值算法。

完整来源条目见 [coverage.csv](docs/coverage.csv)，来源见 [SOURCES.md](docs/SOURCES.md)。原始目录中的重复实现与旧版本须逐项注明替代关系，不能静默遗漏。

## 两套码风

- `src/compact/`：基于队伍实际提交，`vector`、小写短名、清晰分行；目录名不表示压缩代码。
- `src/classic/`：静态容量、分列头文件、`Init`/`Insert`/`Query`、疏空格。两套分别实现和验证。

[码风证据](docs/STYLE.md)。共享队号不能直接推断每份代码的个人作者。

## 验证

```sh
tools/test.sh
SANITIZE=1 tools/test.sh
```

需要 GCC、C++20 和 Boost（只用于测试中的独立精确几何参考）。每份可提交代码必须与测试及打印代码同源。OJ 证据见 [oj.json](verification/oj.json)：两套最大流和动态树分别已在洛谷 P3376、P3690 获得 100 分 AC；动态版有序 Treap、递归点双分别已在 P3369、P8435 获得 100 分 AC；其余模块不声称 OJ 已通过。

当前实现仅是首批核心模块；覆盖表的 `pending` 表示尚未完成对应项的完整迁移和验证。

## LaTeX

运行 `tools/build_pdf.sh`（需要 XeLaTeX、latexmk）。[当前 PDF](output/pdf/xcpc-template.pdf) 含双风格源码、目录、接口索引与数学速查；为建设稿。

所有模板以赛时快速抄写为先：一行一条语句，展开函数体，按算法需要选择函数或轻量 struct。见 [码风规范](docs/STYLE.md)。
