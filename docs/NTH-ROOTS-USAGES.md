# N 次剩余与互质数对用法（194–195）

本批补齐现有 vector/STL 模板的可抄写用法。算法核心未修改，测试不再引用已删除的 classic 目录。GitHub CI 保持停用。

## P5668：组合全部根入口

[官方题面](https://www.luogu.com.cn/problem/P5668) 要求每组按 n,m,k 读入，输出 x^n≡k(mod m) 的所有根。指数和模数不超过10⁹，组数不超过100，总输出根数及单个素数幂根数有10⁶上界。

用法194先调用 root_factors，素数、素数幂、一般合数分别直接使用 KthResidue、PrimePowerRoots、CompositeRoots。最后统一排序，既不假定生成顺序，也不靠去重掩盖重复根。m=1为空因子列表，唯一根0；无解只输出根数0。输出界保证可以展开根族，不能将此枚举写法无条件用于没有输出限制的题目。

精确打印程序已获[洛谷 AC](https://www.luogu.com.cn/record/300024458)，12个测试点通过。总用时372ms，单点最大172ms，峰值5.19MB。提交原文归档为 verification/submitted/P5668.compact.cpp，与当前打印程序指纹完全一致。普通打包器的默认前缀不同，其比较仍显示不一致；不能把这两个比较混为一谈。全提交速度排名尚未核实。

运行 `python3 tests/nth_roots_usages.py`，普通和ASan/UBSan每种模式均核验131724组、1334次进程调用。独立参照包括小模数完整幂值桶、随机根枚举、素数阶证书、零根的整除条件和不同素数幂的独立CRT组合。两个官方样例亦完整枚举核验。覆盖百万根输出、非单位根、2的幂、无解、m=1、大指数以及100组大素数批输入。记录在 verification/nth-roots-usages-{normal,sanitizer}.json，线上观察另存 verification/nth-roots-online.json。

这里的AC不覆盖 CompositeRoots 的自动模数重载、非法输入及完整uint64边界；这些仍依赖核心本地测试。Library Checker kth_root_mod允许指数0且要求更强批量性能，当前BSGS版本不能借P5668结果冒记覆盖。OI Wiki整页覆盖及改进Tonelli–Shanks仍未完成。

## P2522：闭区间矩形计数

[官方题面](https://www.luogu.com.cn/problem/P2522) 给出最多50000组查询，端点及k在1..50000，求两个闭区间中gcd(x,y)=k的数对。用法195只初始化一次 CoprimePairs(50000)，每组读入后调用 rectangle，输出long long。四个缩放后的互质前缀容斥，k超过区间上界时允许零前缀。一般使用count(A,B)须预处理至少min(A,B)。本题是HAOI应用，不计独立模板题覆盖。

`python3 tests/coprime_pairs_application.py --usage` 原样展开打印程序，普通和ASan/UBSan分别执行50000条查询：500条随机矩形直接枚举gcd，独立埃氏式欧拉函数筛给出大正方形参照，另检查k缩放和边界窄条，再重复边界用例达到最大查询数。重复用例只说明批量执行，没有50000份独立随机数据的含义。

核心 tests/coprime_pairs.cpp 迁移为vector单版本；核验0..100所有前缀、1..12全部闭区间及k=1..15、百万正方形独立欧拉函数和INT_MAX长窄前缀。两种模式都通过。报告分别为 verification/coprime-pairs-core.json 和 coprime-pairs-usage-{normal,sanitizer}.json。没有新增P2522线上AC或排名。

## 覆盖边界

当前200个算法、195份打印用法：136项正式题本地覆盖，31项仅应用覆盖，33项待补。仍有646条上游主题待去重映射，完整kuangbin/WIDA/近三年中国ICPC/CCPC/OI Wiki范围未完成。本地独立参照、线上AC与速度排名分别登记。

## 书册排版

N次剩余用法在数学41–42页、总册70–71页，外层一般合数分支处显式续页。互质数对核心完整在数学43/总册72页，用法完整在数学44/总册73页。共渲染检查三册25页，保持字号；八册编译无排版警告。infra的NTT跳转更新为数学63页，12个跨册跳转全部通过。verification/nth-roots-layout.json记录观察页与PDF指纹，nth-roots-regressions.json绑定本批测试和源码。
