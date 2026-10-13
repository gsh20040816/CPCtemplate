# WIDA 11C complex 静态凸包

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `9f831125f80c5236db53eefd13ede34cd5c1ecaf`，路径 `03 - jiangly模板收集/03 - 数论、几何与多项式/11C - 静态凸包（with. complex）.cpp`。

点类型是 `complex<i64>`，但文件没有定义 `i64`，单独编译失败。`#define x real` 和 `#define y imag` 会替换之后所有同名标识符。`rot` 把 `(x, y)` 变成 `(-y, x)`。`sgn` 在上半平面或负 x 轴返回 0，其余返回 1；原点返回 1。

`complexHull` 先按 x、再按 y 排序，用单调链去掉共线点：下链在叉积 `<= 0` 时弹栈，上链在叉积 `>= 0` 时弹栈。返回的多边形从最右点开始，先沿上链到最左点，再接上下链去掉两端后的中间点。至少两个不同点的例子与按同一规则独立计算的结果一致，包括共线三点、正方形和内部点。

空集或单点会把 `begin() + 1` 用到空范围上。UBSan 报对空指针做非零偏移。少于两个点不是可用输入。

`python3 tests/wida_hullc.py` 在普通 `-O2` 和 ASan/UBSan 下通过点数不少于 2 的例子，并记录了空集失败。LOJ 提交页面没有打开，没有新的在线 AC，也没有新增模板。来源保持 partial。
