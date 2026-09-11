# 图论来源与接口覆盖核对（2026-09-12）

本次核对 21 个来源条目，针对的是功能、输入约束、编号约定与验证范围，不要求复制原文件的字段布局。没有修改算法代码，也没有新增在线 AC。7 个原先 pending 的条目现可明确映射到已验证实现；一项原有 local-tested 标记因额外字段尚未覆盖而改为 partial。

[审计快照](../verification/graph-coverage-review.json)保存参考文件摘要、WIDA 提交号、被检查的本库源码与测试摘要。初次审计时，9 个本库文件的摘要与当时完成的普通回归及 ASan/UBSan 清单逐项一致，测试日志也与该清单完全一致。快照保留当时的基线；后续实现以当前 manifest 和 coverage.csv 为准。删点增量、定向、缩点统计及下表中的调用适配现已补齐本地验证。

## 强连通分量

| 来源 | 当前接口 | 已核对内容 | 状态 |
| --- | --- | --- | --- |
| WIDA 在线 08 - SCC (Tarjan) | TarjanSCC / Tarjan_SCC | 分量编号、分量数、缩点邻接表、块大小的计算方式 | 本地覆盖 |
| WIDA 打印稿有向图缩点 | 同上 | 逆拓扑编号，缩点保留重边 | 本地覆盖 |
| WIDA jiangly SCC | 同上 | 0-based 原编号转为 1-based；work 返回值改为读取 bel | 本地覆盖 |
| kuangbin 4.4.1 Tarjan | 同上 | 栈内回边更新、弹栈归属、块大小 | 本地覆盖 |
| kuangbin 4.4.2 Kosaraju | SCC / Strong_Component | 原图完成序、反图 DFS、分量归属、块大小 | 本地覆盖 |
| kuangbin 4.4 总项 | 上述两种算法 | 两个子算法都有独立实现和对应测试 | 本地覆盖 |

源码位于 [Tarjan 动态版](../src/compact/tarjan.hpp)、[传统版](../src/classic/tarjan.hpp)及 [graph 动态版](../src/compact/graph.hpp)、[传统版](../src/classic/graph.hpp)。

`bel[u]` 在执行 run/Run 后是完整的分量映射；原文件的 `num/setNum/siz` 可按下面方式取得，不需要另写 SCC 算法：

```cpp
vector<int> size(graph.cnt + 1);
for (int u = 1; u <= n; u++)
    size[graph.bel[u]]++;
```

Tarjan 的跨分量边从大编号到小编号，Kosaraju 的跨分量边从小编号到大编号。不能把两者的编号大小含义互换。[tests/tarjan.cpp](../tests/tarjan.cpp)同时检查四个实现，用全对可达性作为分量参照，并检查编号方向、缩点边及重复运行；覆盖四点有向图的全部边子集及随机重边图。上述有向 SCC 仍没有独立在线 AC 记录，点双/边双题通过不能替代它。

## 双连通分量

双连通分解使用 [Biconnected](../src/compact/biconnected.hpp) 与 [Biconnected_Graph](../src/classic/biconnected.hpp)。`edges[id]` 是逻辑无向边，`bridge[id]` 是桥标记，`bel[u]` 为边双归属，`blocks` 为点双顶点列表。

