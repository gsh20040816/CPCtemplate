# WIDA 07A 取模类 Z

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `7b8778e7f670850df2c660f7d98b16c234f5178b`，路径 `03 - jiangly模板收集/03 - 数论、几何与多项式/07A - 取模运算类（Z）.cpp`。

模数固定为 `998244353`。`int` 构造函数只调用一次 `norm`：小于 0 就加 `P`，不小于 `P` 就减 `P`。注释要求参数已经在 `[-P, 2P)`。因此 `Z(-P)` 是 0，而 `Z(-P - 1)` 得到 -1，没有收进模数。`i64` 构造函数先做 `x % P` 再 `norm`，所以 `Z((i64)-1)` 和 `Z((i64)(-P - 1))` 都是 `P - 1`。

加、减、乘、除和 `power(Z(2), 10)` 与整数取模一致。输入 `-5` 得到 `P - 5`。`inv` 用费马小定理，并 `assert(x != 0)`。断言开启时 `inv(0)` 会中止。原稿使用 `assert`，但没有包含 `<cassert>`。

如果在包含这份代码之前写了 `using namespace std`，`norm(x % P)` 里的 `x % P` 是 `long long`，可能匹配到 `std::norm` 而不是这里的 `int norm(int)`。测试因此不引入 `std` 名字。

`python3 tests/wida_z.py` 在普通 `-O2` 和 ASan/UBSan 下通过上述例子，并记录了 `inv(0)` 中止。Codeforces 提交页面没有打开，没有新的在线 AC，也没有新增模板。来源保持 partial。
