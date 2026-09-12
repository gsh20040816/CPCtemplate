#!/usr/bin/env python3
import json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
cat=json.loads((root/'docs/catalog.json').read_text())
def esc(s):
 for a,b in [('\\',r'\textbackslash{}'),('&',r'\&'),('%',r'\%'),('$',r'\$'),('#',r'\#'),('_',r'\_'),('{',r'\{'),('}',r'\}')]:
  if a!='\\': s=s.replace(a,b)
 s=s.replace('^',r'\textasciicircum{}')
 s=re.sub('[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+',lambda m:'$^{'+m[0].translate(str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁻','0123456789-'))+'}$',s)
 for a,b in {'λ':r'$\lambda$','ω':r'$\omega$','≡':r'$\equiv$','≤':r'$\le$','≥':r'$\ge$','≠':r'$\ne$','Σ':r'$\sum$','α':r'$\alpha$','μ':r'$\mu$','φ':r'$\varphi$','²':r'$^2$','³':r'$^3$','⁹':r'$^9$','⁶':r'$^6$','⁻¹²':r'$^{-12}$','¹²':r'$^{12}$','¹¹':r'$^{11}$','√':r'$\sqrt{\vphantom x}$','–':'--'}.items():s=s.replace(a,b)
 return s
classic={'MatrixTreeMod':'Matrix_Tree_Mod','determinant_mod':'Determinant_Mod','MatrixTree':'Matrix_Tree','root_factors':'Root_Factors','CompositeRoots':'Composite_Roots','PrimePowerRoots':'Prime_Power_Roots','KthResidue':'Kth_Residue','CirclePolygon':'Circle_Polygon','EnclosingCircle':'Enclosing_Circle','CircleTangents':'Circle_Tangents','ClosestPair':'Closest_Pair','IntegerHalfplanes':'Integer_Halfplanes','cut_tree_values':'Cut_Tree_Values','gomory_hu':'Gomory_Hu','floor_moments':'Floor_Moments','power_sum':'Power_Sum','divisor_sum_power':'Divisor_Sum_Power','Partitions':'Integer_Partitions','CoprimePairs':'Coprime_Pairs','euler_phi':'Euler_Phi','linear_congruence':'Linear_Congruence','linear_equation':'Linear_Equation','segmented_primes':'Segmented_Primes','inverse_table':'Inverse_Table','batch_inverse':'Batch_Inverse','carmichael':'Carmichael','PrimitiveRoot':'Primitive_Root','Lucas':'Lucas_Theorem','garner':'Garner','LexTwoSAT':'Lex_Two_SAT','odd_cycle_vertices':'Odd_Cycle_Vertices','mixed_euler_orientation':'Mixed_Euler_Orientation','mixed_euler_trail':'Mixed_Euler_Trail','word_chain':'Word_Chain','UndirectedEuler':'Undirected_Euler','DirectedEuler':'Directed_Euler','path_intersection':'Path_Intersection','LiftingLCA':'Lifting_LCA','EulerLCA':'Euler_LCA','OfflineLCA':'Offline_LCA','bridge_augmentation':'Bridge_Augmentation','EdgeCompression':'Edge_Compression','orient_edges':'Orient_Edges','removal_components':'Removal_Components','XorWalk':'Xor_Walk','basis_intersection':'Basis_Intersection','basis_sum_intersection':'Basis_Sum_Intersection','PositionBasis':'Position_Basis','SuffixLCP':'Suffix_LCP','prefix_lcs':'Prefix_Lcs','square_counts':'Square_Counts','SupportHull':'Support_Hull','maximum_closure':'Maximum_Closure','mod_sqrt':'Mod_Sqrt','PersistentDistinct':'Persistent_Distinct','DynamicKth':'Dynamic_Kth','TreePathKth':'Tree_Path_Kth','Lagrange':'Lagrange_Interpolation','ExLucas':'Ex_Lucas','WeightedMatching':'Weighted_Matching','PersistentArray':'Persistent_Array','VirtualTree':'Virtual_Tree','AffineSegTree':'Affine_Segment_Tree','SubtreeColors':'Subtree_Colors','CentroidPairs':'Centroid_Pairs','PalindromicTree':'Palindromic_Tree','Biconnected':'Biconnected_Graph','TarjanSCC':'Tarjan_SCC','berlekamp_massey':'Berlekamp_Massey','recurrence_nth':'Recurrence_Nth','Blossom':'General_Matching','OrderedSplay':'Ordered_Splay','GcdSequenceTreap':'Gcd_Sequence_Treap','LinkCutTree':'Link_Cut_Tree','OrderedTreap':'Ordered_Treap','SequenceTreap':'Sequence_Treap','prefix_function':'Prefix_Function','kmp_match':'Kmp_Match','z_function':'Z_Function','manacher':'Manacher','minimum_rotation':'Minimum_Rotation','RollbackDSU':'Rollback_DSU','XorBasis':'Xor_Basis','GeometryExtra':'Geometry_Extra','IntegerGeometry3D':'Integer_Geometry_3D','BoundedCirculation':'Bounded_Circulation','Hungarian':'Kuhn_Munkres','Arborescence':'Directed_MST','StoerWagner':'Global_Min_Cut','MaxPlusMatrix':'Max_Plus_Matrix','LiChao':'Li_Chao_Tree','PersistentKth':'Persistent_Kth','DSU':'Disjoint_Set','Fenwick':'Binary_Indexed_Tree','LazySeg':'Segment_Tree','Dinic':'Network_Flow','MinCostFlow':'Min_Cost_Flow','Dijkstra':'Shortest_Path','SCC':'Strong_Component','TwoSAT':'Two_SAT','BipartiteMatching':'Bipartite_Matching','Lowlink':'Low_Link','HLD':'Heavy_Light_Decomposition','StringAlgo':'String_Algorithm','AhoCorasick':'AC_Automaton','SuffixArray':'Suffix_Array','SuffixAutomaton':'Suffix_Automaton','NumberTheory':'Number_Theory','PollardRho':'Pollard_Rho','LinearSieve':'Linear_Sieve','ModInt':'Mod_Int','Binomial':'Combination','Polynomial':'Polynomial','IntegerGeometry':'Integer_Geometry','RealGeometry':'Real_Geometry','LinearAlgebra':'Linear_Algebra','DuJiao':'Du_Jiao','DiscreteLog':'Discrete_Log'}
chapters={'tarjan':'Tarjan 与缩点','biconnected':'双连通分量与圆方树','odd_cycle_vertices':'奇环顶点判定','vertex_removal':'删点连通性','edge_components':'边双缩点与边定向','bridge_augmentation':'桥树最少加边','data_structure':'数据结构','position_basis':'带位置线性基','basis_intersection':'线性空间求交','affine_segment_tree':'线段树常用修改','flow':'网络流','maximum_closure':'最大权闭合子图','graph':'图论','lex_two_sat':'字典序最小 2-SAT','directed_euler':'有向欧拉路','word_chain':'字典序单词链','undirected_euler':'无向欧拉路','mixed_euler':'混合图欧拉定向','xor_walk':'图上异或行走','tree':'树上算法','offline_lca':'离线最近公共祖先','euler_lca':'在线最近公共祖先','lifting_lca':'倍增祖先与路径最值','path_intersection':'树上路径交','centroid':'点分治','dsu_on_tree':'树上启发式合并','virtual_tree':'虚树','string':'字符串','suffix_lcp':'后缀查询与重复子串','palindromic_tree':'回文树','number_theory':'数论','linear_equation':'二元一次不定方程','linear_congruence':'线性同余方程','segmented_sieve':'区间筛素数','batch_inverse':'批量模逆元','inverse_table':'连续整数逆元表','garner':'混合进制中国剩余定理','primitive_root':'乘法阶与原根','coprime_pairs':'矩形 GCD 计数','floor_moments':'带权类欧几里德','divisor_sum':'模几何级数与约数和','euler_phi':'单个数的欧拉函数','carmichael':'Carmichael 函数','partitions':'整数分拆','lucas':'素数模数组合数','exlucas':'合数模数组合数','modular_sqrt':'二次剩余','kth_residue':'素数模高次剩余','prime_power_roots':'素数幂模高次剩余','root_factors':'合数求根的准备','composite_roots':'合数模高次剩余','interpolation':'多项式插值','polynomial':'多项式','algebra':'代数与数论进阶','determinant_mod':'任意模数行列式','matrix_tree':'带权生成树计数','matrix_tree_mod':'合数模生成树计数','geometry':'计算几何','optimization':'优化与可持久化','persistent_array':'可持久化数组','tree_path_kth':'树上路径第 k 小','dynamic_kth':'动态区间顺序统计','persistent_distinct':'区间不同数统计','graph_advanced':'图论进阶','gomory_hu':'最小割树','cut_tree_queries':'最小割树查询','weighted_matching':'带权二分图匹配','halfplanes':'精确有界半平面交','circle_polygon':'圆与多边形面积','enclosing_circle':'最小覆盖圆','circle_tangents':'圆的切线','closest_pair':'浮点最近点对','geometry_extra':'精确几何进阶','support_hull':'凸包支撑点查询','dynamic_tree':'动态树','treap':'随机平衡树','splay':'伸展树','gcd_sequence':'状态序列维护','blossom':'一般图匹配','recurrence':'线性递推'}
body=[]
for style in ['compact','classic']:
 body.append(r'\part{'+('动态容器风格' if style=='compact' else '传统接口风格')+'}')
 for file,title in chapters.items():
  body.append(r'\chapter{'+title+'}')
  for f,name,cn,info in cat:
   if f!=file:continue
   target=name if style=='compact' else classic.get(name)
   if not target: continue
   filename='min_cost_flow' if style=='classic' and name=='MinCostFlow' else file
   p=root/f'src/{style}/{filename}.hpp';lines=p.read_text().splitlines()
   marker='// BEGIN '+target
   if marker in lines:
    start=lines.index(marker)+1
    end=lines.index('// END '+target,start)
   else:
    starts=[]
    for i,line in enumerate(lines):
     m=re.match(r'^(?:template.*?\s+)?struct\s+(\w+)',line)
     if m: starts.append((i,m[1]))
    idx=next(i for i,x in enumerate(starts) if x[1]==target)
    start=starts[idx][0]
    end=starts[idx+1][0] if idx+1<len(starts) else len(lines)
    if start and lines[start-1].startswith('template'): start-=1
    if end and lines[end-1].startswith('template'): end-=1
   estimate=sum(max(1,(len(line.expandtabs(4))+109)//110) for line in lines[start:end])*10.2+70+(len(info)/65)*12
   if name=='LexTwoSAT':
    split=next(i for i in range(start,end) if re.match(r'    bool (paint|Paint)\(',lines[i]))
    estimate=(split-start)*10.2+70+(len(info)/65)*12
   if name=='odd_cycle_vertices':
    split=next(i for i in range(start,end) if 'edges(graph.blocks.size())' in lines[i])
    estimate=(split-start)*10.2+70+(len(info)/65)*12
   if name=='mixed_euler_orientation':
    split=next(i for i in range(start,end) if '!edges.empty()' in lines[i])
    estimate=(split-start)*10.2+70+(len(info)/65)*12
   if name in ('DirectedEuler','UndirectedEuler'):
    split=next(i for i in range(start,end) if re.match(r'    bool (run|Run)\(',lines[i]))-1
    estimate=(split-start)*10.2+70+(len(info)/65)*12
   if name=='LiftingLCA':
    split=next(i for i in range(start,end) if re.match(r'    void (dfs|Dfs)\(',lines[i]))
    estimate=(split-start)*10.2+70+(len(info)/65)*12
   if name=='EulerLCA':
    split=next(i for i in range(start,end) if re.match(r'    void (dfs|Dfs)\(',lines[i]))
    estimate=(split-start)*10.2+70+(len(info)/65)*12
   if name=='OfflineLCA':
    split=next(i for i in range(start,end) if re.match(r'    int (find|Find)\(',lines[i]))
    estimate=(split-start)*10.2+70+(len(info)/65)*12
   if name=='Lowlink':
    split=next(i for i in range(start,end) if re.match(r'    void (dfs|Dfs)\(',lines[i]))
    estimate=(split-start)*10.2+70+(len(info)/65)*12
   if name=='SuffixLCP':
    split=next(i for i in range(start,end) if re.match(r'    int (query|Query)\(',lines[i]))
    estimate=(split-start)*10.2+70+(len(info)/65)*12
   if name=='divisor_sum_power' and style=='compact': body.append(r'\newpage')
   if name=='Arborescence':
    split=next(i for i in range(start,end) if lines[i].strip()=='int cnt = 0;')
    estimate=(split-start)*10.2+100+(len(info)/55)*12
   if name=='StoerWagner':
    split=next(i for i in range(start,end) if 'step + 1 ==' in lines[i])
    estimate=(split-start)*10.2+100+(len(info)/55)*12
   if name=='IntegerHalfplanes':
    split=next(i for i in range(start,end) if re.match(r'    static I (value|Value)\(',lines[i]))
    estimate=(split-start)*10.2+100+(len(info)/55)*12
   if name=='ClosestPair':
    split=next(i for i in range(start,end) if lines[i].strip()=='int m = (l + r) / 2;')
    estimate=(split-start)*10.2+100+(len(info)/55)*12
   if name=='CircleTangents':
    split=next(i for i in range(start,end) if lines[i].strip()=='Result answer;')
    estimate=(split-start)*10.2+100+(len(info)/55)*12
   if name=='EnclosingCircle':
    split=next(i for i in range(start,end) if 'static optional<Circle>' in lines[i])
    estimate=(split-start)*10.2+100+(len(info)/55)*12
   if name=='CirclePolygon':
    split=next(i for i in range(start,end) if lines[i].strip()=='R answer = 0;')
    estimate=(split-start)*10.2+100+(len(info)/55)*12
   if name=='PrimePowerRoots':
    split=next(i for i in range(start,end) if 'static optional<Prime' in lines[i])
    estimate=(split-start)*10.2+100+(len(info)/55)*12
   if name=='CompositeRoots':
    split=next(i for i in range(start,end) if 'static optional<Composite' in lines[i])
    estimate=(split-start)*10.2+100+(len(info)/55)*12
   if estimate<680: body.append(r'\Needspace{'+str(round(estimate))+'pt}')
   if name in ('SuffixArray','XorBasis','IntegerGeometry3D'): body.append(r'\newpage')
   body.append(r'\section{'+cn+r'}\label{'+style+'-'+name+r'}\index{'+target.replace('_',r'\_')+'}')
   if style=='compact': body.append(esc(info))
   else:
    body.append('算法约束见动态版本第~\\pageref{compact-'+name+'}~页。本节代码独立可抄；采用下列实际接口名。')
    if name in ['DSU','Fenwick','LazySeg','Dinic']:body.append('先声明容量模板参数，再调用 Init(n) 初始化；大对象必须置于全局或 static 存储。')
    if name=='LinkCutTree':body.append('声明 Link\\_Cut\\_Tree<N>，然后 Init(n) 初始化；N 为最大点号。Set、Link、Cut、Connected、Query 分别对应动态版的小写接口。大对象放在全局或 static。')
    if name in ['OrderedTreap','SequenceTreap']:body.append('声明容量模板参数 N，然后 Init() 或 Init(seed)。N 限制累计插入次数，不是当前元素个数；大对象放在全局或 static。接口采用 Insert、Erase、Kth/Query 等命名。')
    if name=='OrderedSplay':body.append('声明 Ordered\\_Splay<N> 后调用 Init()；N 为累计新建节点上限。接口采用 Insert、Erase、Rank、Kth、Prev、Next。大对象放在全局或 static。')
    if name=='GcdSequenceTreap':body.append('声明 Gcd\\_Sequence\\_Treap<N> 后调用 Init(seed)；N 为峰值元素数。Build 重建序列，Insert、Erase、Set、Toggle、Query 对应动态版接口。大对象放在全局或 static。')
    if name=='Blossom':body.append('声明 General\\_Matching<N> 后调用 Init(n)，N 为点数上限。Insert 加边，Solve 返回匹配边数，mate 保存配对点，点号仍为 0-based。大对象放在全局或 static。')
    if name=='LexTwoSAT':body.append('声明 Lex\\_Two\\_SAT<N>，Init(n) 清空子句；Add、Force、Solve 与动态版对应，answer[1..n] 为答案。内部 Id 的字面量编号从 0 开始，大对象放全局或 static。')
    if name in ('mixed_euler_orientation','mixed_euler_trail'):body.append('调用时额外传入 Network\\_Flow<N,M> 工作区作为临时最大流图；N 至少为 n+2，M 至少为可反转边数+n。大流对象放全局或 static。')
    if name=='UndirectedEuler':body.append('声明 Undirected\\_Euler<N>，Init(n) 清空图，Insert 返回从 0 开始的逻辑边编号，Run 参数与动态版一致。vertices、edge\\_ids 和原边 edges 可直接读取；N 为最大点数，大对象放全局或 static。')
    if name=='DirectedEuler':body.append('声明 Directed\\_Euler<N>，Init(n) 清空图，Insert 加边并返回从 0 开始的边编号，Run 求解（参数默认值同动态版）。vertices、edge\\_ids、edges 可直接读取；N 为最大点数，大对象放全局或 static。')
    if name=='LiftingLCA':body.append('声明 Lifting\\_LCA<N,LOG>，Init(n) 清空树；Insert、Build、Jump、Lca、Distance、Max\\_Edge 对应动态接口。LOG 层要求 2 的 LOG 次方大于 n，默认 20；大对象放全局或 static。')
    if name=='EulerLCA':body.append('声明 Euler\\_LCA<N,LOG>，Init(n) 清空树；Insert 加边，Build(root) 预处理，Lca 与 Distance 在线查询。LOG 层必须满足 2 的 LOG 次方大于 2n-1，默认 20 支持 50 万点；st 固定容量为 LOG 乘以 2N。大对象放全局或 static。')
    if name=='OfflineLCA':body.append('声明 Offline\\_LCA<N>，Init(n) 清空树与查询；Insert 加无向树边，Add\\_Query 返回从 0 开始的查询编号，Run(root) 统一计算，answer[id] 为答案。大对象放全局或 static。')
    if name=='TarjanSCC':body.append('声明 Tarjan\\_SCC<N>，先 Init(n)，Insert 加边，Run 求分量，Dag 输出缩点图。bel 与 cnt 可直接读取；大对象放在全局或 static。')
    if name=='Biconnected':body.append('声明 Biconnected\\_Graph<N>，Init(n) 初始化，Insert 加边，Run 分解，Block\\_Forest 和 Bridge\\_Forest 输出两种森林。blocks、cut、bridge、bel、cnt 可直接读取。大对象放在全局或 static。')
    if name=='PalindromicTree':body.append('声明 Palindromic\\_Tree<N> 后调用 Init()；N 为最大追加字符数，内部另留两个根节点。Insert、Distinct、Occurrences 对应动态版接口；t、last、total 可直接读。大对象放在全局或 static。')
    if name=='CentroidPairs':body.append('声明 Centroid\\_Pairs<N>，Init(n) 初始化，Insert 加边，Build 预处理；Count\\_Leq 和 Count\\_Exact 返回计数，parent 保存点分树父节点。大对象放在全局或 static。')
    if name=='SubtreeColors':body.append('声明 Subtree\\_Colors<N>，Init(n) 初始化，Insert 加边，Run(colors,root) 计算；answer 与 max\\_freq 为最终结果。Add\\_Color 为内部统计函数。大对象放在全局或 static。')
    if name=='AffineSegTree':body.append('声明 Affine\\_Segment\\_Tree<N> 后 Init(a,mod)，N 为最大数组长度。Update(l,r,mul,add) 修改，Query(l,r) 求和；支持重复初始化。大对象放在全局或 static。')
    if name=='VirtualTree':body.append('声明 Virtual\\_Tree<N,LOG>，要求 2 的 LOG 次方大于实际点数，默认 LOG=20。Init(n)、Insert、Prepare、Build 对应初始化、加边、预处理和查询；Lca、Ancestor、Path 为对应辅助接口。大对象放在全局或 static。')
    if name=='PersistentArray':body.append('声明 Persistent\\_Array<NODES>，Init(a) 初始化；NODES 限制节点总数，不是数组长度。建议按 2n-1 加上修改数乘以 (ceil(log2(n))+1) 分配；Copy 不分配节点。Set、Copy、Query 对应动态接口。大对象放在全局或 static，Init 会丢弃全部旧版本。')
    if name=='XorWalk':body.append('声明 Xor\\_Walk<N>，Init(n) 清空，Insert 加边，Build(root) 预处理指定连通块，Query(u,v) 返回可选最大值。N 为最大点号，大对象置于全局或 static；空间 O(N+m+64)。DFS 保持递归。')
    if name=='HLD':body.append('声明 Heavy\\_Light\\_Decomposition<N> 后 Init(n)，Insert 加边，Build(root) 剖分；Lca 与 Path 对应动态接口。大对象放在全局或 static。')
    if name=='maximum_closure':body.append('Maximum\\_Closure(weight,dependencies,graph) 额外接收 Network\\_Flow<N,M> 引用，并在每次调用中 Init 重建该网络。N 至少为原点数加 2，M 至少为依赖边数加非零权点数；这是原有向边容量，不是残量边总数。将网络对象放在全局或 static，模板参数可由对象自动推导。')
    if name=='PersistentDistinct':body.append('声明 Persistent\\_Distinct<N,NODES> 后 Init(a)，Query(l,r) 为查询。N 限制数组长度；NODES 至少取 n 乘以 (ceil(log2(n))+1)，另有编号 0 空节点。n 不超过 1000000 时可取 NODES=21000000。大对象放在全局或 static，Init 可重复调用并清空全部旧版本。')
    if name=='DynamicKth':body.append('声明 Dynamic\\_Kth<N,NODES> 后 Init(a,future)，Set 与 Kth 为公开操作。N 限制数组长度，NODES 限制分配节点的最大编号，另有编号 0 空节点。按照上面的 B 分配一定足够；例如 n 不超过 100000 且 D 不超过 200000 时，B 不超过 16682000。节点回收使此界与修改次数无关。大对象放在全局或 static，Init 清空旧状态。')
    if name=='TreePathKth':body.append('声明 Tree\\_Path\\_Kth<N,NODES,LOG>，Init(a) 清空图并保存权值；Insert、Build、Kth、Lca 对应动态接口。要求 2 的 LOG 次方大于实际点数，默认 LOG=20。若不同权值数为 D，NODES 至少取 n 乘以 (ceil(log2(D))+1)，另有编号 0 空节点。大对象放在全局或 static；Init 与 Build 分别清空图和重建版本。')
    if name=='Lagrange':body.append('声明 Lagrange\\_Interpolation<N>；Init、Consecutive、Query 对应动态接口，N 为最大样本数。坐标、权值与工作数组均为静态数组，大对象放在全局或 static；Query 会改写工作数组。')
    if name=='PrimitiveRoot':body.append('构造 Primitive\\_Root(n)，Init、Order、Is\\_Root、Minimum、All 对应动态接口；Factors 为 phi 的不同素因子，依赖 Number\\_Theory::Power。')
    if name=='Binomial':body.append('Combination<prime>(n=0) 构造，Init(n) 扩大上限；Choose、Permute 对应组合数和排列数，fac、ifac 可只读访问。')
    if name=='Lucas':body.append('声明 Lucas\\_Theorem<N>，Init(p) 重建素数模数下的表，Choose(n,k) 查询。要求 p 不超过 N；大对象放全局或 static。传统版空间 O(N)。')
    if name=='ExLucas':body.append('声明 Ex\\_Lucas<N> 后 Init(mod)，要求 mod 不超过 N；Choose 为查询接口。fac 是共用静态前缀积数组，各素数幂通过 start 分段；各段总长度不超过 mod+1，所以 N 限制模数即可。Init 可切换模数并清空旧预处理，大对象放在全局或 static。')
    if name=='WeightedMatching':body.append('声明 Weighted\\_Matching<N,M> 后 Init(n,m)，N、M 分别限制左右点数。Insert 加边，Solve 求解；l、r 保存方案，Init 清空原图。权值矩阵是静态数组，内部增广辅助数组按实际规模分配，大对象放在全局或 static。')
    if name=='BipartiteMatching':body.append('声明 Bipartite\\_Matching<N,M> 后 Init(n,m)，两侧容量分别为 N、M。Insert 加边，Solve 求匹配，Cover 返回最小点覆盖；l、r 保存方案。大对象放在全局或 static。')
    if name=='MinCostFlow':body.append('使用 Insert 加边、Flow 求流、Used 查看方案。')
   if name in ('DirectedEuler','UndirectedEuler') and style=='classic':
    cuts=[start,next(i for i in range(start,end) if re.match(r'    int Insert\(',lines[i])),next(i for i in range(start,end) if re.match(r'    bool Run\(',lines[i]))-1,end]
    for j in range(len(cuts)-1):
     if j: body.append(r'\newpage')
     body.append(r'\lstinputlisting[firstline='+str(cuts[j]+1)+',lastline='+str(cuts[j+1])+',firstnumber='+str(cuts[j]-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   elif name=='Arborescence':
    split=next(i for i in range(start,end) if lines[i].strip()=='int cnt = 0;')
    body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(split)+']{../src/'+style+'/'+filename+'.hpp}')
    body.append(r'\newpage')
    body.append(r'\noindent 判环与缩点（接上页同一函数）：')
    body.append(r'\lstinputlisting[firstline='+str(split+1)+',lastline='+str(end)+',firstnumber='+str(split-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   elif name=='StoerWagner':
    split=next(i for i in range(start,end) if 'step + 1 ==' in lines[i])
    body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(split)+']{../src/'+style+'/'+filename+'.hpp}')
    body.append(r'\newpage')
    body.append(r'\noindent 本轮割、合并与继续扩张（接上页同一函数）：')
    body.append(r'\lstinputlisting[firstline='+str(split+1)+',lastline='+str(end)+',firstnumber='+str(split-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   elif name=='CompositeRoots':
    split=next(i for i in range(start,end) if 'static optional<Composite' in lines[i])
    body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(split)+']{../src/'+style+'/'+filename+'.hpp}')
    body.append(r'\newpage')
    body.append(r'\noindent 局部求根与 CRT 系数（接上页同一结构体）：')
    body.append(r'\lstinputlisting[firstline='+str(split+1)+',lastline='+str(end)+',firstnumber='+str(split-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   elif name=='PrimePowerRoots':
    first=next(i for i in range(start,end) if 'static optional<Prime' in lines[i])
    second=next(i for i in range(first,end) if lines[i].strip().startswith('ll scale ='))
    cuts=[start,first,second,end]
    for j in range(3):
     if j:
      body.append(r'\newpage')
      body.append(r'\noindent 接上页同一结构体（第三页继续同一函数）：')
     body.append(r'\lstinputlisting[firstline='+str(cuts[j]+1)+',lastline='+str(cuts[j+1])+',firstnumber='+str(cuts[j]-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   elif name=='CirclePolygon':
    split=next(i for i in range(start,end) if lines[i].strip()=='R answer = 0;')
    body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(split)+']{../src/'+style+'/'+filename+'.hpp}')
    body.append(r'\newpage')
    body.append(r'\noindent 分段面积与逐边累加（接上页同一结构体与函数）：')
    body.append(r'\lstinputlisting[firstline='+str(split+1)+',lastline='+str(end)+',firstnumber='+str(split-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   elif name=='EnclosingCircle':
    split=next(i for i in range(start,end) if 'static optional<Circle>' in lines[i])
    body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(split)+']{../src/'+style+'/'+filename+'.hpp}')
    body.append(r'\newpage')
    body.append(r'\noindent 随机增量主过程（接上页同一结构体）：')
    body.append(r'\lstinputlisting[firstline='+str(split+1)+',lastline='+str(end)+',firstnumber='+str(split-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   elif name=='CircleTangents':
    split=next(i for i in range(start,end) if lines[i].strip()=='Result answer;')
    body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(split)+']{../src/'+style+'/'+filename+'.hpp}')
    body.append(r'\newpage')
    body.append(r'\noindent 内外公切线枚举（接上页同一函数）：')
    body.append(r'\lstinputlisting[firstline='+str(split+1)+',lastline='+str(end)+',firstnumber='+str(split-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   elif name=='ClosestPair':
    split=next(i for i in range(start,end) if lines[i].strip()=='int m = (l + r) / 2;')
    body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(split)+']{../src/'+style+'/'+filename+'.hpp}')
    body.append(r'\newpage')
    body.append(r'\noindent 分治、归并与跨分界线点对（接上页同一函数）：')
    body.append(r'\lstinputlisting[firstline='+str(split+1)+',lastline='+str(end)+',firstnumber='+str(split-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   elif name=='IntegerHalfplanes':
    first=next(i for i in range(start,end) if re.match(r'    static I (value|Value)\(',lines[i]))
    second=next(i for i in range(first,end) if lines[i].strip()=='deque<Line> q;')
    cuts=[start,first,second,end]
    for j in range(3):
     if j:
      body.append(r'\newpage')
      body.append(r'\noindent 接上页同一结构体与函数：')
     body.append(r'\lstinputlisting[firstline='+str(cuts[j]+1)+',lastline='+str(cuts[j+1])+',firstnumber='+str(cuts[j]-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   elif name=='garner' and style=='compact':
    split=next(i for i in range(start,end) if lines[i].startswith('// Return the least'))
    body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(split)+']{../src/'+style+'/'+filename+'.hpp}')
    body.append(r'\Needspace{180pt}')
    body.append(r'\subsection*{规范解对目标数取模}')
    body.append(r'\lstinputlisting[firstline='+str(split+1)+',lastline='+str(end)+',firstnumber='+str(split-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   elif name=='Lucas':
    split=next(i for i in range(start,end) if re.match(r'    int (choose|Choose)\(',lines[i]))
    body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(split)+']{../src/'+style+'/'+filename+'.hpp}')
    body.append(r'\Needspace{270pt}')
    body.append(r'\lstinputlisting[firstline='+str(split+1)+',lastline='+str(end)+',firstnumber='+str(split-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   elif name=='PrimitiveRoot':
    cuts=[start,next(i for i in range(start,end) if re.match(r'    void (init|Init)\(',lines[i])),next(i for i in range(start,end) if re.match(r'    bool (is_root|Is_Root)\(',lines[i])),end]
    for j in range(len(cuts)-1):
     if j: body.append(r'\newpage')
     body.append(r'\lstinputlisting[firstline='+str(cuts[j]+1)+',lastline='+str(cuts[j+1])+',firstnumber='+str(cuts[j]-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   elif name=='Binomial':
    split=next(i for i in range(start,end) if re.match(r'    Z (choose|Choose)\(',lines[i]))
    body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(split)+']{../src/'+style+'/'+filename+'.hpp}')
    body.append(r'\Needspace{220pt}')
    body.append(r'\lstinputlisting[firstline='+str(split+1)+',lastline='+str(end)+',firstnumber='+str(split-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   elif name=='LiftingLCA':
    cuts=[start,next(i for i in range(start,end) if re.match(r'    void (dfs|Dfs)\(',lines[i])),next(i for i in range(start,end) if re.match(r'    int (lca|Lca)\(',lines[i])),end]
    for j in range(len(cuts)-1):
     if j: body.append(r'\newpage')
     body.append(r'\lstinputlisting[firstline='+str(cuts[j]+1)+',lastline='+str(cuts[j+1])+',firstnumber='+str(cuts[j]-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   elif name=='XorBasis':
    if style=='compact':
     cuts=[start,
           next(i for i in range(start,end) if re.match(r'    bool contains\(',lines[i])),
           next(i for i in range(start,end) if re.match(r'    optional<U> kth\(',lines[i]))-1,
           end]
    else:
     cuts=[start,next(i for i in range(start,end) if re.match(r'    void Rebuild\(',lines[i])),end]
    for j in range(len(cuts)-1):
     if j: body.append(r'\newpage')
     body.append(r'\lstinputlisting[firstline='+str(cuts[j]+1)+',lastline='+str(cuts[j+1])+',firstnumber='+str(cuts[j]-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   elif name=='SuffixArray':
    split=next(i for i in range(start,end) if re.search(r'for \(\s*int k = 1; k < n;',lines[i]))
    body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(split)+']{../src/'+style+'/'+filename+'.hpp}')
    body.append(r'\newpage')
    body.append(r'\lstinputlisting[firstline='+str(split+1)+',lastline='+str(end)+',firstnumber='+str(split-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
    body.append(r'\newpage')
   elif name in ('ExLucas','DynamicKth','SupportHull','SuffixLCP','PositionBasis','XorWalk','Lowlink','OfflineLCA','EulerLCA','DirectedEuler','UndirectedEuler','mixed_euler_orientation','odd_cycle_vertices','LexTwoSAT'):
    if name=='LexTwoSAT':
     split=next(i for i in range(start,end) if re.match(r'    bool (paint|Paint)\(',lines[i]))
    elif name=='odd_cycle_vertices':
     split=next(i for i in range(start,end) if 'edges(graph.blocks.size())' in lines[i])
    elif name=='mixed_euler_orientation':
     split=next(i for i in range(start,end) if '!edges.empty()' in lines[i])
    elif name in ('DirectedEuler','UndirectedEuler'):
     split=next(i for i in range(start,end) if re.match(r'    bool (run|Run)\(',lines[i]))-1
    elif name=='EulerLCA':
     split=next(i for i in range(start,end) if re.match(r'    void (dfs|Dfs)\(',lines[i]))
    elif name=='OfflineLCA':
     split=next(i for i in range(start,end) if re.match(r'    int (find|Find)\(',lines[i]))
    elif name=='Lowlink':
     split=next(i for i in range(start,end) if re.match(r'    void (dfs|Dfs)\(',lines[i]))
    elif name=='XorWalk':
     split=next(i for i in range(start,end) if re.match(r'    void (add|Insert)\(',lines[i]))
    elif name=='PositionBasis':
     split=next(i for i in range(start,end) if re.match(r'    void (insert|Insert)\(',lines[i]))
    elif name=='SuffixLCP':
     split=next(i for i in range(start,end) if re.match(r'    int (query|Query)\(',lines[i]))
    elif name=='SupportHull':
     split=next(i for i in range(start,end) if 'template <class Oracle>' in lines[i]) - 2
    else:
     split=next(i for i in range(start,end) if re.match(r'    (?:int (?:choose|Choose)|void (?:set|Set))\(',lines[i]))
    body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(split)+']{../src/'+style+'/'+filename+'.hpp}')
    if name in ('SupportHull','SuffixLCP','PositionBasis','XorWalk','Lowlink','OfflineLCA','EulerLCA','DirectedEuler','UndirectedEuler','mixed_euler_orientation','odd_cycle_vertices','LexTwoSAT'):
     body.append(r'\newpage')
    else:
     body.append(r'\Needspace{'+str((end-split+2)*11)+'pt}')
    body.append(r'\lstinputlisting[firstline='+str(split+1)+',lastline='+str(end)+',firstnumber='+str(split-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   else:
    body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(end)+']{../src/'+style+'/'+filename+'.hpp}')
(root/'docs/generated.tex').write_text('\n\n'.join(body)+'\n')
print('Generated source-linked book sections')
