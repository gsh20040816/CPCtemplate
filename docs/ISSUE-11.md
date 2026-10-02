# Issue 11 附件核对清单

附件共 201 页、55 个主要主题，连同章节和变体共 88 个目录项。PDF SHA-256：`b5ce46f7cf542be2d9846d8f01898c8ccd7f4619521036b0b7895206895745f3`。

目录页码与实际 PDF 页码分别保留；正文标题已用于定位起始页。标题相同只产生候选，不等于实现或验证完成。

## 层级统计与原登记状态

88 行由 6 个章节、55 个主要主题和 27 个变体组成。其中 26 行有子项，62 行是最末级条目（叶项）；主题有变体时只数最末级变体，不能把父项与子项相加当作独立实现数。

原登记中 62 个叶项已有正文核对记录，61 个叶项的原状态登记了契约内的本地验证；1 个叶项标记为部分覆盖，0 个叶项待正文核对。本地验证数量不是全功能完成数量，更不是线上 AC 数量。

原状态中有 38 个叶项显式带 `online_pending`；其余叶项没有这个后缀也不构成线上通过证据。所有原 `status`、`review` 和来源行保持不变。

| 章节 | 原父项状态 | 主要主题数 | 叶项数 | 已核对叶项 | 契约内本地验证叶项 | 部分覆盖叶项 | 待正文核对叶项 | 显式线上待验证叶项 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 字符串 | reviewed_partial_coverage | 6 | 8 | 8 | 8 | 0 | 0 | 2 |
| 2 图论 | reviewed_partial_coverage | 15 | 16 | 16 | 16 | 0 | 0 | 11 |
| 3 数学 | pending_content_review | 9 | 10 | 10 | 10 | 0 | 0 | 10 |
| 4 数据结构 | pending_content_review | 7 | 8 | 8 | 8 | 0 | 0 | 8 |
| 5 多项式 | pending_content_review | 13 | 13 | 13 | 13 | 0 | 0 | 6 |
| 6 计算几何 | reviewed_partial_coverage | 5 | 7 | 7 | 6 | 1 | 0 | 1 |

父项原登记待正文核对：3、4、5。其子项汇总与原父项状态分开读取；若子项均已有审阅记录，不能再把父项的旧登记解释为整章尚未审阅，也不能反过来抹掉线上或契约范围缺口。
原登记最末级部分覆盖项：6.5.2。全部父项（含主题下变体）的计算结果见 JSON 的 `hierarchy_summary.parents`。

## 全部原始目录项

