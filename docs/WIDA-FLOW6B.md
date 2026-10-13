# WIDA 06B 旧版浮点最大流

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `0c820e9e44641bc6b80950037bd10b0fb9dd6a21`，路径 `03 - jiangly模板收集/02 - 图与网络/06B - 最大流（Flow 旧版其二，浮点数应用）.cpp`。

它和 06A 一样是 0-based Dinic，BFS 在第一次看到汇点时返回。不同处是 `dfs` 把增广量累加到 `double res`，剩余流量正好减完时返回最初的限额 `f`，否则返回 `res`。`maxFlow` 把 `1E100` 当作单次增广上界。

`Flow<double>` 在手工例子和 30 组随机小图上与 Edmonds-Karp 的绝对误差为 0。例子包含 0.05、0.1、0.2 和自环，`s == t` 时结果为 0。这不是任意 `long double` 或极大容量的误差上界。

`Flow<int>` 也会把 `1E100` 转成 `int`。在当前 g++ 的 UBSan 构建里，一条容量 3 的边得到 3，且没有诊断。这只说明这次转换没有触发检查，不能当成整数实例的定义行为。现有整数 `Dinic` 不覆盖这个浮点实现。

`python3 tests/wida_flow6b.py` 跑了普通 `-O2`、ASan/UBSan 和上述整数探针。提交页面没有打开，没有新的在线 AC。来源保持 partial。
