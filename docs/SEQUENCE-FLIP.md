# 附件 FHQ Treap 位翻转核对

来源为 issue #11 固定 PDF 的实际 109–112 页。附件节点 val 和 rev 为 bool；Reverse(L,R) 只翻转 val 与 rev，下传对子节点也只执行 val^=1，不交换儿子。因此它表示二进制值取反。现有 SequenceTreap 的 reverse 表示顺序反转，两者不能混作覆盖。

新增 `flip_bits(l,r)`，要求区间非空、1-based、全为 0/1；不扫描检查这个前提。它保持位置次序，等价于对所有值执行 1-x。`query` 仍返回和，对于二进制区间即 1 的个数。插入、删除、区间加、顺序反转和输出接口保持原义。

## 标记组合

每个节点用 neg 和 tag 表示尚待下传的 `s*x+b`，s 为 1 或 -1。apply_negate 同时取负 val、sum、tag，并翻转 neg；随后 apply_add(1)，得到 1-x。push 先向子节点传 neg，再传 tag。若颠倒次序，当旧 tag 不为零时会得到 `s*(x+b)` 而不是 `s*x+b`。反转顺序的 rev 可先处理，因为对整个区间统一做数值变换与顺序置换可交换。

二进制纯翻转的值和不会越界。与任意 long long 加法混用时，仍要求所有值、子树和、累积标记、长度乘积及取负中间值都可表示；最终值可表示并不足够，不允许取负 LLONG_MIN。不会扩展为任意精度算术。

## 构造、递归与空间

附件按中点建立平衡树，再给节点随机优先级，没有 heapify；优先级堆序可能不成立，因此不能直接套用随机 Treap 的分裂合并平衡证明。本库以 insert 构建，所有 merge 均按优先级选择根，保持堆序。构建期望 O(n log n)，单次操作期望 O(log n)，values 为 O(n)；没有确定性最坏对数保证。递归 split/merge/collect 保持不变。节点池不回收已删除节点，内存按累计插入次数计算。

## 验证与使用范围

- tests/sequence_flip.cpp：穷举 n<=7 的所有 01 序列及区间，验证翻转、翻转两次还原、区间和；500 组各 1000 次插入、删除、反转、位翻转、加值和查询，对照独立 vector。定期递归检查随机优先级堆序、子树大小和总和。20 万节点、反复整段翻转与反转作为规模检查。
- tests/sequence_flip_application.py：151 组完整驱动，包括 n=q=200000。独立 XOR 差分数组计算最后字符串，既不使用树也不复用懒标记递推。
- tests/trees.cpp：重新验证原有非二进制加法/反转、OrderedTreap、Splay 和 LCT，普通及消毒器模式均通过。
- 打印使用例 example-8、example-10 因共享头文件重新执行，新增 example-109 明确区分两种翻转。

本次全部普通与 ASan/UBSan 通过，证据及指纹见 verification/sequence-flip.json。附件没有完整题号，example-109 仅作本地应用，不计新正式模板题或在线 AC。P3391 的历史提交与本次变更的源文件是否相同以 OJ 审计为准，不能自动沿用 AC。
