# 压位小波矩阵

新增 `src/compact/wavelet_matrix.hpp`，统一使用 vector 和轻量 `WaveletMatrix`，对应 issue #1 的来源缺项与 #12 的用法。没有新增线上 AC 或提交排名。

## 来源与范围

已阅读 WIDA 固定版本 `484e9e0e6e4f127f187eb3df5bc419e9ec863795` 的[数据结构章](https://github.com/hh2048/XCPC/blob/484e9e0e6e4f127f187eb3df5bc419e9ec863795/02%20-%20打印稿模板汇总/08%20-%20数据结构.md)小波矩阵条目。落实其压位存储、静态区间顺序统计用途。本项目重新采用每层整体稳定划分，代码没有沿用上游按节点偏移的布局；接口独立约定为 0-based 半开区间、0-based k，并补严格小于与等值计数。第 k 大为 `kth(l,r,r-l-1-k)`，不沿用上游闭区间与排名转换写法。

OI Wiki 固定导航没有独立小波矩阵页面，收录于“数据结构 → 划分树”，标记 related。kuangbin 的原划分树实现还需单独审计，不能仅因同样能做第 k 小就把该来源行关闭。

## 使用与证明

`WaveletMatrix(a)` 接受完整 signed 64 位数值，不改变输入。先排序离散化成 `0..s-1`，层数为 `bit_width(s-1)`；空/单值域取零层。各层保留一位标记的压缩字和每字之前的一位总数，另外保留一个尾字。`rank(d,i)` 为内部函数，支持 i=n，包括 n 为 64 的倍数。掩码位移用 i%64，没有移位 64 的未定义行为。

当前区间 [l,r) 在本层有 `r-l-rank(r)+rank(l)` 个零位。稳定划分使零分支映射为 `[l-rank(l),r-rank(r))`，一分支映射为 `[mid+rank(l),mid+rank(r))`。因此 kth 比较 k 与零位数量，逐位恢复离散值；less 在阈值该位为 1 时累加零分支数量；freq 一直沿目标值路径走到底。重复值不会丢失，每份出现各占一个位置。

- kth 要求非空区间与 `0 <= k < r-l`；最大值不能拿作“查询失败”哨兵。
- less/freq 允许空数组、空区间、不存在的查询值。less 的阈值大于所有值时直接返回 r-l。
- 值域 `[lo,hi)` 计数为 `less(l,r,hi)-less(l,r,lo)`，要求 lo<=hi。freq 不用 x+1，所以 LLONG_MAX 也可查询。
- 构造 O(n log(n+1))，查询 O(log(s+1))。常驻数据 O(n+ceil(n/64)log(s+1)) 个机器字，构造临时 O(n)。本地 n=500000、互异值时，各 vector 数据容量合计小于 6MB；这不是进程峰值内存，输入、临时数组、分配器和 sanitizer 开销另计。
- 不支持修改、历史版本。成员只读；n<INT_MAX。

## 完整用法

example-140：Library Checker [Range Kth Smallest](https://judge.yosupo.jp/problem/range_kth_smallest)，N/Q≤200000，值 0..10⁹。

example-141：[Static Range Frequency](https://judge.yosupo.jp/problem/static_range_frequency)，N/Q≤500000，允许 N=0、Q=0、空区间。

example-142：[P3834](https://www.luogu.com.cn/problem/P3834)，当前题面是非负值 0..10⁹、N/Q≤200000；适配 1-based 闭区间与排名为 `kth(l-1,r,k-1)`。负数和 64 位边界由核心扩展测试验证，不冒充当前题面数据。

## 本地证据

`tests/wavelet_matrix.cpp`：3280 份长度 0..7、三值字母表的全部数组；遍历所有子区间与合法 k，独立排序/直接计数；600 份随机、27 份跨 63/64/65 等字边界输入；三份 500000 元素的递增、递减、全同值数组各做 500000 组查询。共 10316541 次 API 对照，普通与 ASan/UBSan 均通过；同时检查原输入不变、rank 与逐位计数一致。

`tests/wavelet_applications.py`：160 份输入分别运行三个完整驱动，参考直接排序与计数；空输入/空查询；完整程序 N=Q 为 200000/200000/500000，用递减序列闭式答案验证。打印程序也原样展开执行。

固定 Library Checker `e64660561a995c357cdc61ddee1bde68b80528db`：kth 的 24 组、frequency 的 11 组生成数据，普通/ASan/UBSan 共 70 次本地官方 checker 接受；错误输出负对照拒绝。记录 `verification/wavelet-kth-official*.json`、`wavelet-freq-official*.json`、`wavelet-matrix.json` 含源码与输出指纹。未运行 GitHub CI。
