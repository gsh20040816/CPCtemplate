# 曼哈顿最小生成树

## 赛时接口

`ManhattanMST::solve(points)` 返回 `Result{weight, edges}`，其中 `points` 为 `vector<pair<long long,long long>>`，`weight` 为 signed `__int128`，边端点为输入顺序的0基编号。不修改输入。空集和单点返回零与空边集；重合点保留为不同顶点，以零权边连接。

`candidates(points)` 返回 `(distance,u,v)` 候选边，未按边权排序，允许重复边。非空输入至多 `4(n-1)` 条；包含至少一棵完整 L1 图的 MST，不承诺保存每条最优边。带禁边、颜色或其他约束的 MST 不能直接使用这个稀疏图。

输入长度须能用 `int` 表示且所需分配可行。所有坐标在求和、求差、变号前转成 signed128；完整 signed64 坐标域安全，最大单边距离 `2^65-2`，通常32位 int 顶点范围下总权小于 `2^96`。不要先在 long long 中相减再强转。此接口独立使用整数对，不继承其他几何 Point 的更窄坐标合同。

四轮 map 扫描与候选 Kruskal 均为 O(n log n)，额外空间 O(n)。调用普通 `dsu` 前按大小选择根顺序，未改变共享 dsu 的根附着规则或返回值语义。

## 算法与重复点

四轮坐标为 `(x,y),(y,x),(-y,x),(x,-y)`，分别处理向右的浅上、陡上、陡下、浅下闭锥。各轮按 `(x+y,id)` 扫描，map 以 `-y` 排序；活动点的 `x-y` 随 y 递减而严格递增。当前点从 lower_bound 开始，遇到 `dx<dy` 后可停止；首次满足条件的当前点就是被删除活动点的锥内最近邻。每点每轮至多被删除一次。

相同坐标按编号形成零权链。相同 x+y 的其他位置无法以非零边删除代表，最后代表仍参与非重合最近邻选择。割若拆开一个重合类，零链已有最小过割边；其余割可在收缩图讨论。

## 闭锥平局证明

闭锥内只能得到 `d(r,q) <= max(d(p,r),d(p,q))`，不能照抄半开八分区的严格不等式。例如 `(0,0),(2,0),(1,1)` 的三条边都是2。

在任意割中，选择最短过割点对 p,q，再在平局中最大化 `p.x+q.x`；从左端 p 选择含 q 的右向锥。若 pq 在对角线上，选择靠水平轴的浅锥。令 r 为该锥选出的最近邻：d(p,r)≤δ=d(p,q)。若 r 位于割另一侧，pr 已提供所需候选；否则 rq 过割，且 d(r,q)≤δ。严格小于矛盾；等号且 r≠p 时必有 r.x>p.x，违反横坐标和最大。

等号条件可直接在局部 `X>=Y>=0` 的三角形 `(0,0),(δ,0),(δ/2,δ/2)` 检查：q 在锥严格内部时只有原点可达到距离δ；在主轴时非零等号点位于对角射线；在对角边界时仅主轴最远端点达到等号。四种右向锥的对角射线都向右，对角边界选择浅锥则主轴也向右。这样每个割都有候选最小边，候选图上的 Prim 按完整图的割性质同样最优。实现最后用 Kruskal。

## 正式题与本地验证

正式用法 example-236 对应 [Library Checker Manhattan MST](https://judge.yosupo.jp/problem/manhattanmst)。题面 n∈[1,200000]、坐标∈[0,10^9]，允许重复点，输出总权与 n−1 对原0基编号，任何最优树均可。该范围总权低于4×10^14，故正式驱动可将128位总权转为 long long；扩展 signed64 API 不可照抄此输出转换。

- 核心：Python 任意精度完整图 dense Prim；3×3 网格重复点多重集及顺序变换、闭边界、signed64 极端、随机点；六类20万点闭式实例
- n≤8 额外检查每个非平凡割的候选最小边、候选权值与重复调用确定性；更大实例检查树证书、总权和输入不变
- 头文件/最小复制分别启用与关闭断言；五种定向错误变体应被拒绝，其中连通性错误可由内部断言拒绝，不声称全部由 NDEBUG 独立判定器捕获
- 正式驱动/打印展开/最小复制三种程序使用独立树证书检查；可选锁定官方 verifier、checker、不同结构的 Fenwick 参考解与五类生成器，种子0、1、2是明确本地选择，不是完整官方隐藏测试集
- ASan/UBSan 针对被测程序，不覆盖 Python 算术和普通构建的官方工具；关闭 LSan。目标测试、复制语法检查与完整回归各自记录，不能互相代替

没有新增线上 AC，也没有 OJ 排名或正式时间限制认证。最终源绑定记录见 verification 中本批检查点；生成过程中的 build 报告仅是阶段性证据。

## 锁定来源与覆盖边界

- [KACTL ManhattanMST.h](https://github.com/kth-competitive-programming/kactl/blob/27faa89f9b47e5fa4578eadea6122b59da544052/content/geometry/ManhattanMST.h)：CC0，作者 chilli、Takanori MAEHARA；四轮 map 方案，当前版本加宽算术、封装结果和 Kruskal。只引用该文件，不新增整个 KACTL 库的覆盖承诺
- [官方任务源](https://github.com/yosupo06/library-checker-problems/tree/e64660561a995c357cdc61ddee1bde68b80528db/geo/manhattanmst)：题面、参数、校验器、不同 Fenwick 参考解、生成器共同锁定
- Zhou–Shenoy–Nicholls, Efficient minimum spanning tree construction without Delaunay triangulation, 2002，[作者论文](https://users.ece.northwestern.edu/~haizhou/publications/zhou02ipl.pdf)，DOI 10.1016/S0020-0190(01)00232-0。原论文严格引理基于半开八分区，本说明单独处理闭边界平局

kuangbin 4.19 是需求线索，未取得并逐页核验原 PDF 的事实不改变；不能仅因新增这个组件就把整页或全部来源审计标为完成。
