# WIDA 在线模板：平面几何

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `23de33672e259d662d64cd99d4bb4f43f4ac664e`，路径 `01 - 常用在线模板汇总/03 - 数论、几何/22 - 平面几何.cpp`。内容在命名空间 `Geometry` 里，但使用 `acos`、`numeric_limits`、`cout` 和 `sqrt` 时没有头文件，也没有 `std::`，单独编译失败。

`(3,4)` 与 `(1,0)` 的点积是 3，叉积是 -4。曼哈顿距离 `dis1((3,4),(-1,2))` 是 6。`rotate` 返回 `p1-p2` 逆时针转 90 度后的向量，不是绕 `p2` 转完的点：`(3,4)` 相对 `(1,0)` 得到 `(-4,2)`。`operator+(Point, T)` 把标量同时加到 x 和 y，`(3,4)+10` 变成 `(13,14)`。

比较使用 `EPS=1e-7`。`sign(1e-8)` 是 0。`(3,4)` 单位化得到 `(0.6,0.8)`。零向量单位化的结果不是有限数。`dis` 先用坐标类型做平方；`Point<int>` 上 `100000` 的平方在 UBSan 下报 signed integer overflow。`#define cc(x)` 写在命名空间里，宏仍然泄漏到外面。

`python3 tests/wida_plane.py` 在普通 `-O2` 和 ASan/UBSan 下通过这些例子。没有新的在线 AC，也没有新增模板。来源保持 partial。
