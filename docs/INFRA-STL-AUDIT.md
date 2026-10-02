# Infra 标准库增补审计

日期：2026-10-02。范围：issue #9 中当前模板实际使用的 C++20 接口与本地环境说明。此次没有把 OI Wiki 的比赛相关、工具软件、语言基础三板块标为全覆盖，也没有新增 OJ AC 证据。

## 从源码补缺

| 源码用法 | 本册补充的调用约定 | 执行检查 |
|---|---|---|
| `src/compact/fft.hpp` 的 `ComplexFFT`；`convolution_fft.hpp` 提取实部 | `complex<long double>` 的实虚部、共轭；`abs` 为模长、`norm` 为模长平方，与 `RealPlane::norm` 的长度含义不同；不放宽浮点卷积范围 | 3+4i、零、乘共轭、乘 i 后逆变换 |
| `src/compact/string.hpp` 的 `SuffixAutomaton::counts` 长度桶 | `partial_sum` 累加器由输入值类型决定；宽输出不会扩大中间类型；可原地写回，空输入不写输出 | 30亿宽前缀和；回调静态检查输入累加器仍为 int；空/单元素区间 |
| `src/compact/dynamic_modint.hpp` 的扩展欧几里得；`second_mst.hpp` 的权值/编号排序 | `tie` 保存引用；右侧值 `pair` 保存更新前的值；引用元组互相赋值不能代替 `swap` | 引用随原变量变化、值快照保持、欧几里得一步及重复权值排序 |
| `src/compact/division_tree.hpp`、`wavelet_matrix.hpp`、`mo_secondary.hpp` | 无符号位操作；零的位宽与前导/后缀零计数不同；保护零再减一；64位块掩码不移位64 | 0..65535 与独立除法/余数参考逐一核对；最高位、全1、0..63位掩码与层数边界 |
| `src/compact/enclosing_circle.hpp` 的 `shuffle` | 打乱保留元素和重复次数；同种子复现还依赖输入、调用顺序和库实现，不能承诺跨标准库逐项一致 | 空、单元素、重复元素和不同长度的排列性质、同环境重放；分布上下界 |

已存在的 move、容器区间、PBDS 句柄迁移示例保留。排序部分仅补 NaN 导致比较等价关系不传递的提示，没有复制一节通用二分百科。数值部分补“先提升再乘”的类型检查，不故意执行有符号溢出。测试也不会把 NaN 送入不满足前提的排序，或调用零参数 GCC clz/ctz。

## 来源

技术约定依据以下一手资料；当前草案可能展示更晚标准的声明，本册示例仅编译使用 C++20 已有接口，不据此采用较新 API 或较新 constexpr 能力。

- [complex 分量](https://eel.is/c++draft/complex.members)、[模长与共轭](https://eel.is/c++draft/complex.value.ops)
- [accumulate](https://eel.is/c++draft/accumulate)、[partial_sum](https://eel.is/c++draft/partial.sum)、[算术类型转换](https://eel.is/c++draft/expr.arith.conv)
- [tuple 创建](https://eel.is/c++draft/tuple.creation)、[tuple 赋值](https://eel.is/c++draft/tuple.assign)
- [bit_width](https://eel.is/c++draft/bit.pow.two)、[位计数](https://eel.is/c++draft/bit.count)、[移位](https://eel.is/c++draft/expr.shift)、[GCC 位内建函数](https://gcc.gnu.org/onlinedocs/gcc/Bit-Operation-Builtins.html)
- [shuffle](https://eel.is/c++draft/alg.random.shuffle)、[分布算法由实现定义](https://eel.is/c++draft/rand.dist.general)
- [严格弱序](https://eel.is/c++draft/alg.sorting.general)、[浮点关系比较](https://eel.is/c++draft/expr.rel)

“跨库排列不保证相同”由 shuffle 未规定具体排列算法、分布生成算法由实现定义共同得出；测试只验证当前实现，不把有限样本当作均匀性证明。

## 环境与证据边界

- 编译器说明改为运行时选择：显式 `CXX` 优先，未设置时尝试 g++-16，再回退 g++，与 `tools/run_provenance.py` 一致
- Linux 栈说明改为继承硬上限内调整软上限；与 `tools/test.sh` 的实际设置、`test_baseline.py` 的计划/观测收据一致，不无条件要求 unlimited
- 增补前 `docs/infra-links.json` 与旧审计各有13项，旧说明的12已过期；增加三个模板入口后生成索引为16项。新 PDF 的命名目的地及印刷页码须单独重建审计，本聚焦检查不替代该步骤
- `tests/infra_examples.cpp` 普通模式与 ASan/UBSan 模式通过；实际编译器为 Debian GCC 14.2.0，未使用不存在的 g++-16
- 此环境中 LeakSanitizer 因 ptrace 限制报致命错误；通过的 ASan/UBSan 运行显式设置 `detect_leaks=0`，不宣称泄漏检查通过
- Python/Bash 示例通过，包括大整数、不可逆异常、列表浅复制、引号、diff返回1与pipefail

精确命令、输出、状态、编译器指纹及本次输入 SHA-256 见 [`verification/infra-contracts-20261002.json`](../verification/infra-contracts-20261002.json)。这是聚焦接口示例证据，不是全库回归、跨编译器兼容性或新 PDF 审计。没有运行 CI，也没有访问凭据、提交、推送或发表评论。
