# WIDA 08B 组合数

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `a5e737ce7e6bd1dc8be55aaabe0e1a4b6dc6be8c`，路径 `03 - jiangly模板收集/03 - 数论、几何与多项式/08B - 组合数（Comb, with. ModIntBase）.cpp`。

`Comb` 使用未定义的类型 `Z`。`Z` 必须能从整数构造、相乘，并提供 `inv()`。单独编译原稿会失败。

测试里用模 `1000000007` 的 `Z`。`binom(n, m)` 在 `n < m` 或 `m < 0` 时返回 0，否则与整数组合数取模一致，包括 `C(100, 50)`。`fac(10)` 是 `10!`。`inv(1)` 是 1。构造时 `_inv[0] = 0`，所以 `inv(0)` 返回 0，不是 0 的逆元。表不够时按 `2 * m` 扩容。

这只验证了上述素数模。没有证明任意 `Z`、负数下标或乘法不可逆时的行为。

`python3 tests/wida_comb8b.py` 在普通 `-O2` 和 ASan/UBSan 下通过。Codeforces 提交页面没有打开，没有新的在线 AC，也没有新增模板。来源保持 partial。
