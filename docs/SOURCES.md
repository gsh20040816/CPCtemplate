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
