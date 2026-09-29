# 线段树维护单调栈与动态接雨水

附件 4.6 实际 120–125 页，120 页图片给出原题 **Great City Saint Petersburg**。2026-09-29 核验 [CF1912G](https://codeforces.com/problemset/problem/1912/G) 与 [Luogu P12438](https://www.luogu.com.cn/problem/P12438)，为 NERC 2023 G 比赛应用。n,q<=200000，初始高度 1..1e9，每次闭区间加一，输出初始及每次操作后的雨水量。应用例不计正式非比赛模板题覆盖；不以普通单调栈的存在判断附件覆盖。

## 接口与范围

`MonotoneStackSeg(a)`：非空 long long 高度数组，公开区间统一为 0-based 半开。

- `add(l,r,delta)`：区间加任意有符号增量，空区间不变。
- `water()`：整个序列的雨水体积，不附加两端外墙。
- `scan(l,r,height,reverse=false)`：带外部初始最高值扫描；默认左到右，reverse=true 则右到左。对每个元素先更新 height=max(height,a[i])，再累加 height-a[i]。返回 `(累加值,最终最高值)`；空区间返回 `(0,初始高度)`。

高度和增量可以是负数，平移整个序列不改变体积。所有高度、和、外部高度与区间长度的乘积、懒标记及中间运算必须在 long long 范围内；不声称支持任意 int64 极值组合。4n 及索引须可由 int 表示。t、extra、pull、push 及带节点编号的重载是内部实现；不要直接修改节点。

## 缓存的含义

节点记录长度 len、最大值 mx、原值和 sum、整体加标记 lazy，以及两个方向的 fill。fill[0] 是从该段左端开始的运行最大值与原值之差的和，fill[1] 是从右端开始的对应量。单元素两个 fill 都为零。

将两个孩子按扫描顺序记为 F（先扫描）、S（后扫描）。父节点 fill 为

`F.fill + extra(S,F.mx,dir)`。

`extra(p,x,dir)` 在该节点上以 x 为外部最高值，返回扫描差值和。若 x>=mx，整段被同一高度覆盖，答案为 x*len-sum；叶子否则为零。内部节点只递归到一个孩子：

- x>=F.mx：F 整段由 x 覆盖，加上 extra(S,x,dir)。
- x<F.mx：先算 extra(F,x,dir)，离开 F 后最高值必为 F.mx，S 的贡献已经缓存在 `parent.fill-F.fill` 中。

因此 extra 最坏 O(log n)，不是遍历整棵树。区间整体加 delta 后，各元素和运行最大值同步平移，两个 fill 保持不变；只更新 mx、sum、lazy。部分修改回溯时重新合并。

## O(1) 全局雨水

令 L_i、R_i 为含自身的前缀/后缀最大值，M 为全局最大值。每个位置总有 max(L_i,R_i)=M，因此 min(L_i,R_i)=L_i+R_i-M。记 `gap=n*M-sum(a)`，得到

`water = fill[0] + fill[1] - gap`。

实现写成 `fill[0]-(gap-fill[1])`，避免先把两个可能很大的非负 fill 相加。无需维护某个最大值的位置，不受并列最大平台影响。附件分别查最大点左右两段；本实现使用等价恒等式。附件的 MinL/MinR 字段没有参与查询，当前删除；MaxL、MaxR、max_val 实际同为区间最大值，合并为 mx。

附件 QueryL/QueryR 从高度 0 开始，原题高度为正时合法，但不能推广到负高度。当前 root.fill 从实际端点定义，scan 显式保留调用者传入的初始高度；例如 [-3,-5,-3] 雨水为 2，全体减 100 后仍为 2。

## 复杂度

建树 O(n)：每个高度 h 的节点做 O(h) 的两次单路扫描，整棵平衡树上的加权和为 O(n)。区间加最多访问 O(log n) 个需重算祖先，每次 pull 为 O(log n)，最坏 O(log²(n+1))。scan 把查询分成 O(log n) 个完整节点，每次 extra 为 O(log n)，故同样最坏 O(log²(n+1))；沿查询方向依次传递外部最高值。water 只读根，O(1)。空间 O(n)，所有遍历保持递归，深度 O(log n)。不是均摊 beats 复杂度，也不宣称本版本达到原题官方最优算法或速度排名。

## 使用与验证

`example-112` / `verify/luogu/P12438.compact.cpp` 实现附件原题格式；只把 l 减一，打印 q+1 个结果。`example-113` 展示正负区间加、双向外部高度扫描及空区间。

`tests/monotone_stack_seg.cpp` 的独立参考显式建立前缀/后缀极大值，逐位置相减；扫描参考逐元素循环，不使用缓存递推。长度 1..6、值域 {-1,0,1} 全部数组，全部区间、双向和初始高度 -2..2；长度<=4 另枚举区间及正负更新。1200 组随机树共 30 万次更新，逐次核验雨水、双向扫描，定期递归审计所有节点的 len/mx/sum/fill。20 万点盆地、10^12 量级正负高度、10 万次更新、单调升降数组检查规模和整数；整段平移应保持体积。

`tests/monotone_stack_application.py` 运行两组原题样例、150 组各 200 次操作的完整主程序，以及 n=q=200000 的闭式盆地参考。所有普通/ASan/UBSan 的指纹和结果见 `verification/monotone-stack-seg.json`。打印程序另行编译执行。无新增线上 AC；本地耗时不等于平台通过或速度排名。
