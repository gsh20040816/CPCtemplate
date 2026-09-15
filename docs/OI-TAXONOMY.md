# OI Wiki 分类映射

固定官方导航来源：[bc070e827180](https://github.com/OI-wiki/OI-wiki/blob/bc070e827180fbd75c2e27a16c1212f1d671d949/mkdocs.yml)。

issue #7 指定的 oi-wiki.com 未能通过网页工具访问；此处明确采用 OI Wiki 官方仓库，不声称已核验该域名与官方导航相同。

此表驱动 PDF 的导航层级；复合条目的内部拆分与相关挂靠仍待处理。direct 表示直接知识点，application 表示应用，composite 表示一个代码条目横跨多个页面，related 表示仅有相关挂靠，需进一步处理。分类不代表上游整页内容已实现或验证。

| 模板 | 上游完整层级 | 关系 | 处理说明 |
| --- | --- | --- | --- |
| kmp_match | 字符串 → 前缀函数与 KMP 算法 | direct |  |
| prefix_function | 字符串 → 前缀函数与 KMP 算法 | direct |  |
| z_function | 字符串 → Z 函数（扩展 KMP） | direct |  |
| AhoCorasick | 字符串 → AC 自动机 | direct |  |
| ac_shortest | 字符串 → AC 自动机 | direct |  |
| SuffixArray | 字符串 → 后缀数组 (SA) → 后缀数组简介 | application | 后缀数组及 LCP 查询应用；保持依赖。 |
| SuffixLCP | 字符串 → 后缀数组 (SA) → 后缀数组简介 | application | 后缀数组及 LCP 查询应用；保持依赖。 |
| prefix_lcs | 字符串 → 后缀数组 (SA) → 后缀数组简介 | application | 后缀数组及 LCP 查询应用；保持依赖。 |
| square_counts | 字符串 → 后缀数组 (SA) → 后缀数组简介 | application | 用后缀 LCP 枚举重复子串；不归为 Main–Lorentz 算法实现。 |
| SuffixAutomaton | 字符串 → 后缀自动机 (SAM) | direct |  |
| GeneralSAM | 字符串 → 广义后缀自动机 | direct |  |
| manacher | 字符串 → Manacher | direct |  |
| PalindromicTree | 字符串 → 回文树 | direct |  |
| minimum_rotation | 字符串 → 最小表示法 | direct |  |
| Mod64 | 数学 → 快速幂 | application | 包含uint128模乘作为64位模幂与判素的底层组件。 |
| power_sum | 数学 → 快速幂 | application | 模幂与几何级数的联合倍增。 |
| divisor_sum_power | 数学 → 数论 → 数论基础 | related | 约数和公式应用；需核对正文定位，导航无独立幂约数和页。 |
| ModInt | 数学 → 数论 → 模算术简介 | application | 静态/动态模整数实现，属于模算术的可复用组件。 |
| mint | 数学 → 数论 → 模算术简介 | application | 静态/动态模整数实现，属于模算术的可复用组件。 |
| Prime64 | 数学 → 数论 → 素数 | direct |  |
| euler_phi | 数学 → 数论 → 欧拉函数 | direct |  |
| LinearSieve | 数学 → 数论 → 筛法 | direct |  |
| segmented_primes | 数学 → 数论 → 筛法 | direct |  |
| PollardRho | 数学 → 数论 → 分解质因数 | direct |  |
| extended_gcd | 数学 → 数论 → 裴蜀定理 & 一次不定方程 | direct |  |
| linear_equation | 数学 → 数论 → 裴蜀定理 & 一次不定方程 | direct |  |
| carmichael | 数学 → 数论 → 费马小定理 & 欧拉定理 | related | 公共指数与欧拉定理相关；导航无独立 Carmichael 页，不伪造叶节点。 |
| batch_inverse | 数学 → 数论 → 模逆元 | direct |  |
| batch_units | 数学 → 数论 → 模逆元 | direct |  |
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
| CompositeRoots | 数学 → 数论 → 高次剩余 & 单位根 | application | 高次剩余求根及素数幂、CRT 组合，准备函数保留依赖。 |
| KthResidue | 数学 → 数论 → 高次剩余 & 单位根 | application | 高次剩余求根及素数幂、CRT 组合，准备函数保留依赖。 |
| PrimePowerRoots | 数学 → 数论 → 高次剩余 & 单位根 | application | 高次剩余求根及素数幂、CRT 组合，准备函数保留依赖。 |
| root_factors | 数学 → 数论 → 高次剩余 & 单位根 | application | 高次剩余求根及素数幂、CRT 组合，准备函数保留依赖。 |
| CoprimePairs | 数学 → 数论 → 莫比乌斯反演 | application | Möbius 反演的矩形计数应用。 |
| DuJiao | 数学 → 数论 → 狄利克雷双曲线法 & 杜教筛 | direct |  |
| prime_count | 数学 → 数论 → 素数计数 | direct | 整除分块埃筛精确计算素数个数。 |
| Min25 | 数学 → 数论 → Min_25 筛 | direct | 低次素数多项式加素数幂回调的递归版本。 |
| floor_moments | 数学 → 数论 → 类欧几里德算法 | direct |  |
| floor_sum | 数学 → 数论 → 类欧几里德算法 | direct |  |
| NttConvolution | 数学 → 多项式与生成函数 → 快速数论变换 | application | NTT 卷积及三模重构扩展；整数范围契约保留。 |
| convolution_i64 | 数学 → 多项式与生成函数 → 快速数论变换 | application | NTT 卷积及三模重构扩展；整数范围契约保留。 |
| SetConvolution | 数学 → 多项式与生成函数 → 快速沃尔什变换 | application | 按位卷积及分层子集卷积；分别说明运算规则。 |
| subset_convolution | 数学 → 多项式与生成函数 → 快速沃尔什变换 | application | 按位卷积及分层子集卷积；分别说明运算规则。 |
| chirp_z | 数学 → 多项式与生成函数 → Chirp Z 变换 | direct |  |
| FpsInverse | 数学 → 多项式与生成函数 → 多项式牛顿迭代 | direct |  |
| FpsFunctions | 数学 → 多项式与生成函数 → 多项式初等函数 | direct |  |
| BostanMori | 数学 → 多项式与生成函数 → 常系数齐次线性递推 | direct |  |
| recurrence_nth | 数学 → 多项式与生成函数 → 常系数齐次线性递推 | direct |  |
| polynomial_shift | 数学 → 多项式与生成函数 → 多项式平移\|连续点值平移 | direct |  |
| Binomial | 数学 → 组合数学 → 排列组合 | direct |  |
| stirling_first_row | 数学 → 组合数学 → 斯特林数 | direct |  |
| stirling_second_row | 数学 → 组合数学 → 斯特林数 | direct |  |
| Partitions | 数学 → 组合数学 → 分拆数 | direct |  |
| MaxPlusMatrix | 数学 → 线性代数 → 矩阵 | application | max-plus 半环矩阵；不是普通域矩阵运算。 |
| ModMatrix | 数学 → 线性代数 → 矩阵 | direct |  |
| matrix_inverse | 数学 → 线性代数 → 矩阵 | direct | 素数模方阵求逆，使用 Gauss-Jordan 消元。 |
| matrix_inverse_mod2 | 数学 → 线性代数 → 矩阵 | direct | F2 上的方阵求逆，uint64_t 按位消元。 |
| det_prime | 数学 → 线性代数 → 行列式 | direct |  |
| determinant_mod | 数学 → 线性代数 → 行列式 | direct |  |
| PositionBasis | 数学 → 线性代数 → 线性基 | direct |  |
| XorBasis | 数学 → 线性代数 → 线性基 | direct |  |
| XorWalk | 数学 → 线性代数 → 线性基 | application | 图上异或行走的线性基应用；关联图 DFS。 |
| basis_intersection | 数学 → 线性代数 → 线性基 | direct |  |
| basis_sum_intersection | 数学 → 线性代数 → 线性基 | direct |  |
| Lagrange | 数学 → 数值算法 → 插值 | direct |  |
| GaussMod | 数学 → 数值算法 → 高斯消元 | direct |  |
| berlekamp_massey | 数学 → Berlekamp–Massey 算法 | direct |  |
| gp_map | 数据结构 → 哈希表 | application | GNU 哈希表组件，保留 GNU 扩展依赖。 |
| RollbackDSU | 数据结构 → 并查集 → 并查集 | direct |  |
| dsu | 数据结构 → 并查集 → 并查集 | direct |  |
| pheap | 数据结构 → 堆 → 配对堆 | application | GNU pairing_heap_tag 实现，按实际数据结构归堆；另在infra语言基础索引中登记。 |
| LeftistHeap | 数据结构 → 堆 → 左偏树 | direct |  |
| Fenwick | 数据结构 → 树状数组 | direct |  |
| AffineSegTree | 数据结构 → 线段树 → 线段树基础 | direct |  |
| LazySeg | 数据结构 → 线段树 → 线段树基础 | direct |  |
| lazy_segtree | 数据结构 → 线段树 → 线段树基础 | direct |  |
| segtree | 数据结构 → 线段树 → 线段树基础 | direct |  |
| LiChao | 数据结构 → 线段树 → 李超线段树 | direct |  |
| SegmentLiChao | 数据结构 → 线段树 → 李超线段树 | direct |  |
| ost | 数据结构 → 二叉搜索树 & 平衡树 → 二叉搜索树 & 平衡树 | application | 按用户 issue #8 明确要求放在平衡树板块，覆盖之前的默认 OI Wiki 归属。 |
| rp | 数据结构 → 二叉搜索树 & 平衡树 → 二叉搜索树 & 平衡树 | application | 按用户 issue #8 明确要求放在平衡树板块，覆盖之前的默认 OI Wiki 归属。 |
| GcdSequenceTreap | 数据结构 → 二叉搜索树 & 平衡树 → Treap | direct |  |
| OrderedTreap | 数据结构 → 二叉搜索树 & 平衡树 → Treap | direct |  |
| SequenceTreap | 数据结构 → 二叉搜索树 & 平衡树 → Treap | direct |  |
| OrderedSplay | 数据结构 → 二叉搜索树 & 平衡树 → Splay 树 | direct |  |
| PersistentArray | 数据结构 → 可持久化数据结构 → 可持久化线段树 | application | 可持久化线段树的区间、树路径、数组和版本应用。 |
| PersistentDistinct | 数据结构 → 可持久化数据结构 → 可持久化线段树 | application | 可持久化线段树的区间、树路径、数组和版本应用。 |
| PersistentKth | 数据结构 → 可持久化数据结构 → 可持久化线段树 | application | 可持久化线段树的区间、树路径、数组和版本应用。 |
| PersistentRange | 数据结构 → 可持久化数据结构 → 可持久化线段树 | application | 可持久化线段树的区间、树路径、数组和版本应用。 |
| TreePathKth | 数据结构 → 可持久化数据结构 → 可持久化线段树 | application | 可持久化线段树的区间、树路径、数组和版本应用。 |
| DynamicKth | 数据结构 → 树套树 → 树状数组套权值线段树 | direct |  |
| LinkCutTree | 数据结构 → 动态树 → Link Cut Tree | direct |  |
| odd_induced_partition | 图论 → DFS（图论） | application | DFS 后序与回边构造奇度诱导子图划分；固定导航没有此定理的独立条目，不等同于普通图染色。 |
| TreeDiameter | 图论 → 树上问题 → 树的直径 | direct |  |
| EulerLCA | 图论 → 树上问题 → 最近公共祖先 | application | LCA 不同算法及路径交应用。 |
| LiftingLCA | 图论 → 树上问题 → 最近公共祖先 | application | LCA 不同算法及路径交应用。 |
| OfflineLCA | 图论 → 树上问题 → 最近公共祖先 | application | LCA 不同算法及路径交应用。 |
| path_intersection | 图论 → 树上问题 → 最近公共祖先 | application | LCA 不同算法及路径交应用。 |
| HLD | 图论 → 树上问题 → 树链剖分 | direct |  |
| SubtreeColors | 图论 → 树上问题 → 树上启发式合并 | direct |  |
| VirtualTree | 图论 → 树上问题 → 虚树 | direct |  |
| CentroidPairs | 图论 → 树上问题 → 树分治 | direct |  |
| Dijkstra | 图论 → 最短路问题 → 最短路 | direct |  |
| Johnson | 图论 → 最短路问题 → 最短路 | direct |  |
| release_bfs | 图论 → 最短路问题 → 最短路 | application | 开放时间松弛的单位边特例。 |
| Arborescence | 图论 → 生成树问题 → 最小树形图 | direct |  |
| FunctionalGraph | 图论 → 连通性相关 → 强连通分量 | related | 函数图包含尾链与环分解，导航无独立页；需正文定位，不应等同一般 SCC 算法。 |
| SCC | 图论 → 连通性相关 → 强连通分量 | direct |  |
| TarjanSCC | 图论 → 连通性相关 → 强连通分量 | direct |  |
| BiconnectedCore | 图论 → 连通性相关 → 双连通分量 | direct |  |
| EdgeCompression | 图论 → 连通性相关 → 双连通分量 | application | 边双缩点及强连通定向应用。 |
| bridge_component_forest | 图论 → 连通性相关 → 双连通分量 | direct |  |
| odd_cycle_vertices | 图论 → 连通性相关 → 双连通分量 | application | 点双分解与二分图判定找奇环顶点。 |
| orient_edges | 图论 → 连通性相关 → 双连通分量 | application | 边双缩点及强连通定向应用。 |
| Lowlink | 图论 → 连通性相关 → 割点和桥 | application | 割点/桥及其删点、增边应用。 |
| bridge_augmentation | 图论 → 连通性相关 → 割点和桥 | application | 割点/桥及其删点、增边应用。 |
| removal_components | 图论 → 连通性相关 → 割点和桥 | application | 割点/桥及其删点、增边应用。 |
| block_cut_forest | 图论 → 连通性相关 → 圆方树 | direct |  |
| enumerate_triangles | 图论 → 环计数问题 | direct |  |
| LexTwoSAT | 图论 → 2-SAT | direct |  |
| TwoSAT | 图论 → 2-SAT | direct |  |
| DirectedEuler | 图论 → 欧拉图 | application | 有向、无向、混合和字典序应用，保留差异。 |
| UndirectedEuler | 图论 → 欧拉图 | application | 有向、无向、混合和字典序应用，保留差异。 |
| mixed_euler_orientation | 图论 → 欧拉图 | application | 有向、无向、混合和字典序应用，保留差异。 |
| mixed_euler_trail | 图论 → 欧拉图 | application | 有向、无向、混合和字典序应用，保留差异。 |
| word_chain | 图论 → 欧拉图 | application | 有向、无向、混合和字典序应用，保留差异。 |
| Dinic | 图论 → 网络流 → 最大流 | direct |  |
| unit_flow_edges | 图论 → 网络流 → 最大流 | application | 固定最大流值下的单位边流量可行性，通过残量环与 SCC 分类；不是最小割边分类。 |
| cut_tree_values | 图论 → 网络流 → 最小割 | application | 最小割的应用或查询；需在对应小节下保留本库名称。 |
| gomory_hu | 图论 → 网络流 → 最小割 | application | 最小割的应用或查询；需在对应小节下保留本库名称。 |
| maximum_closure | 图论 → 网络流 → 最小割 | application | 最小割的应用或查询；需在对应小节下保留本库名称。 |
| mincut_edges | 图论 → 网络流 → 最小割 | direct |  |
| MinCostFlow | 图论 → 网络流 → 费用流 | direct |  |
| NegativeCostFlow | 图论 → 网络流 → 费用流 | direct | 通过负边预流与需求修复处理负环，随后继续最短增广。 |
| BoundedCirculation | 图论 → 网络流 → 上下界网络流 | direct |  |
| BoundedMaxFlow | 图论 → 网络流 → 上下界网络流 | direct |  |
| StoerWagner | 图论 → 网络流 → Stoer–Wagner 算法 | direct |  |
| BipartiteMatching | 图论 → 图的匹配 → 二分图最大匹配 | direct |  |
| matching_edges | 图论 → 图的匹配 → 二分图最大匹配 | direct |  |
| Hungarian | 图论 → 图的匹配 → 二分图最大权匹配 | direct |  |
| WeightedMatching | 图论 → 图的匹配 → 二分图最大权匹配 | direct |  |
| Blossom | 图论 → 图的匹配 → 一般图最大匹配 | direct |  |
| MatrixTree | 图论 → 矩阵树定理 | direct |  |
| MatrixTreeMod | 图论 → 矩阵树定理 | direct |  |
| DominatorTree | 图论 → 支配树 | direct |  |
| CirclePolygon | 计算几何 → 二维计算几何基础 | application | 二维圆构造与面积应用，保留退化和精度条件。 |
| CircleTangents | 计算几何 → 二维计算几何基础 | application | 二维圆构造与面积应用，保留退化和精度条件。 |
| IntegerPlane | 计算几何 → 二维计算几何基础 | direct |  |
| RealPlane | 计算几何 → 二维计算几何基础 | direct |  |
| circle_intersections | 计算几何 → 二维计算几何基础 | direct |  |
| circle_overlap_area | 计算几何 → 二维计算几何基础 | direct |  |
| line_circle_intersections | 计算几何 → 二维计算几何基础 | direct |  |
| line_intersection_real | 计算几何 → 二维计算几何基础 | direct |  |
| line_projection | 计算几何 → 二维计算几何基础 | direct |  |
| polygon_area2 | 计算几何 → 二维计算几何基础 | direct |  |
| polygon_contains | 计算几何 → 二维计算几何基础 | direct |  |
| IntegerGeometry3D | 计算几何 → 三维计算几何基础 | direct |  |
| segment_distance_real | 计算几何 → 距离 | direct |  |
| SupportHull | 计算几何 → 凸包 | application | 支撑点查询恢复下凸包。 |
| convex_contains_i64 | 计算几何 → 凸包 | direct |  |
| integer_hull | 计算几何 → 凸包 | direct |  |
| minkowski_sum | 计算几何 → 凸包 | related | 固定导航没有独立 Minkowski 和条目，按凸包的相关应用归档。 |
| convex_diameter2 | 计算几何 → 旋转卡壳 | direct |  |
| IntegerHalfplanes | 计算几何 → 半平面交 | direct |  |
| ClosestPair | 计算几何 → 平面最近点对 | direct |  |
| closest_pair_i64 | 计算几何 → 平面最近点对 | direct |  |
| EnclosingCircle | 计算几何 → 随机增量法 | application | 随机增量最小覆盖圆。 |
| ModifiedMo | 杂项 → 离线算法 → 莫队算法 → 带修改莫队 | direct |  |
