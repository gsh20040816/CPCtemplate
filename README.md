# Morning Flower and Evening Oath — XCPC Template

同济大学队伍 **Morning Flower and Evening Oath** 的个性化模板库。

**建设中，尚未达到完整覆盖或全部 OJ 验证要求。** 不把参考目录、原版代码、仅编译通过的模板标记为已完成。

后续按[编写优先级](docs/PRIORITIES.md)补齐高频且易错的模板，以平衡树、Tarjan 等为难度参照；已完成高级模板保留。

执行顺序见 [issue #1 计划](docs/ISSUE-1.md)，码风与待确认移除名单见 [issue #2](docs/ISSUE-2.md)，ACL 结构与缺项见 [issue #3 对照](docs/ACL-REVIEW.md)；已审题入口见 [模板题表](docs/TEMPLATE-PROBLEMS.md)，完整候选见 [映射清单](docs/template-problems.json)。

## 范围

1. kuangbin 2018 ACM 模板的完整目录。
2. WIDA XCPC 在线模板、打印稿及补充模板。
3. 2023–2025 中国 ICPC/CCPC 赛题使用的缺项，追加已公开的 2026 场次。
4. OI Wiki 有价值的数学：数论、组合、代数、多项式、概率与数值算法。

完整来源条目见 [coverage.csv](docs/coverage.csv)，来源见 [SOURCES.md](docs/SOURCES.md)。中国赛站的逐题需求与缺口另见 [赛题审计](docs/CONTESTS.md)。原始目录中的重复实现与旧版本须逐项注明替代关系，不能静默遗漏。

数学配套知识补充见 [计数建模、生成函数、概率与博弈](docs/MATH-KNOWLEDGE-COMPLETION.md)：包含选型条件、推导、例子和误用反例，并与数学分册同源生成；知识补全不等同于新增算法或线上 AC。

任意点多项式求值的乘积树、重复点约定及独立验证见 [多点求值](docs/MULTIPOINT-EVALUATION.md)。互异点的快速系数插值见 [快速插值](docs/POLYNOMIAL-INTERPOLATION.md)，两者的重复点约定不同。

后续补充见 [整除反演与对称计数](docs/MATH-COUNTING-MODELS.md)：GCD 建模、整除分块、Burnside/Pólya、固定库存与非可逆群阶除法。

当前有 32 个分类知识节（数学 27、图论 4、计算几何 1），按固定 OI Wiki 导航纳入总册和所属分册；包括上述主题以及 LTE、Lagrange 反演、递推、容斥、类欧几里德、矩阵树、整数分拆、模运算条件、Catalan／投票反射建模、一次不定方程范围计数、数值积分、曼哈顿最小生成树证明、Pick格点计数、Prüfer树计数和Legendre／Kummer赋值判据。映射与尚未分类的旧附录范围见 [知识分类](docs/KNOWLEDGE-TAXONOMY.md)，不把这些节数当作完整知识体系的覆盖比例。

线性诱导排序后缀数组见 [SA-IS](docs/SAIS.md)，与既有倍增版并列，保留相同 sa/rk/lcp 下标约定；不继承旧版线上成绩。

成都2025 I 的完整三角形包含计数应用见 [Inside Triangle](docs/INSIDE-TRIANGLE.md)：包含贴边的精确判定与单调区间计数；本地应用验证不替代线上AC。

精确覆盖的稀疏建模、可重复求解及完整恢复见 [Dancing Links](docs/EXACT-COVER.md)，配套 P4929 完整用法。

## 码风

- `src/compact/`：基于队伍实际提交，`vector`、小写短名、清晰分行；目录名不表示压缩代码。

[码风证据](docs/STYLE.md)。共享队号不能直接推断每份代码的个人作者。

只保留 `src/compact/` 的 vector 实现。历史静态版已从当前源码与驱动中移除；历史 AC 快照仍保留原样。

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

- [OJ 记录与实际受测接口](verification/oj.json)：保留原始提交源码和 SHA256，不把同文件未调用模块算作通过评测。
- [当前源码与 AC 快照对照](verification/oj-source-audit.json)：完整文件相同或受测结构的排版归一化比对结果。
- [待评测队列](verification/pending-oj.md)：尚未提交、网站错误与未完成验证的接口。

覆盖表中的 `pending` 表示对应项尚未完成迁移和验证；当前仍未达到完整覆盖要求。

区间不同子串的完整来源审计见 [HDU4622 来源模型](docs/INTERVAL-SUBSTRING-SOURCE-AUDIT.md)：复现原稿负下标问题，并用现有 SAM 给出不依赖哈希碰撞的精确适配，完整用法325已纳入总册和字符串册。

## LaTeX

运行 `tools/build_pdf.sh`（需要 XeLaTeX、latexmk）。[当前 PDF](output/pdf/xcpc-template.pdf) 含 vector 版源码、目录、接口索引与数学速查；为建设稿。

所有模板以赛时快速抄写为先：允许适度合并短语句，复杂控制流保持清晰，按算法需要选择函数或轻量 struct。见 [码风规范](docs/STYLE.md)。

## 分册

总册与字符串、数学、数据结构、图论、计算几何、杂项六本独立 PDF 一并生成，见 [分册说明](docs/VOLUMES.md) 与 [输出目录](output/pdf/)。各册有独立目录、页码引用和算法索引；几何知识随几何代码收录。

Library Checker 的完整逐题队列见 [LIBRARY-CHECKER.md](docs/LIBRARY-CHECKER.md)，包含官方分类之外的待核对题目；清单登记不代表已实现或 AC。

固定版本官方数据的本地复验与报告口径见 [OFFICIAL-TESTS.md](docs/OFFICIAL-TESTS.md)。它与线上 AC 档案分开记录。

环境和标准库速查见 [Infra说明](docs/INFRA.md)，构建时另生成 `output/pdf/infra.pdf`，集中提供到算法分册的页码跳转。

标准库实际使用点、复数、前缀和累加类型、tuple 引用、shuffle 和位操作的验证边界见 [Infra 补充审计](docs/INFRA-STL-AUDIT.md)。

各模板的“最简题意＋使用代码”补齐进度见 [使用示例覆盖表](docs/USAGE-COVERAGE.md)，生成与执行检查方式见 [使用示例说明](docs/USAGE-EXAMPLES.md)。正式模板题、应用用法与接口演示分开标记，不以有示例代替线上验证。

最小表示法 [P13270 用法](docs/MINIMUM-ROTATION-USAGE.md)与保留的 Fenwick 第 k 小 [P3369 用法](docs/fenwick-selection.md)均有独立本地验证；不恢复已排除的基础树状数组题。

压位小波矩阵的接口、来源范围和本地证据见 [WAVELET-MATRIX.md](docs/WAVELET-MATRIX.md)；模2压位消元、特解和零空间基见 [GAUSS-XOR.md](docs/GAUSS-XOR.md)。

划分树的重复值配额与区间转换见 [DIVISION-TREE.md](docs/DIVISION-TREE.md)。

次小生成树的两种定义与换边方案见 [SECOND-MST.md](docs/SECOND-MST.md)；模2消元的最少开关应用见 [SWITCH-MINIMUM.md](docs/SWITCH-MINIMUM.md)。

闭合集选点、最小树形图和全局最小割的完整调用见 [CUT-APPLICATIONS.md](docs/CUT-APPLICATIONS.md)。

kuangbin HK 源体、最短层与增量调用差异见 [HOPCROFT-SOURCE-AUDIT.md](docs/HOPCROFT-SOURCE-AUDIT.md)。

完整无符号64位模乘/模幂的保留组件见 [Mod64接口用法](docs/MOD64-USAGE.md)，不恢复已排除的基础快速幂题。

自适应积分的资源上限、采样混叠及误差估计边界见 [Adaptive Simpson说明](docs/ADAPTIVE-SIMPSON.md)。

前缀可持久化01 Trie及P4735区间异或转化见 [接口、证明与容量约定](docs/PERSISTENT-XOR-TRIE.md)。

严格凸多边形外点的两条切线、最近接触端点和可见边链证明见 [整数凸多边形切线](docs/CONVEX-POLYGON-TANGENTS.md)。

无权最少行重复覆盖的方案接口、下界与恢复证明见 [MINIMUM-COVER.md](docs/MINIMUM-COVER.md)；用法为本地接口演示，未新增线上AC。

活动点启用/停用后的最近距离与最小点号见 [动态点分树最近点](docs/CENTROID-NEAREST.md)；包含 QTREE5 完整应用，线上验证待补。

稀疏坐标点加／矩形和，以及稠密矩形加／矩形和见 [二维Fenwick的接口与四矩证明](docs/FENWICK2D.md)。

可持久化并查集的版本语义，以及线段树合并／分裂的独占节点与回收约定见 [历史版本与集合所有权](docs/OWNERSHIP-TREES.md)；包含 P3402、P5494 完整用法，本地验证不等于在线 AC。

两串扩展KMP及KMP/Z/Manacher的10项来源核对见 [接口、索引转换与剩余缺口](docs/STRING-PREFIX-AUDIT.md)。

固定编号、集合合并与改值的 [可合并 Splay](docs/MERGE-SPLAY.md)，以及三态距离、原边路径和负环方案的 [Bellman–Ford](docs/BELLMAN-FORD.md)均附完整用法与独立本地验证记录。

队列 [SPFA 与差分约束](docs/SPFA-CONSTRAINTS.md)包含源点负环、全图可行解、三类不等式及递归 Tarjan 缩点后的最少糖果应用；明确区分一般负权图与0/1约束的复杂度。

DAG最长路、原边方案与重复运行约定见 [DAG-LONGEST](docs/DAG-LONGEST.md)。

Floyd全源最短路、负环提前退出与路径约定见 [FLOYD](docs/FLOYD.md)。

最小总边权最短路树、零权块与原边方案见 [SHORTEST-PATH-TREE](docs/SHORTEST-PATH-TREE.md)。

二分图最大独立集、最小点覆盖方案与棋盘应用见 [BIPARTITE-INDEPENDENT-SET](docs/BIPARTITE-INDEPENDENT-SET.md)。

稠密图矩阵最短路、堆复杂度与三份来源核对见 [DENSE-DIJKSTRA](docs/DENSE-DIJKSTRA.md)。

Kruskal生成森林、原边方案及三份来源差异见 [KRUSKAL](docs/KRUSKAL.md)。

矩阵Prim、父点森林及两份来源核对见 [PRIM](docs/PRIM.md)。

无权二分图匹配的五份原实现、重跑语义与独立验证见 [MATCHING-SOURCE-AUDIT](docs/MATCHING-SOURCE-AUDIT.md)。

右侧容量匹配的 Dinic 建图、方案还原及原稿数组边界核验见 [CAPACITATED-MATCHING-SOURCE-AUDIT](docs/CAPACITATED-MATCHING-SOURCE-AUDIT.md)。

最大流边流量方案唯一性、独立环流及原稿漏判核验见 [FLOW-UNIQUE](docs/FLOW-UNIQUE.md)。

kuangbin曼哈顿MST的完整原程序、第k大边和数值范围映射见 [MANHATTAN-SOURCE-AUDIT](docs/MANHATTAN-SOURCE-AUDIT.md)。

kuangbin SPFA费用流的残量接口、负环前提与int边界见 [SPFA-FLOW-SOURCE-AUDIT](docs/SPFA-FLOW-SOURCE-AUDIT.md)。

递归ISAP、gap正确性及两份邻接表来源边界见 [ISAP](docs/ISAP.md)。

两种矩阵SAP的重复调用、反对称净流和原稿边界见 [MATRIX-SAP-SOURCE-AUDIT](docs/MATRIX-SAP-SOURCE-AUDIT.md)。

kuangbin Dinic的瓶颈/点数边界及最大流父节范围见 [DINIC-SOURCE-AUDIT](docs/DINIC-SOURCE-AUDIT.md)。

zkw费用流的可行势、递归调标和来源前提见 [ZKW-FLOW](docs/ZKW-FLOW.md)。

动态点分治HDU4918来源协议和整数边界见 [CENTROID-SUM-SOURCE-AUDIT](docs/CENTROID-SUM-SOURCE-AUDIT.md)。

树上新增市场的距离/编号规则、点分治证明及来源边界见 [TREE-MARKET](docs/TREE-MARKET.md)。

树边翻转、奇路径计数及树分治父节范围见 [TREE-PATH-PARITY](docs/TREE-PATH-PARITY.md)。

按位置插删、区间等值计数及CF455D在线解码见 [序列替罪羊树](docs/SEQUENCE-SCAPEGOAT.md)，与按值排序的替罪羊树分开。

带插入区间第k小的来源协议及不伸展Splay查询退化反例见 [树套树来源审计](docs/SEQUENCE-KTH-SOURCE-AUDIT.md)；对应[SequenceKth实现](docs/SEQUENCE-KTH.md)和用法327已完成本地验证，官方题面及线上评测待核实。

自适应 Simpson 的 [kuangbin 来源核验](docs/SIMPSON-SOURCE-AUDIT.md)已覆盖原稿13行，保留光滑函数漏采样反例；数值估计满足不代表严格误差保证。
