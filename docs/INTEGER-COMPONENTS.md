# 整数几何知识点拆分

按 issue #7，将原 IntegerGeometry 复合正文拆为六个独立条目：IntegerPlane 基础点向量/线段判定，integer_hull 凸包，polygon_area2 有向面积，polygon_contains 简单多边形包含，convex_contains_i64 凸包二分包含，convex_diameter2 旋转卡壳直径。

固定官方 OI Wiki 导航的二维基础承载基础运算、面积和一般多边形包含；凸包承载构造和凸包包含；旋转卡壳承载直径。不是通过新增自定义导航节点伪装成原站分类。算法数量没有增加，复合条目减少一个。

新头文件只依赖实际需要的基础或函数。IntegerGeometry 仅作未打印的兼容入口，继承基础类型以保留旧 Point 身份，并转发旧方法，不复制算法体；赛时只抄所需独立条目。最近点对和 Minkowski 和也已改用基础类型，后者显式依赖 integer_hull。

函数体除别名限定外与原实现核对一致。既有 property、边界、cpp_int/gift-wrapping 和命名空间兼容回归覆盖旧入口；新增直接包含各头文件的分析解测试覆盖正反面积、旋转凸包起点、近万亿坐标、边界/外部点和退化线段。普通及 ASan/UBSan 均通过，详见 verification/integer-components.json。没有新增在线 AC。
