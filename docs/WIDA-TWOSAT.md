# WIDA TwoSat

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `3964b5b9bdd16bc9de0e3558078d13691617bda4`，路径 `03 - jiangly模板收集/02 - 图与网络/05 - TwoSat（2-Sat）.cpp`。

`addClause(u, f, v, g)` 表示 0-based 变量满足 `u == f` 或 `v == g`。它用 Tarjan 给蕴含图缩点。`id[2i] == id[2i+1]` 时无解；否则 `ans[i] = id[2i] > id[2i+1]`。节点 `2i` 是假，`2i+1` 是真。重复调用 `satisfiable` 会重算，边集保留。

现有 `TwoSAT` 表示同一类子句，但变量从 1 编号，接口是 `add(x, a, y, b)`。两边的具体真值不必相同，只要求可满足性一致，并且原稿返回的赋值满足全部子句。

`python3 tests/wida_twosat.py` 在普通 `-O2` 和 ASan/UBSan 下各核对 502 项，包含空公式、单变量强制、矛盾式，以及 80 组不超过 10 个变量的随机公式。没有打开 AtCoder 提交页面，也没有新的在线 AC。
