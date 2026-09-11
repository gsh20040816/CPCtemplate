# 待在线评测

以下提交驱动尚无本库的新 AC 记录；列表由当前 verify/luogu 与 oj.json 对照生成。

- `verify/luogu/CF600E.classic.cpp`
- `verify/luogu/CF600E.compact.cpp`
- `verify/luogu/P2495.classic.cpp`
- `verify/luogu/P2495.compact.cpp`
- `verify/luogu/P3369.classic.cpp`
- `verify/luogu/P3369.splay.classic.cpp`
- `verify/luogu/P3369.splay.compact.cpp`
- `verify/luogu/P3373.classic.cpp`
- `verify/luogu/P3384.classic.cpp`
- `verify/luogu/P3384.compact.cpp`
- `verify/luogu/P3386.classic.cpp`
- `verify/luogu/P3386.compact.cpp`
- `verify/luogu/P3391.classic.cpp`
- `verify/luogu/P3391.compact.cpp`
- `verify/luogu/P3649.classic.cpp`
- `verify/luogu/P3649.compact.cpp`
- `verify/luogu/P3834.classic.cpp`
- `verify/luogu/P3834.compact.cpp`
- `verify/luogu/P3919.classic.cpp`
- `verify/luogu/P3919.compact.cpp`
- `verify/luogu/P5496.classic.cpp`
- `verify/luogu/P6113.classic.cpp`
- `verify/luogu/P6113.compact.cpp`

## 已解决的提交异常

- P8436、P3806 曾在旧页面的文件及文本提交入口返回 `The route object cannot be resolved`。2026-09-12 在新标签页重新提交后，两套版本均 AC；具体记录在 oj.json。错误原因尚未确定。
- P6113 动态版之前因 10 秒请求超时未生成记录，可在新标签页重试。
- 当前无待确认的验证码。后续出现验证码仍按工具要求当次确认。

OJ 只验证驱动实际调用的接口。点分治 P3806 只核验距离存在性，完整计数与零权等扩展仍由本地独立测试提供证据。

- `verify/luogu/P2495.classic.cpp` 与 `verify/luogu/P2495.compact.cpp`：已对实际打包程序做枚举删边验证，在线评测待完成。
- 2026-09-12 曾因 Mac 锁定暂停 UI；之后已可读取，但在准备 P3384 文件时工具报告用户改变了 Firefox 状态，已暂停输入，未提交。

- P3919 双风格已对打包程序验证随机版本分叉与查询编号；P3834 双风格打包程序已检查区间第 k 小。两类模板分别验证，不混用版本语义。

- P3384 双风格驱动已完成路径/子树加法及求和的本地组合测试，尚未在线提交；传统 HLD 的接口现为 Heavy_Light_Decomposition<N> + Init(n)。

- P3386 双风格驱动已完成本地检查。Hopcroft–Karp 匹配与最小点覆盖由独立穷举测试验证，尚未在线提交。

- P4779、P4782 双风格驱动已按官方题面核对输入输出，对四份实际打包程序分别完成 100 组独立随机检查；尚未在线提交。P4779 使用 Bellman–Ford 距离参照，P4782 枚举赋值并核验输出方案。接口级完整边界检查见 tests/graph_contracts.cpp。

- P6577 双风格驱动已准备；2026-09-12 动态版经 Firefox 新标签页上传并选择 C++20，提交返回 `The route object cannot be resolved`，刷新、重新上传重试仍同错，没有生成记录，也未出现验证码。两套实现已通过独立子集 DP 与方案证书检查，在线 AC 待补。

- P4720 双风格驱动已完成实际打包与 Python 精确组合数检查，尚未在线提交；算法级证据见 tests/exlucas.cpp，包括模数 1、素数幂、混合合数、下标最大值以及切换模数后的重算。

- P4781 双风格驱动已完成实际打包测试，以随机多项式直接求值为参照，尚未在线提交。连续横坐标模式与整数幂和应用另外由 tests/interpolation.cpp 验证，不计入 P4781 的 OJ 覆盖范围。
