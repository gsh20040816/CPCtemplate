# 整数圆交点与 AOJ 完整用法

新增 `line_circle_i64`、`circle_intersections_i64`，保留浮点容差接口。两者依赖 IntegerPlane 的整数点和 RealPlane 的结果类型；时间、空间均 O(1)。输入坐标绝对值≤10⁹，半径0..10⁹。结果种类见 catalog，返回点不排序，相切只返回一点。几何构造仍使用 long double；不承诺十亿坐标的绝对误差小于1e-6。

直线参数式的二次方程提供独立测试参考；实现使用叉积判别式。两圆的独立分类使用中心距离平方与半径和/差平方比较，实现使用消元后的判别式。int128 范围及几何公式见书册的「整数圆交点：精确判定与浮点构造」。所有计算均先提升到 int128。

圆心(-7717,-10000)、半径9758，直线经过(-10000,-367)、(-5909,-108)时，判别式2168、两交点距离约0.0227。浮点 eps=1e-12 的近似分类会合并两点，不能满足 AOJ D 的1e-6绝对精度。此例与直线反向均纳入测试，没有把原容差函数的用法缺项冒记为已覆盖。

## 正式题面与适配

- [CGL_7_D](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_7_D&lang=en)：整数坐标±10000、半径1..10000，非退化直线且保证交点，q≤1000；四坐标按x/y字典序，相切点复制，绝对误差<1e-6。
- [CGL_7_E](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_7_E)：同样坐标/半径范围，不同圆心且保证交点；输出与D相同。
- [CGL_7_H](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_7_H&lang=en)：原点圆，n=3..100，逆时针简单多边形允许凹形，整数坐标±100、半径1..100，绝对误差<1e-5。
- [CGL_7_I](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_7_I&lang=en)：两圆公共面积，坐标/半径范围同D，含相离、同心、内含，绝对误差<1e-6。

## 可重现验证

`tests/integer_circles.cpp`：cpp_int 精确分类、cpp_dec_float_100 坐标参考，小整数网格穷举、随机AOJ/十亿尺度、极端点、退化直线、零半径和交换顺序。普通与ASan/UBSan分别运行。

`build/tools-env/bin/python tests/circle_applications.py`（依赖mpmath；设CPC_SANITIZE=1切换消毒器）：编译并执行四份完整驱动，80位参考；D最大1000查询批次，E/I随机及近内外切、交换圆顺序；H含凹多边形与100顶点。H参考按顶点和边圆交点切分竖直积分区间，排序截线边界后对直线或半圆解析积分，不使用被测的有向三角形/扇形累加公式。用整圆、半圆、四分之一圆校验参考自身。五个负例检查次序错误、相切输出数目、NaN、Inf和超误差结果会被拒绝。

`python3 tests/usage_examples.py --only example-151 example-152 example-153 example-154`：编译书册中精确拼装的程序，并分别执行普通与消毒器模式。

这些是本地证据，尚未产生新的线上AC或速度排名。GitHub CI保持停用。
