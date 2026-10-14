# OI Wiki 分类映射

固定官方导航来源：[bc070e827180](https://github.com/OI-wiki/OI-wiki/blob/bc070e827180fbd75c2e27a16c1212f1d671d949/mkdocs.yml)。

issue #7 指定的 oi-wiki.com 未能通过网页工具访问；此处明确采用 OI Wiki 官方仓库，不声称已核验该域名与官方导航相同。

当前代码映射：direct 184，application 32，composite 4，related 20。这些是分类关系，不是模板题用法、算法完成度或线上AC计数。

此表驱动 PDF 的导航层级。direct 表示直接知识点，application 表示应用，composite 表示一个代码条目横跨多个页面，related 表示仅有相关挂靠。按各行说明核对适用范围；分类不代表上游整页内容已实现或验证。

| 模板 | 上游完整层级 | 关系 | 处理说明 |
| --- | --- | --- | --- |
| ExactCover | 搜索 → Dancing Links | direct | 仅精确覆盖首解；不含重复覆盖、最少行数、解计数及可选列。 |
| MinimumCover | 搜索 → Dancing Links | direct | 无权最少行重复覆盖及方案；不含带权、多重次数与解计数。 |
| grid_cycle | 动态规划 → 插头 DP | direct | 轮廓线连通性最小编号表示，单个闭环覆盖所有可用格子，Count可取精确或模计数。 |
| grid_cycles | 动态规划 → 插头 DP | direct | 恰好K个回路，默认禁止嵌套；与单闭环模板分开保留。 |
| DynamicDP | 动态规划 → 动态 DP | direct |  |
| MonotoneHull | 动态规划 → DP 优化 → 斜率优化 | direct | Monotonicity and exact arithmetic contracts; complete partition or path-selection application. |
| monotone_dp_layer | 动态规划 → DP 优化 → 四边形不等式优化 | direct | Monotonicity and exact arithmetic contracts; complete partition or path-selection application. |
| wqs_independent_set | 动态规划 → DP 优化 → WQS 二分 | direct | Monotonicity and exact arithmetic contracts; complete partition or path-selection application. |
| StringHash | 字符串 → 字符串哈希 | direct | 双模子串/反串与拼接；概率判等，非零碰撞保证。 |
| kmp_match | 字符串 → 前缀函数与 KMP 算法 | direct |  |
| prefix_function | 字符串 → 前缀函数与 KMP 算法 | direct |  |
| exkmp | 字符串 → Z 函数（扩展 KMP） | direct | 模式与文本各后缀LCP；无需分隔符。 |
| z_function | 字符串 → Z 函数（扩展 KMP） | direct |  |
| AhoCorasick | 字符串 → AC 自动机 | direct |  |
| SAIS | 字符串 → 后缀数组 (SA) → 后缀数组简介 | direct | 独立SA-IS线性诱导排序，与倍增版本并列；不等于整页上游内容或线上验证。 |
| SuffixArray | 字符串 → 后缀数组 (SA) → 后缀数组简介 | application | 后缀数组及 LCP 查询应用；保持依赖。 |
| SuffixLCP | 字符串 → 后缀数组 (SA) → 后缀数组简介 | application | 后缀数组及 LCP 查询应用；保持依赖。 |
| SAMLex | 字符串 → 后缀自动机 (SAM) | application | 自动机DAG上的加权字典序查询。 |
| SuffixAutomaton | 字符串 → 后缀自动机 (SAM) | direct |  |
| sam_lcs | 字符串 → 后缀自动机 (SAM) | application | 自动机后缀回退维护两串LCS。 |
| GeneralSAM | 字符串 → 广义后缀自动机 | direct |  |
| SAMDocuments | 字符串 → 广义后缀自动机 | composite | 后缀链接树按文档去重，复用树状数组统计子树颜色；阈值后缀用于多串应用。 |
| manacher | 字符串 → Manacher | direct |  |
| PalindromicTree | 字符串 → 回文树 | direct |  |
| minimum_rotation | 字符串 → 最小表示法 | direct |  |
| lyndon | 字符串 → Lyndon 分解 | direct | Duval 非递增 Lyndon 因子分解；返回右端点。 |
| BigInteger | 数学 → 高精度计算 | direct | 10⁹压位、有符号加减乘、小整数除法与余数；大整数除法及Karatsuba不在本组件内。 |
| Mod64 | 数学 → 快速幂 | application | 包含uint128模乘作为64位模幂与判素的底层组件。 |
| ModInt | 数学 → 数论 → 模算术简介 | application | 静态/动态模整数实现，属于模算术的可复用组件。 |
| mint | 数学 → 数论 → 模算术简介 | application | 静态/动态模整数实现，属于模算术的可复用组件。 |
| Prime64 | 数学 → 数论 → 素数 | direct |  |
| euler_phi | 数学 → 数论 → 欧拉函数 | direct |  |
| LinearSieve | 数学 → 数论 → 筛法 | direct |  |
| segmented_primes | 数学 → 数论 → 筛法 | direct |  |
| PollardRho | 数学 → 数论 → 分解质因数 | direct |  |
| extended_gcd | 数学 → 数论 → 裴蜀定理 & 一次不定方程 | direct |  |
| euler_power | 数学 → 数论 → 费马小定理 & 欧拉定理 | direct | 非互质情形的扩展欧拉降幂。 |
| batch_inverse | 数学 → 数论 → 模逆元 | direct |  |
| inverse_table | 数学 → 数论 → 模逆元 | direct |  |
| mod_inverse | 数学 → 数论 → 模逆元 | direct |  |
| linear_congruence | 数学 → 数论 → 线性同余方程 | direct |  |
| crt_merge | 数学 → 数论 → 中国剩余定理 | direct |  |
| garner | 数学 → 数论 → 中国剩余定理 | direct |  |
| ExLucas | 数学 → 数论 → 卢卡斯定理 | direct |  |
| Lucas | 数学 → 数论 → 卢卡斯定理 | direct |  |
| mod_sqrt | 数学 → 数论 → 二次剩余 | direct |  |
| PrimitiveRoot | 数学 → 数论 → 阶 & 原根 | direct |  |
| DiscreteLog | 数学 → 数论 → 离散对数 | direct |  |
| KthResidue | 数学 → 数论 → 高次剩余 & 单位根 | application | 高次剩余求根及素数幂、CRT 组合，准备函数保留依赖。 |
| DuJiao | 数学 → 数论 → 狄利克雷双曲线法 & 杜教筛 | direct |  |
| Min25 | 数学 → 数论 → Min_25 筛 | direct | 低次素数多项式加素数幂回调的递归版本。 |
| floor_moments | 数学 → 数论 → 类欧几里德算法 | direct |  |
| floor_sum | 数学 → 数论 → 类欧几里德算法 | direct |  |
| ComplexFFT | 数学 → 多项式与生成函数 → 快速傅里叶变换 | direct | 复数FFT及三块拆系数卷积；明确长度、范数与单位根精度前提，不能用随机通过代替最坏误差界。 |
| cdq_convolution | 数学 → 多项式与生成函数 → 快速傅里叶变换 | related | CDQ 分治配合 NTT 的卷积递推，附件标题为分治 FFT；算法不做浮点变换。 |
| convolution_mod_fft | 数学 → 多项式与生成函数 → 快速傅里叶变换 | direct | 复数FFT及三块拆系数卷积；明确长度、范数与单位根精度前提，不能用随机通过代替最坏误差界。 |
| NttConvolution | 数学 → 多项式与生成函数 → 快速数论变换 | application | NTT 卷积及三模重构扩展；整数范围契约保留。 |
| convolution_i64 | 数学 → 多项式与生成函数 → 快速数论变换 | application | NTT 卷积及三模重构扩展；整数范围契约保留。 |
| SetConvolution | 数学 → 多项式与生成函数 → 快速沃尔什变换 | application | 按位卷积及分层子集卷积；分别说明运算规则。 |
| subset_convolution | 数学 → 多项式与生成函数 → 快速沃尔什变换 | application | 按位卷积及分层子集卷积；分别说明运算规则。 |
| chirp_z | 数学 → 多项式与生成函数 → Chirp Z 变换 | direct |  |
| FpsInverse | 数学 → 多项式与生成函数 → 多项式牛顿迭代 | direct |  |
| PolynomialDivision | 数学 → 多项式与生成函数 → 多项式牛顿迭代 | application | 反转后调用逆级数的带余除法；此页挂靠为求逆应用，不代表页面包含全部除法接口。 |
| MultipointEvaluation | 数学 → 多项式与生成函数 → 多项式多点求值\|快速插值 | direct | 任意点求值允许重复点；快速插值为另一个独立函数。 |
| polynomial_interpolation | 数学 → 多项式与生成函数 → 多项式多点求值\|快速插值 | direct | 任意互异点的快速系数插值；复用乘积树，根导数求值后递归合并。拒绝模意义重复点。 |
| FpsFunctions | 数学 → 多项式与生成函数 → 多项式初等函数 | direct |  |
| FpsPower | 数学 → 多项式与生成函数 → 多项式初等函数 | direct | 非负十进制大指数，首项非1与前导零单独处理。 |
| FpsSqrt | 数学 → 多项式与生成函数 → 多项式初等函数 | direct | 一般前导零、无解与二次剩余首项；Newton 开根。 |
| BostanMori | 数学 → 多项式与生成函数 → 常系数齐次线性递推 | direct |  |
| recurrence_nth | 数学 → 多项式与生成函数 → 常系数齐次线性递推 | direct |  |
| polynomial_shift | 数学 → 多项式与生成函数 → 多项式平移\|连续点值平移 | direct |  |
| Binomial | 数学 → 组合数学 → 排列组合 | direct |  |
| stirling_first_row | 数学 → 组合数学 → 斯特林数 | direct |  |
| stirling_second_row | 数学 → 组合数学 → 斯特林数 | direct |  |
| bernoulli | 数学 → 组合数学 → 伯努利数 | direct |  |
| Partitions | 数学 → 组合数学 → 分拆数 | direct |  |
| parts_at_most | 数学 → 组合数学 → 分拆数 | direct |  |
| parts_at_most_fps | 数学 → 组合数学 → 分拆数 | direct |  |
| BurnsideAverage | 数学 → 组合数学 → Pólya 计数 | direct | Group fixed-point average, cycle decomposition and named-color cyclic/dihedral action; arbitrary modulus with exact division. |
| necklace_colorings | 数学 → 组合数学 → Pólya 计数 | direct | Group fixed-point average, cycle decomposition and named-color cyclic/dihedral action; arbitrary modulus with exact division. |
| permutation_cycles | 数学 → 组合数学 → Pólya 计数 | direct | Group fixed-point average, cycle decomposition and named-color cyclic/dihedral action; arbitrary modulus with exact division. |
| MaxPlusMatrix | 数学 → 线性代数 → 矩阵 | application | max-plus 半环矩阵；不是普通域矩阵运算。 |
| ModMatrix | 数学 → 线性代数 → 矩阵 | direct |  |
| matrix_inverse | 数学 → 线性代数 → 矩阵 | direct | 素数模方阵求逆，使用 Gauss-Jordan 消元。 |
| determinant_mod | 数学 → 线性代数 → 行列式 | direct |  |
| PositionBasis | 数学 → 线性代数 → 线性基 | direct |  |
| XorBasis | 数学 → 线性代数 → 线性基 | direct |  |
| basis_intersection | 数学 → 线性代数 → 线性基 | direct |  |
| basis_sum_intersection | 数学 → 线性代数 → 线性基 | direct |  |
| Simplex | 数学 → 线性规划 → 单纯形法 | direct | 独立实现两阶段单纯形与显式变量编号Bland选择；注明浮点容差、退化与非精确保证。 |
| Lagrange | 数学 → 数值算法 → 插值 | direct |  |
| lagrange_consecutive | 数学 → 数值算法 → 插值 | direct |  |
| AdaptiveSimpson | 数学 → 数值算法 → 数值积分 | direct | 有限资源的自适应Simpson、采样复用与可见的估计条件/强制停止；不把局部估计作为任意函数精度保证。 |
| GaussMod | 数学 → 数值算法 → 高斯消元 | direct |  |
| GaussReal | 数学 → 数值算法 → 高斯消元 | direct | 部分选主元实数消元与最终数值模型的特解/自由方向；不是精确秩、附近原输入或全域数值稳定性证书。 |
| GaussXor | 数学 → 数值算法 → 高斯消元 | direct | 模2线性方程组的压位实现，返回特解与完整零空间基；不替代浮点高斯的精度分析。 |
| berlekamp_massey | 数学 → Berlekamp–Massey 算法 | direct |  |
| gp_map | 数据结构 → 哈希表 | application | GNU 哈希表组件，保留 GNU 扩展依赖。 |
| PotentialDSU | 数据结构 → 并查集 → 并查集 | direct | 维护加法差值约束、按大小合并与矛盾拒绝；独立于普通并查集的指定根合并接口，不提供回滚或非交换群。 |
| RollbackDSU | 数据结构 → 并查集 → 并查集 | direct |  |
| TimeConnectivity | 数据结构 → 并查集 → 并查集 | composite | Recursive segment tree over edge lifetimes with rollback DSU; offline dynamic connectivity. |
| dsu | 数据结构 → 并查集 → 并查集 | direct |  |
| pheap | 数据结构 → 堆 → 配对堆 | application | GNU pairing_heap_tag 实现，按实际数据结构归堆；另在infra语言基础索引中登记。 |
| LeftistHeap | 数据结构 → 堆 → 左偏树 | direct |  |
| StaticRMQ | 数据结构 → ST 表 | composite | 块间ST表与块内单调栈位掩码组合；与专题RMQ相关，主分类保持数据结构。 |
| Fenwick | 数据结构 → 树状数组 | direct |  |
| RectangleFenwick | 数据结构 → 树状数组 | direct | 稠密二维差分四矩，矩形加与矩形和；不是基础一维独立模板。 |
| offline_rectangle_sum | 数据结构 → 树状数组 | related | 离线二维扫描线应用，不代表整页覆盖 |
| MonotoneStackSeg | 数据结构 → 线段树 → 线段树基础 | related | 线段树维护单调栈的双向极大值贡献；区间加接雨水应用，不将普通单调栈直接视为覆盖。 |
| lazy_segtree | 数据结构 → 线段树 → 线段树基础 | direct |  |
| segtree | 数据结构 → 线段树 → 线段树基础 | direct |  |
| MergeSplitTree | 数据结构 → 线段树 → 线段树合并 & 分裂 | direct | 非负重数、值域分裂、破坏性合并与节点回收。 |
| LiChao | 数据结构 → 线段树 → 李超线段树 | direct |  |
| SegmentLiChao | 数据结构 → 线段树 → 李超线段树 | direct |  |
| SegmentBeats | 数据结构 → 线段树 → 区间最值操作 & 区间历史最值 | direct | 区间 chmin/chmax/add/sum；不含区间历史最值。 |
| ost | 数据结构 → 二叉搜索树 & 平衡树 → 二叉搜索树 & 平衡树 | application | 按用户 issue #8 明确要求放在平衡树板块，覆盖之前的默认 OI Wiki 归属。 |
| rp | 数据结构 → 二叉搜索树 & 平衡树 → 二叉搜索树 & 平衡树 | application | 按用户 issue #8 明确要求放在平衡树板块，覆盖之前的默认 OI Wiki 归属。 |
| OrderedTreap | 数据结构 → 二叉搜索树 & 平衡树 → Treap | direct |  |
| SequenceTreap | 数据结构 → 二叉搜索树 & 平衡树 → Treap | direct |  |
| OrderedSplay | 数据结构 → 二叉搜索树 & 平衡树 → Splay 树 | direct |  |
| CartesianTree | 数据结构 → 二叉搜索树 & 平衡树 → 笛卡尔树 | direct | 线性单调栈构造，相等值左侧优先；独立完整用法。 |
| PersistentDSU | 数据结构 → 可持久化数据结构 → 可持久化线段树 | direct | 可持久化并查集扩展；不压缩路径、按大小合并。 |
| PersistentKth | 数据结构 → 可持久化数据结构 → 可持久化线段树 | application | 可持久化线段树的区间、树路径、数组和版本应用。 |
| PersistentRange | 数据结构 → 可持久化数据结构 → 可持久化线段树 | application | 可持久化线段树的区间、树路径、数组和版本应用。 |
| PersistentOrderedTreap | 数据结构 → 可持久化数据结构 → 可持久化平衡树 | direct | 历史版本可重集合；复制路径保留分叉版本，不包含可持久化序列操作。 |
| PersistentXorTrie | 数据结构 → 可持久化数据结构 → 可持久化字典树 | direct | 前缀追加版本的区间单值最大异或；不扩张为任意分支版本、普通字符串Trie或整个上游页面。 |
| DynamicKth | 数据结构 → 树套树 → 树状数组套权值线段树 | direct |  |
| KDNearest | 数据结构 → K-D Tree | direct | 静态整数近邻与远邻；动态范围和另见KDTreeSum。 |
| KDTreeSum | 数据结构 → K-D Tree | direct | 动态二维点权累加、闭矩形求和；不包含最近邻或删除坐标。 |
| LinkCutTree | 数据结构 → 动态树 → Link Cut Tree | direct |  |
| DynamicDiameter | 图论 → 树上问题 → 树的直径 | related | 固定拓扑下修改非负边权，递归欧拉序与区间加维护动态直径。 |
| TreeDiameter | 图论 → 树上问题 → 树的直径 | direct |  |
| LiftingLCA | 图论 → 树上问题 → 最近公共祖先 | application | LCA 不同算法及路径交应用。 |
| path_intersection | 图论 → 树上问题 → 最近公共祖先 | application | LCA 不同算法及路径交应用。 |
| HLD | 图论 → 树上问题 → 树链剖分 | direct |  |
| LongChain | 图论 → 树上问题 → 树链剖分 | direct | 按高度剖分长链，O(1)静态K级祖先；递归DFS。 |
| SubtreeColors | 图论 → 树上问题 → 树上启发式合并 | direct |  |
| VirtualTree | 图论 → 树上问题 → 虚树 | direct |  |
| CentroidPairs | 图论 → 树上问题 → 树分治 | direct |  |
| CentroidDiameter | 图论 → 树上问题 → 动态树分治 | direct | 固定有符号边权树，动态启停点；不同重心分支组合直径与端点，非动态拓扑。 |
| CentroidSum | 图论 → 树上问题 → 动态树分治 | direct | 固定单位边树上的点权修改和距离范围求和；不是动态拓扑。 |
| TreeIsomorphism | 图论 → 树上问题 → 树哈希 | related | Deterministic sorted-child interning and centroid rooting; exact alternative to randomized tree hashing. |
| tree_hash | 图论 → 树上问题 → 树哈希 | related | Deterministic sorted-child interning and centroid rooting; exact alternative to randomized tree hashing. |
| tree_hash_reroot | 图论 → 树上问题 → 树哈希 | related | Deterministic sorted-child interning and centroid rooting; exact alternative to randomized tree hashing. |
| BellmanFord | 图论 → 最短路问题 → 最短路 | direct |  |
| Dijkstra | 图论 → 最短路问题 → 最短路 | direct |  |
| Floyd | 图论 → 最短路问题 → 最短路 | direct | Floyd全源最短路；任意负环使全部结果无效，支持原边路径。 |
| Spfa | 图论 → 最短路问题 → 最短路 | direct | FIFO队列SPFA；负环时结果整体无效。差分约束以run(0)覆盖全图。 |
| KShortestWalks | 图论 → 最短路问题 → k 短路 | direct | Strict second distinct distance or positive-weight K shortest walks; repeated vertices allowed. |
| StrictSecondShortest | 图论 → 最短路问题 → k 短路 | direct | Strict second distinct distance or positive-weight K shortest walks; repeated vertices allowed. |
| Kruskal | 图论 → 生成树问题 → 最小生成树 | direct | 边排序最小生成森林，独立块数、int128总权和原边方案。 |
| KruskalTree | 图论 → 生成树问题 → 最小生成树 | direct | 升降序Kruskal重构森林、严格或非严格阈值连通块。 |
| ManhattanMST | 图论 → 生成树问题 → 最小生成树 | direct | 曼哈顿完全图的四方向几何候选边与最小生成树证书；不是恢复基础Kruskal题，不扩张为欧氏或受限边图。 |
| Prim | 图论 → 生成树问题 → 最小生成树 | direct | 稠密图矩阵O(n²)最小生成森林，int128权和父点方案。 |
| SecondMST | 图论 → 生成树问题 → 最小生成树 | direct | Kruskal与树上两个不同最大边权，支持严格/非严格次小树及原边编号换边方案；不表示整页其他MST扩展已覆盖。 |
| Arborescence | 图论 → 生成树问题 → 最小树形图 | direct |  |
| SteinerTree | 图论 → 斯坦纳树 | direct | 小终端数子集DP与多源Dijkstra，附原边方案。 |
| FunctionalGraph | 图论 → 连通性相关 → 强连通分量 | related | 函数图包含尾链与环分解，导航无独立页；需正文定位，不应等同一般 SCC 算法。 |
| TarjanSCC | 图论 → 连通性相关 → 强连通分量 | direct |  |
| BiconnectedCore | 图论 → 连通性相关 → 双连通分量 | direct |  |
| bridge_component_forest | 图论 → 连通性相关 → 双连通分量 | direct |  |
| Cactus | 图论 → 连通性相关 → 圆方树 | direct | 仙人掌专用环虚点森林，非负权最短路，LCA在虚点时修正环上距离。 |
| block_cut_forest | 图论 → 连通性相关 → 圆方树 | direct |  |
| count_four_cycles | 图论 → 环计数问题 | direct | 简单无向图四元环计数，度数定向O(n+m√m)，不要求诱导。 |
| enumerate_triangles | 图论 → 环计数问题 | direct |  |
| MinCycle | 图论 → 最小环 | direct | 非负权无向图至少3点简单环，含原边方案。 |
| minimum_mean_cycle | 图论 → 最小环 | related | Karp最小平均权有向环，目标不同于最小总权环；两遍DP线性空间。 |
| TwoSAT | 图论 → 2-SAT | direct |  |
| DirectedEuler | 图论 → 欧拉图 | application | 有向、无向、混合和字典序应用，保留差异。 |
| UndirectedEuler | 图论 → 欧拉图 | application | 有向、无向、混合和字典序应用，保留差异。 |
| mixed_euler_orientation | 图论 → 欧拉图 | application | 有向、无向、混合和字典序应用，保留差异。 |
| mixed_euler_trail | 图论 → 欧拉图 | application | 有向、无向、混合和字典序应用，保留差异。 |
| Dinic | 图论 → 网络流 → 最大流 | direct |  |
| HLPP | 图论 → 网络流 → 最大流 | direct | 最高标号预流推进；反向BFS、gap、单链桶，退回多余预流并输出流方案。 |
| gomory_hu | 图论 → 网络流 → 最小割 | application | 最小割的应用或查询；需在对应小节下保留本库名称。 |
| maximum_closure | 图论 → 网络流 → 最小割 | application | 最小割的应用或查询；需在对应小节下保留本库名称。 |
| mincut_edges | 图论 → 网络流 → 最小割 | direct |  |
| MinCostFlow | 图论 → 网络流 → 费用流 | direct |  |
| NegativeCostFlow | 图论 → 网络流 → 费用流 | direct | 通过负边预流与需求修复处理负环，随后继续最短增广。 |
| BoundedCirculation | 图论 → 网络流 → 上下界网络流 | direct |  |
| BoundedMaxFlow | 图论 → 网络流 → 上下界网络流 | direct |  |
| StoerWagner | 图论 → 网络流 → Stoer–Wagner 算法 | direct |  |
| BipartiteMatching | 图论 → 图的匹配 → 二分图最大匹配 | direct |  |
| independent_set | 图论 → 图的匹配 → 二分图最大匹配 | application | 最小点覆盖取补集构造二分图最大独立集，复用HK。 |
| matching_edges | 图论 → 图的匹配 → 二分图最大匹配 | direct |  |
| regular_matching | 图论 → 图的匹配 → 二分图最大匹配 | related | 正则多重二分图的随机交替游走；概率只影响耗时，不影响返回方案正确性。 |
| Hungarian | 图论 → 图的匹配 → 二分图最大权匹配 | direct |  |
| Blossom | 图论 → 图的匹配 → 一般图最大匹配 | direct |  |
| WeightedBlossom | 图论 → 图的匹配 → 一般图最大权匹配 | direct |  |
| MatrixTreeMod | 图论 → 矩阵树定理 | direct |  |
| tutte | 图论 → 矩阵树定理 | related | 生成树计数的相关扩展：Tutte多项式，T(1,1)对应连通图生成树数；不将其冒称为矩阵树定理实现。 |
| dag_path_determinant | 图论 → LGV 引理 | direct | DAG 路径矩阵及带排列符号的 LGV 行列式。 |
| DominatorTree | 图论 → 支配树 | direct |  |
| CirclePolygon | 计算几何 → 二维计算几何基础 | application | 二维圆构造与面积应用，保留退化和精度条件。 |
| CircleTangents | 计算几何 → 二维计算几何基础 | application | 二维圆构造与面积应用，保留退化和精度条件。 |
| IntegerPlane | 计算几何 → 二维计算几何基础 | direct |  |
| RealPlane | 计算几何 → 二维计算几何基础 | direct |  |
| RealPolarLess | 计算几何 → 二维计算几何基础 | direct | 对已存储的有限二进制浮点向量精确比较极角；尾数≤64位，原点/同向约定明确，不替代一般稳健几何构造。 |
| circle_coverage_area | 计算几何 → 二维计算几何基础 | related | 分层圆弧积分求每个精确覆盖重数的面积，重复圆按编号分层；有独立高精度截面积分验证。 |
| circle_intersections | 计算几何 → 二维计算几何基础 | direct |  |
| circle_intersections_i64 | 计算几何 → 二维计算几何基础 | direct | 整数输入的精确判别式变体，坐标构造仍为浮点。 |
| circle_overlap_area | 计算几何 → 二维计算几何基础 | direct |  |
| circle_union_area | 计算几何 → 二维计算几何基础 | related | 圆面积并的圆弧覆盖与格林公式；支持包含、同圆、相切及孔洞，明确浮点局限。 |
| convex_cut | 计算几何 → 二维计算几何基础 | related | 凸多边形裁剪：保留有向直线左侧；几何基础上的独立补充接口。 |
| line_circle_i64 | 计算几何 → 二维计算几何基础 | direct | 整数输入的精确判别式变体，坐标构造仍为浮点。 |
| line_circle_intersections | 计算几何 → 二维计算几何基础 | direct |  |
| line_intersection_real | 计算几何 → 二维计算几何基础 | direct |  |
| line_projection | 计算几何 → 二维计算几何基础 | direct |  |
| polygon_area2 | 计算几何 → 二维计算几何基础 | direct |  |
| polygon_centroid | 计算几何 → 二维计算几何基础 | related | 简单多边形面积重心；几何基础上的独立补充接口。 |
| polygon_contains | 计算几何 → 二维计算几何基础 | direct |  |
| polygon_union_area | 计算几何 → 二维计算几何基础 | related | 任意简单整数多边形面积并；符号化右侧极限、共线边编号去重和有理参数排序，浮点面积输出。 |
| triangle_incircle | 计算几何 → 二维计算几何基础 | related | 三角形内心与内切圆，非完整二维几何来源覆盖 |
| Hull3D | 计算几何 → 三维计算几何基础 | related | 不扰动增量凸包，精确方向符号、低维退化输出、面积及六倍体积。 |
| IntegerGeometry3D | 计算几何 → 三维计算几何基础 | direct |  |
| Line3 | 计算几何 → 三维计算几何基础 | direct | Finite floating-point vector/line/plane operations with explicit distance/angular tolerances; not exact topology or a 3D hull. |
| Plane3 | 计算几何 → 三维计算几何基础 | direct | Finite floating-point vector/line/plane operations with explicit distance/angular tolerances; not exact topology or a 3D hull. |
| RealSpace | 计算几何 → 三维计算几何基础 | direct | Finite floating-point vector/line/plane operations with explicit distance/angular tolerances; not exact topology or a 3D hull. |
| segment_distance_real | 计算几何 → 距离 | direct |  |
| convex_contains_i64 | 计算几何 → 凸包 | direct |  |
| convex_tangents_i64 | 计算几何 → 凸包 | direct | 严格凸CCW整数多边形的外点两切线与最近接触端点；不包含圆切线、动态凸包或整道计数题。 |
| integer_hull | 计算几何 → 凸包 | direct |  |
| minkowski_sum | 计算几何 → 凸包 | related | 固定导航没有独立 Minkowski 和条目，按凸包的相关应用归档。 |
| rectangle_union_area | 计算几何 → 扫描线 | direct | 整数轴对齐矩形面积并；不含周长和动态更新。 |
| convex_diameter2 | 计算几何 → 旋转卡壳 | direct |  |
| minimum_rectangle | 计算几何 → 旋转卡壳 | related | 凸包的三组支撑点旋转卡壳，最小包围矩形面积与逆时针四角。 |
| IntegerHalfplanes | 计算几何 → 半平面交 | direct |  |
| ClosestPair | 计算几何 → 平面最近点对 | direct |  |
| EnclosingCircle | 计算几何 → 随机增量法 | application | 随机增量最小覆盖圆。 |
| Dominance3D | 杂项 → 离线算法 → CDQ 分治 | direct | 静态无权三维弱偏序计数，CDQ按点对归并；不把卷积递推或整个CDQ页面当作已覆盖。 |
| OverallKth | 杂项 → 离线算法 → 整体二分 | direct | Stable value-domain divide and conquer for offline point assignments and range kth. |
| Mo | 杂项 → 离线算法 → 莫队算法 → 普通莫队算法 | direct | 静态普通莫队与蛇形排序，半开区间、运行后恢复空状态。 |
| manhattan_order | 杂项 → 离线算法 → 莫队算法 → 普通莫队算法 | composite | kuangbin8.7.2：以曼哈顿MST递归DFS生成莫队查询顺序。 |
| ModifiedMo | 杂项 → 离线算法 → 莫队算法 → 带修改莫队 | direct |  |
| TreeMo | 杂项 → 离线算法 → 莫队算法 → 树上莫队 | direct | Static offline Mo template; recursive tree Euler tour or rollback-only interval state. |
| RollbackMo | 杂项 → 离线算法 → 莫队算法 → 回滚莫队 | direct | Static offline Mo template; recursive tree Euler tour or rollback-only interval state. |
| xor_hamming_pairs | 杂项 → 离线算法 → 莫队算法 → 莫队二次离线 | direct | 附件及 P4887 的异或 popcount 配对应用；不声称任意问题可直接代入。 |
| dinkelbach | 杂项 → 分数规划 | direct |  |
| Expression | 杂项 → 表达式求值 | direct |  |
| ODT | 杂项 → 珂朵莉树/颜色段均摊 | direct |  |
