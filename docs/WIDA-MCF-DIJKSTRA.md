# WIDA 在线模板：Dijkstra 费用流

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `5962310cf2167a3559b9285ae18bd71fef59d01c`，路径 `01 - 常用在线模板汇总/02 - 图、树、网络流/18 - 费用流 (Djikstra).cpp`。它使用 `pair`、`vector` 和 `priority_queue`，但没有包含头文件，也没有 `std::`，单独编译失败。节点从 0 编号。

正权例子和一条所有点都可达的负边与手算一致：两条路合成流量 2、费用 7；两条并行边流量 2、费用 5；费用 -5 的一条边流量 1、费用 -5。处理负费用的分支整段被注释掉了。

每次成功增广都会执行 `h[i] += dis[i]`。到不了的点距离是 `long long` 的最大值。第一次只是把势设成这个最大值；下一次增广再加一次就会有符号溢出。两条 0→1 的边再加一个孤立点，UBSan 报 signed integer overflow。没有检测负环。

`python3 tests/wida_mcf_dijkstra.py` 在普通 `-O2` 和 ASan/UBSan 下通过三组完全可达的图，并记录了孤立点溢出。没有新的在线 AC，也没有新增模板。来源保持 partial。
