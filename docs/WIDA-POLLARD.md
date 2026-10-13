# WIDA 在线模板：Miller-Rabin 与 Pollard-Rho

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `52991fffeb1f8b3664b7bcc6bb7df866b984c861`，路径 `01 - 常用在线模板汇总/03 - 数论、几何/21 - Miller-Rabin + Pollard-Rho.cpp`。它使用 `vector`、`gcd` 和 `abs`，但没有包含头文件，也没有 `std::`，单独编译失败。

`MR` 和 `fac` 都用 `int`。`mul` 先做有符号 `a * b`，再用 `long double` 估计商。1 到 20000 的素数判定与试除一致，1 到 4000 的因数分解也一致，因为这些模数下的乘积还放得进 32 位。`MR(1000000007)` 在 UBSan 下报 signed integer overflow。`fac(0)` 会回到 `fac(0)`，这轮没有跑。

`python3 tests/wida_pollard.py` 在普通 `-O2` 和 ASan/UBSan 下通过小范围，并记录了大素数上的溢出。没有新的在线 AC，也没有新增模板。来源保持 partial。
