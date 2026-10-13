# WIDA 09B complex 平面几何

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `4ef14be1f9d5b7f2207742e28a952bfeb5c59818`，路径 `03 - jiangly模板收集/03 - 数论、几何与多项式/09B - 平面几何（with. complex）.cpp`。

点是 `complex<long double>`。`#define x real` 和 `#define y imag` 会替换之后所有名为 `x`、`y` 的标识符。`dot` 和 `cross` 分别是 `conj(a) * b` 的实部和虚部。`(3,4)` 与 `(1,0)` 的点积是 3，`(1,0)` 与 `(0,1)` 的叉积是 1，`(3,4)` 的长度是 5。

`get(a, b, c, d)` 先求直线 `ab` 与 `cd` 的交点，再返回该交点到 `d` 的距离。`cross(c - a, d - a)` 等于 `cross(c - a, d - c)`，所以分子就是两条直线求交的常用分子。`(0,0)-(4,0)` 与 `(1,1)-(1,3)` 的结果是 3。两条平行线 `y = 0` 和 `y = 2` 的分母为 0，结果不是有限数。这不是一套已证明的退化谓词。

`python3 tests/wida_complex.py` 在普通 `-O2` 和 ASan/UBSan 下通过这些例子。QOJ 提交页面没有打开，没有新的在线 AC，也没有新增模板。来源保持 partial。
