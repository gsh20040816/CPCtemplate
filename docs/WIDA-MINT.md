# WIDA 07B MLong 与 MInt

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `c0c6ceb5a52f5f248fbbfc1d70ecd099bdc851ae`，路径 `03 - jiangly模板收集/03 - 数论、几何与多项式/07B - 取模运算类（MLong & MInt）.cpp`。文件使用 `i64`，但没有定义它，单独编译失败。`assert` 也没有包含 `<cassert>`。

`MInt<1000000007>` 的加减乘除、`power(2, 10)` 和负数构造与整数取模一致。`MInt<0>` 的默认模数是 `998244353`，`setMod(7)` 后 `10` 得到 `3`。`inv` 用费马小定理并 `assert(x != 0)`。断言开启时 `inv(0)` 中止。这只说明模数是素数时上述例子成立，没有覆盖合数模。

`MLong` 的 `mul` 先做有符号 `a * b`，再用 `long double` 估计商，没有 `0.5` 的舍入修正。`1000000000000000 * 1000000000000000` 在 UBSan 下报 signed integer overflow。`1` 到 `50` 乘 `97` 的小范围与 `__int128` 一致，不能推广到所有 64 位乘积。`MLong<0>` 的默认模数是 `10^18 + 9`。

`python3 tests/wida_mint.py` 在普通 `-O2` 和 ASan/UBSan 下通过 `MInt` 例子，并记录了 `inv(0)` 和乘法溢出。提交页面没有打开，没有新的在线 AC，也没有新增模板。来源保持 partial。
