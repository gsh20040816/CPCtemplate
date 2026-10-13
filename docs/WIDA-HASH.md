# WIDA 在线模板：手工随机哈希

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `52848daa42461f0ebba6cef6eb4524e4ecc2933d`，路径 `01 - 常用在线模板汇总/01 - 初始与杂类/04 - 手工随机哈希.cpp`。它包含了 pb_ds 头，但 `uint64_t`、`chrono` 和 `pair` 没有自己的头文件，单独编译失败。

`hash` 是 splitmix64。`operator()` 第一次调用时用 `steady_clock` 取种子，所以哈希值不能跨运行固定。两个重载各有一份 `static` 种子。同一次运行里，同一个 `uint64_t` 的哈希相同，`0` 到 `999` 的哈希互不相同。

`unordered_map<int, int, myhash>` 能保存 `-1`、`0`、`1`。`mymap` 是 `__gnu_pbds::gp_hash_table`。键 `{1,2}` 读回 9，键 `{2,1}` 不是这个值。这只说明这组键没有撞上，不是哈希质量证明。

`python3 tests/wida_hash.py` 在普通 `-O2` 和 ASan/UBSan 下输出 `1 0`、`3 4 5 0`、`9 0`、`1000`。没有新的在线 AC，也没有新增模板。来源保持 partial。
