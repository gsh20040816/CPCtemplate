# issue #21：精简模板库

目标：贴近队伍码风、封装后易抄写、覆盖赛事常用算法；不以页数为硬指标，正确性与完整性优先。

## 结果

| 项目 | 之前（b930c4d1） | 之后 |
|---|---|---|
| 头文件 | 303 | 153 |
| 头文件行数 | 约 25000 | 15688 |
| 目录条目（catalog） | 337 | 230 |
| 登记使用示例 | 460 | 313（只印 168 份模板题用法） |
| 总册页数 | 1237 | 662 |

## 做了什么

1. **使用示例**：每个模板只印第一份 kind 为 template 的示例；application 与 api 驱动照常作为本地测试，不进 PDF。
2. **封面与维护章**：状态说明与“使用与验证”压成一页；删去“来源与覆盖维护”“后续覆盖项”。原第九部分的遗留内容已全部按 OI Wiki 分类印在各部分中，空的附录外壳一并去掉。
3. **兼容层**：删除 geometry、geometry_extra、integer_geometry、real_geometry、polynomial 头文件及 LinearAlgebra、NumberTheory、LazySeg、Lowlink；测试仍需的转发放在 `tests/compat_layers.hpp`、`tests/compat_number_theory.hpp`。IntegerGeometry3D 是实际代码，移入 `space3.hpp`。
4. **重复实现与单题解法**：按 issue 表格删除 105 个文件、112 个符号，逐项替代关系见 [issue21-removed.json](issue21-removed.json)，coverage.csv 中相应行改指替代模板。被删模板的 verify 驱动与 AC 存档保留，`verification/oj-source-audit.json` 中标为 retired，待评测队列不再列出它们。
5. **简单算法并入**：
   - `number_theory.hpp`：Mod64、Prime64（为避免与 Mod64 循环包含一并并入）、exgcd、逆元、线性同余、CRT 合并、区间筛、逆元表、批量逆元、单点 φ。
   - `graph.hpp`：Kruskal、Prim、Floyd、SPFA、Bellman–Ford（去掉 `__int128`、valid 标志与大段 assert，各 30 到 65 行），匹配边分类、二分图独立集。
   - `real_plane.hpp`、`integer_plane.hpp`：投影、距离、交点、圆交面积、内切圆、重心、凸包裁剪；整数面积、点在多边形、凸包包含、直径、整数圆交点。
   - 新建 `space3.hpp`（RealSpace、Line3、Plane3、IntegerGeometry3D）、`gnu.hpp`（rope、配对堆、有序树、哈希表）、`mo.hpp`（普通、带修、回滚、树上莫队）。
   - `flow.hpp` 并入最小割边分类与最大权闭合子图；`string.hpp` 并入 SuffixLCP；`tree.hpp` 并入树上路径交。
   - 被删的变体写成说明：Dijkstra（最短路树、Johnson）、extended_gcd（ax+by=c 通解）、BoundedCirculation（负环费用流）、OrderedTreap（启发式合并）、LinkCutTree（路径最值/和）、PersistentKth（树上路径第 k 小、区间不同数）、Mo（曼哈顿排序）、SuffixLCP（前缀最长公共后缀、平方串计数）。
6. **共享核心改到保留模块**：LGV 改用 determinant_mod；运行时模数 mint 内联 Barrett 约减（不再依赖 barrett32）；匹配边与最小割边分类改用 graph.hpp 的 SCC。
7. **知识节**：印刷版只留公式、适用条件和复杂度；原文完整保存在 `docs/knowledge-full/`，由 `tools/knowledge_markdown.py` 生成 [KNOWLEDGE-DETAILS.md](KNOWLEDGE-DETAILS.md)。依赖知识原文的测试改读 knowledge-full。
8. **README** 只留范围、码风、验证、构建四节；[PRIORITIES.md](PRIORITIES.md) 增加删减原则。

## 恢复的模板

按队内复核，以下四个模板覆盖赛时真实需求，现有模板不能直接替代，已从删除名单中恢复，代码、目录条目、模板题用法与专属测试与删除前一致：

