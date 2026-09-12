# AtCoder Library 对照与可抄写设计

依据 [issue #3](https://github.com/gsh20040816/CPCtemplate/issues/3)，固定参考版本 [`864245a00b00`](https://github.com/atcoder/ac-library/tree/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder)。许可为 CC0-1.0。本次检查覆盖 `atcoder/all` 中的 12 个公开模块及 6 个内部支持头文件；逐文件摘要见 [acl-coverage.json](acl-coverage.json)。

这是接口、分类与缺项审查，不把 ACL 的正确性或验证记录直接转移给本库。

## 分类和覆盖

| ACL 模块 | 分类 | 当前状态 | 本库对应 |
|---|---|---|---|
| [dsu](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/dsu.hpp) | 数据结构 | 功能已有，按用户约定保留 | [data_structure.hpp](../src/compact/data_structure.hpp) |
| [fenwicktree](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/fenwicktree.hpp) | 数据结构 | 基础功能已有，组合约束不同 | [data_structure.hpp](../src/compact/data_structure.hpp)、[number_theory.hpp](../src/compact/number_theory.hpp) |
| [segtree](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/segtree.hpp) | 数据结构 | 部分覆盖 | [data_structure.hpp](../src/compact/data_structure.hpp) |
| [lazysegtree](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/lazysegtree.hpp) | 数据结构 | 部分覆盖 | [affine_segment_tree.hpp](../src/compact/affine_segment_tree.hpp) |
| [math](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/math.hpp) | 数学 | 核心功能已有，范围需适配 | [number_theory.hpp](../src/compact/number_theory.hpp) |
| [modint](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/modint.hpp) | 数学 | 部分覆盖 | [number_theory.hpp](../src/compact/number_theory.hpp) |
| [convolution](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/convolution.hpp) | 数学 | 模卷积已有，精确整数卷积缺失 | [ntt_convolution.hpp](../src/compact/ntt_convolution.hpp)、[polynomial.hpp](../src/compact/polynomial.hpp) |
| [maxflow](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/maxflow.hpp) | 图论 | 主算法已有，部分编辑接口缺失 | [flow.hpp](../src/compact/flow.hpp) |
| [mincostflow](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/mincostflow.hpp) | 图论 | 主算法已有，费用曲线缺失 | [flow.hpp](../src/compact/flow.hpp) |
| [scc](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/scc.hpp) | 图论 | 核心功能已有 | [tarjan.hpp](../src/compact/tarjan.hpp)、[graph.hpp](../src/compact/graph.hpp) |
| [twosat](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/twosat.hpp) | 图论 | 核心功能已有 | [graph.hpp](../src/compact/graph.hpp) |
| [string](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/string.hpp) | 字符串 | 功能已有，复杂度与表示有差异 | [string.hpp](../src/compact/string.hpp)、[suffix_lcp.hpp](../src/compact/suffix_lcp.hpp) |

## 结构配合

以下箭头表示基础模块被上层使用。内部支持层用于理解依赖，不自动作为独立算法章节收录。

```mermaid
graph LR
  modint --> convolution
  internal_math --> modint
  internal_math --> math
  internal_scc --> scc
  internal_scc --> twosat
  internal_csr --> internal_scc
  internal_csr --> mincostflow
  internal_queue --> maxflow
  internal_queue --> mincostflow
  internal_bit --> segtree
  internal_bit --> lazysegtree
```

适合赛时借鉴的做法：

1. **把运算约定与树结构分开。** 通用线段树需要 op/e；懒标记还需要 mapping/composition/id。实现可以按题目删减，但先写明结合律、单位元与组合方向。
2. **组合顺序要用非交换例子校验。** 先做 `g(x)=2x+1`，再做 `f(x)=3x+4`，应得到 `6x+7`；反过来是 `6x+9`。仿射标签 `composition(f,g)` 必须对应前者。
3. **区间运算保持左右顺序。** 对矩阵乘法、字符串拼接等非交换 op，左右累积器不能交换；只有加法测试不能覆盖这个性质。
4. **把坐标与编号作为接口契约。** ACL 普遍使用 0-based/半开区间，本库有 1-based/闭区间。适配空区间时不能直接传入 `r-1` 而触发原接口断言。SCC 的编号方向、2-SAT 的真假编码与赋值不等式也必须整体校验。
5. **稳定原边编号有利于输出方案。** 本库 Dinic 返回正向残量边 ID，ACL 返回逻辑原边编号；二者不是可随意互换的同一种整数。修改边容量/流量必须同时维护正反残量。
6. **静态图可借鉴 CSR。** `vector` 扁平存储和起止偏移可减少小分配，适合 SCC 等静态建图；不直接套到需要增删边的接口。
7. **只带必要支持代码。** 了解 internal_bit、internal_math、internal_queue 等作用，优先使用选定 C++ 标准提供的简短设施；不把兼容旧编译器的全部工程分支搬入可抄写正文。
8. **保持用户指定版本。** #2 中的 dsu 保留指定合并方向与 bool 返回值，不用 ACL 的按大小合并/返回根接口覆盖它。

## 逐模块差异

### dsu

ACL 返回合并后的根并采用按大小合并；本库按用户 #2 回复保留 bool merge、指定根连接方向和 fa/sz。双方均能给出 groups，不能用 ACL 版本覆盖用户指定实现。

### fenwicktree

ACL 为 0-based 点更新、半开区间和；本库为 1-based，另有仅适用于有序频数的 kth。Fenwick<ModInt> 的 add/sum 当前因缺少 operator+= 无法编译，已留可复现实例。

后续项：ModInt 复合赋值运算符与 Fenwick 的组合。

### segtree

当前有专门的区间加/区间和实现，不是任意幺半群线段树。ACL 双向累积保持 op 顺序，可支持非交换运算。

后续项：通用 op/e 点修改区间聚合；max_right/min_left 单调谓词边界搜索。

### lazysegtree

当前仿射线段树是具体实例。ACL 将 S/op/e 与 F/mapping/composition/id 分离，composition(f,g) 表示先 g 后 f；当前库尚无这套通用映射接口。

后续项：通用作用幺半群懒标记；带懒标记的 max_right/min_left。

### math

power、inverse、crt、floor_sum 已存在。ACL crt 批量返回 pair，本库原位逐条合并；ACL floor_sum 的 n,m 范围到 2^32 且溢出取模2^64，本库说明范围较小并返回精确 int128，不能直接宣称契约完全相同。

后续项：逐项核对 floor_sum 的边界范围及溢出语义。

### modint

当前 ModInt 支持固定模数算术，inv 按素数模数约定。ACL 静态合数模逆采用 inv_gcd，另有按 id 区分的动态模数类型；小类型及 unsigned 内部存储与溢出界不能只抄一半。

后续项：运行时模数类型；静态合数模数的单位元求逆契约；复合赋值等算术互操作。

### convolution

已有参数化素数模 NTT 卷积。ACL convolution_ll 返回有符号64位精确系数，采用三模重构并限制结果范围；单模卷积或把结果随意取模不能替代。

后续项：convolution_ll 等精确有符号整数卷积封装。

### maxflow

Dinic 已有加边、最大流、used 和 cut；ACL 以稳定逻辑边号公开 get_edge/edges/change_edge。当前没有按容量与流量成对修改正反残量的受约束接口。

后续项：change_edge 及对应残量不变量验证。

### mincostflow

当前 flow 返回最终流量和 int128 费用，初始负费用边也有单独契约。ACL 要求初始 cost 非负并提供 slope；两者不能混写成本域和重入条件。

后续项：最小费用随流量变化的 slope 折点输出。

### scc

ACL 通过 internal_scc 共享实现并输出拓扑顺序分组。本库有逆拓扑编号的 Tarjan 与正向编号的 Kosaraju，已对 QOJ906 适配；编号方向必须保留在组合说明中。

### twosat

本库 TwoSAT 已复用 SCC。ACL 的变量编号、真假节点编码与比较方向应整体核对；不能仅替换 SCC 类型或照抄答案不等式。

### string

后缀数组、LCP 和 Z 已有。ACL 用 SA-IS，本库用倍增；ACL LCP 长 n-1，本库长度 n 且首项0；两者 Z[0] 均取 n。SA-IS 是性能/复杂度上的未实现替代，不是后缀数组功能全缺。

后续项：SA-IS 线性后缀数组实现尚无。

## 已复现的组合缺口

当前 `Fenwick<ModInt<998244353>>` 的 add/sum 无法编译，原因是 ModInt 没有复合赋值 `operator+=`。这说明两份模板各自通过测试，不能自动证明它们能直接组合。

复现实例：[fenwick_modint.cpp](../verification/probes/fenwick_modint.cpp)；[编译诊断](../verification/acl-fenwick-modint-probe.txt)。这是预期失败的兼容性审查，未放入“算法测试通过”记录。后续应补充算术互操作并用模数下的区间和参考验证；模数和仍不适合 Fenwick 的 kth 顺序统计。

## 后续实施顺序

与 #1 的模板题清单对齐后，优先处理可复现的组合缺口和通用线段树边界搜索，再补 slope、精确整数卷积与动态模数。SA-IS 属于性能/复杂度替代，不把已验证的倍增后缀数组标为缺失。每项仍须独立题目、边界和性能验证。
