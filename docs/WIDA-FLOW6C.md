# WIDA 06C 新版最大流

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `a51f7e70858f6002bbe4bedb8f8c6e5f8aefd66b`，路径 `03 - jiangly模板收集/02 - 图与网络/06C - 最大流（MaxFlow 新版）.cpp`。

`MaxFlow<T>` 是 0-based Dinic。`addEdge` 加正向容量和 0 容量反向边。BFS 在第一次看到汇点时返回。`flow` 用 `numeric_limits<T>::max()` 作为单次增广上界。

`edges()` 按添加顺序还原每条正向边：起点是反向边的 `to`，终点是正向边的 `to`，容量是两条残量之和，流量是反向残量。因此它要求反向边最初没有容量。`minCut()` 把最后一次 BFS 里层次不为 -1 的点当作源侧。最大流结束后，离开这个集合的原始边都已饱和，割容量等于流量。不同增广顺序可以得到不同的源侧集合，不能要求与另一份实现逐点相同。

`init` 只把层次扩成 0。在任何 BFS 之前调用 `minCut`，所有点都会被当成源侧。`s == t` 时流量为 0，现有 1-based `Dinic` 不允许这种情况。

`python3 tests/wida_flow6c.py` 在普通 `-O2` 和 ASan/UBSan 下各核对 30 组。流量与 Edmonds-Karp 一致，`s != t` 时也与库 `Dinic` 一致。容量很小，没有证明 `T` 的总流量不溢出。Nowcoder 提交页面没有打开，没有新的在线 AC。
