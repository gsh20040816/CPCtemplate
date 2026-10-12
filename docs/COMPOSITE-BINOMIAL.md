# 有界上标的任意模数组合数

新增 `CompositeBinomial`，与小模数、大上标的 `ExLucas` 互补。当前 328 个组件、446 份完整用法。对应 WIDA 13C，精确原稿保存于 `tests/fixtures/wida_composite_binomial/13C.cpp`，blob 为 `dc2eacad3e2e7eb6206c3fb9f9bc02d382bc3f60`。

## 接口及适用范围

`CompositeBinomial(N, mod)` 预处理所有上标 0..N；要求 0≤N<INT_MAX、1≤mod≤INT_MAX，模数不要求素数，实际 N 受可用内存限制。`choose(n,k)` 在 n<0、k<0、k>n 时返回 0；其余要求 n≤N。模数为 1 时全部结果为 0，包括 C(0,0)。不支持自动扩表。limit、mod、factors 及辅助函数属于内部实现，调用者不得修改。

模数分解成互素素数幂 q=p^a。每个因子存三张长度 N+1 的表：去掉全部 p 因子的阶乘、其逆元、n! 的 p 指数。逆阶乘只在末尾做一次欧拉求逆，再倒推；所有被求逆的数都与 q 互素。另存 p^0..p^(a-1)，查询指数达到 a 时余数为零，否则由三张表与 p 次幂表在常数时间求余数。CRT 系数只在构造时计算。

设 s 是不同素因子数。预处理 O(√mod+s(N+log mod)) 时间、O(s(N+1)) 空间；查询 O(s) 时间、O(1) 额外空间。对每个 p，去因子循环总次数为 Σ floor(N/p^j)，小于 N，因此不会多出 N log N 因子。表长按 N，既不按整个模数也不按素数幂分配；例如 N=100000、mod=INT_MAX 时只需一个因子的三张表。

当上标很大而模数小，应选已有 ExLucas，它按素数幂长度预处理，接受完整 unsigned long long 上标。不能把新的有界上标接口声称为任意大上标的通用替代。

## 整数范围

素数幂构造的每次 q*p 不超过 mod，因此有符号 int 安全。指数前缀 v_p(n!)≤n，且 N<INT_MAX。模乘全部提升为 long long；每个乘法操作后都取模，最大 CRT 累加不超过 (mod-1)^2+(mod-1)，严格小于 LLONG_MAX。短 p 次幂表使用 long long 更新，最后一次更新恰到 q。没有原稿中以 int 计算不必要平方的溢出。

## 来源审计

WIDA 原稿将表长限制为 min(100001,q)，因而确实支持小上标、大模数场景。它在大上标且 q>100001 时不能一般性地使用；不能因形参为 i64 就推断无限制。原引用是 [CF 896D 提交219861532](https://codeforces.com/contest/896/submission/219861532)，原完整提交本轮未读取，不宣称其历史判定。

未修改原稿的构造 `Binomial(1000003)` 已在 UBSan 下复现 signed integer overflow：二参数整数 power 在 exp=1 的循环末尾仍计算 base*=base，虽然该平方不会再被使用。1000003 是原题允许的模数。诊断与精确文件哈希保存在 `verification/composite-binomial.json`。原稿只在安全小域与新实现对照；其可能发生未定义行为的大模数运行结果不充当正确性真值。

## 原题驱动与独立验证

[CF 896D Nephren Runs a Cinema](https://codeforces.com/problemset/problem/896/D) 的官方题面限制为 n≤100000、1≤mod≤2×10^9。三类顾客分别对应 +1、-1、0 步；前缀高度不能为负，最终高度在 [l,r]。设 S(h) 为不限制前缀的 h 高度计数。反射原理给出合法数 S(h)-S(h+2)，区间求和望远镜相消为 S(l)+S(l+1)-S(r+1)-S(r+2)。按向下步数 d 枚举，S(h)=Σ C(n,d)C(n-d,d+h)。驱动时间 O(√mod+s(n+log mod))，空间 O(s(n+1))。

普通 NDEBUG 与 ASan/UBSan 各通过：

- 1418545 次 Pascal 递推/原稿安全域检查；模数含 1、素数幂、大素数、多个素因子的合数和 INT_MAX。
- 五种模数下预处理 N=100000，各 200000 次对称性压力检查。
- 完整头文件和准确纸面 API 程序各 4838 项 Python `math.comb` 任意精度真值，含中央组合数及 N=100000 的端点附近。
- 完整头文件和准确纸面 CF 驱动各 42 项独立逐步非负游走 DP 对照，另有四个大规模端点；包含两个官方样例。

完整 API 用法为 445，原题应用为 446。本轮没有新线上 AC；来源核对、本地对照及纸面程序测试均与线上验收分开记录。
