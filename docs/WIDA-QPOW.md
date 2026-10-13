# WIDA 快速幂

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `73f8c65c32b46ef3bc067a263a5c542f55352e12`，路径 `03 - jiangly模板收集/03 - 数论、几何与多项式/01 - 快速幂.cpp`。

文件前半的 `power(int, i64, int)` 使用 `i64`，定义却在后半。单独编译这份原稿会失败。把 `using i64 = long long` 放在前面后，两个 `power` 可以共存。

整数版在底数 0 到 19、指数 0 到 19、模数 1、2、3、7、97 和 1000000007 上，与 `__int128` 二进制幂只差 20 项：指数为 0 且模为 1 时返回 1。`__int128` 参照把模 1 的结果定为 0。指数为正时，模 1 会在循环里变成 0。

`mul` 先做有符号 `a * b`，再用 `long double` 估计商。UBSan 在 `229993854253 * 328149755486` 报 signed integer overflow。不开消毒器的 `-O2` 对 20000 个随机积碰巧与 `__int128` 一致，这不是全部 `int64` 的定义行为。不新增普及组快速幂模板。

`python3 tests/wida_qpow.py` 记录了单独编译失败、普通对照和 UBSan。AtCoder 与 QOJ 提交页面没有打开，没有新的在线 AC。来源保持 partial。
