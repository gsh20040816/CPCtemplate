# Segment Tree Beats 区间截断与求和

`SegmentBeats` 补充普通懒标记线段树不能直接处理的区间 chmin/chmax 与区间和组合。单独保存区间最大值、最小值、和，并不能知道截断会改变多少元素；本模板维护严格第二极值和极值出现次数，用可判定的条件决定是否能整段更新。

## 接口与边界

`SegmentBeats(a)` 传入 0-based `vector<long long>`。`chmin(l,r,x)` 将每个值限制为至多 x；`chmax(l,r,x)` 限制为至少 x；`add(l,r,x)` 加 x；`sum(l,r)` 返回区间和。全部为半开区间 `[l,r)`。空数组和空区间允许，空和为 0；重建对象用于多测。

n 不超过 `(INT_MAX-4)/4` 且内存可用。实际数值、阈值、尚未下传的加法标记、有限第二极值以及下传先加后截断的临时值，均须严格位于 `(-2^60,2^60)`。正负哨兵只代表不存在的第二极值，不能充当真实元素。公开返回的区间和必须位于 signed 64-bit 范围；内部总和使用 `__int128`，并在返回时检查范围。`sum` 会下传标记，不是 const 查询；不改变逻辑数组。

## 三个局部更新

节点保存最大值 mx、严格第二大值 mx2、最大值次数 cmx，对最小值也保存对称三项，另有区间和与加法标记。

- chmin：x≥mx 时不变；mx2<x<mx 时只有最大值组改变，区间和增加 `(x-mx)*cmx`；x≤mx2 时继续递归
- chmax：x≤mn 时不变；mn<x<mn2 时只有最小值组改变；x≥mn2 时继续递归
- add：所有有限极值与加法标记平移，区间和增加 x 乘区间长度；第二极值哨兵不参与平移

阈值恰等于第二极值时不能沿用“只有一个极值组变化”的快速分支，因为两组会合并，次数需要重新计算。全相等和仅有两种值时，修改最大值还可能改变 mn 或 mn2，反方向同理。

下传先传加法，再按父节点的最大值/最小值夹住两个孩子。父节点未保留额外 chmin/chmax 标记，其当前极值本身就是对子节点的截断约束。不能把普通 lazy_segtree 的一个映射函数换成 min/max 就认为区间和也能正确维护。

## 为什么内部和要更宽

合法最终数组不保证尚未同步的孩子在“先加后截断”的瞬间仍有同样范围。例如对整段重复加 10^12 后立刻 chmin 为 0，根节点的真实值一直有界；孩子可能长期没接收截断，父亲积累了很大的加法标记。某次局部查询下传时，孩子先得到累计加法，其临时区间和可能超过 long long，随后才被截断回正确范围。

因此仅保证答案不溢出还不够。本模板把内部和、差值乘次数以及求和合并都放在 `__int128` 中；有限极值和加法标记仍使用 long long，并明确要求上述中间范围。它不承诺任意 long long 元素与任意次数更新都安全。

## 复杂度与空间

建树、空间 O(n)，通常 64 位构建的节点为 64 字节，分配 `4*n+4` 个节点。区间和与区间加为 O(log n)；一次截断最坏可访问 O(n) 节点，不能写成每次最坏 O(log n)。混合截断和加法使用标准 Beats 的总摊还 O((n+q)log²(n+1)) 界；没有为了模板更短而删掉严格第二极值条件。

## Library Checker 用法与证据

[官方题目](https://judge.yosupo.jp/problem/range_chmin_chmax_add_range_sum) 的驱动把操作 0/1/2/3 直接映射为 chmin/chmax/add/sum，不改变半开区间。官方参数 N,Q≤200000，校验器要求运行中实际元素绝对值≤10^12、更新参数绝对值≤2×10^12。于是累计加法的保守大小至多 q×2×10^12，连同历史元素仍小于 2^60；实际公开区间和至多 2×10^17。

官方来源为 [题面](https://github.com/yosupo06/library-checker-problems/blob/master/data_structure/range_chmin_chmax_add_range_sum/task.md)、[参数](https://github.com/yosupo06/library-checker-problems/blob/master/data_structure/range_chmin_chmax_add_range_sum/info.toml)与[校验器](https://github.com/yosupo06/library-checker-problems/blob/master/data_structure/range_chmin_chmax_add_range_sum/verifier.cpp)。固定来源账本继续保留旧快照，不以本次读取覆盖整个上游审计。

独立验证包括 n=0..6 的全部三值数组、30 万次随机更新、排序数组计算的节点极值/次数/和不变量、空区间、第二极值相等、哨兵附近值和两端 signed 64-bit 合法总和。完整打包驱动对照 160 份小数组暴力输入及三份 N=Q=200000 的闭式答案输入。另用 4 个官方 issue_1369_log2 生成种子与官方实现对照；这属于补充一致性证据，不能代替独立 oracle。

普通和 ASan/UBSan 分别执行；当前环境关闭 LeakSanitizer，不宣称泄漏检查通过。来源摘要、测试输出与资源观测见 `verification/segment-beats.json`。未提交线上评测，不将本地运行时间当作 OJ 排名。
