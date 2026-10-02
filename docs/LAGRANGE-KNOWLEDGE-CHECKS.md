# Lagrange 反演知识补充与检查

`knowledge-lagrange.tex` 补充隐式生成函数 `T=xΦ(T)` 的单系数提取：条件和边界、一般 `H(T)` 公式、形式留数证明、按内部结点计数的满有序多叉树、带标号有根树 EGF，以及现有 `FpsPower` 接口和模除法的使用限制。主分类是固定 OI 导航的“数学 / 多项式与生成函数 / Lagrange 反演”，总册与数学册均独立起页。

知识分类现为六份文件、17 个带标签节。算法数207、完整题目用法221、正式模板覆盖153均不因本节增加；没有新增通用 FPS 复合、复合逆或整段隐式解算法，没有新增线上 AC。

来源以 [Gessel, Lagrange Inversion](https://arxiv.org/abs/1609.05988) 的定理2.1.1、形式留数第4.1节和树模型第3.2–3.3节为主；[OI Wiki](https://oi-wiki.org/math/poly/lagrange-inversion/)用于中文导航。正文为重新组织的解释与推导。

## 数学精确检查

运行 `python3 tests/lagrange_knowledge.py`，默认结果在build；发布报告为 `verification/lagrange-knowledge.json`。检查使用任意精度整数/有理数，对128个不同的Φ（常数1或2、次数≤3、其他系数取-1/0/1/2）、次数≤12，独立迭代隐式方程再比对取系数公式：21504项恒等式/边界检查、14592项整除检查。另实际枚举小规模满有序二/三叉树形状，以及1–5结点带标号有根树，检查OGF/EGF建模和阶乘还原。

边界包含n=0、k=0、k>n；Φ(0)=0排除在本节声明的可复合求逆契约之外，不表示其隐式方程一定无解。Catalan在n=p=3时先整数除法得5、模3得2，而分子分母先取模均为0，验证不能替换成模逆元。

这些有限检查支持具体实现/建模，不替代一般定理的证明。

## 原样代码片段执行

运行 `python3 tests/lagrange_fps_usage.py`，sanitizer使用 `SANITIZE=1 python3 tests/lagrange_fps_usage.py`。测试直接提取正文唯一的lstlisting，在薄输入/输出包装中编译，调用未修改的 `fps_power.hpp`，没有另写一份目标算法。

每种模式7098项：7040个整数小模型、55个有理系数EGF模型由独立隐式迭代给出答案；另3项检查长截断或大n小L的接口映射，包括n=65536，以及n=p−1、L=65和非1常数项。大项以精确组合数/独立模幂核对，不声称暴力展开了接近十亿项的隐式级数。

有效分支严格限于1≤k≤n<p=998244353、L=n−k+1≤2^22、Φ(0)可逆，且输入/内存满足实际需求。7种无效分支由测试前置校验拒绝，不传入C++。普通模式与ASan+UBSan报告分别在 `verification/lagrange-fps-normal.json`、`verification/lagrange-fps-sanitizer.json`；保留编译器默认PIE与ASan默认quarantine，当前环境关闭LSan。报告绑定正文、测试、递归头文件和编译器的前后哈希。

## 文档与回归范围

分类及引用集成检查覆盖17节，正文中每个模板引用都有节号与页码。PDF视觉记录与布局/引用检查见 `verification/lagrange-visual.json` 和 `verification/lagrange-layout.json`；字体字号未改变。

前一版52d81d1源快照的整库普通/sanitizer完整证据在证明提交4a66e69中。本次新增知识和测试不倒算进该历史整库回执；本节发布依据是上述当前源绑定的精确数学、实际片段双模式、分类和PDF检查。两个默认浮点几何核心与AOJ判题精度的已知不兼容仍保留，见 `GEOMETRY-JUDGE-CONTRACTS.md`。
