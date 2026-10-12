# WIDA 区间加与懒标记线段树核验

精确原稿、blob 和 GPL-3.0 许可保存在 `tests/fixtures/wida_lazy/`，上游树为 hh2048/XCPC 的 `cfdb12db6792eb2303798541fb5c760ed2bc618b`。对应 03A（区间加、单点修改）和 04（LazySegmentTree）。

## 03A 的 Info 缺失与初始化

原稿直接引用未定义的 Info，要求其有 max 字段，且 operator+ 能合并区间。不能仅复制文件便声称是完整程序。

本批在原稿外围提供整数区间最大值 Info，空区间单位元为 -10^9，并在任何区间操作前逐点赋初值。原稿构造只填默认 Info，不能将这个默认值误当成全零数组。有限值和所有中间 tag 都须留在所选整数范围内。

区间为零基半开 [l,r)。rangeAdd(l,r,v) 对应当前 lazy_segtree::apply(l,r,{v})，modify(x,info) 对应 set(x,info)，query(l,r) 对应 prod(l,r)。当前版须提供区间最大值与加法作用所需的 op/e/mapping/composition/id，不能直接套用求和节点而不保存区间长度。

## 04 通用核心的验证范围

原稿本身是模板，末尾仅示范区间取 max 的 Info/Tag；它又混合了多个其他应用的专用成员。非依赖名字 inf 没有定义，测试在包含原稿前补充该常量，未改原稿字节。

本次另行实例化 Summary={min,max,act,sum} 和 Add={x}：act 是有效叶子数量，合并时相加；加法同时作用于 min/max，并使 sum 增加 act*x。空节点 act=0，加法保持其单位元。普通实验所有叶子均有效。

比较 rangeApply/modify/rangeQuery/findFirst/findLast 与当前 lazy_segtree，以及独立字面数组更新和扫描。搜索条件为区间最大值达到阈值；具体 max_right/min_left 转换和谓词前提见 WIDA-BASIC-DS.md。

原稿 tag.apply(v) 表示先执行旧标记再执行 v；当前 composition(f,g) 表示 f 在 g 之后执行。本次是可交换的加法标记，**不能用本批证据声称非交换标记的组合顺序也已验证**。原稿的所有任意 Info/Tag 类型不在本批覆盖范围内。

点赋值后原稿未清除叶子的 tag，但其通用操作不再向叶子下推，该测试范围内结果正确；当前 set 会清空叶子标记。这不是鼓励外部直接调用原稿的内部 push。

## half 只完成原稿的受限语义验证

原稿 half 判断 (min+1)/2 与 (max+1)/2 相同后统一减去该值，否则递归。对非负整数且全部有效的数组，本批独立验证其效果是每个元素变为 floor(x/2)。测试穷举长度 1 至 6、元素 0 至 3，并连续执行四次。所有这些操作均直接运行精确原稿。

本批只验证上述定义域；没有覆盖负数、无效叶子与原题对 act 的定义，也没有证明摊还复杂度。当前通用 lazy_segtree 没有 half 接口，SegmentBeats 的 chmin/chmax/add 也不能凭名称当作该操作。**此项仍是实现/用法覆盖缺口**，没有通过逐点赋值的慢替代将其标记完成。

maintainL/maintainR 依赖 difl/difr、maxlowl/maxlowr、maxl/maxr 等字段；末尾示范 Info 不提供这些字段。它们的原应用、不变量和替代接口尚未核验，本批没有实例化这些成员，不作正确性结论。

## 证据与剩余任务

`python3 tests/wida_lazy.py` 在普通优化（关闭 assert）和 ASan/UBSan 下各通过 **652,992 项检查**：

- 529,200 项通用操作检查：长度 1 至 63，每个长度 1,200 次混合操作，每次比较七个结果；包含负增量、空区间、单点覆盖已有懒标记和双向搜索。
- 123,792 项原稿 half 的逐叶结果检查，不算作当前替代模板验证。

结果和 SHA-256 见 `verification/wida-lazy.json`。两份来源继续 partial，没有新增线上 AC，也未核验注释中所有 Nowcoder、CF、QOJ、AtCoder 完整应用。本批不新增组件/用法或修改 PDF；当前仍为 335 个组件、457 个完整用法。

后续更新：DivideSegmentTree 已补充非负、全部位置有效时的区间加/赋值/整除/求和及折半，见 DIVIDE-SEGMENT-TREE.md 和用法458/459。本文上方记录的是原稿核验当批状态；无效叶子语义与 maintainL/maintainR 仍未覆盖。
