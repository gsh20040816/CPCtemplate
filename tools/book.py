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
 for a,b in {'≡':r'$\equiv$','≤':r'$\le$','≥':r'$\ge$','≠':r'$\ne$','Σ':r'$\sum$','α':r'$\alpha$','μ':r'$\mu$','φ':r'$\varphi$','²':r'$^2$','³':r'$^3$','⁹':r'$^9$','⁶':r'$^6$','⁻¹²':r'$^{-12}$','¹²':r'$^{12}$','¹¹':r'$^{11}$','√':r'$\sqrt{\vphantom x}$','–':'--'}.items():s=s.replace(a,b)
 return s
classic={'TreePathKth':'Tree_Path_Kth','Lagrange':'Lagrange_Interpolation','ExLucas':'Ex_Lucas','WeightedMatching':'Weighted_Matching','PersistentArray':'Persistent_Array','VirtualTree':'Virtual_Tree','AffineSegTree':'Affine_Segment_Tree','SubtreeColors':'Subtree_Colors','CentroidPairs':'Centroid_Pairs','PalindromicTree':'Palindromic_Tree','Biconnected':'Biconnected_Graph','TarjanSCC':'Tarjan_SCC','berlekamp_massey':'Berlekamp_Massey','recurrence_nth':'Recurrence_Nth','Blossom':'General_Matching','OrderedSplay':'Ordered_Splay','GcdSequenceTreap':'Gcd_Sequence_Treap','LinkCutTree':'Link_Cut_Tree','OrderedTreap':'Ordered_Treap','SequenceTreap':'Sequence_Treap','prefix_function':'Prefix_Function','kmp_match':'Kmp_Match','z_function':'Z_Function','manacher':'Manacher','minimum_rotation':'Minimum_Rotation','RollbackDSU':'Rollback_DSU','XorBasis':'Xor_Basis','GeometryExtra':'Geometry_Extra','IntegerGeometry3D':'Integer_Geometry_3D','BoundedCirculation':'Bounded_Circulation','Hungarian':'Kuhn_Munkres','Arborescence':'Directed_MST','StoerWagner':'Global_Min_Cut','MaxPlusMatrix':'Max_Plus_Matrix','LiChao':'Li_Chao_Tree','PersistentKth':'Persistent_Kth','DSU':'Disjoint_Set','Fenwick':'Binary_Indexed_Tree','LazySeg':'Segment_Tree','Dinic':'Network_Flow','MinCostFlow':'Min_Cost_Flow','Dijkstra':'Shortest_Path','SCC':'Strong_Component','TwoSAT':'Two_SAT','BipartiteMatching':'Bipartite_Matching','Lowlink':'Low_Link','HLD':'Heavy_Light_Decomposition','StringAlgo':'String_Algorithm','AhoCorasick':'AC_Automaton','SuffixArray':'Suffix_Array','SuffixAutomaton':'Suffix_Automaton','NumberTheory':'Number_Theory','PollardRho':'Pollard_Rho','LinearSieve':'Linear_Sieve','ModInt':'Mod_Int','Binomial':'Combination','Polynomial':'Polynomial','IntegerGeometry':'Integer_Geometry','RealGeometry':'Real_Geometry','LinearAlgebra':'Linear_Algebra','DuJiao':'Du_Jiao','DiscreteLog':'Discrete_Log'}
chapters={'tarjan':'Tarjan 与缩点','biconnected':'双连通分量与圆方树','data_structure':'数据结构','affine_segment_tree':'线段树常用修改','flow':'网络流','graph':'图论','tree':'树上算法','centroid':'点分治','dsu_on_tree':'树上启发式合并','virtual_tree':'虚树','string':'字符串','palindromic_tree':'回文树','number_theory':'数论','exlucas':'合数模数组合数','interpolation':'多项式插值','polynomial':'多项式','algebra':'代数与数论进阶','geometry':'计算几何','optimization':'优化与可持久化','persistent_array':'可持久化数组','tree_path_kth':'树上路径第 k 小','graph_advanced':'图论进阶','weighted_matching':'带权二分图匹配','geometry_extra':'精确几何进阶','dynamic_tree':'动态树','treap':'随机平衡树','splay':'伸展树','gcd_sequence':'状态序列维护','blossom':'一般图匹配','recurrence':'线性递推'}
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
   if estimate<680: body.append(r'\Needspace{'+str(round(estimate))+'pt}')
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
    if name=='TarjanSCC':body.append('声明 Tarjan\\_SCC<N>，先 Init(n)，Insert 加边，Run 求分量，Dag 输出缩点图。bel 与 cnt 可直接读取；大对象放在全局或 static。')
    if name=='Biconnected':body.append('声明 Biconnected\\_Graph<N>，Init(n) 初始化，Insert 加边，Run 分解，Block\\_Forest 和 Bridge\\_Forest 输出两种森林。blocks、cut、bridge、bel、cnt 可直接读取。大对象放在全局或 static。')
    if name=='PalindromicTree':body.append('声明 Palindromic\\_Tree<N> 后调用 Init()；N 为最大追加字符数，内部另留两个根节点。Insert、Distinct、Occurrences 对应动态版接口；t、last、total 可直接读。大对象放在全局或 static。')
    if name=='CentroidPairs':body.append('声明 Centroid\\_Pairs<N>，Init(n) 初始化，Insert 加边，Build 预处理；Count\\_Leq 和 Count\\_Exact 返回计数，parent 保存点分树父节点。大对象放在全局或 static。')
    if name=='SubtreeColors':body.append('声明 Subtree\\_Colors<N>，Init(n) 初始化，Insert 加边，Run(colors,root) 计算；answer 与 max\\_freq 为最终结果。Add\\_Color 为内部统计函数。大对象放在全局或 static。')
    if name=='AffineSegTree':body.append('声明 Affine\\_Segment\\_Tree<N> 后 Init(a,mod)，N 为最大数组长度。Update(l,r,mul,add) 修改，Query(l,r) 求和；支持重复初始化。大对象放在全局或 static。')
    if name=='VirtualTree':body.append('声明 Virtual\\_Tree<N,LOG>，要求 2 的 LOG 次方大于实际点数，默认 LOG=20。Init(n)、Insert、Prepare、Build 对应初始化、加边、预处理和查询；Lca、Ancestor、Path 为对应辅助接口。大对象放在全局或 static。')
    if name=='PersistentArray':body.append('声明 Persistent\\_Array<NODES>，Init(a) 初始化；NODES 限制节点总数，不是数组长度。建议按 2n-1 加上修改数乘以 (ceil(log2(n))+1) 分配；Copy 不分配节点。Set、Copy、Query 对应动态接口。大对象放在全局或 static，Init 会丢弃全部旧版本。')
    if name=='HLD':body.append('声明 Heavy\\_Light\\_Decomposition<N> 后 Init(n)，Insert 加边，Build(root) 剖分；Lca 与 Path 对应动态接口。大对象放在全局或 static。')
    if name=='TreePathKth':body.append('声明 Tree\\_Path\\_Kth<N,NODES,LOG>，Init(a) 清空图并保存权值；Insert、Build、Kth、Lca 对应动态接口。要求 2 的 LOG 次方大于实际点数，默认 LOG=20。若不同权值数为 D，NODES 至少取 n 乘以 (ceil(log2(D))+1)，另有编号 0 空节点。大对象放在全局或 static；Init 与 Build 分别清空图和重建版本。')
    if name=='Lagrange':body.append('声明 Lagrange\\_Interpolation<N>；Init、Consecutive、Query 对应动态接口，N 为最大样本数。坐标、权值与工作数组均为静态数组，大对象放在全局或 static；Query 会改写工作数组。')
    if name=='ExLucas':body.append('声明 Ex\\_Lucas<N> 后 Init(mod)，要求 mod 不超过 N；Choose 为查询接口。fac 是共用静态前缀积数组，各素数幂通过 start 分段；各段总长度不超过 mod+1，所以 N 限制模数即可。Init 可切换模数并清空旧预处理，大对象放在全局或 static。')
    if name=='WeightedMatching':body.append('声明 Weighted\\_Matching<N,M> 后 Init(n,m)，N、M 分别限制左右点数。Insert 加边，Solve 求解；l、r 保存方案，Init 清空原图。权值矩阵是静态数组，内部增广辅助数组按实际规模分配，大对象放在全局或 static。')
    if name=='BipartiteMatching':body.append('声明 Bipartite\\_Matching<N,M> 后 Init(n,m)，两侧容量分别为 N、M。Insert 加边，Solve 求匹配，Cover 返回最小点覆盖；l、r 保存方案。大对象放在全局或 static。')
    if name=='MinCostFlow':body.append('使用 Insert 加边、Flow 求流、Used 查看方案。')
   if name=='ExLucas':
    split=next(i for i in range(start,end) if re.match(r'    int (choose|Choose)\(',lines[i]))
    body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(split)+']{../src/'+style+'/'+filename+'.hpp}')
    body.append(r'\Needspace{'+str((end-split+2)*11)+'pt}')
    body.append(r'\lstinputlisting[firstline='+str(split+1)+',lastline='+str(end)+',firstnumber='+str(split-start+1)+']{../src/'+style+'/'+filename+'.hpp}')
   else:
    body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(end)+']{../src/'+style+'/'+filename+'.hpp}')
(root/'docs/generated.tex').write_text('\n\n'.join(body)+'\n')
print('Generated source-linked book sections')
