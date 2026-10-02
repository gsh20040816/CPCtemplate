# 任意点多项式快速插值

新增无状态函数 [`polynomial_interpolation`](../src/compact/polynomial_interpolation.hpp)，补 issue #1 / #12 的任意互异点快速系数插值。正式使用程序对应 [Library Checker Polynomial Interpolation](https://judge.yosupo.jp/problem/polynomial_interpolation)，登记为 `example-212`。复用现有 `MultipointEvaluation` 的乘积树和求值接口，不修改其实现或任何底层依赖，也不增加通用 FPS 框架。

## 接口与约定

```cpp
using Poly = MultipointEvaluation::Poly;
Poly x = {0, 1, 2}, y = {1, 6, 17};
auto f = polynomial_interpolation(x, y); // optional<Poly>，值为 {1, 2, 3}
auto constant = polynomial_interpolation(Poly{2, 0, 1}, Poly{9, 9, 9});
// constant 的值为 {9, 0, 0}，不去掉高次零
```

- 固定素数模数 `p=998244353`；`Poly=vector<ModInt<998244353>>`，下标从 0 开始，输出系数按升幂排列
- `polynomial_interpolation(const Poly &x, const Poly &y)` 不修改两个输入；每次调用独立构造并销毁工作数据，多组测试无额外重置步骤
- 令 `m=x.size()`，成功返回恰好 `m` 项、次数小于 `m` 的唯一插值多项式，包括高次端的零系数；所有点值为零时仍返回 `m` 个零
- `x.size()!=y.size()` 或横坐标在模意义下重复时返回 `nullopt`。两个空数组返回有值的空向量，不能把它与失败混淆
- 重复横坐标即使对应点值相同也拒绝；本接口不求非唯一解，不实现重节点的导数/Hermite 插值。**独立的 `MultipointEvaluation::evaluate` 仍然允许重复点**
- 原始整数先经过 `ModInt` 构造器归一化，例如 `−1` 与 `998244352`、`0` 与 `998244353` 均是重复横坐标。不要绕过构造器写入未归一化的公开 `v` 成员
- 长度上限是调用前提，由 `assert` 检查；超容量不属于 `nullopt` 表示的两类失败。空输入及非法数据的可选返回契约由核心测试验证，正式题保证非空合法输入

## 乘积树与递归合并

设根多项式 `P(X)=∏(X−x[i])`。对互异点，有

`P′(x[i])=∏(x[i]−x[j]) (j≠i)`，故这些值都非零。先直接从树根系数计算导数，再调用同一棵树的 `evaluate` 得到全部 `P′(x[i])`，令 `w[i]=y[i]/P′(x[i])`。代码在任何逐点求逆前检查所有导数值：若出现零，恰说明存在重复横坐标，返回 `nullopt`，不会对零调用 `inv()`。

叶子返回常数 `{w[i]}`。若左右区间乘积分别为 `P_L`、`P_R`，左右递归答案分别为 `A_L`、`A_R`，父节点返回

`A=A_L·P_R+A_R·P_L`。

归纳可得，任一节点保存其区间内 `Σ w[i]·∏(X−x[j]) (j≠i)`；树根即拉格朗日插值公式。代入 `x[i]` 后只有第 `i` 项非零，值为 `y[i]`；次数小于 `m`，结合互异点条件得到唯一性。合并时两个乘积都恰好有当前区间长度项，直接相加而不去高次零，因此自然保留完整的 `m` 项输出。

递归通过函数内的短辅助 lambda 完成，没有外部状态。输入长度为 1 时导数是常数 1，直接返回对应点值；空输入在构建乘积树前返回。

## 依赖、容量与复杂度

抄写依赖链：`ModInt → NttConvolution → FpsInverse → PolynomialDivision → MultipointEvaluation → polynomial_interpolation`。导数只需要 `d[i−1]=i·P[i]`，无需引入 `FpsFunctions`；本测试额外包含该组件仅用于同翻译单元兼容验证。

