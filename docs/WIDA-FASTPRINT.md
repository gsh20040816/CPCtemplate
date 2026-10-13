# WIDA 打印稿：卡常

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `f78e56d873d9b1297f19c70b658a2ac5a1556a6d`，路径 `02 - 打印稿模板汇总/13 - 卡常.md`。

二进制 `gcd` 在 0 到 200 的非负范围内与 `std::gcd` 一致，`gcd(0,0)` 是 0，`gcd(-4,6)` 是 2。`is_prime` 在 0 到 5000 与试除一致。循环上界用的是 `n/5`，这个范围内没有因此漏掉因子。

蒙哥马利乘法和 Miller-Rabin 都使用没有定义的 `i64`。补上 `long long` 之后，模 `1000000007` 时，0 到 49 的加减乘除和 `pow(2,10)` 与整数取模一致。Miller-Rabin 在 0 到 3000 与试除一致，并且接受 `1000000007` 和 `1000000009`。偶数模数没有测。

Pollard-Rho 那段把 `Montgomery` 和 `isprime` 写成空声明，单独编译失败。不能当成可用的因数分解。

HLPP 与以前核过的版本相同。单边、空图和经典分流与 Edmonds-Karp 一致。

快读在文件结束时返回 0，不是 `EOF`。输入 `  -12 0 34x` 写出 `-12 0 34`，没有换行。空输入三秒内没有结束。`Cout(INT_MIN)` 对 `-2147483648` 取负，UBSan 报错。

`python3 tests/wida_fastprint.py` 在普通 `-O2` 和 ASan/UBSan 下通过这些例子。没有新的在线 AC，也没有新增模板。来源保持 partial。
