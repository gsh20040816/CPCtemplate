# 划分树：稳定中位数划分

`DivisionTree` 补齐 kuangbin 2018 正文 56–57 页 3.1 节。来源 SHA256 为 `f1c90eae0c3fb309d58a14b050fe12b239efb474b033299a547b55646c2768ad`。原注释写“第 k 大”，但其分支先统计较小半区，实际实现第 k 小。本库接口明确为第 k 小，不能照抄该注释理解排名。

## 接口与边界

`DivisionTree(v)` 接受 vector<long long>，不改变输入，支持完整 signed 64 位值、重复值和空构造。`kth(l,r,k)` 查询半开区间 [l,r) 的 0-based 第 k 小，要求 `0 <= l < r <= n`、`0 <= k < r-l`；空数组不能查询。第 k 大可转换为 `kth(l,r,r-l-1-k)`。只支持静态数组；修改输入后需要重新构造。内部 sorted/a/pre 和 build/query 是工作状态，调用者只使用构造与 kth，不直接修改成员。

每个节点对应全局排序结果的 [L,R)，以 sorted[m-1] 为中位数。严格小于中位数的元素全部放左边；等于中位数的元素只取恰好填满左半的份数，其余放右边。保持原相对顺序，故每个查询区间的左右子序列仍连续。pre 的差分给出区间内进入左边的数量，以及区间之前进入左边的数量，由此转换两个端点。k 小于左边数量时递归左边，否则减去该数量并递归右边。

重复值不能简单全部归入同一边，否则会破坏半区大小。相邻节点共享 pre 的边界下标，不能在构造右兄弟时把 pre[d][l] 重置为零；查询只用节点内的前缀差。右区间下标用 `m + (l-L-before)` 计算，避免先相加造成不必要的 int 中间值溢出。

构造时间与空间 O(n log(n+1))，查询 O(log(n+1))；n<INT_MAX。build/query 均递归，深度 O(log(n+1))。本版逐层保存 long long 数值和 int 前缀，空间大于压位小波矩阵；二者分别保留，来源审计不以功能相同相互替代。OI Wiki 直接映射为“数据结构→划分树”，小波矩阵仍为相关条目。

## 完整用法与证据

example-146 对应 [P3834](https://www.luogu.com.cn/problem/P3834)，将题面 1-based 闭区间和排名转为 `kth(l-1,r,k-1)`。example-147 对应 [Library Checker range_kth_smallest](https://judge.yosupo.jp/problem/range_kth_smallest)，直接使用半开区间与 0-based k。两题 N/Q≤200000、值 0..10⁹；负值与 signed64 极值属于额外核心测试范围。原 kuangbin 主程序读至 EOF，这两个评测适配程序按各自单组题面读取；多组时逐次重新构造即可。

`tests/division_tree.cpp` 对 3280 份穷举数组、700 份随机数组、36 份二次幂边界/重复中位数配额输入，以及三份 500000 元素数组做 1928342 次独立排序或闭式答案比较；同时检查空构造和输入不变。`tests/division_applications.py` 检查 P3834 完整程序的 240 份独立排序参考输入，以及三份 N=Q=200000 的递增、递减和全等输入。上述测试与两份原样打印用法均在普通和 ASan/UBSan 下通过。

固定 Library Checker `e64660561a995c357cdc61ddee1bde68b80528db` 的 24 组官方生成数据，双模式共 48 次本地 checker 接受；错误输出负对照被拒绝。记录见 `verification/division-tree.json` 与 `division-tree-official*.json`。这是本地证据，没有新增线上 AC 或排名。
