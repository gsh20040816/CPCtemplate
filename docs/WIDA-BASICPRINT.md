# WIDA 打印稿：基础算法

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `227a378410344eba94b973647318d2311fdbfb8d`，路径 `02 - 打印稿模板汇总/01 - 基础算法.md`。

头文件把 `int` 定义成 `long long`，`main` 按读入的组数空转。空输入、`0` 和 `4` 都退出，没有输出。负数的组数没有跑。

`mysqrt` 在 0 到 5000 是不超过参数的最大整数平方根。`LLONG_MAX` 时，`(ans + 1) * (ans + 1)` 有符号溢出。`mylcm` 需要能看见 `gcd`。`mylcm(4,6)` 是 12。`mylcm(100000,100003)` 在相乘前溢出。

`floor` 和 `ceil` 对 `5/2`、`-5/2` 给出 2、-3 和 3、-2。`floor(5,0)` 中止。模板版 `log2floor(8)` 是 3，`log2ceil(3)` 是 2。32 位的 `log2floor` 用 `__builtin_clz`，`log2floor(0)` 不是合法参数。

旧二分在 `{-5,-1,3}` 上，`-2` 的后继是 `-1`，前驱是 `-5`。比末项还大时，后继返回末项 3，并不是一个大于等于查询值的元素。新二分在 0 到 `1E8` 上找到 5。实数二分 100 次后靠近 `sqrt(2)`。整数三分找到 3。实数三分靠近 1.5。

`mygcd` 写的是 `gcd(b, a % b)`，不是调用自己。在 `using namespace std` 下它转到 `std::gcd`。`mygcd(15,25)` 是 5，`mygcd(-4,6)` 是 2。

`python3 tests/wida_basicprint.py` 在普通 `-O2` 和 ASan/UBSan 下通过这些例子，并记录了三处边界。没有新的在线 AC，也没有新增模板。来源保持 partial。