| 节号 | 标题 | 原目录页 | PDF 实际页 | 状态 |
|---|---|---:|---:|---|
| 1 | 字符串 | 2 | 4 | reviewed_partial_coverage |
| 1.1 | 1. manacher | 2 | 4 | existing_implementation_local_verified |
| 1.1.1 | (1) 数组 | 2 | 4 | existing_implementation_local_verified |
| 1.1.2 | (2) vector + string | 3 | 5 | existing_implementation_local_verified |
| 1.2 | 2. 后缀数组 | 3 | 5 | existing_implementation_local_verified |
| 1.2.1 | (1) 模板 1 | 3 | 5 | existing_implementation_local_verified |
| 1.2.2 | (2) 模板 2 | 5 | 7 | existing_implementation_local_verified |
| 1.3 | 3. AC 自动机 | 6 | 8 | implemented_local_verified_online_pending |
| 1.4 | 4. 后缀自动机 | 8 | 10 | existing_implementation_local_verified |
| 1.4.1 | (1) 模板 1 | 8 | 10 | existing_implementation_local_verified |
| 1.5 | 5. 广义后缀自动机 | 9 | 11 | implemented_local_verified_online_pending |
| 1.6 | 6. 回文自动机 | 12 | 14 | existing_implementation_local_verified |
| 2 | 图论 | 13 | 15 | reviewed_partial_coverage |
| 2.1 | 1. 2-SAT | 13 | 15 | existing_implementation_local_verified |
| 2.2 | 2. 支配树 | 16 | 18 | implemented_local_verified_online_pending |
| 2.2.1 | (1) 洛谷模板 | 16 | 18 | implemented_local_verified_online_pending |
| 2.3 | 3. 割点 | 22 | 24 | implemented_local_verified_online_pending |
| 2.4 | 4. 网络最大流 | 24 | 26 | existing_implementation_local_verified |
| 2.5 | 5. Johnson | 26 | 28 | implemented_local_verified_online_pending |
| 2.6 | 6. 点双连通分量 | 31 | 33 | existing_implementation_local_verified |
| 2.7 | 7. 边双连通分量 | 33 | 35 | existing_implementation_local_verified |
| 2.8 | 8. 最小费用最大流 | 35 | 37 | implemented_local_verified_online_pending |
| 2.8.1 | (1) Dijkstra 费用流 | 35 | 37 | existing_implementation_local_verified |
| 2.8.2 | (2) SPFA 费用流 | 37 | 39 | implemented_local_verified_online_pending |
| 2.9 | 9. 无向图三元环计数 | 40 | 42 | implemented_local_verified_online_pending |
| 2.10 | 10. 二分图最大匹配的可行边与必经边 | 41 | 43 | implemented_local_verified_online_pending |
| 2.11 | 11. 最小割可行边与必经边 | 42 | 44 | implemented_local_verified_online_pending |
| 2.12 | 12. 有源汇有上下界的最大流 | 44 | 46 | implemented_local_verified_online_pending |
| 2.12.1 | (1) 洛谷模板 | 44 | 46 | implemented_local_verified_online_pending |
| 2.13 | 13. 有负圈的费用流 | 50 | 52 | implemented_local_verified_online_pending |
| 2.13.1 | (1) 洛谷模板 | 50 | 52 | implemented_local_verified_online_pending |
| 2.14 | 14. 最大流的必经边与可行边 | 54 | 56 | implemented_application_local_verified_online_pending |
| 2.14.1 | (1) The 2024 ICPC Northern Eurasia Finals vp | 54 | 56 | implemented_application_local_verified_online_pending |
| 2.15 | 15. 划分子图使每个点度数为奇数 | 59 | 61 | implemented_local_verified_online_pending |
| 3 | 数学 | 63 | 65 | pending_content_review |
| 3.1 | 1. Min_25 筛 | 63 | 65 | implemented_local_verified_online_pending |
| 3.1.1 | (1) 洛谷模板 | 63 | 65 | implemented_local_verified_online_pending |
| 3.1.2 | (2) min_25 筛质数个数 | 68 | 70 | implemented_local_verified_online_pending |
| 3.2 | 2. 原根 | 69 | 71 | implemented_local_verified_online_pending |
| 3.2.1 | (1) 洛谷模板 | 69 | 71 | implemented_local_verified_online_pending |
| 3.3 | 3. 杜教筛 | 72 | 74 | implemented_local_verified_online_pending |
| 3.3.1 | (1) 洛谷模板 | 72 | 74 | implemented_local_verified_online_pending |
| 3.4 | 4. LGV 引理 | 79 | 81 | implemented_local_verified_online_pending |
| 3.5 | 5. 扩展欧拉定理 | 80 | 82 | implemented_local_verified_online_pending |
| 3.6 | 6. 矩阵求逆 | 80 | 82 | implemented_local_verified_online_pending |
| 3.6.1 | (1) 洛谷模板 | 80 | 82 | implemented_local_verified_online_pending |
| 3.7 | 7. Matrix-Tree 定理 | 83 | 85 | implemented_local_verified_online_pending |
| 3.7.1 | (1) 洛谷模板 | 83 | 85 | implemented_local_verified_online_pending |
| 3.8 | 8. 中国剩余定理 | 87 | 89 | implemented_local_verified_online_pending |
| 3.9 | 9. 扩展卢卡斯定理 | 88 | 90 | implemented_local_verified_online_pending |
| 4 | 数据结构 | 96 | 98 | pending_content_review |
| 4.1 | 1. 可并堆/左偏树 | 96 | 98 | implemented_local_verified_online_pending |
| 4.1.1 | (1) 洛谷模板 | 96 | 98 | implemented_local_verified_online_pending |
| 4.2 | 2. LCT 动态树 | 98 | 100 | implemented_local_verified_online_pending |
| 4.2.1 | (1) 洛谷模板 | 98 | 100 | implemented_local_verified_online_pending |
| 4.2.2 | (2) 爱莲说 | 103 | 105 | implemented_local_verified_online_pending |
| 4.3 | 3. FHQ_Treap | 107 | 109 | implemented_local_verified_online_pending |
| 4.3.1 | (1) 牛客 | 107 | 109 | implemented_local_verified_online_pending |
| 4.4 | 4. 替罪羊树 | 111 | 113 | implemented_local_verified_online_pending |
| 4.4.1 | (1) 洛谷模板 | 111 | 113 | implemented_local_verified_online_pending |
| 4.5 | 5. 莫队二次离线 | 115 | 117 | implemented_local_verified_online_pending |
| 4.6 | 6. 线段树维护单调栈 | 118 | 120 | implemented_local_verified_online_pending |
| 4.7 | 7. K-D Tree | 124 | 126 | implemented_local_verified_online_pending |
| 5 | 多项式 | 128 | 130 | pending_content_review |
| 5.1 | 1. 拉格朗日插值 | 128 | 130 | existing_formula_implementation_local_verified |
| 5.2 | 2. 多项式乘法 FFT | 128 | 130 | implemented_local_verified_online_pending |
| 5.3 | 3. 多项式乘法 NTT | 129 | 131 | existing_implementation_local_verified |
| 5.4 | 4. 分治 FFT | 132 | 134 | implemented_local_verified_online_pending |
| 5.5 | 5. 多项式求逆 | 134 | 136 | existing_implementation_local_verified |
| 5.6 | 6. 多项式除法 | 140 | 142 | implemented_local_verified_online_pending |
| 5.7 | 7. 多项式开根 | 148 | 150 | implemented_local_verified_online_pending |
| 5.8 | 8. 多项式 ln | 154 | 156 | existing_implementation_local_verified |
| 5.9 | 9. 多项式 exp | 159 | 161 | existing_implementation_local_verified |
| 5.10 | 10. 快速莫比乌斯 / 沃尔什变换 (FMT / FWT) | 167 | 169 | existing_implementation_local_verified |
| 5.11 | 11. 多项式快速幂 | 169 | 171 | implemented_local_verified_online_pending |
| 5.12 | 12. 任意模数多项式乘法 | 176 | 178 | implemented_local_verified_online_pending |
| 5.13 | 13. 常系数齐次线性递推 | 178 | 180 | existing_implementation_local_verified |
| 6 | 计算几何 | 184 | 186 | reviewed_partial_coverage |
| 6.1 | 1. 二维凸包 | 184 | 186 | existing_implementation_local_verified |
| 6.1.1 | (1) 洛谷模板 | 184 | 186 | existing_implementation_local_verified |
| 6.2 | 2. 李超线段树 | 186 | 188 | implemented_local_verified_online_pending |
| 6.2.1 | (1) 洛谷模板 | 186 | 188 | implemented_local_verified_online_pending |
| 6.3 | 3. 旋转卡壳 | 189 | 191 | existing_implementation_local_verified |
| 6.4 | 4. 半平面交 | 194 | 196 | existing_implementation_local_verified |
| 6.5 | 5. 极角排序 | 196 | 198 | reviewed_partial_coverage |
| 6.5.1 | (1) The 2025 ICPC Asia Seoul Regional Contest vp 写法 | 196 | 198 | existing_implementation_local_verified |
| 6.5.2 | (2) 模板 1 | 197 | 199 | reviewed_partial_coverage |
| 6.5.3 | (3) 模板 2 | 198 | 200 | existing_implementation_local_verified |

