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
classic={'PalindromicTree':'Palindromic_Tree','Biconnected':'Biconnected_Graph','TarjanSCC':'Tarjan_SCC','berlekamp_massey':'Berlekamp_Massey','recurrence_nth':'Recurrence_Nth','Blossom':'General_Matching','OrderedSplay':'Ordered_Splay','GcdSequenceTreap':'Gcd_Sequence_Treap','LinkCutTree':'Link_Cut_Tree','OrderedTreap':'Ordered_Treap','SequenceTreap':'Sequence_Treap','prefix_function':'Prefix_Function','kmp_match':'Kmp_Match','z_function':'Z_Function','manacher':'Manacher','minimum_rotation':'Minimum_Rotation','RollbackDSU':'Rollback_DSU','XorBasis':'Xor_Basis','GeometryExtra':'Geometry_Extra','IntegerGeometry3D':'Integer_Geometry_3D','BoundedCirculation':'Bounded_Circulation','Hungarian':'Kuhn_Munkres','Arborescence':'Directed_MST','StoerWagner':'Global_Min_Cut','MaxPlusMatrix':'Max_Plus_Matrix','LiChao':'Li_Chao_Tree','PersistentKth':'Persistent_Kth','DSU':'Disjoint_Set','Fenwick':'Binary_Indexed_Tree','LazySeg':'Segment_Tree','Dinic':'Network_Flow','MinCostFlow':'Min_Cost_Flow','Dijkstra':'Shortest_Path','SCC':'Strong_Component','TwoSAT':'Two_SAT','BipartiteMatching':'Bipartite_Matching','Lowlink':'Low_Link','HLD':'Heavy_Light_Decomposition','StringAlgo':'String_Algorithm','AhoCorasick':'AC_Automaton','SuffixArray':'Suffix_Array','SuffixAutomaton':'Suffix_Automaton','NumberTheory':'Number_Theory','PollardRho':'Pollard_Rho','LinearSieve':'Linear_Sieve','ModInt':'Mod_Int','Binomial':'Combination','Polynomial':'Polynomial','IntegerGeometry':'Integer_Geometry','RealGeometry':'Real_Geometry','LinearAlgebra':'Linear_Algebra','DuJiao':'Du_Jiao','DiscreteLog':'Discrete_Log'}
chapters={'tarjan':'Tarjan 与缩点','biconnected':'双连通分量与圆方树','data_structure':'数据结构','flow':'网络流','graph':'图论','tree':'树上算法','string':'字符串','palindromic_tree':'回文树','number_theory':'数论','polynomial':'多项式','algebra':'代数与数论进阶','geometry':'计算几何','optimization':'优化与可持久化','graph_advanced':'图论进阶','geometry_extra':'精确几何进阶','dynamic_tree':'动态树','treap':'随机平衡树','splay':'伸展树','gcd_sequence':'状态序列维护','blossom':'一般图匹配','recurrence':'线性递推'}
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
    if name=='MinCostFlow':body.append('使用 Insert 加边、Flow 求流、Used 查看方案。')
   body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(end)+']{../src/'+style+'/'+filename+'.hpp}')
(root/'docs/generated.tex').write_text('\n\n'.join(body)+'\n')
print('Generated source-linked book sections')