统一充分容量条件为 `0≤m≤2^22−1`，与既有乘积树一致：

- 树根有 `m+1≤2^22` 项，导数有 `m` 项；每次带余除法的输入满足既有 `2^22` 项上限
- 既有反转求逆除法的完整卷积长度在 NTT 容量 `2^23` 内。构树乘积至多 `m+1` 项；插值合并的两个乘积分别至多 `m` 项，不引入更紧的卷积限制
- `4*max(1,m)` 的树节点数组及递归区间下标运算均可由 `int` 表示；系数乘法继续用 `long long`，`(998244353−1)^2<2^63−1`

这些是代数、下标与底层卷积的充分条件，不是时间/内存承诺。官方规模最大 `m=131072`，本批最大实测也为该规模；没有实测 `2^22−1` 个点的完整插值，不能把容量界写成已通过的规模。

- 构树、根导数求值和递归合并合计 `O(m log²(m+1))` 时间
- 每个权重仍独立调用既有模幂 `inv()`，需要额外 `O(m log p)` 时间；没有使用批量逆元优化，完整时间界为 `O(m log²(m+1)+m log p+1)`
- 保存的乘积树占 `O(m log(m+1)+1)` 空间；导数、权重和深度优先合并的临时多项式总量为 `O(m+1)`，递归深度 `O(log(m+1))`
- 总空间 `O(m log(m+1)+1)`；每次调用重新建树，不声称跨调用缓存或摊还加速

## 正式题目与覆盖边界

