# 线性代数组件拆分

为按 OI Wiki 知识点分类并减少抄写依赖，原 LinearAlgebra 手册条目拆为三个独立组件：

| 组件 | 接口 | OI Wiki 位置 |
| --- | --- | --- |
| GaussMod<p> | solve(a,n)，返回是否有解、秩、特解、零空间基 | 数学 / 数值算法 / 高斯消元 |
| det_prime<p> | 素数模方阵行列式，零维返回1 | 数学 / 线性代数 / 行列式 |
| ModMatrix<p> | multiply、power | 数学 / 线性代数 / 矩阵 |

三个头文件各自只依赖 number_theory.hpp 中的 ModInt。GaussMod 和 det_prime 要求素数模数；ModMatrix 只用加乘，允许合数模数。原来的 LinearAlgebra 留在 algebra.hpp 作为兼容入口，旧 solve、determinant、multiply、power、spanning_trees 仍可调用，但不再作为一整块手册代码重复印刷。

MatrixTree 直接包含 det_prime.hpp，只调用行列式，归图论 / 矩阵树定理。它的加权、有向/无向和指定根接口没有改变。POJ2947 驱动改为直接使用 GaussMod<7>。

独立验证在 tests/algebra_components.cpp：GF(2)、GF(3)、GF(5) 上枚举完整仿射解集，与特解加零空间所有组合逐项比较，包含空系统、零变量、欠定和不相容情形；行列式使用排列展开参考，矩阵幂使用逐次整数余数乘法参考，另核对合数模数下 uint64 最大指数的 Jordan 块解析结果及矩形乘法。普通与 ASan/UBSan 日志为 verification/algebra-components-*.txt。

兼容回归使用现有 tests/algebra.cpp 与矩阵树的独立边集枚举/方向证书，传统基线固定在 Git 历史，未恢复到当前源码目录。工厂工期驱动的912组独立枚举/大规模证书也在普通与 ASan/UBSan 下通过。日志分别为 verification/algebra-split-regression-*.txt、verification/gauss-widget-*.txt。

这些是当前拆分版本的本地证据；不将历史组合头文件的 OJ 记录自动转移为新组件的在线 AC，也不声称目录所对应的 OI Wiki 整页已全部覆盖。