## 仍须保留的范围限制

- 6.5.2 的历史部分覆盖状态与 review 保留。后续 RealPolarLess 补入了有限二进制、尾数不超过64位的精确极角比较，契约、独立验证及与原 double 代码的起点/原点/同向约定差异见 [浮点极角排序](REAL-POLAR-SORT.md)。这不使历史汇总或第6章变成全功能/全平台覆盖，也不扩展到调用前坐标差或其他浮点几何谓词。
- 6.1 的定点凸包只覆盖约定小数位输入；6.4 的整数有界半平面交不提供通用浮点半平面交、无界分类。这类接口范围限制不会仅因叶项登记本地验证而消失。见 [几何核对](GEOMETRY-ATTACHMENT.md)。
- 4.2.2 爱莲说、4.3.1 牛客变体仍保留原题外部身份/线上验证限制；6.5.1 没有明确 Seoul 原题或完整应用。竞赛应用及本地接口用法不代替正式模板题覆盖，普通 LCT 的证据不替代虚子树变体。见 [路径乘积](TREE-PATH-PRODUCTS.md)、[位翻转](SEQUENCE-FLIP.md)及 [几何核对](GEOMETRY-ATTACHMENT.md)。
- 3.4 LGV 只证明所列 DAG 接口，3.7 Matrix-Tree 不含引用题 P4336/P3317 的完整应用适配；3.1 Min25 不承诺任意次数或全部时限，5.1 一般插值公式不等于快速插值实现。详见各项原 `review` 及所链接的专项核对，不能由章节汇总扩大能力范围。
- 旧 [多项式基础核对](POLYNOMIAL-ATTACHMENT-BASE.md) 的 5.2 待补段和 [递推核对](RECURRENCE-ATTACHMENT.md) 的 5.12 待补段是较早批次记录；这两项当前登记依据是后续 [浮点 FFT 核对](FFT-ATTACHMENT.md) 与各自原 `review`。保留后续记录的舍入、平台、长度和系数限制，不恢复已补的旧缺口，也不新增实现/验证结论。

来源为 issue #11 用户提供附件；完整 PDF 留在本地 build 中，仓库仅登记来源、摘要与覆盖状态。
已核对项与实现、验证范围见 JSON 中各项 review；本地通过不等于线上 AC，其余目录按上表状态继续核对，不排除任何主题或变体。

## 复算与一致性检查

`python3 tools/issue11_inventory.py --refresh-summary` 仅从现有登记复算 JSON 汇总并重写本页，不读取或生成 PDF。
`python3 tests/issue11_rollup.py` 校验固定来源、层级计数、父子状态约束和本页一致性，含伪造完成状态的负对照；不运行算法或新增 OJ 结论。
原 `python3 tools/issue11_inventory.py <原附件.pdf>` 入口仍可重建定位，但要求同一 SHA-256 和完全相同的来源行，保留原状态与 review，并重新计算汇总。