[官方题面](https://raw.githubusercontent.com/yosupo06/library-checker-problems/master/polynomial/polynomial_interpolation/task.md)和 [verifier](https://raw.githubusercontent.com/yosupo06/library-checker-problems/master/polynomial/polynomial_interpolation/verifier.cpp)要求 `1≤m≤131072`、`0≤x[i],y[i]<998244353`，横坐标两两不同。完整驱动 [`polynomial_interpolation.compact.cpp`](../verify/library_checker/polynomial_interpolation.compact.cpp) 依次读取 `m`、全部横坐标、全部点值，输出恰好 `m` 个标准模数代表及结尾换行；不省略零系数。

本组件返回全部系数，既有 `Lagrange` 查询接口、等比点求值 `chirp_z` 和一般任意点求值各自保留。新增组件不表示所有 FPS 操作、重节点插值、其他模数或运行时模数已经覆盖。QOJ 622 的输入边界和线上提交也不是本驱动的验证结论。

## 独立核心验证

[`tests/polynomial_interpolation.cpp`](../tests/polynomial_interpolation.cpp) 的两条小规模参考路径均不依赖新插值实现或乘积树求值：

- 800 组任意点值，独立整数 Vandermonde 矩阵构造及高斯消元得到系数；矩阵运算和求逆用测试内整数取模/模幂
- 独立生成已知系数，再由整数 Horner 生成点值并核对恢复后的全部系数。含长度 0..7 的二元系数全枚举、1000 组随机长度与系数、二次幂前后及奇数长度、signed64 构造输入、空/零/常数多项式与高次零
- 小规模阶段共 2126 次系数恢复、256 次明确拒绝，包含长度不符、同值/异值重复横坐标、取模后重复、1025 个全相等点以及 2049 个点中仅一对重复。每次成功及失败都核对输入数组未变
- 官方最大 `m=131072`：全一系数、交替正负系数分别用独立整数有限几何和生成全部点值；常数多项式核对 131071 个高次零完整保留。横坐标为打乱后的互异整数，包含 `0/1/−1`
- `m=65537` 的稀疏高次多项式以单项式模幂和生成点值；`m=65535` 的全零多项式检查非二次幂划分与完整零输出
- 同一翻译单元调用插值、允许重复点的求值、除法、FPS 导数/逆以及 `chirp_z`。每项用独立整数参考或明确系数核对，未把求值/插值互相往返当作唯一正确性证据

两个模式使用完全相同的固定随机种子与语料，均按七个阶段拆成独立进程，避免多个昂贵家族在一个 sanitizer 进程中累积临时分配记录。执行命令：

```sh
mkdir -p build/polynomial-interpolation
g++ -std=c++20 -O2 -Wall -Wextra -Wshadow tests/polynomial_interpolation.cpp -o build/polynomial-interpolation/core-normal
for stage in small dense alternating sparse zero constant composition; do
    build/polynomial-interpolation/core-normal "$stage"
done
g++ -std=c++20 -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -Wall -Wextra -Wshadow tests/polynomial_interpolation.cpp -o build/polynomial-interpolation/core-sanitizer
for stage in small dense alternating sparse zero constant composition; do
    ASAN_OPTIONS=detect_leaks=0:halt_on_error=1:quarantine_size_mb=32:thread_local_quarantine_size_kb=128 UBSAN_OPTIONS=halt_on_error=1 build/polynomial-interpolation/core-sanitizer "$stage"
done
```

核心报告为 `verification/polynomial-interpolation-core-normal.json` 和 `verification/polynomial-interpolation-core-sanitizer.json`，绑定测试、完整本地依赖、驱动及二进制哈希，记录各阶段退出码、输出、编译器与本机用时。它们仅证明列明核心测试；完整驱动、精确打印文本和固定官方数据由独立报告负责。关闭泄漏检查时不声称完成泄漏验证；局部双模式通过也不能冒充整个仓库回归、在线 AC、评测机限时通过或速度排名。

首次 sanitizer 执行的小规模阶段通过，随后单独的最大稠密阶段被 `SIGKILL` 终止，未留下 ASan/UBSan 诊断；未运行其余阶段。`verification/polynomial-interpolation-core-sanitizer-incomplete.json` 保留这次不完整结果，不把它计作通过。原因未确认，运行环境未提供可读的 cgroup 内存事件计数。重试不修改核心、驱动或测试语料，显式设定 ASan 全局 quarantine 为 32 MiB、线程本地为 128 KiB，并继续逐阶段执行；这些设置仍启用地址/未定义行为检测，但释放后内存的保留窗口与默认配置不同。实际选项逐项写入报告。


## 完整程序与固定官方数据

独立脚本 `tests/polynomial_interpolation_application.py` 分别测试完整驱动和精确打印的 example-212。每种程序、每种模式各 341 组，包括 96 个任意 y 的 Vandermonde 消元系统、171 个高次零保留案例和 7 个 n=131072 的解析输入。普通及 ASan/UBSan 均通过；见 `verification/interpolation-application*.json`，测试不使用本库求值/NTT产生预期答案。

精确打印程序通过固定上游 `e64660561a995c357cdc61ddee1bde68b80528db` 的全部 9 组官方数据，普通与 ASan/UBSan 均由实际官方 checker 接受；独立驱动另通过官方普通模式。18 份生成输入/答案哈希与上游清单相同，全部输入通过官方 verifier；格式错误及长度正确但数值错误的两个输出负对照均被拒绝。见 `verification/interpolation-official*.json`。这些结果不冒充线上 AC、OJ 限时或速度排名。

中央精确打印程序也通过五组规范用例双模式执行。发布本批时为 206 算法、212 份用法：149 项正式题、35 项仅应用、4 项仅 API、18 项待补。OI Wiki 联合页面仅按实际固定模数契约记为部分覆盖；未用新增组件抹去其他来源范围或线上待验证项。

数学册按先求值后插值排列，核心与完整 main 各自同页；数学册物理页93–96、总册131–134实际渲染检查，字号不变。修复 U+2032 字体缺字后，八册最终日志无警告；1048 组依赖名称/页码/章节与16处跨册跳转通过。数学册及总册变更，其余六册比对文本、注释和目标后恢复原PDF字节。见 `verification/interpolation-layout.json`。本批没有重新执行全仓完整双模式回归，历史全量收据保留原适用范围。
