# 因子和、Carmichael 与几何级数用法（191–193）

本批不增加新的基础算法；补齐现有函数的打印用法，并修复六个历史核心测试引用已删除classic目录的问题。仅使用当前vector/STL源码，不修改算法核心、DFS或字号。

## 题面及适配

[Luogu P1593 因子和](https://www.luogu.com.cn/problem/P1593) 给定1≤a≤50000000、0≤b≤50000000，求a^b的正约数和模9901。用法191复用PollardRho，分解a，调用divisor_sum_power；a=1或b=0得到1。只需抄main及依赖模板，不需要构造a^b。此独立因子和题计入正式模板题本地用法覆盖。

[UVa 10006 Carmichael Numbers](https://onlinejudge.org/external/100/10006.pdf) 输入3≤n<65000，0结束。用法192先排除素数，再判断λ(n)整除n-1。其充分性：对任一素因子p，p-1整除λ(n)，从而p不整除n-1；若p²整除n，则p整除λ(n)，与λ(n)整除n-1矛盾，因此n必平方自由。对每个p，由Fermat定理（包括p整除底数的情形）有a^n≡a，再由CRT推广到n。反向由单位群指数λ(n)的最小性得到。该题判定结果不能证明λ(n)本身的最小性，因此核心测试仍独立枚举单位阶。本题按应用用法登记，不计独立模板题覆盖。

[AtCoder ABC293 E Geometric Progression](https://atcoder.jp/contests/abc293/tasks/abc293_e) 给定1≤A,M≤10⁹、1≤X≤10¹²，求从A⁰到A^(X-1)的和模M。用法193读取power_sum的第二分量。M可能为合数，A-1不一定可逆；该递归算法不用逆元。M=1结果0，A=1结果X mod M。比赛应用，不计独立模板题覆盖。

## 当前源码的独立验证

运行`python3 tests/math_current.py`：六个核心分别在-O2和ASan/UBSan下执行，展开源码指纹绑定在`verification/math-current-core.json`。没有恢复任何classic代码或Boost依赖。

- power_sum：小模数1..40、底数0..2mod、项数0..100直接迭代；300组完整uint64底数/模数及uint128项数以2×2矩阵作参照；最大uint128项数及mod=1/6/9901/ULLONG_MAX。矩阵乘法先将每个uint128乘积取模，再累加，避免两个乘积相加溢出。
- divisor_sum_power：a=1..30、b=0..4直接枚举a^b的所有约数；四种模数包含合数及ULLONG_MAX；a=2^63、b=ULLONG_MAX的63*b+1项长度以uint128矩阵检查。
- carmichael：n=2..800枚举所有单位的乘法阶，取LCM核验数值与最小性；大素数、大素数幂、2^30、2500个随机int32模数的单位指数证书，以及LCM合成性质。
- KthResidue：小素数下所有原根、正指数及归一化输入的完整根集合；uint64指数和signed极值；压缩表示998244352个根，以及近10¹²素数的已植入根。小模数原根由独立单位循环枚举准备，避免借生产PrimitiveRoot验证它自身。
- PrimePowerRoots：小素数幂、单位和非单位、正负输入的完整根集合；2进符号因子、uint64指数、2^39与3^20的大提升族，检查根数及抽样根证书。
- CompositeRoots/root_factors：模数1..180及反转因子顺序的完整根集合；自动分解入口在模数1..80枚举；试除参照核验模数至10¹²的分解和原根阶，模1、多个不同素因子、1024个平方根唯一性及大零根族。

独立Python任意精度矩阵另核验2090组power_sum结果（90组边界、2000组随机），覆盖偶合数模数、ULLONG_MAX、底数0、项数0、2^64及2^128-1。它与C++矩阵共同记录，但不是线上AC。

运行`python3 tests/math_usages.py`：精确展开书册191–193的文本，各模式执行456组P1593试除分解/几何商参照、UVa全部64997合法n及仅终止符输入、339组ABC293 E任意精度矩阵参照。执行报告记录精确打印程序指纹，见`verification/math-usages-{normal,sanitizer}.json`。用法样例另由`tests/usage_examples.py --only example-191 example-192 example-193`双模式核验。

## 尚未完成的范围

高次剩余当前仍是BSGS的O(√p)版本，只接受k>0；不能直接声称覆盖允许k=0、每组5000次且5秒时限的Library Checker kth_root_mod。根集合测试不代替这类性能要求，也不代替线上AC和全提交速度榜。

当前200算法、193份用法：132项正式题本地覆盖、30项仅应用覆盖、38项待补。646条上游主题仍待去重映射，完整kuangbin/WIDA/近三年中国ICPC/CCPC/OI Wiki数学范围未完成。GitHub CI保持停用。

## 书册排版

三份main均完整在一页：191为数学4/总册33页，192为数学18/总册47页，193为数学2/总册31页。相邻mint核心改为显式新页，完整在数学5/总册34页；不缩字号。检查三册19页，八册无排版警告。infra的NTT跳转更新为数学60页，12个外部跳转通过；其余五册比对内容流、注释和命名目的地后保留原文件。当前193份用法位置/源码及PDF指纹同步，记录见verification/math-current-layout.json。
