# 斯特林数：整行、整列与反演（issue 26）

issue 18 曾完成四种行列求解，但 issue 21 精简时删去了 `stirling_column.hpp`（记录为并入 `stirling.hpp`，实际未并入），打印册只剩整列原理。本批把两个整列函数恢复进 `src/compact/stirling.hpp`，并按“定义与性质 → 行列求解及代码 → 斯特林反演与应用”重排该节。

## 接口

| 需求 | 函数 | 方法 | 复杂度 | 模数 |
| --- | --- | --- | --- | --- |
| 第一类整行 c(n,0..n) | `stirling_first_row<mod,primitive>(n)` | 倍增 + 泰勒平移 | O(n log n) | 任意 NTT 素数 |
| 第一类整列 c(0..N,k) | `stirling_first_column(N,k)` | exp(k log A)，A=-log(1-x)/x | O(N+m log m) | 998244353 |
| 第二类整行 S(n,0..m) | `stirling_second_row<mod,primitive>(n,m)` | 容斥一次卷积 | O(m log m + m log mod) | 任意 NTT 素数 |
| 第二类整列 S(0..N,k) | `stirling_second_column(N,k)` | exp(k log A)，A=(e^x-1)/x | O(N+m log m) | 998244353 |

m=N-k+1。整列直接调用 `FpsFunctions::log/exp`，不再经过 `FpsPower`，依赖链为 FpsFunctions → FpsInverse → NttConvolution → ModInt。k>N 返回全零列，k=0 只有第零项为 1，0≤N<2^22。

## 正文

`docs/knowledge-stirling.tex`：组合意义、递推与边界、有/无符号约定、普通幂与上升/下降阶乘幂的六向转换、生成函数；四种算法的推导与选择表；两对反演公式（求和范围、符号）、矩阵证明、EGF 复合形式、手算检查、“按块数赋权”的建模、以及自然数幂和的完整代码示例。各函数后紧随 Library Checker / 洛谷模板题用法（example-54、433、53、434）。

## 验证

- `tests/stirling_columns.cpp`：递推表核对 69158 个行列系数、两类矩阵互逆、50 万规模边界；`tests/stirling_columns.py` 普通与 ASan/UBSan，`tests/stirling_columns_copy.py` 只用 catalog 抄写段重编译。
- `tests/stirling_columns_official.py`：固定提交 e6466056 的两题各 14 组官方生成数据与官方 checker，普通/ASan 均接受，最大单点约 0.43 秒；错误输出被拒绝。
- `tests/stirling_inversion.py`：抽出 TeX 中印刷的 `power_sum` 原样编译，与直接求和及 k≤3 闭式（n=10^18）核对；两对反演在 n≤40 随机序列上双向核对。
- 完整用法 example-433/434/53/54 通过 `tests/usage_examples.py --only ... --refresh`。

旧版整列的 Library Checker AC 409999/410000 属于已退役的 FpsPower 实现，不计作当前源码证据；当前两份 fixed-k 驱动已列入 `verification/pending-oj.md`，待在线提交。
