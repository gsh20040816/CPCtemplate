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
classic={'prefix_function':'Prefix_Function','kmp_match':'Kmp_Match','z_function':'Z_Function','manacher':'Manacher','minimum_rotation':'Minimum_Rotation','RollbackDSU':'Rollback_DSU','XorBasis':'Xor_Basis','GeometryExtra':'Geometry_Extra','IntegerGeometry3D':'Integer_Geometry_3D','BoundedCirculation':'Bounded_Circulation','Hungarian':'Kuhn_Munkres','Arborescence':'Directed_MST','StoerWagner':'Global_Min_Cut','MaxPlusMatrix':'Max_Plus_Matrix','LiChao':'Li_Chao_Tree','PersistentKth':'Persistent_Kth','DSU':'Disjoint_Set','Fenwick':'Binary_Indexed_Tree','LazySeg':'Segment_Tree','Dinic':'Network_Flow','MinCostFlow':'Min_Cost_Flow','Dijkstra':'Shortest_Path','SCC':'Strong_Component','TwoSAT':'Two_SAT','BipartiteMatching':'Bipartite_Matching','Lowlink':'Low_Link','HLD':'Heavy_Light_Decomposition','StringAlgo':'String_Algorithm','AhoCorasick':'AC_Automaton','SuffixArray':'Suffix_Array','SuffixAutomaton':'Suffix_Automaton','NumberTheory':'Number_Theory','PollardRho':'Pollard_Rho','LinearSieve':'Linear_Sieve','ModInt':'Mod_Int','Binomial':'Combination','Polynomial':'Polynomial','IntegerGeometry':'Integer_Geometry','RealGeometry':'Real_Geometry','LinearAlgebra':'Linear_Algebra','DuJiao':'Du_Jiao','DiscreteLog':'Discrete_Log'}
chapters={'data_structure':'数据结构','flow':'网络流','graph':'图论','tree':'树上算法','string':'字符串','number_theory':'数论','polynomial':'多项式','algebra':'代数与数论进阶','geometry':'计算几何','optimization':'优化与可持久化','graph_advanced':'图论进阶','geometry_extra':'精确几何进阶'}
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
    if name=='MinCostFlow':body.append('使用 Insert 加边、Flow 求流、Used 查看方案。')
   body.append(r'\lstinputlisting[firstline='+str(start+1)+',lastline='+str(end)+']{../src/'+style+'/'+filename+'.hpp}')
(root/'docs/generated.tex').write_text('\n\n'.join(body)+'\n')
print('Generated source-linked book sections')
