# 来源与范围

- kuangbin 2018 模板：[作者入口](https://kuangbin.github.io/2018/08/01/ACM-template/)，[PDF](https://github.com/kuangbin/ACM-ICPC/blob/master/kuangbin%E7%9A%84ACM%E6%A8%A1%E6%9D%BF%EF%BC%88%E6%96%B0%EF%BC%89.pdf)。目录逐项登记，不把参考原稿视为已经改写验证。
- [WIDA XCPC](https://github.com/hh2048/XCPC)，覆盖在线、打印稿和补充模板；原项目 GPL-3.0。`coverage.csv` 保留来源条目，重复/旧版项需明确替代关系后才能关闭。
- [OI Wiki 数学](https://oi-wiki.org/math/)：补充数论、组合数学、线性代数、多项式、概率期望、博弈、数值计算；定理须注明假设，随机算法须标识性质。
- 中国 ICPC/CCPC：2023–2025 完整赛季为主，追加公开的 2026 场次。须用具体题目与题解建立映射，世界赛和境外站不替代中国赛站覆盖审计。

## 已取得的赛题资料

- [2025 香港题解](https://qoj.ac/download.php?id=3169&r=1&type=attachments)：A 二分图匹配；F 强连通/拓扑处理；G 线段树维护；K 单调栈、树上倍增与比较。训练账号参加过 QOJ 3169。
- [2025 CCPC 济南资料](https://contest.ucup.ac/download.php?id=2693&r=0&type=attachments)：已取得，待逐题核对。

这是一份来源登记，不代表完整赛季调研已经结束。不能把题名带有某个关键词直接当作算法证据。

## 进一步核对的中国赛站需求

| 年份 / 赛站 | 题目 | 题解定位 | 模板需求与边界 |
|---|---|---|---|
| 2023 ICPC 杭州 | G Snake | [题解第 9–11 页](https://icpcarchive.github.io/Asia%20East%20Continent%20Contests/Hangzhou/2023%20Asia%20Hangzhou%20Regional%20Contest/solution.pdf) | 带最早可达时间的最短路松弛；普通 Dijkstra 需改松弛函数，不能直接声称裸模板覆盖整题 |
| 2024 CCPC 郑州 | A A+B=C | [题解第 24 页](https://codeforces.com/gym/105632/attachments/download/29064/CCPC_2024_Zhengzhou_Tutorial.pdf) | CRT 的结构性计数解释，属于定理应用 |
| 2024 CCPC 郑州 | E 排列路由 | 同上第 26–27 页 | 重心/点分治与构造，需要独立实现 |
| 2025 ICPC 成都 | B Blood Memories | [题解第 10–11 页](https://contest.ucup.ac/download.php?id=2567&r=1&type=attachments) | 状压 DP 的 max-plus 矩阵幂；普通模矩阵乘法不适用 |
| 2025 ICPC 成都 | I Inside Polygon | 同上第 29–32 页 | 凸多边形切线、旋转双指针与计数；仅有凸包函数不足以覆盖 |

以上是已定位的具体需求，不是三年全部赛站审计完成的声明。

## 一般图匹配的实现核对

- 算法依据：[Edmonds, Paths, Trees, and Flowers](https://ftp.eecs.umich.edu/~pettie/matching/Edmonds-paths-trees-flowers.pdf)。实现采用逐个未匹配根进行交错树搜索、收缩奇环、沿父指针增广。
- 对照 WIDA 一般图最大匹配新版及 kuangbin 4.13 的接口需求，重新编写双风格实现；带权条目另行实现。
- 验证题：[Luogu P6113](https://www.luogu.com.cn/problem/P6113)，要求输出匹配数量与配对方案。当前先完成本地穷举和子集 DP 对拍，OJ 状态以记录表为准。

## 线性递推核对

- [OI Wiki：Berlekamp–Massey](https://oi-wiki.org/math/berlekamp-massey/)：有限前缀的最短递推及有界阶序列恢复条件。实现采用连接多项式与上次非零偏差更新，独立重写为两套函数。
- [OI Wiki：常系数齐次线性递推](https://oi-wiki.org/math/poly/linear-recurrence/)：特征多项式降幂。当前提供 O(k² log n) 版；快速多项式版仍待实现，不能把整个页面记为完成。
- tests/recurrence.cpp 穷举 GF(2)、GF(3) 上长度至多 8 的序列，与枚举系数的最小阶数比较；生成递推后用前 2k 项学习并核验后续项；使用独立矩阵幂核对 uint64 最大下标和合数模数。

## 双连通分量与圆方树

核对 WIDA 的 VDCC、EDCC 新版及 jiangly 圆方树条目，统一输出点双顶点集合、割点、桥、边双编号和两种缩点森林。编号与孤立点约定见手册。

[OI Wiki 圆方树](https://oi-wiki.org/graph/block-forest/)提供结构定义参考。点双验证题为 [P8435](https://www.luogu.com.cn/problem/P8435)，边双为 [P8436](https://www.luogu.com.cn/problem/P8436)。P8435 双风格已在记录 297517446、297517662 获得 100 分 AC，其余输出接口状态见 verification/oj.json 与本地测试。

测试通过枚举诱导子集并逐点删除，独立求极大无割点连通子图；逐边删除判桥、逐点删除判割点，并核对圆方森林和桥森林。包含 20 万点链及闭环后重算。测试线程配置 256 MiB 栈，模板保持递归 DFS，不包含手写调用栈。

## 回文树 PAM

核对 WIDA 打印稿字符串章节及 jiangly PAM 条目：二者中的 cnt 表示回文后缀链长度，不能直接当作某个回文串的总出现次数。新模板分别使用 suffixes、hits 和 occurrences()，并提供首次出现端点。验证题：[P5496](https://www.luogu.com.cn/problem/P5496) 检查在线解码与回文后缀数量，[P3649](https://www.luogu.com.cn/problem/P3649) 检查出现次数乘长度。OJ 状态单独登记。

## 静态点分治

对照 WIDA 在线模板的树上距离存在性需求。当前采用重心距离集合排序、双指针统计并扣除同一子块的方法，预处理后支持多次距离计数。通过 count_exact(k)>0 回答 [P3806](https://www.luogu.com.cn/problem/P3806) 的询问。仅覆盖静态树距离查询，kuangbin HDU5016/HDU4918 特殊需求仍需单独核对，未据此标为完成。

独立 Floyd 距离参考使用 int128，核对随机森林、零权和极值权；10 万点单位权链与零权星形树使用闭式计数核验。测试配置 256 MiB 线程栈，模板均为递归 DFS。

## 树上启发式合并

对照 WIDA 打印稿树上问题的 DSU on tree 条目，实现子树最高频颜色编号和；使用 DFS 序枚举轻子树、保留重子树统计。验证题为 [CF600E](https://www.luogu.com.cn/problem/CF600E)。独立测试通过沿父链累加各祖先的颜色直方图核对结果，包含换根、重新着色、负数颜色、10 万点链和星形树。OJ 状态另行登记。

## 区间乘加线段树

核对 WIDA jiangly 03B 的区间乘、单点加、区间和语义；用仿射懒标记扩展至区间加与赋值，公开接口改用 1-based 闭区间。验证题为 [P3373](https://www.luogu.com.cn/problem/P3373)。本地 int128 数组参考核对全部更新结果，涵盖模数 1、合数模数、INT_MAX、负参数及 long long 极值。

## 补充：虚树

参考 [OI Wiki 虚树](https://oi-wiki.org/graph/virtual-tree/) 的关键点与 LCA 闭包构造。此项作为补充模板，不冒充 WIDA 原目录的已完成映射，也不据此宣称某个赛站题目已覆盖。当前支持虚树结构、压缩路径长度及最小边权；具体题目的 DP 另行编写与验证。

本地对照关键点两两 LCA 的完整闭包，并沿原树父链核验每条虚边。包含重复关键点、空/单点、多次查询、重新选根、零权边与 10 万点递归长链。

虚树调用示例：[P2495 消耗战](https://www.luogu.com.cn/problem/P2495)。显式将原树根加入关键点，逆序遍历虚边完成断边费用 DP；只清空本次虚树顶点及关键点标记。tests/virtual_tree_application.py 对实际打包的两份提交程序执行枚举删边对拍，未声称在线 AC。

## 可持久化的版本语义

重新核对 WIDA 主席树条目：原条目是前缀频率版本差求第 k 小，对应已有 PersistentKth，而不是任意历史数组赋值。新增 PersistentArray 是独立补充，支持任意历史版本分叉与 O(1) 复制。验证题 [P3919](https://www.luogu.com.cn/problem/P3919) 要求每次查询也复制被访问的版本，驱动显式调用 Copy/copy。

本地测试保存每个版本的完整数组，与随机分叉、查询、复制后的结果逐一对照；检查旧版本不变、单节点容量极限及动态预留容量。

## 圆构造数值回归

2026-09-12 修复本库两套圆圆交点：近同心不再当作重合，零半径圆按点处理；仅相同圆心、相同正半径返回无限交点。相切判定改用圆心弦投影到圆周的径向差，避免近同心情况下用两圆心距离接近半径差误判。圆相关容差使用局部尺度，保留浮点问题的误差预算约定。

小角度圆弓面积采用 $\theta-\sin(2\theta)/2=2\theta^3/3-2\theta^5/15+4\theta^7/315+O(\theta^9)$，避免接近外切时直接相减丢失有效位。tests/circle_precision.cpp 使用 Boost 100 位十进制三角函数计算独立面积参考，覆盖近同心、退化点、缩放与近外切。旧实现确实触发新回归断言，证据见 verification/circle-regression.txt；没有把这些测试解释为任意实数输入的精确保证。

## 早期 DFS 实现的递归统一

2026-09-12 将早期 HLD、Kosaraju 的手写 DFS 调用栈改为递归。Kosaraju 保留原来的分量拓扑递增编号，因此 TwoSAT 的使用约定不变；Tarjan 分量编号仍为逆拓扑序。传统版 HLD 改用 Heavy_Light_Decomposition<N> 与 Init(n)，明确静态容量。

对照 WIDA 在线 HLD 的路径/子树修改与查询，组合已验证的区间乘加线段树编写 [P3384](https://www.luogu.com.cn/problem/P3384) 驱动。tests/hld.cpp 检查点权路径、排除 LCA 的边权路径、子树 DFS 区间及换根后重建，还检查 20 万点链；tests/tarjan.cpp 的全部 4 点有向图枚举同时核验两套递归 Kosaraju。

2026-09-12 进一步把 Treap 的序列中序输出、状态序列建树后聚合与删除回收改为递归辅助函数。笛卡尔树构造仍使用算法本身的单调栈。P3369 只调用同头文件中的 OrderedTreap，相关结构和主程序与旧 AC 快照一致，SequenceTreap 的变更由本地独立测试覆盖。

## Hopcroft–Karp 复杂度与方案

算法分析依据：[Hopcroft and Karp, 1973](https://epubs.siam.org/doi/10.1137/0202019)，界为 O((V+E)√V)。本实现用 NIL 层距离限制最短增广路，DFS 带当前弧；最后一次失败 BFS 的交错可达集合用于构造最小点覆盖。替换此前只声明保守 O(VE) 的分层增广版。

核对 WIDA 在线二分图最大匹配条目后实现，接口保留 1-based 编号。tests/hopcroft_karp.cpp 穷举两侧至多 4 点的全部二分图，以子集 DP 核验最大匹配；再检查点覆盖覆盖每条边且大小等于最优匹配数，并验证重边、空侧、增量加边与 10 万点长增广路。

## 图论接口与双风格证据补齐

核对 WIDA 在线 Dijkstra 与 2-SAT 条目后，加入 tests/graph_contracts.cpp：每个源点的最短距离与 int128 Floyd 对照，并检查返回路径的端点、无重复点和真实边权总和。二分图匹配之外的 2-SAT 单独枚举真值表，验证两套实现的可满足性及其返回赋值，涵盖逐步添加约束、强制变量、矛盾与重算。

原有 Hungarian 只覆盖完整矩阵最小费用分配；最大权、缺边与可不匹配语义由下述新增 weighted_matching.hpp 补齐，不能凭同名算法自动视为覆盖。

P4779 与 P4782 提交驱动的输入输出分别核对 [洛谷 P4779](https://www.luogu.com.cn/problem/P4779) 与 [洛谷 P4782](https://www.luogu.com.cn/problem/P4782) 官方题面（2026-09-12）。驱动本地打包检查不计作在线 AC。

## 带权二分图匹配补齐（2026-09-12）

参考并核对 kuangbin 4.12、WIDA 在线 KM 与打印稿最大权匹配章节的功能。新增 weighted_matching.hpp 的双风格实现，使用逐左点最短增广的势能算法，提供必须匹配全部左点与允许不匹配两种模式；缺边明确跳过，零权边保持为真实边。完整 long long 边权先扩展到 int128 再取负。可选模式的虚拟点不写入真实匹配方案。

[OI Wiki 带权二分图匹配](https://oi-wiki.org/graph/graph-matching/bigraph-weight-match/) 用于算法术语及功能交叉核对；[洛谷 P6577](https://www.luogu.com.cn/problem/P6577) 用于驱动协议，特别是题目要求按右点输出左点。本地 tests/weighted_matching.cpp 枚举小规模缺边图，以子集 DP 独立计算最优值，并核验两侧配对、真实边、总权、无解清空、重算和极值算术；另测 500×500 全等负权矩阵。

WIDA 打印稿“匈牙利算法（KM算法）解”实际是无权最大基数匹配，映射到已有 Hopcroft–Karp。jiangly MaxAssignment 额外暴露 labels() 和每种匹配基数的 weights()，当前尚未提供，因此该条仍为 partial；不能把逐个处理左点的中间值当成任意 k 条匹配的最优权值。

## 合数模数的组合数（2026-09-12）

按 [OI Wiki 卢卡斯定理的 exLucas 部分](https://oi-wiki.org/math/number-theory/lucas/) 核对素数幂分解、去除阶乘内的素因子、指数判零与 CRT 合并。新增 exlucas.hpp 的两套独立可抄实现，动态版本连接各素数幂前缀积，传统版本使用同一静态数组分段；上界总长度不超过 mod+1。构造时预处理，适用于小模数、大下标的重复组合数查询。并未将该实现视作大素数模数的低空间替代算法。

验证以杨辉三角模任意小整数、Boost 精确大整数组合数为主；大下标的小 k 用任意精度整数直接乘除，达到 unsigned long long 最大值；另以小素数杨辉表加 Lucas 分位公式检查 n、k 均为大数的情形。OI Wiki 页面中的独立 Lucas 分位模板及定理说明仍待补，不将整个页面标完成。

[洛谷 P4720](https://www.luogu.com.cn/problem/P4720) 提交协议已核对：输入 n、m、p，输出 C(n,m) 模 p。WIDA 在线名为“组合数 (Lucas)”的源码实际是阶乘/逆阶乘预处理，且额外提供排列数和动态扩容；它不包含 Lucas 分位递推，不能只按标题替它关闭覆盖项。