| 来源 | 已有能力 | 仍缺内容／约定 | 状态 |
| --- | --- | --- | --- |
| WIDA 旧版链式前向星 EDCC | 桥、边双、缩点森林 | 每对半边合并为一个逻辑边号，存储布局不同 | 本地覆盖 |
| WIDA 新版 EDCC | 真正的桥、边双、逐边号定向 | 原 `bridge` 的两种语义分别由桥标记与方向数组提供；新增接口在线待验证 | 本地覆盖 |
| WIDA 打印稿割边缩点 | 桥、边双、缩点森林、块大小和定向 | 新增接口在线待验证 | 本地覆盖 |
| WIDA jiangly EBCC | 分量、桥森林、逐边定向、块大小和内部边数 | 新增接口在线待验证；自环计一次，重边保留 | 本地覆盖 |
| WIDA 在线 VDCC、打印稿割点缩点 | 割点、点双顶点集合、正确圆方森林 | 使用明确的原点／方点编号，不复制原重建片段的冲突编号 | 本地覆盖 |
| kuangbin 4.5 概念及构造 | 割点、桥、点双／边双与连通图最少加边方案 | 条件与方案已本地验证；在线待补 | 本地覆盖 |
| kuangbin 4.6、4.6.1 | Lowlink 的割点、桥、components/delta；点双复用辅助函数 | 在线评测待补 | 本地覆盖 |
| kuangbin 4.6.2 调用 | UVA796 格式与排序输出、POJ2117 删点最大值，两套打包程序均已对拍 | 在线评测待补 | 本地覆盖 |
| kuangbin 4.7 | 边双、桥树最少加边与原图点号方案 | P2860 同题意双风格驱动已本地验证，在线待补 | 本地覆盖 |
| kuangbin 4.8 | 点双顶点集合 | POJ2942 补图与非二分点双中的奇圈顶点标记 | 部分覆盖 |

上游片段有几处必须明确的区别：

- 新版 EDCC 的 `bridge` 集合在所有 DFS 树边和部分返祖边上插入端点，不是“仅所有桥”的集合。当前 `bridge[id]` 则严格按删边连通性定义，不把两者视为同一字段。
- jiangly EBCC 跳过父顶点并只从顶点 0 开始遍历，需额外考虑重边和断开图。当前实现按父边号处理，遍历所有连通块；新增方向和块内边数接口也保留这一范围。
- 在线 VDCC 的时间戳从 0 开始，却用 0 判断未访问，会与首个顶点冲突；`x==y` 实际去掉的是自环，不是重边。
- 两份 VDCC 的重建片段把布尔 `point[j]` 当作节点编号，会把多个割点混为编号 1。当前圆方森林以原顶点 `1..n` 和方点 `n+i+1` 编号，保留所有原顶点。它与仅保留割点的紧缩表示不同，调用者应按本库约定使用，不能沿用原片段的数组下标。

[tests/biconnected.cpp](../tests/biconnected.cpp)以枚举点集、删点、删边得到独立参照，核验点双、桥、边双、圆方森林和桥森林；包含自环、重边、断开图、重复运行及长链。P8435/P8436 的双风格 AC 只覆盖实际提交的分量输出，森林接口及额外边界仍依靠本地证据。保留明确的自环约定：保存原边号，但不令自环额外生成点双块。

## 2-SAT

kuangbin 4.18.2 的强连通方法可映射到 `TwoSAT` / `Two_SAT` 的可满足性与任意解接口，但其 POJ3648 Wedding 文本解析、文字到布尔值的约定、强制字面量和输出格式尚无本库驱动验证，因此该子项仍为 partial。父项 4.18 也仍是 partial，因为 4.18.1 要求的字典序最小染色解还未实现。

本库 `add(x,a,y,b)` 表示 `(x==a) OR (y==b)`。变量编号从 1 开始；内部字面量 `id(x,value)=2*x-1+value`，取反要用 `id(x,!value)`，不能直接把这个 1-based 字面量编号异或 1。两套实现使用 Kosaraju 正拓扑分量号，因此按真字面量分量号大于假字面量分量号选择；若换成 Tarjan，不能保留相同比较方向。

[tests/graph_contracts.cpp](../tests/graph_contracts.cpp)枚举真值赋值判定可满足性，并逐条检验返回方案，包含重复求解及追加子句；[P4782 驱动](../verify/luogu/P4782.compact.cpp)仍待在线验证。不能把任意可行解称为字典序最小解。

## 后续缺口

删点连通块增量、边定向及缩点统计已补；桥树增广已完成，下一步验证奇圈点双应用。2-SAT 的字典序最小版本和 Wedding 适配分别验证。kuangbin 4.20.2 的离线 Tarjan LCA 已另行实现与验证，见下节；它与 SCC 是不同算法。

