# 动态仿射序列

## 解决的缺口

`SequenceTreap` 的有符号整数区间加、顺序反转和二进制取反继续保持原义；固定位置的仿射线段树也不承担插入或删除位置。本条独立给出 `AffineSequenceTreap<mod>`，在同一动态序列中支持插入、删除区间、顺序反转、模意义仿射修改和区间和。它复用 `ModInt`，不改已有树的接口或算术域。

正式目标是 [Library Checker Dynamic Sequence Range Affine Range Sum](https://judge.yosupo.jp/problem/dynamic_sequence_range_affine_range_sum)。固定版本 `e64660561a995c357cdc61ddee1bde68b80528db` 的题目要求初始长度和操作数各不超过 500000，模数为 998244353，仿射乘数允许为零。官方操作区间为 0-based 半开；使用代码将其转换为模板沿用的 1-based 闭区间。

## 使用契约

- `AffineSequenceTreap<mod> t(seed)` 建立空序列，默认模数 998244353，默认随机种子 712367821；`size()` 为当前长度
- `insert(k,x)` 在前 k 个元素之后插入；`0 <= k <= size()`，即 k 同时是新元素的 0-based 位置
- `erase(l,r)`、`reverse(l,r)`、`affine(l,r,b,c)`、`query(l,r)` 均要求非空的 1-based 闭区间，`1 <= l <= r <= size()`
- `affine` 将每个值改为 `b*x+c`，`query` 返回模整数，读取结果用 `.v`。`b=0` 是合法赋值操作，不能跳过；`reverse` 只反转顺序
- 删除最后一个元素或整个区间后允许为空，仍可插入。空对象可求 `size()` 和 `values()`，不能调用非空区间接口
- `values()` 递归导出当前顺序的 `vector<Z>`；它会下传标记，`query` 也会分裂、合并，因此二者不提供物理只读或并发读保证
- 正模数可为 1 或合数；本实现不做除法或求逆，既有 `ModInt` 的加乘使用 signed64 中间值，覆盖正 int 模数范围。传入 long long 值时通过构造器归一化，不直接改 `.v`
- 节点索引用 int，累计节点数、长度及相关索引须可表示且内存可用；官方 N+Q 上限至多分配 1000000 个非哨兵节点
- 使用 `t = AffineSequenceTreap<mod>(seed)` 重建空对象。默认复制会复制节点池、根及 RNG 状态，两个对象之后独立修改

`pull/apply/flip/push/split/merge/cut/collect` 是内部组合步骤，不是允许在任意根状态下随意调用的独立用户接口。`a` 与 `root` 暴露方便竞赛调试和预留容量，不应直接改写节点。

## 仿射标记与顺序

设节点尚未传下去的旧标记为 `u*x+v`，新修改为 `b*x+c`。新合成为 `b*u*x + (b*v+c)`，因此必须同时更新 `mul = b*mul` 与 `add = b*add+c`。只累加 add、颠倒复合方向、或把零乘数当成无标记都会出错。节点 val 与 sum 也立即更新，sum 的常数项是 `c*siz`。

顺序反转立即交换左右子树并翻转 rev；向子节点传播时仍执行交换。对整个区间统一施加同一仿射变换与顺序反转可交换，所以 push 可以先反转，再传仿射。但不同仿射变换一般不交换，必须保留新旧顺序。

## 构造、空间与随机化

沿用递归 split/merge 和 vector 节点池，没有模拟递归栈。按优先级合并维护随机 Treap 堆序；从空树逐个 insert 构建期望 O(N log(N+1))，单次动态操作期望 O(log(n+1))，导出 O(n)。这不是确定性最坏对数保证；递归深度最坏可为 n。固定种子便于复现，不保证抵御按已知优先级刻意构造的对抗操作。

删除只从活树摘除节点，不回收池中槽位，空间按累计插入次数计，不按当前存活长度计。驱动可预先 `reserve(N+Q+1)`，不预留也支持正常 vector 扩容。插入在 split 之前分配节点，递归分裂合并过程不分配，避免扩容使递归传入的节点字段引用失效。容量规划只是一项优化，不是正确性前提。

## 验证状态

- 独立核心 oracle：每模式 14799496 项检查，包括三值小序列穷举、480000 次随机动态操作、旧标记不下传时的非交换复合、乘数零、全部删除后重插、无 reserve 的扩容、复制隔离与重建。随机测试使用八种模数，另有模5穷举；含模1、合数和 INT_MAX，以及 long long 两端值的归一化。结构检查在副本上下传后独立重算堆序、大小和和，不提前清除原受测对象的待传标记。
- 独立大规模核心检查：500000 个初始节点与 500000 个区间查询，用反向等差序列的整数求和式作 oracle，并检查零乘数复合及删除全区间。每模式 500018 项检查；不是遍历全部可能输入的证明。
- 完整驱动：每模式、每程序形态各242个字面数组 oracle 数据集，覆盖正式输入语义、位置边界、连续非交换修改和没有输出的合法数据。分别编译完整驱动和精确打印代码。
- 固定官方数据：精确打印 example-214 的全部33组在普通和ASan/UBSan模式通过官方 verifier、输入/答案哈希匹配及实际checker；两种模式的错误数值输出负对照均被拒绝。打印程序与当前登记程序逐字节一致。

核心报告为 `verification/affine-sequence-oracle-{normal,sanitizer}-{small,max}.json`，完整驱动为 `verification/affine-sequence-application-{normal,sanitizer}.json`，官方报告为 `verification/affine-sequence-official-printed-{normal,sanitizer}.json`。运行时报告默认落在 build，归档副本放在 verification，避免测试改动 docs 导致全量回执失效。

本条新增测试使用默认 ASan quarantine，无降配重试，LSan明确关闭。普通官方单例本机最慢约3.428秒，sanitizer约10.694秒；后者不能拿来判定正常评测时限。所有计时是在共享主机上取得，官方辅助运行器记录的wait4 RSS包含启动前继承内存，不是候选程序独占内存测量。没有线上AC或排名声明。

此前 ede7858 归档的全量回归仅对应 b5e25ec 的206条目/213用法，不能自动扩展为本条新增后的全量通过。本批证据是新增条目的独立核心、驱动、精确打印和固定官方数据复核；既有核心未改。