| 模板 | 需求 | 现有模板为何不够 |
|---|---|---|
| convolution_i64 精确整数卷积 | 输出真实整数，系数可能超过单个模数 | 任意模 FFT 只给余数；临时拼多模 NTT、CRT 与负数还原容易出错 |
| centroid_diameter 动态点集直径 | 树固定、点反复开关，查询当前最远点对（QTREE4 型） | 静态点分治不能直接回答，需要维护分支最优值、删除与全局答案 |
| negative_cost_flow 允许负环的最小费用流 | 建模后有负费用环，循环流也能改善费用 | MinCostFlow 拒绝初始负环；上下界可行流不保证费用最优 |
| circle_coverage 圆的多重覆盖面积 | 求至少／恰好被 k 个圆覆盖的面积 | 圆并只保留未覆盖弧；按层积分还要处理重圆、包含与角度事件 |
| TarjanSCC 强连通分量 | Tarjan 系列（SCC、割点、割边、点双、边双）不可省略 | 割点、割边、点双、边双由 BiconnectedCore 的一次 lowlink DFS 给出；SCC 只保留 Tarjan，并入 graph.hpp，Kosaraju SCC 删除，TwoSAT 与边分类改用 TarjanSCC |
| static_rmq 静态 RMQ | 区间最值位置查询 | 删除后库内没有任何 RMQ；位掩码版 O(n) 预处理、O(1) 查询，赛时不易写对 |

对照 WIDA 后确认不恢复的条目：分数类、DAG 最长路（太简单）；q-二项式、二维 RMQ、稀疏二维树状数组、动态/带权 AC（太偏）；KM 由 Hungarian 覆盖并补缺边建模说明；Montgomery/Barrett/64 位静态模的功能由 ModInt、mint、Mod64 覆盖；Lowlink、旧 biconnected、edge_components 由 BiconnectedCore 覆盖。

割点模板 P3388 与桥模板 UVa 796 的驱动改用 BiconnectedCore（cut、bridge），P3388 的删点连通块判据测试加回 test.sh。TwoSAT 改用 TarjanSCC 后取真条件为真文字分量编号更小，2500 组真值表判据通过。

coverage.csv 中被删模板所在行以删减前映射为准重写：被删项换成替代项、被合并文件换成目标头文件、保留项原样保留（此前的脚本曾误删 48 行中的保留项）。

## 正确性核对

- 重写的 Kruskal、Prim、Floyd、SPFA、Bellman–Ford 与旧实现在 20000 组随机小图（含负权、负环、多源）上逐项比较距离、路径、负环边序列与生成森林，ASan/UBSan 下一致。
- 内联 Barrett 的 mint 与旧 Barrett32 版及 `__int128` 精确值在 2000 余个模数（含 1 与 2^31-1）、各 2000 组含极值输入上一致。
- 重写的 P4897（最小割树查询）与 P5431（批量逆元）驱动用小例与暴力结果核对。
- 全部保留的 C++ 测试、verify 驱动与使用示例驱动均可编译；仍不可编译的只有已 retired 的 AC 存档驱动，以及本机 `long double` 位宽导致静态断言失败的三处（与改动前相同）。
- 测试套件结果见下节。

## 测试套件

- 改动前（b930c4d1）在本机按 `tools/test.sh` 的分阶段方式（含固定的 src/classic 基线）逐步运行，已有 22 个步骤失败，主要是复制上下文缺少 `<cassert>`、知识节迁移计数过期和本机 `long double` 位宽断言，与本 issue 无关。
- 本 issue 中被删模块的专属测试随模块删除；保留模块的测试改用保留实现或测试内适配。中途对照中新出现的失败均已逐个修复并单独复跑通过：ACL 映射、凸多边形切线、联合用法引用、矩阵树/整数分拆知识、FFT、费用流、行列式、SCC、矩阵树与 QOJ8235 应用。
- 最终完整运行（a01d1b8b）与改动前对照：没有算法测试新增失败；唯一新增的 inclusion_knowledge 是知识原文迁移后映射路径未同步，已修复并复跑通过。改动前失败的 22 步中，6 步随被删模块或改写的驱动消失，其余仍为原有问题。
- 恢复后 convolution_i64、negative_cost_flow、centroid_diameter、circle_coverage 的单元与应用测试均通过，前三者及其应用测试已加回 test.sh；TarjanSCC 单元与 QOJ906 应用测试加回 test.sh，StaticRMQ 另做约 299 万次随机区间最值位置对拍（static_rmq.py 依赖仓库外的 WIDA 原始源码，与删除前一样不在 test.sh 中）（circle_coverage 依赖 mpmath，与删除前一样不在 test.sh 中）。
- `tools/build_pdf.sh` 生成全部 PDF，`pdf_audit` 与 `infra_audit` 通过，总册 662 页，无未定义引用。
