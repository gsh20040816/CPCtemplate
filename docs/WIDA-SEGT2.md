# WIDA 在线模板：Segt++

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `70f64fe0d8fb9db507246830308a0edb9f917a38`，路径 `01 - 常用在线模板汇总/04 - 串与数据结构/26 - Segt++.cpp`。它使用 `vector`，但没有头文件，单独编译失败。文件末尾没有 `using Segt`。下标从 1 开始。`n` 为 0 时建树会递归停不下来，这轮没有构造。

`modify` 是区间加，`modify2` 是区间乘，结点保存区间和。乘法标记的初值是 1。对 `1,2,3,4` 依次做整段加 1、`1..2` 乘 4、`2..4` 加 5、`3..4` 乘 -1。所有子区间的和都与普通数组一致。

`Segt_<int>` 上对长度 3 加上 `1000000000` 时，长度与增量的乘积超过 `int`，UBSan 报 signed integer overflow。

`python3 tests/wida_segt2.py` 在普通 `-O2` 和 ASan/UBSan 下通过 `long long` 例子，并记录了这次溢出。没有新的在线 AC，也没有新增模板。来源保持 partial。
