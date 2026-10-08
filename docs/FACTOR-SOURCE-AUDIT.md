# kuangbin 合数分解片段来源核对

§2.2 的完整37行片段已与既有 `PollardRho::factor` 核对，不新增另一份试除模板。原稿分解循环有素数表末尾缺陷，不能将它的 `long long` 参数理解为支持所有正64位整数。

## 原稿边界

原稿印刷27页（物理29页），固定 PDF SHA256 为 `f1c90eae0c3fb309d58a14b050fe12b239efb474b033299a547b55646c2768ad`。夹具 `tests/fixtures/factor_source/kuangbin.cpp` 保留全部37行，仅移除行号和缩进；已目视核对，没有修补算法。

筛法把素数列表与筛法标记存入同一数组。实测 `prime[0]=1229`、`prime[1229]=9973`、`prime[1230]=1`。分解循环只有 `prime[i] <= tmp / prime[i]`，缺少 `i <= prime[0]` 和余数为1时停止的条件。

输入 `9973²=99460729` 时，处理9973后余数成为1，下轮读到标记1，条件仍成立。随后不断除以1，余数不变，指数计数持续增加；继续执行最终还会发生有符号计数溢出。普通及消毒器构建的原程序均在独立2秒诊断运行中超时，报告不将超时冒充已检测到的UBSan溢出。

本批原程序数值比较限定 `1 <= n < 9973²`。此时任何剩余因子的平方根均小于9973，循环会在读取列表外标记之前停止。此范围仅用于安全审计原片段，不是新接口限制。

## 现有接口对应

`PollardRho::factor(n)` 接收正 `uint64`，返回升序且含重数的质因子；n=1返回空vector。连续相同元素分组即可得到原稿 `factor[i][0]` 与 `factor[i][1]` 的质数、指数对，分组数量对应 `fatCnt`。它不依赖10000范围的静态素数表。

```cpp
auto values = solver.factor(n);
vector<pair<unsigned long long, int>> groups;
for (auto p : values)
{
    if (groups.empty() || groups.back().first != p)
        groups.push_back({p, 1});
    else
        groups.back().second++;
}
```

仅需含重数列表时直接使用返回vector，不必额外分组。分解使用随机重试，不能由本地通过推导出固定最坏运行时间或评测速度排名。0不属于接口定义域。

## 验证范围

`tests/factor_source_audit.py` 对1..10000、400组随机正整数和6组边界/幂/半素数，共10406组输入使用独立试除生成完整质数—指数对。完整原程序与当前header、NDEBUG、实际抄写依赖组件的输出全部一致，并通过普通及ASan/UBSan构建。

额外7组只测试替代实现，包括9973²、10007²、9973×10007、2⁶³、3⁴⁰、5²⁷和2⁶⁴−1；各预期质因子独立试除判素，乘积重构输入。不把这些超出安全对照域的用例归为原程序通过。

报告 `verification/factor-source-normal.json` 与 `verification/factor-source-sanitizer.json` 记录代码哈希、输入数量及原稿诊断。§2.2 改为local-tested，表示原片段接口已由验证过的组件替代；不是原稿无缺陷，也不是新增线上AC。
