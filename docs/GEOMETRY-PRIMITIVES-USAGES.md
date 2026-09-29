# 几何基础组件完整用法（180–184）

本批补齐已有组件的完整输入、调用与输出程序，没有新增基础算法。五题均属于AOJ Library of Computational Geometry的独立模板练习；打印代码只保留所需模板声明与main。算法核心和字号不变。

## 题面与适配

| 用法 | 组件 | 官方题面 | 关键约定 |
|---|---|---|---|
| 180 | RealPlane | [CGL_2_A](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_2_A) | 两条非退化直线；平行2、垂直1、其他0。仅覆盖点向量、dot/cross。 |
| 181 | line_projection | [CGL_1_A](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_1_A) | 固定直线的点投影；不截断到线段内；参数(p,a,b)。 |
| 182 | segment_distance_real | [CGL_2_D](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_2_D) | 闭线段间距离；整数相交判定为真时输出0，否则取四次点线段距离的最小值。 |
| 183 | line_intersection_real | [CGL_2_C](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_2_C) | 输入保证非平行且相交，可取one；通用接口求的是无限直线交点。 |
| 184 | polygon_area2 | [CGL_3_A](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_3_A) | 简单逆时针多边形允许凹形；有向二倍面积取绝对值，精确打印.0/.5。 |

前四题1≤q≤1000，面积题3≤n≤100；坐标均为绝对值≤10000的整数。距离、投影和交点的题面误差要求严格小于1e-8；面积保留一位小数。

整数方向分量绝对值≤20000，点积/叉积绝对值≤8×10^8，能在通常二进制64位及更高精度浮点中精确表示。因此用法180直接比较零是本题范围内的选择，不能照搬到一般实数。非零方向叉积的绝对值至少1，而默认平行判定阈值eps×|u|×|v|至多0.0008，故用法183不会将本题非平行直线误判为平行。交点坐标仍经浮点构造，并以独立精确分数参考核验误差。

两线段距离先用IntegerPlane::intersect做精确相交判定，包含端点接触、共线重叠；不依赖浮点符号。面积题的int128累加再除以2，在题目上界下缩窄到long long安全；一般规模的int128面积结果不能任意缩窄。

## 独立本地验证

`python3 tests/geometry_primitives_usages.py`与`--sanitizer`分别编译当前打印程序，在普通及ASan/UBSan模式通过：

- 平行/垂直：8272组，含3×3点网格的全部非退化有向线段对、3000随机组及88组大方向向量、行列式为±1的端点交叉变形。
- 投影：274000组正式范围查询，另2组退化直线扩展；含1000次查询上界、水平/竖直、反向直线和投影在线段外。参考用Fraction精确计算。
- 线段距离：8272组正式范围，加1377组退化输入扩展。相交参考解两个线段参数及共线区间；距离参考用精确平方距离和70位Decimal开方，不复用浮点投影构造。
- 交点：3561组题目范围内相交且非平行线段；Fraction求交点，含反向和几乎平行的非零小行列式。
- 面积：255个正式方向的简单多边形，包括凹形、100点、最大坐标、整数及半整数面积；另将其全部反向作扩展。参考按水平截线的内部宽度积分，不复用鞋带公式。输出精确核对数值和小数位数。

普通与ASan/UBSan中，投影/距离/交点最大绝对误差均小于4×10^-12；这只是本次样本的实测界，不是任意实数输入的精度承诺。两份核心回归`tests/real_components.cpp`、`tests/integer_components.cpp`同样双模式通过，另覆盖none/infinite/degenerate分类、点圆、面积符号及10^12尺度整数边界。

184份实际打印程序的执行指纹均与当前源码一致，新5份均实际执行双模式。

## AOJ公开数据复验

`tools/aoj_cases.py`从官方`judgedat.u-aizu.ac.jp`接口读取每题header和所有序号的完整输入、标准输出，按header的字节数核对文件；若元信息与实际长度不同，必须再取官方JSON接口并确认输入、输出逐字节一致，单独记录差异和第二接口哈希，不能静默忽略。记录header、输入、答案、实际输出、程序和比较脚本SHA256。缓存位于build/aoj-data；报告归档在verification。局部数字比较器拒绝错误数值、NaN和输出项数错误；它不是AOJ官方checker。

例如：

```sh
python3 tools/aoj_cases.py --usage example-181 --atol 1e-8 --report verification/geometry-primitives-aoj-181-normal.json
python3 tools/aoj_cases.py --usage example-181 --atol 1e-8 --sanitizer --report verification/geometry-primitives-aoj-181-sanitizer.json
```

本批五题公开数据分别32、32、20、20、20组，共124组；每组在普通和ASan/UBSan模式均通过本地比较器。平行/垂直和面积按精确数值比较，其余要求绝对误差严格小于1e-8。完整结果见`verification/geometry-primitives-aoj-180..184-{normal,sanitizer}.json`（范围表示五组文件名）。这不新增线上AC或全站排名。

已有几何用法也通过相同来源的完整数据双模式复验：CGL_3_C点在多边形内20组、CGL_7_D整数直线圆交点12组、CGL_7_E整数两圆交点25组、CGL_7_H圆与多边形交面积32组、CGL_7_I两圆交面积40组、CGL_7_F点到圆切线20组、CGL_7_G两圆公切线40组。加上本批五题，共12题、313组数据、626次进程验证；没有改动这些既有驱动或核心。报告编号135、151–156分别绑定对应打印程序。

其中CGL_7_F第4组header声明输入9字节，原始与JSON接口均给出相同的10字节输入`3 4\n0 0 2\n`；标准输出长度54字节一致。报告保留这个差异及第二接口哈希，其余312组的输入/答案长度均与header一致。未静默删减数据或降低输出误差要求。

## 排版与剩余范围

几何册新增用法180/181/182/183/184分别在2/3/25/4/14页，总册412/413/435/414/424页；所有main完整同页。已逐页检查两册新增页及相邻核心/用法，共22页，未缩小字号。其余六册逐页比较内容流、注释、命名目的地后保留原文件。八册构建无警告、10个跨册跳转有效。最终文件指纹见`verification/geometry-primitives-usage-layout.json`。

当前200算法、184份完整用法：128项正式模板题本地用法，27项仅应用覆盖，45项待补；646条上游覆盖记录仍需完成映射和核验。本批不新增线上AC。浮点圆交点仍不借整数版用法冒记覆盖：近相切反例及精确分类替代见[INTEGER-CIRCLES.md](INTEGER-CIRCLES.md)。GitHub CI保持停用。
