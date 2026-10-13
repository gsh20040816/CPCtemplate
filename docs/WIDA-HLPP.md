# WIDA 在线模板：HLPP 最大流

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `1669a535c09dd16a9bf47a4eb7d68c297e98b142`，路径 `01 - 常用在线模板汇总/02 - 图、树、网络流/17 - 最大流 (HLPP).cpp`。它使用 `vector` 和 `queue`，但没有包含头文件，也没有 `std::`，单独编译失败。

`PushRelabel<long long>(n)` 分配 `0..n`。测试用的点是 `1..n`。`addedge` 的容量是 `int`。`work(s, t)` 从汇点沿残量反向做 BFS 标高，再把源点高度设成 `n` 并预流。计数器名字是 `gobalcnt`。全局重贴标签的阈值是 `10 * n`。

一条容量 5 的边、没有边、经典分流网络、两条并行边，以及 5 张不超过 6 个点的随机图，最大流都与 Edmonds-Karp 一致。点 0、第二次调用 `work`，以及容量超过 `int` 的图没有测。

`python3 tests/wida_hlpp.py` 在普通 `-O2` 和 ASan/UBSan 下输出 `ok`。没有新的在线 AC，也没有新增模板。来源保持 partial。
