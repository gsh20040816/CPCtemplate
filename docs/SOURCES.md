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
