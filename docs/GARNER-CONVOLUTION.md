# 三模 NTT 与 Garner 的正式卷积用法

本批只补 issue #1 / #12 的正式使用示例：[`example-213`](usage/example-213.cpp) 对应 [Library Checker Convolution (Mod 1,000,000,007)](https://judge.yosupo.jp/problem/convolution_mod_1000000007)。新增[完整驱动](../verify/library_checker/convolution_mod_1000000007.garner.compact.cpp)，复用既有 `NttConvolution`、`ModInt` 和 `garner`，不新增算法条目、不修改算法核心，也不借用 `convolution_i64`。

## 题目与输入输出

固定上游版本为 [`e64660561a995c357cdc61ddee1bde68b80528db`](https://github.com/yosupo06/library-checker-problems/tree/e64660561a995c357cdc61ddee1bde68b80528db/convolution/convolution_mod_1000000007)：

- [题面](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/convolution/convolution_mod_1000000007/task.md)、[参数](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/convolution/convolution_mod_1000000007/info.toml)、[verifier](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/convolution/convolution_mod_1000000007/verifier.cpp)共同限定 `1≤n,m≤524288`，`0≤a[i],b[i]<1000000007`
- 单组输入为 `n m`、全部 `a`、全部 `b`；下标从 0 开始，系数按升幂排列
- 输出恰好 `n+m−1` 个标准模数代表，包括高次端零；用空格分隔，最后换行。长度 1、全零、多项式有前导或末尾零均是合法输入
- 本驱动按正式非空输入契约编写，未把空数组、负系数或未归一化整数输入登记为正式题支持范围

## 为什么三模结果足够

令目标模数 `q=1000000007`，先考虑取模之前的真实整数系数

`C[k]=Σ(i+j=k) a[i]·b[j]`。

每个系数至多含 `min(n,m)` 个非负乘积，故

`0≤C[k]≤524288×1000000006²=524288006291456018874368`。

选择两两互素的 NTT 素数

`p₁=167772161`、`p₂=469762049`、`p₃=1224736769`，

它们的乘积为

`P=96525171769480128904560641 > 524288006291456018874368`。

三次 NTT 得到 `C[k] mod pᵢ`。CRT 在 `[0,P)` 内的唯一代表因此就是 `C[k]` 本身，调用现有 `garner(r,p,q)` 后得到 `C[k] mod q`，恰好是答案。

这里不可省略严格的系数界：Garner 的通用接口只返回**最小非负 CRT 代表再对 target 取余**，并不能从三组余数恢复任意大小的原整数。`C` 与 `C+P` 有完全相同的三模余数，但它们对 `q` 的余数不同，因为 `P` 不被 `q` 整除。输入模数两两互素并不单独保证任意模卷积正确；换输入范围或长度时必须重新核对系数界与 NTT 容量。

本题最大真实系数超过 signed64。把三个 NTT 的结果交给只保证 signed64 真值的 `convolution_i64`，或者先用 `long long` 拼完整 CRT 值再取模，都不能作为这里的合法替代。现有 Garner 逐层处理混合进制，只使用模意义的中间量，不需要构造 `P` 或 `C[k]`；其通用契约也不要求全部模数乘积装入 int128。

## 容量、类型与抄写依赖

- 三个素数均以 `3` 为原根；`pᵢ−1` 分别为 `5×2^25`、`7×2^26`、`73×2^24`，公共二次幂变换容量为 `2^24`
- 正式输入的输出长度最大为 `1048575=2^20−1`，补齐后的 NTT 长度最大只需 `2^20`，在三者容量内。这不是声称已实测 `2^24` 的完整卷积
- 原数组保留为 `vector<int>`；短辅助函数 `conv<p>` 使用迭代器构造 `NttConvolution<p>::Poly`，每项经 `ModInt<p>` 构造器归一化。不能直接把原输入写进较小 NTT 模数的公开 `v` 成员，因为合法题目输入可以大于该模数
- 现有 `ModInt` 的加减先转 `long long`，乘法用 `1LL*v*b.v`；最大素数下 `(1224736769−1)^2<2^63−1`，无需改写成新的模整数实现
- 三份结果分别有自己的 `ModInt<p>` 类型。每次把相同下标的三个 `.v` 写入一个复用的长度 3 `vector<long long> r`，再调用既有 `garner`。循环外保留同序模数数组，不为每个系数另造外层余数数组
- `garner` 本体仍按原实现为每个系数分配混合进制工作数组并求逆；没有新增跨系数缓存、专用 CRT 算法或全局多模框架
- 抄写依赖为 `ModInt → NttConvolution` 和 `extended_gcd → mod_inverse → garner` 两条链。实际文件包括关系保留原有兼容入口，不改底层组织
- `// BEGIN USAGE` 后的 `template <int p>`、`auto conv(...)` 和完整 `main` 一起打印；`configuration_functions: ["conv"]` 是使用处短转换函数的登记，不是新增核心算法

令 `s=n+m−1`、`L` 为覆盖 `s` 的最小二次幂。三次现有卷积耗时 `O(L log L)`；通用 Garner 对每个系数处理 3 个固定模数，按其接口一般界为 `O(s·(3²+3 log p_max))`。由于素数固定，常用整体记法为 `O(L log L)`。额外空间 `O(L+n+m)`；三份结果与两份输入、当前 NTT 工作空间同时存在，但不存储完整真值系数或所有位置的余数向量。

## 独立验证

[`tests/garner_convolution.py`](../tests/garner_convolution.py) 不使用库内任何卷积来生成预期答案。普通和 ASan/UBSan 模式各完成同样的 426 组完整驱动输入：

1. 6 组明确边界，196 组长度 1..3 的二元数组两两全枚举，160 组固定种子随机输入。预期先用 Python 任意精度整数做朴素卷积，最后才对目标模数取余
2. 对 `2^1` 至 `2^19` 的每个二次幂，分别测试输出长度 `2^k−1`、`2^k`、`2^k+1`，共 57 组。高值常数数组的精确答案由三角形或梯形重叠项数给出，覆盖变换补齐的各级边界
3. 7 组至少有一个长度达到 524288 的输入：双最大高值常数、相邻不等长高值常数、零乘随机稠密数组、多个冲激、左标量、右标量、随机稠密数组乘内部冲激。分别使用重叠计数、零恒等式、有限个显式乘积、逐项标量乘法与平移闭式核对**全部**输出

单独的 [`tests/garner_convolution_core.cpp`](../tests/garner_convolution_core.cpp) 只是协议适配器，调用实际 `garner` 和 `garner_digits`；Python 另做 428 组通用 Garner 验证，不把固定三模卷积的正式题目覆盖外推成全部通用接口都获在线验证：

- 直接 CRT 求和公式用 Python 任意精度整数与独立 `pow(a,-1,m)` 得到规范解，再反复 `divmod` 得到混合进制各位，核对实际接口的答案、各位、范围与原同余式
- 含空输入、模数 1、signed64 余数极值、目标 1、与输入模数共享因子的目标、`LLONG_MAX` 目标及 400 组两两互素随机模数组合；成功调用还检查两个输入数组未变
- 1000 个素数的乘积有 **11271 bits**，远超过 int128；仍比较实际 Garner 输出和全部混合进制各位。这是通用核心的独立本地证据，与本题只有 3 个模数的证据分开记录
- 6 组不互素模数组合即使余数全部为 0、方程相容也必须抛 `invalid_argument`，目标为 1 时同样拒绝
- 脚本独立试除核对三素数，按 `pᵢ−1` 的全部素因子验证原根阶，并检查上述系数界和 `C`/`C+P` 别名反例

执行命令：

```sh
python3 tests/garner_convolution.py
python3 tests/garner_convolution.py --sanitize
```

结果为 [`verification/garner-convolution-normal.json`](../verification/garner-convolution-normal.json) 和 [`verification/garner-convolution-sanitizer.json`](../verification/garner-convolution-sanitizer.json)。两个报告绑定测试脚本、协议适配器、驱动、展开后的完整程序、全部递归本地依赖和二进制 SHA256，逐例记录输入/预期/实际输出哈希、退出码与本机用时。每个受测进程上限 180 秒；失败立即留存部分报告和当前输入、输出、诊断文件，不把未跑完的集合记为通过。旧的 classic 依赖测试没有修改，本批的新证据直接测试当前 compact 接口。

ASan/UBSan 用 `-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer`，`ASAN_OPTIONS=detect_leaks=0:halt_on_error=1` 与 `UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1`。本批全部独立测试在默认 quarantine 配置成功，**没有使用 32 MiB / 128 KiB 的降配重试**；LSan 明确关闭，因此不声称泄漏检查通过。脚本提供显式 `--sanitizer-profile bounded` 以便未来资源问题下有记录地重试，不能将两种配置的证据混称。

## 未改实现的本机测量

先运行正式最大规模，再决定是否需要额外缓存。本批使用 `g++ (Debian 14.2.0-19) 14.2.0`，普通模式 `-O2`。最终独立普通报告中的双大型输入耗时约 `1.35–1.54 s`，标量乘最大数组约 `0.64–0.68 s`；ASan/UBSan 的双大型输入约 `4.06–4.22 s`，标量情形约 `1.93–2.05 s`。据此保留既有逐系数 Garner，不因预想的常数开销引入新框架。

内存有两种明确不同的记录：`wait4` 的进程生命周期峰值可能含 Python 启动器在 `exec` 前继承的内存，不能冒充候选程序独占峰值；脚本另按 10 ms 间隔，在 `/proc/PID/exe` 确认已切换到受测程序后采样 `VmHWM`。最大普通实例采到约 26 MiB，sanitizer 约 241 MiB，但采样值只是候选峰值的下界，不能据此作严格内存上限承诺。

这些数字只描述本机、当前编译器和对应开关。官方 `info.toml` 的时限为 10 秒，也不能把这里的合成输入、本机计时或 sanitizer 用时直接写成评测机限时通过、性能排名或线上 AC。

固定版本全部 48 组官方输入、实际官方 checker、精确打印程序及负对照由独立官方数据报告负责。仅编译、上述自造输入通过、旧在线快照或依赖模板的历史 AC，都不能替代这一层证据；本批没有新增线上提交记录。

## 固定官方数据复核

精确打印的 example-213 在固定上游版本 `e64660561a995c357cdc61ddee1bde68b80528db` 的全部 **48** 组数据上，普通模式和 ASan/UBSan 模式均通过实际官方 checker。96 个输入/答案哈希匹配，48 个输入通过官方 verifier，并确认 checker 拒绝故意错误的输出。sanitizer 使用默认 quarantine、关闭 LSan，无候选程序失败或降配重试。最慢单例本机墙钟时间分别为 1.427266 秒和 4.217434 秒；官方运行器的 RSS 是含启动阶段的进程生命周期峰值，不能称为候选程序独占内存。

汇总见 [`verification/garner-official-summary.json`](../verification/garner-official-summary.json)，来源见 [`verification/garner-official-provenance.json`](../verification/garner-official-provenance.json)。准备阶段的文件偏移错误已经修复并独立保留；它发生在候选程序执行之前，不计为候选失败。这些是本地官方数据结果，不是线上 AC。