## 桥树最少加边补充

`bridge_augmentation` / `Bridge_Augmentation` 在完成边双分解后使用，仅接受非空连通图，允许新增重边。返回原图顶点对，不修改原图。已经无桥时返回空列表；非连通森林不能直接套用本函数。

DFS 叶序中，每条桥一侧的叶集合是循环连续区间。奇数叶时重复首叶，偶数叶表按前后半段配对。对于任意桥，取两侧中较小的非空区间，其长度不超过半周，因此至少一对端点跨过该割。每条原桥由此落在新形成的环上；新边自身也与原图路径形成环。桥树每个叶子都需要新边端点，所以 ceil(L/2) 同时是下界，方案最优。两叶树可能必须新增重边，不应去重。

[tests/bridge_augmentation.cpp](../tests/bridge_augmentation.cpp) 穷举至五点的简单图、随机树与重边/自环图、星形树以及二十万点递归长链；用独立删边连通性验证原图桥、叶子下界及整个加边方案。[P2860](https://www.luogu.com.cn/problem/P2860) 明确允许新路与旧路端点相同；两套完整程序由 tests/bridge_augmentation_application.py 对拍，含 5000 点链、星形与 10000 边图。它只输出最少数量，方案正确性依靠前述本地证据，尚未有本库在线 AC。kuangbin 4.5/4.7 的算法功能据此更新为 local-tested；不将该结论推广到非连通增广或点双增广。

## 离线 Tarjan LCA

`OfflineLCA` / `Offline_LCA<N>` 提供无向树加边、带编号的查询登记、指定根统一求解及 answer 数组。只支持非空树；保留递归 DFS。按大小合并与路径压缩保证 O((n+q) α(n)) 总时间，ancestor 数组独立记录树上祖先，因此不能用 DSU 代表本身代替 LCA。子树完成后才并入父点；查询另一端已完成时，其集合的 ancestor 就是两端 LCA。重复 run 可以换根；追加查询后必须重新 run。

[tests/offline_lca.cpp](../tests/offline_lca.cpp) 穷举 n≤6 的全部标号树、全部根与点对，并用父链独立对拍；包含同点、重复调用、追加查询、重新初始化、零查询及 n=q=500000 的长链，三个根分别验证。P3379 两份打包程序以 n=q=500000 测试；仅本地启动器提供 256MB pthread 栈，提交源码仍为普通递归程序。

kuangbin 4.20.2 的 POJ1470 调用也已提供双风格驱动：解析 `u:(k)` 子节点表，推断根，解析 `(u v)` 查询，再按点号输出非零 LCA 出现次数。测试覆盖乱序子节点行、多组数据、非 1 根、零查询。输入格式依据本地 kuangbin 2018 原文第 181–183 页，而非声称已获 POJ 在线判定。P3379 与 POJ1470 的驱动证据见 verification/offline-lca-driver-tests.txt，在线均待补。

参考：[OI Wiki LCA](https://oi-wiki.org/graph/lca/)、[P3379 题面](https://www.luogu.com.cn/problem/P3379)。kuangbin 原注释的 O(n+Q) 不直接沿用为本实现的复杂度；这里明确包含并查集的反阿克曼因子。父项 4.20 仍为 partial，其他 LCA 实现分别审计。

离线 LCA 库的 50 万层 ASan 测试首次在 256MB 线程栈上触发栈溢出（verification/offline-lca-stack-limit.txt）；测试线程调整为 512MB 后复测。此调整只在 tests/offline_lca.cpp 中，模板 DFS 不变。P3379 普通优化驱动使用的测试线程仍为 256MB。

## 欧拉序与 ST 表 LCA

`EulerLCA` / `Euler_LCA<N,LOG>` 以递归 DFS 生成长度 2n-1 的完整欧拉序，保存各点首次出现位置，ST 表存区间最浅顶点。Lca/lca 和 Distance/distance 都是 O(1)；只接受非空树。Build/build 可换根重建，查询要求 ready，Init 清空图。传统版 LOG 必须满足 2^LOG > 2n-1，N 控制顶点容量；因此默认 LOG=20 可用于 n=500000。不能沿用仅覆盖 n 的倍增表层数约定。

[tests/euler_lca.cpp](../tests/euler_lca.cpp) 穷举 n≤6 的全部标号树、根和点对，以 BFS 父链验证 LCA/无权距离；同时验证欧拉序长度、首次出现位置、重建和重置，另有 50 万点链的三种根测试。P3379 的完整程序测试 n=q=500000；POJ1330 程序从有向父子边推断根，支持多组输入，按 kuangbin 2018 第 179–181 页格式验证，含 n=10000 长链，均为本地证据。日志为 verification/euler-lca-driver-tests.txt；不声称 POJ 在线 AC。

kuangbin 4.20.1 据此更新为 local-tested，4.20 父项仍保留 partial，倍增法单独审计。参考定义与欧拉序方法见 [OI Wiki LCA](https://oi-wiki.org/graph/lca/)，P3379 输入与最大规模见 [题面](https://www.luogu.com.cn/problem/P3379)。

后续倍增范围已核对：kuangbin 4.20.3 是 POJ1330 的祖先倍增实现，不能仅用已有 HLD.lca 关闭；WIDA 打印稿“最近公共祖先 LCA”还包括基础倍增与路径最大边权扩展。其 clac 计算的是边数而非权值和，最大边权 query 以 0 初始化，负边权需要另行规定。后续实现应明确无边路径、负权最大值与跳出根的返回语义，再逐项验证，不把本次无权欧拉序版本标为这些功能的覆盖。

## 倍增祖先与路径最大边权

`LiftingLCA` / `Lifting_LCA<N,LOG>` 已实现基本倍增 LCA、无权距离、k 级祖先和带符号最大边权。root 的上级为 0，jump 超过根返回 0；max_edge(u,u) 返回 nullopt，非空路径即使最大值为 LLONG_MIN 也返回有值的 optional。LOW 仅用于最大值合并，不能作为空路径标记。depth 表示边数，不暗示带权距离和。全程递归 DFS，按 n 配置倍增层数，传统版要求 2^LOG > n。

验证见 tests/lifting_lca.cpp：所有 n≤6 标号树、根、点对与父链暴力参照，权重包含 LLONG_MIN/MAX、负值、零、正值；查询祖先包含超过根和 LLONG_MAX 跳数。50 万点全负链验证换根后的 LCA、距离、祖先及最大边权。P3379 与 POJ1330 双风格完整程序本地测试见 verification/lifting-lca-driver-tests.txt，它们仅检查 LCA，未将其扩大为路径最大值的在线证据。

kuangbin 4.20.3 与 WIDA 打印稿“树上倍增解法”据此更新为 local-tested。kuangbin 4.20 的三个实现及各自应用均已本地验证，父项可标 local-tested；所有在线记录仍单独登记。WIDA 的 HLD 子项经下述映射验证后，LCA 父项也更新为 local-tested。

WIDA 树链剖分 LCA 的 work/add/lca 对应本库 build/add/lca 与传统版 Init/Insert/Build/Lca。原 clac 由公开 dep 数组计算 dep[u]+dep[v]-2*dep[lca(u,v)]；本库根深度为 0，根父亲为根自身，与原片段的约定不同但不改变距离。tests/lifting_lca.cpp 将两套 HLD 接入全部小标号树、全部根与点对的同一父链参照，分别验证 LCA 和该距离公式；普通重测日志为 verification/lifting-lca-mapping-tests.txt，全库 ASan 日志包含最终同一测试源码。树链剖分接口本身未改动。WIDA 该父项及两个子项现在均为本地覆盖，不包括相邻“树上路径交”条目。

## 树上路径交

WIDA 打印稿的 intersection 对四个 LCA 顶点直接按编号排序，再用下标 0/2/3 判断深度与计数，不能用于任意编号的树。例如根为 1、边为 1-3 和 3-2 时，路径 3-2 与自身有两个公共点，原片段排序后为 [2,3,3,3]，返回 1。该反例也在全部小标号树验证范围内。

本库 `path_intersection` / `Path_Intersection` 用树上投影替代编号排序。投影是三个两两 LCA 中最深的点，是 x 到目标路径的唯一连接点。c、d 的投影 p、q 不同时，树上唯一的 c-d 路径必须经过 p-q，其与 a-b 的交集就是 p-q；投影相同则交集至多为该点，用距离可加性判定是否包含它。返回端点和公共顶点数；空交三字段均为 0，单点交点数为 1。depth 必须是边数深度，不能把负权或零权距离用作路径包含判据。

`tests/path_intersection.cpp` 穷举 n≤5 所有标号树、所有根、四端点（包含重复端点），并测试随机换号树，用 BFS 得到的独立路径位集合交验证完整返回路径与点数；分别接入动态 EulerLCA 和传统 HLD。`tests/path_intersection_application.py` 检查 P3398 的 Y/N 输出，含 n=q=100000 链。P3398 只判相交性，不为端点和点数提供在线证据；当前仍无新在线记录。

题面：[P3398](https://www.luogu.com.cn/problem/P3398)。WIDA“树上路径交”据此标为 local-tested，函数不依赖特定 LCA 模板或编号的深度顺序。

## 后续欧拉路审计提示（仍待实现）

WIDA 打印稿的度数判定与输出片段不能直接照搬：有向图仅统计入度等于出度的点数，未排除差值绝对值大于 1；例如两点间两条 1→2 边会被其 cnt=n-2 条件接受，但不存在欧拉路。其 DSU.size(1)==n 还把孤立点算进连通要求；三点图只有边 1→2 时，本应忽略孤立点 3。无向片段在递归前输出边，没有逆后序拼接；图含三角形 1-3-4-1 和边 1-2 时，先走 1-2 再回溯输出 1-3，输出不构成连续走法。

后续模板应保留逻辑边编号，正确处理重边和自环，验证实际消耗了全部边；有向字典序最小序列、无向序列、混合图定向是分别待补的范围。此审计提示不改变这些条目的 pending 状态。

## 有向欧拉路实现

`DirectedEuler` / `Directed_Euler<N>` 已实现度数差严格检查、可选固定起点、忽略无关孤立点、完整边消费检查以及递归 Hierholzer。默认按终点排序邻接表并逆后序输出，求顶点序列字典序最小的欧拉路；并列重边按原编号排序以保持可重复性。关闭排序时只要求任意连续走法。保存 m+1 个顶点与 m 个原边编号，失败时清空方案。无边图取指定起点或点 1；n 必须正。

tests/directed_euler.cpp 穷举三点内全部有向简单图（包括自环），以及两点间每种有向边出现 0/1/2 次的重图；以枚举全部边走法作独立参照，检验所有固定起点、自动起点和字典序最优。证书逐原边号检查唯一消费、方向和连续性，包含加边后重算、反复切换排序模式与失败清空。大例在仅两个非孤立点间交替经过 20 万条边，专门验证递归深度依赖边数而非点数。P7771 完整程序以 n=100000、m=200000 边界测试；日志见 verification/directed-euler-driver-tests.txt。在线待补。

WIDA 有向存在判定与字典序求解两子项更新为 local-tested，父项仍为 partial。kuangbin 4.21.1 包含 POJ2337 单词链应用：单词作为边的字典序与本接口的顶点序列字典序不同，尚未验证，因此继续保留 partial；无向和混合图也分别待补。

题面：[P7771](https://www.luogu.com.cn/problem/P7771)。提交题面保证底层无向图连通，但本库另外验证断开非孤立分量应失败、无关孤立点应被忽略。
