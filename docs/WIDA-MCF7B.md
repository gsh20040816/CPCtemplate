# WIDA 07B 新版费用流

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `7d59e03ce2f94fe2990de3f44e360acdf737250c`，路径 `03 - jiangly模板收集/02 - 图与网络/07B - 费用流（MinCostFlow 新版）.cpp`。

`addEdge(u, v, cap, cost)` 这次是正常方向：正向容量为 `cap`、费用为 `cost`，反向容量为 0、费用为 `-cost`。`edges()` 按添加顺序还原起点、终点、容量、费用和流量。

小图上的最小费用最大流与 Bellman-Ford 一致，包括一条负费用边、自环和并行路径。容量 `3000000000`、费用 1 的单边得到流量和费用都是 `3000000000`。单次增广上界写成 `numeric_limits<int>::max()`，所以更大的容量要分多轮，不能把它理解成一次送完任意 `T`。

`s == t` 时 Dijkstra 立刻认为到达，增广循环不走，流量每次加上 `int` 最大值，两秒内没有返回。图里有到不了的点时，下一次成功增广会把该点势能加上 `int64` 最大值，UBSan 报溢出。因此它不是现有 `MinCostFlow` 的完全替代。

`python3 tests/wida_mcf7b.py` 跑了普通 `-O2`、ASan/UBSan、大容量、溢出和源汇相同。QOJ 提交页面没有打开，没有新的在线 AC。来源保持 partial。
