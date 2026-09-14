# 精确几何独立条目

按 issue #7 将 GeometryExtra 的两个二维算法拆为独立函数：

- closest_pair_i64.hpp：精确整数最近点对，置于固定 OI Wiki 导航的平面最近点对。
- minkowski_sum.hpp：严格逆时针凸包的 Minkowski 和，置于凸包相关应用；固定导航没有独立 Minkowski 页面，不伪造目录节点。

geometry_extra.hpp 的旧静态接口只转发，三维整数几何暂仍在原文件。现有调用和命名空间内嵌入保持可用；赛时抄写使用新独立函数。两函数仍依赖 IntegerGeometry，后续继续拆分整数/浮点几何与双连通复合条目。

本批不新增数学算法覆盖。两段算法体除局部类型别名与缩进外未变，脚本已比较；直接函数用 cpp_int 距离和独立 gift-wrapping 凸包参考验证，旧包装用既有调用与命名空间测试验证。普通及 ASan/UBSan 日志和源码哈希见 verification/geometry-split.json。在线 AC 未新增。

导航依据仍为已披露的官方 GitHub 固定快照，非对 oi-wiki.com 域名的访问确认。

整数与浮点类型现分别位于 integer_geometry.hpp / real_geometry.hpp；geometry.hpp 保留为兼容聚合入口。精确最近点对/Minkowski 只包含整数依赖，圆多边形、切线、最小覆盖圆只包含浮点依赖。类型定义不变，当前知识点复合条目数量仍为 3，不能把物理文件拆开算作细分类完成。

后续整数知识点拆分见 INTEGER-COMPONENTS.md：IntegerGeometry 已退出打印正文，现为六个独立条目；剩余复合条目为 RealGeometry 与 Biconnected。

浮点知识点拆分见 REAL-COMPONENTS.md：基础类型和六个函数分别收录，RealGeometry 保留为兼容入口；知识点复合条目仅剩 Biconnected。
