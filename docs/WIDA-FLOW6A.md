# WIDA 06A 旧版整数最大流

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `c02700f9bec81ff3c4184ee16f11bdbd977bc379`，路径 `03 - jiangly模板收集/02 - 图与网络/06A - 最大流（Flow 旧版其一，整数应用）.cpp`。

`Flow<T>` 使用 0-based 点。`addEdge(u, v, c)` 添加容量 `c` 的正向边和容量 0 的反向边。`maxFlow` 是 Dinic：BFS 在第一次到达汇点时就返回，不把该层剩余点全部标完。测试覆盖的图上，这不影响源汇最大流。自环不增加源汇流量。`s == t` 时返回 0。

现有 `Dinic` 是 1-based，并且要求 `s != t`。除源汇相同的这一差异外，随机小图和手工例子的流量与 Edmonds-Karp、库实现一致。本次容量都很小，没有把 `int` 总流量溢出或 `numeric_limits<T>::max()` 的单次增广上界当成已验证。

`python3 tests/wida_flow6a.py` 在普通 `-O2` 和 ASan/UBSan 下各核对 45 组。Codeforces 1717 的提交页面没有打开，没有新的在线 AC。
