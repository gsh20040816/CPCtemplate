# 连续与批量逆元用法（196–198）

为现有vector/STL模板补齐可抄写调用，不修改算法核心。P5431必须保留快速输入，因此在登记表增加utility_functions，取出同一驱动的read函数和main一起打印、编译。read适用于题目的非负十进制输入，不处理负数。所有打印程序的依赖和执行指纹仍单独检查，GitHub CI不查询、不维护。

## 题面、接口与使用约束

[Luogu P3811](https://www.luogu.com.cn/problem/P3811) 给定1≤n≤3000000、n<p<20000528，p为素数，每行输出i的逆元。用法196调用inverse_table(n,p)，输出1..n，位置0仅为占位。该递推要求素数，不能直接搬到合数，即使某些元素与模数互素。

[Luogu P5431](https://www.luogu.com.cn/problem/P5431) 给定最多5000000个非零模p元素，p≤10⁹为素数，2≤k<p，求Σ(i=1..n)k^i/a_i模p。用法197调用batch_inverse(move(a),p)，权重每次先乘k，再加入本项逆元；首项权重为k。按值入口接收move(a)，之后不再读取a。一般模数时返回optional，任一非单位元素使整个调用失败，不能输出部分逆元。题目内所有元素保证可逆。

用法198对同一道题展示mint和batch_units组合：设置动态模数后再构造对象，所有元素来自同一模环，计算期间不切换模数；返回后读取v输出。动态模数、构造、乘法与复合赋值由完整题目调用，合数、不可逆元素及tag独立性仍用核心测试核验。历史long long版AC不能覆盖这个组合实现。

三个条目均为题面明确标注的模板题用法。batch_units在198中直接调用，mint亦直接设置模数和参与运算，不以依赖包含关系代替使用。

## 当前源码的独立验证

`python3 tests/inverse_current.py`分别用普通和ASan/UBSan执行四个核心：

- batch_inverse：mod=1..25全部三元素组合，用gcd判定可逆和乘积证书核验每项；2000组任意有符号64位输入、非单位、空数组、模1及百万元素。
- inverse_table：试除认证的小素数全部前缀、n=0、300万项及INT_MAX素数下百万项，所有结果逐项乘法核验；兼容NumberTheory::inverse的合数前缀亦直接枚举参照。
- batch_units：mod=1..100全部两元素单位/非单位组合、空数组、普通左值输入保持不变及move输入，随机10000项逐项证书。
- mint：小合数所有加减乘除、try_inv和直接枚举逆元，int128参照的完整有符号输入、复合赋值别名、tag独立性、uint64指数与Fenwick组合。

记录在 verification/inverse-current-core.json。不存在旧classic实现比较，也没有借生产批量逆元作另一个实现的参照。

`python3 tests/inverse_usages.py`展开精确打印文本，每种模式执行346次：196检查6组，逐项认证300万行输出；197/198各检查170组，168组用Python独立单个逆元加权参照，两组500万常量数组用几何级数解析参照。所有输出行数和stderr都检查。百万重复常量用于规模核验，不等同于百万独立随机数据。报告为 verification/inverse-usages-{normal,sanitizer}.json。

## 历史线上结果与当前源码范围

[P3811历史AC](https://www.luogu.com.cn/record/297563298)和[P5431历史AC](https://www.luogu.com.cn/record/297561197)归档仍保留，但当前整份程序字节并不匹配。`python3 tests/inverse_archive_audit.py`仅比较限定范围：main与read词法一致；算法函数体在移除inline后相同，P5431还需将原NumberTheory::inverse调用映射为拆分后的mod_inverse。头文件、依赖和整体程序不因此视为相同，这个机械比对不证明依赖语义等价，也不算新的当前源码AC。

报告 verification/inverse-archive-scope.json 与常规oj-source-audit.json保留完整源码不匹配。当前组合版没有线上AC，全提交速度排名也未核实。

## 尚未完成的范围

当前200算法、198份打印用法：140项正式题本地覆盖、31项仅应用、29项待补。646条上游主题仍待去重映射，OI Wiki数学页的完整内容及完整kuangbin/WIDA/近三年中国ICPC/CCPC范围仍未完成。该批仅补逆元相关用法，不能据此宣称全库正确性已保证。

## 排版与infra索引

用法196在数学22/总册51页，197在数学21/总册50页，198在数学7/总册36页，均完整单页且保留原字号；两个P5431用法含read和main。相邻linear_congruence改为显式新页，完整在数学23/总册52页。三册25页渲染检查通过，八册无排版警告。infra新增move数组到用法198的链接，NTT跳转更新为数学65页，13个跨册跳转核验通过。其余五册比对内容流、注释和命名目的地后保留原文件。证据见 verification/inverse-usages-layout.json。
