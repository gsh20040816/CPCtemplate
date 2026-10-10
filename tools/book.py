#!/usr/bin/env python3
import json, re
from pathlib import Path
root = Path(__file__).resolve().parents[1]
cat = json.loads((root / 'docs/catalog.json').read_text())
from usage_examples import generate as generate_usage
usage_rows = generate_usage()

def esc(s):
    for a, b in [('\\', '\\textbackslash{}'), ('&', '\\&'), ('%', '\\%'), ('$', '\\$'), ('#', '\\#'), ('_', '\\_'), ('{', '\\{'), ('}', '\\}')]:
        if a != '\\':
            s = s.replace(a, b)
    s = s.replace('^', '\\textasciicircum{}')
    s = re.sub('[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+', lambda m: '$^{' + m[0].translate(str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁻', '0123456789-')) + '}$', s)
    for a, b in {'π': '$\\pi$', '⊆': '$\\subseteq$', 'λ': '$\\lambda$', 'ω': '$\\omega$', '≡': '$\\equiv$', '≤': '$\\le$', '≥': '$\\ge$', '≠': '$\\ne$', 'Σ': '$\\sum$', 'α': '$\\alpha$', 'β': '$\\beta$', 'μ': '$\\mu$', 'φ': '$\\varphi$', '²': '$^2$', '³': '$^3$', '⁹': '$^9$', '⁶': '$^6$', '⁻¹²': '$^{-12}$', '¹²': '$^{12}$', '¹¹': '$^{11}$', '√': '$\\sqrt{\\vphantom x}$', '–': '--'}.items():
        s = s.replace(a, b)
    return s
chapters = {'exact_cover': '精确覆盖', 'minimum_cover': '最少行重复覆盖', 'sais': '线性后缀数组', 'convex_tangents_i64': '凸多边形外点切线', 'persistent_xor_trie': '前缀可持久化01字典树', 'dominance_3d': '静态三维偏序', 'manhattan_mst': '曼哈顿最小生成树', 'multipoint_evaluation': '任意点多项式求值', 'polynomial_interpolation': '任意点多项式快速插值', 'rectangle_union': '整数矩形面积并', 'centroid_sum': '动态点分树距离和', 'centroid_nearest': '动态点分树最近点', 'fenwick2d': '稀疏二维树状数组', 'rectangle_fenwick': '矩形加与矩形和', 'segment_beats': '区间最值截断线段树', 'persistent_ordered_treap': '可持久化有序平衡树', 'division_tree': '中位数划分树', 'second_mst': '次小生成树与换边方案', 'gauss_xor': '压位异或方程组', 'wavelet_matrix': '压位小波矩阵', 'euler_power': '扩展欧拉降幂', 'dag_path_determinant': 'LGV 路径行列式', 'prime_count': '素数计数', 'min25': 'Min_25 积性函数求和', 'general_sam': '广义后缀自动机', 'segment_li_chao': '精确线段李超树', 'dominator_tree': '支配树', 'johnson': 'Johnson 全源最短路', 'leftist_heap': '左偏树可并堆', 'biconnected_core': '点双与边双：共享 lowlink 核心', 'block_cut_forest': '由点双构造圆方森林', 'bridge_component_forest': '边双缩点森林（保留桥编号）', 'enumerate_triangles': '三元环枚举', 'real_plane': '浮点点向量、圆与交点结果', 'real_polar': '浮点极角精确排序', 'line_projection': '点在直线上的投影', 'segment_distance_real': '点到闭线段的距离', 'line_intersection_real': '浮点两直线交点', 'line_circle_intersections': '浮点直线与圆交点', 'circle_intersections': '浮点两圆交点', 'circle_overlap_area': '两圆交面积', 'integer_plane': '整数点向量与线段判定', 'line_circle_i64': '整数直线与圆交点', 'circle_intersections_i64': '整数两圆交点', 'integer_hull': '整数凸包：单调链', 'polygon_area2': '整数多边形有向面积', 'polygon_contains': '点在整数简单多边形内', 'convex_contains_i64': '点在整数凸包内（二分）', 'convex_diameter2': '整数凸包直径：旋转卡壳', 'integer_geometry': '整数几何', 'real_geometry': '浮点几何', 'closest_pair_i64': '整数最近点对', 'minkowski_sum': '凸包 Minkowski 和', 'pbds_heap': 'GNU 配对堆', 'batch_units': '模整数的批量运算', 'dynamic_modint': '运行时模数运算', 'lazy_segtree': '通用懒标记线段树', 'segtree': '通用线段树', 'rope': 'GNU 扩展可持久化序列', 'ordered_set': 'GNU 扩展有序树', 'hash_table': 'GNU 扩展哈希表', 'tarjan': 'Tarjan 与缩点', 'functional_graph': '函数图', 'biconnected': '双连通分量与圆方树', 'odd_cycle_vertices': '奇环顶点判定', 'vertex_removal': '删点连通性', 'edge_components': '边双缩点与边定向', 'bridge_augmentation': '桥树最少加边', 'data_structure': '数据结构', 'modified_mo': '带修改的莫队', 'position_basis': '带位置线性基', 'basis_intersection': '线性空间求交', 'affine_segment_tree': '线段树常用修改', 'flow': '网络流', 'spfa_flow': 'SPFA 费用流', 'negative_cost_flow': '允许负环的费用流', 'unit_flow_edges': '最大流单位边分类', 'mincut_edges': '最小割边分类', 'bounded_maxflow': '有源汇上下界最大流', 'maximum_closure': '最大权闭合子图', 'graph': '图论', 'odd_induced_partition': '奇度诱导子图划分', 'matching_edges': '二分图匹配边分类', 'release_bfs': '开放时间最短路', 'lex_two_sat': '字典序最小 2-SAT', 'directed_euler': '有向欧拉路', 'word_chain': '字典序单词链', 'undirected_euler': '无向欧拉路', 'mixed_euler': '混合图欧拉定向', 'xor_walk': '图上异或行走', 'tree': '树上算法', 'offline_lca': '离线最近公共祖先', 'euler_lca': '在线最近公共祖先', 'tree_diameter': '树上点集摘要', 'lifting_lca': '倍增祖先与路径最值', 'path_intersection': '树上路径交', 'centroid': '点分治', 'dsu_on_tree': '树上启发式合并', 'virtual_tree': '虚树', 'string': '字符串', 'ac_shortest': 'AC 自动机最短后缀匹配', 'suffix_lcp': '后缀查询与重复子串', 'palindromic_tree': '回文树', 'mod64': '64位模运算', 'prime64': '64位判素', 'extended_gcd': '扩展欧几里得', 'mod_inverse': '单个逆元', 'crt_merge': '广义CRT合并', 'floor_sum': '有符号整除和', 'number_theory': '数论', 'linear_equation': '二元一次不定方程', 'linear_congruence': '线性同余方程', 'segmented_sieve': '区间筛素数', 'batch_inverse': '批量模逆元', 'inverse_table': '连续整数逆元表', 'garner': '混合进制中国剩余定理', 'primitive_root': '乘法阶与原根', 'coprime_pairs': '矩形 GCD 计数', 'floor_moments': '带权类欧几里德', 'divisor_sum': '模几何级数与约数和', 'euler_phi': '单个数的欧拉函数', 'carmichael': 'Carmichael 函数', 'partitions': '整数分拆', 'lucas': '素数模数组合数', 'exlucas': '合数模数组合数', 'modular_sqrt': '二次剩余', 'kth_residue': '素数模高次剩余', 'prime_power_roots': '素数幂模高次剩余', 'root_factors': '合数求根的准备', 'composite_roots': '合数模高次剩余', 'interpolation': '多项式插值', 'ntt_convolution': '参数化 NTT 卷积', 'fft': '复数 FFT', 'convolution_fft': '浮点整数卷积', 'convolution_mod_fft': '拆系数任意模卷积', 'convolution_i64': '精确整数卷积', 'polynomial_shift': '多项式平移', 'chirp_z': '等比点求值', 'stirling': '斯特林数整行计算', 'set_convolution': '集合变换与卷积', 'subset_convolution': '不相交子集卷积', 'fps_inverse': '形式幂级数求逆', 'polynomial_division': '多项式除法', 'fps_sqrt': '形式幂级数开根', 'fps_functions': '形式幂级数初等函数', 'fps_power': '形式幂级数快速幂', 'polynomial': '多项式', 'gauss_mod': '模高斯消元', 'det_prime': '素数模行列式', 'mod_matrix': '模矩阵运算', 'matrix_inverse': '素数模矩阵求逆', 'matrix_inverse_mod2': '模 2 矩阵求逆', 'algebra': '代数与数论进阶', 'determinant_mod': '任意模数行列式', 'matrix_tree': '带权生成树计数', 'matrix_tree_mod': '合数模生成树计数', 'geometry': '计算几何', 'optimization': '优化与可持久化', 'persistent_array': '可持久化数组', 'persistent_range': '可持久化区间操作', 'tree_path_kth': '树上路径第 k 小', 'dynamic_kth': '动态区间顺序统计', 'persistent_distinct': '区间不同数统计', 'graph_advanced': '图论进阶', 'gomory_hu': '最小割树', 'cut_tree_queries': '最小割树查询', 'weighted_matching': '带权二分图匹配', 'halfplanes': '精确有界半平面交', 'circle_polygon': '圆与多边形面积', 'enclosing_circle': '最小覆盖圆', 'circle_tangents': '圆的切线', 'integer_tangents': '整数圆公切线与精确排序', 'closest_pair': '浮点最近点对', 'geometry_extra': '精确几何进阶', 'support_hull': '凸包支撑点查询', 'dynamic_tree': '动态树', 'tree_path_products': '动态换根路径乘积总和', 'treap': '随机平衡树', 'affine_sequence': '动态仿射序列', 'splay': '伸展树', 'scapegoat_tree': '替罪羊树', 'mo_secondary': '莫队二次离线', 'monotone_stack_seg': '线段树维护单调栈', 'kd_tree_sum': '动态二维 K-D Tree', 'cdq_convolution': 'CDQ 卷积递推', 'gcd_sequence': '状态序列维护', 'blossom': '一般图匹配', 'recurrence': '线性递推', 'bostan_mori': '快速线性递推'}
chapters['exkmp'] = '两串扩展KMP'
chapters['order_match'] = '顺序同构匹配'
chapters['sam_queries'] = '后缀自动机查询'
chapters['online_sam'] = '指定状态在线扩展SAM'
chapters['sam_documents'] = 'SAM文档频率'
chapters['ac_weighted'] = '带权与动态AC'
chapters['kd_nearest'] = '静态 K-D Tree 近邻'
chapters['kd_range'] = '动态 K-D Tree 矩形取点'
chapters['chain_3d'] = '三维最长链CDQ'
chapters['kd_min'] = '静态 K-D Tree 矩形最小权'
chapters['static_rmq'] = '位掩码静态RMQ'
chapters['static_rmq_2d'] = '二维静态RMQ'
chapters['merge_splay'] = '可合并伸展树'
chapters['dag_longest'] = '有向无环图最长路'
chapters['floyd'] = '全源最短路'
chapters['shortest_path_tree'] = '最短路树与最小总边权'
chapters['independent_set'] = '二分图独立集与覆盖方案'
chapters['tree_market'] = '树上市场选址'
chapters['zkw_flow'] = 'zkw费用流'
chapters['isap'] = '递归ISAP最大流'
chapters['flow_unique'] = '最大流方案唯一性'
chapters['prim'] = '矩阵最小生成森林'
chapters['kruskal'] = '最小生成森林'
chapters['dense_dijkstra'] = '稠密图矩阵最短路'
chapters['spfa'] = '队列松弛与差分约束'
chapters['bellman_ford'] = '负边最短路与负环方案'
chapters['dynamic_path_max'] = '动态森林路径加与最大值'
chapters['sequence_kth'] = '在线序列区间第k小'
chapters['sequence_scapegoat'] = '序列替罪羊树'
chapters['sequence_splay'] = '区间翻转与固定编号定位'
chapters['centroid_diameter'] = '有符号边权活动点直径'
chapters['persistent_dsu'] = '可持久化并查集'
chapters['merge_split_tree'] = '线段树合并与分裂'
chapters['potential_dsu'] = '带势并查集与差值约束'
chapters['gauss_real'] = '实数高斯消元'
chapters['polya'] = 'Burnside与Pólya计数'
chapters['monotone_hull'] = '单调斜率优化'
chapters['monotone_dp'] = '分治决策单调性'
chapters['wqs_independent_set'] = 'WQS二分'
chapters['shortest_walks'] = '严格次短路与K短行走'
chapters['overall_kth'] = '整体二分'
chapters['tree_isomorphism'] = '确定性树同构'
chapters['tree_mo'] = '树上莫队'
chapters['rollback_mo'] = '回滚莫队'
chapters['time_connectivity'] = '离线动态连通性'
chapters['real_space'] = '三维向量运算'
chapters['line3'] = '三维直线与线段'
chapters['plane3'] = '三维平面与求交'
chapters['convolution_mod'] = '精确任意模数卷积'
chapters['dc3'] = 'DC3后缀数组'
chapters['dag_dominator'] = 'DAG支配树'
chapters['fibonacci_period'] = '斐波那契最小循环节'
chapters['assignment_spectrum'] = '按匹配基数最大权与顶标'
chapters['determinant_exact'] = '精确整数行列式'
chapters['matrix_tree_exact'] = '精确整数生成树计数'
chapters['adaptive_simpson'] = '自适应Simpson积分'
body = []
records = []
for style in ['compact']:
    body.append('\\part{' + 'vector 模板' + '}')
    for file, title in chapters.items():
        body.append('\\chapter{' + title + '}')
        for f, name, cn, info in cat:
            if f != file:
                continue
            target = name
            if not target:
                continue
            begin = len(body)
            filename = file
            p = root / f'src/{style}/{filename}.hpp'
            lines = p.read_text().splitlines()
            marker = '// BEGIN ' + target
            if marker in lines:
                start = lines.index(marker) + 1
                end = lines.index('// END ' + target, start)
            else:
                starts = []
                for i, line in enumerate(lines):
                    m = re.match('^(?:template.*?\\s+)?struct\\s+(\\w+)', line)
                    if m:
                        starts.append((i, m[1]))
                idx = next((i for i, x in enumerate(starts) if x[1] == target))
                start = starts[idx][0]
                end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
                if start and lines[start - 1].startswith('template'):
                    start -= 1
                if end and lines[end - 1].startswith('template'):
                    end -= 1
            estimate = sum((max(1, (len(line.expandtabs(4)) + 109) // 110) for line in lines[start:end])) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'ac_shortest':
                estimate = max(estimate, 380)
            if name == 'HLD':
                split = next(i for i in range(start, end) if 'void dfs2(' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'SCC':
                split = next(i for i in range(start, end) if '// Recursive Kosaraju' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'orient_edges':
                estimate = 650
            if name == 'PalindromicTree':
                split = next(i for i in range(start, end) if '// Append a lowercase letter' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'SuffixAutomaton':
                split = next(i for i in range(start, end) if 'void extend(' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'SpfaFlow':
                split = next(i for i in range(start, end) if '// Internal:' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'ComplexFFT':
                split = next(i for i in range(start, end) if 'void transform(' in lines[i])
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'IntegerPlane':
                body.append('\\newpage')
                split = next(i for i in range(start, end) if 'struct PolarLess' in lines[i])
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name in ('convolution_fft', 'cdq_convolution'):
                body.append('\\newpage')
            if name == 'TreePathProducts':
                body.append('\\newpage')
                estimate = 650
            if name in ('BurnsideAverage', 'permutation_cycles', 'necklace_colorings', 'MonotoneHull', 'monotone_dp_layer', 'wqs_independent_set', 'StrictSecondShortest', 'KShortestWalks', 'OverallKth', 'TreeIsomorphism', 'TreeMo', 'RollbackMo', 'TimeConnectivity', 'RealSpace', 'Line3', 'Plane3', 'rectangle_union_area', 'convolution_mod', 'DC3', 'DagDominator', 'FibonacciPeriod', 'AssignmentSpectrum', 'DynamicPathMax', 'SequenceKth', 'SequenceScapegoat', 'ScapegoatTree', 'PersistentOrderedTreap', 'SegmentBeats', 'CentroidSum', 'CentroidNearest', 'CentroidDiameter', 'SequenceSplay', 'MergeSplay', 'BellmanFord', 'Spfa', 'DagLongest', 'Floyd', 'ShortestPathTree', 'DenseDijkstra', 'Kruskal', 'Prim', 'Fenwick2D', 'RectangleFenwick', 'PersistentDSU', 'MergeSplitTree', 'SAMLex', 'xor_hamming_pairs', 'MonotoneStackSeg', 'KDTreeSum', 'KDNearest', 'KDRange', 'Chain3D', 'ModifiedMo', 'KDMin', 'StaticRMQ', 'StaticRMQ2D', 'Isap', 'flow_unique', 'ZkwFlow', 'TreeMarket'):
                body.append('\\newpage')
                estimate = 650
            if name == 'Min25':
                split = next(i for i in range(start, end) if 'array<Z, 3> prefix{};' in lines[i])
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'dag_path_determinant':
                split = next(i for i in range(start, end) if 'vector<vector<Z>> a(' in lines[i])
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'LexTwoSAT':
                split = next((i for i in range(start, end) if re.match('    bool (paint|Paint)\\(', lines[i])))
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'odd_cycle_vertices':
                split = next((i for i in range(start, end) if 'edges(graph.blocks.size())' in lines[i]))
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'mixed_euler_orientation':
                split = next((i for i in range(start, end) if '!edges.empty()' in lines[i]))
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name in ('release_bfs', 'MinCostFlow', 'LiChao', 'matrix_inverse', 'matrix_inverse_mod2', 'MaxPlusMatrix', 'Min25', 'dag_path_determinant'):
                body.append('\\newpage')
            if name in ('DirectedEuler', 'UndirectedEuler'):
                split = next((i for i in range(start, end) if re.match('    bool (run|Run)\\(', lines[i]))) - 1
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name in ('Johnson', 'DominatorTree'):
                split = next(i for i in range(start, end) if ('bool build()' if name == 'Johnson' else 'int eval(') in lines[i])
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'odd_induced_partition':
                split = next(i for i in range(start, end) if 'dsu d(n);' in lines[i])
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'NegativeCostFlow':
                split = next(i for i in range(start, end) if 'pair<ll, I> solve(' in lines[i])
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'GeneralSAM':
                split = next(i for i in range(start, end) if 'void build()' in lines[i])
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'LiChao':
                split = next(i for i in range(start, end) if 'void add(int p' in lines[i])
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'SegmentLiChao':
                split = next(i for i in range(start, end) if 'bool better(' in lines[i])
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'LiftingLCA':
                split = next((i for i in range(start, end) if re.match('    void (dfs|Dfs)\\(', lines[i])))
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'EulerLCA':
                split = next((i for i in range(start, end) if re.match('    void (dfs|Dfs)\\(', lines[i])))
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'OfflineLCA':
                split = next((i for i in range(start, end) if re.match('    int (find|Find)\\(', lines[i])))
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'Lowlink':
                split = next((i for i in range(start, end) if re.match('    void (dfs|Dfs)\\(', lines[i])))
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'XorWalk':
                split = next(i for i in range(start, end) if 'void add(' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name in ('SequenceTreap', 'AffineSequenceTreap', 'GcdSequenceTreap', 'OrderedSplay'):
                body.append('\\newpage')
                estimate = 650
            if name in ('SubtreeColors', 'VirtualTree', 'CentroidPairs', 'WaveletMatrix', 'GaussXor', 'SecondMST', 'DivisionTree'):
                estimate = 650
            if name == 'block_cut_forest':
                estimate = 650
            if name == 'polygon_contains':
                estimate = 430
            if name == 'line_intersection_real':
                estimate = 460
            if name in ('line_circle_intersections', 'circle_intersections'):
                body.append('\\newpage')
                estimate = 650
            if name == 'BiconnectedCore':
                split = next(i for i in range(start, end) if 'void dfs(' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name in ('ExactCover', 'MinimumCover'):
                split = next(i for i in range(start, end) if 'vector<int> seen(m, -1);' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
                body.append('\\newpage')
            if name == 'SAIS':
                split = next(i for i in range(start, end) if lines[i] == 'private:')
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
                body.append('\\newpage')
            if name == 'PersistentXorTrie':
                split = next(i for i in range(start, end) if 'bool append(' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
                body.append('\\newpage')
            if name == 'convex_tangents_i64':
                split = next(i for i in range(start, end) if 'int a = G::sign' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
                body.append('\\newpage')
            if name == 'Dominance3D':
                split = next(i for i in range(start, end) if 'auto cdq =' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
                body.append('\\newpage')
            if name == 'ManhattanMST':
                split = next(i for i in range(start, end) if 'map<I, int> sweep;' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
                body.append('\\newpage')
            if name == 'AdaptiveSimpson':
                split = next(i for i in range(start, end) if 'auto rec =' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
                body.append('\\newpage')
            if name == 'GaussReal':
                split = next(i for i in range(start, end) if 'for (int col = 0;' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
                body.append('\\newpage')
            if name == 'PotentialDSU':
                split = next(i for i in range(start, end) if '// Accept potential' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'SuffixLCP':
                estimate = 670
            if name == 'divisor_sum_power':
                body.append('\\newpage')
            if name == 'Arborescence':
                split = next((i for i in range(start, end) if lines[i].strip() == 'int cnt = 0;'))
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'StoerWagner':
                split = next((i for i in range(start, end) if 'step + 1 ==' in lines[i]))
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'IntegerHalfplanes':
                split = next((i for i in range(start, end) if re.match('    static I (value|Value)\\(', lines[i])))
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'ClosestPair':
                split = next((i for i in range(start, end) if lines[i].strip() == 'int m = (l + r) / 2;'))
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'IntegerTangents':
                split = next(i for i in range(start, end) if '// |coordinates|' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'CircleTangents':
                split = next((i for i in range(start, end) if lines[i].strip() == 'Result answer;'))
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'EnclosingCircle':
                split = next((i for i in range(start, end) if 'static optional<Circle>' in lines[i]))
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'CirclePolygon':
                split = next((i for i in range(start, end) if lines[i].strip() == 'R answer = 0;'))
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'PrimePowerRoots':
                split = next((i for i in range(start, end) if 'static optional<Prime' in lines[i]))
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'CompositeRoots':
                split = next((i for i in range(start, end) if 'static optional<Composite' in lines[i]))
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'NttConvolution':
                split = next((i for i in range(start, end) if 'for (int half' in lines[i] or 'for ( int half' in lines[i]))
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if name == 'MultipointEvaluation':
                split = next(i for i in range(start, end) if 'void eval(' in lines[i])
                estimate = (split - start) * 10.2 + 100 + len(info) / 55 * 12
            if estimate < 680:
                body.append('\\Needspace{' + str(round(estimate)) + 'pt}')
            if name in ('SuffixArray', 'XorBasis', 'IntegerGeometry3D', 'ost', 'TreePathKth', 'LeftistHeap', 'ModInt', 'mint', 'CoprimePairs', 'linear_congruence'):
                body.append('\\newpage')
            body.append('\\section{' + esc(cn) + '}\\label{' + style + '-' + name + '}\\index{' + target.replace('_', '\\_') + '}')
            if name == 'RollbackMo':
                info = info.replace('run(add,snapshot,rollback,ans,block=0)', 'run(add, snapshot, rollback, ans, block=0)')
            body.append(esc(info))
            if name in ('ost', 'rp'):
                body.append(r'只需键值查改而不需要有序排名时，gp\_hash\_table / cc\_hash\_table 及选型建议见第~\pageref{compact-gp_map}~页。')
            if name == 'ost':
                body.append(r'序列中间插删、截取与版本共享的 GNU rope 见第~\pageref{compact-rp}~页。')
            if name == 'gp_map':
                body.append(r'\index{gp\_hash\_table}\index{cc\_hash\_table}需要排名与有序前驱时，PBDS 平衡树见第~\pageref{compact-ost}~页。')
            if name == 'SCC':
                split = next(i for i in range(start, end) if '// Recursive Kosaraju' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 重算入口与拓扑编号（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'HLD':
                cuts = [start,
                        next(i for i in range(start, end) if 'void dfs2(' in lines[i]),
                        next(i for i in range(start, end) if '// Emit u-to-v order;' in lines[i]), end]
                for part in range(3):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + ('重编号、LCA与可交换路径' if part == 1 else '按真实方向分解路径') + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'MinimumCover':
                cuts = [start,
                        next(i for i in range(start, end) if 'vector<int> seen(m, -1);' in lines[i]),
                        next(i for i in range(start, end) if 'void restore(int x)' in lines[i]),
                        next(i for i in range(start, end) if 'void dfs()' in lines[i]), end]
                for part in range(4):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + ['','稀疏建链与删列','逆序恢复与可采纳下界','最优搜索与求解入口'][part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'ExactCover':
                cuts = [start,
                        next(i for i in range(start, end) if 'vector<int> seen(m, -1);' in lines[i]),
                        next(i for i in range(start, end) if 'void uncover(int c)' in lines[i]), end]
                for part in range(3):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + ('稀疏行建链与删除' if part == 1 else '逆序恢复与搜索') + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'SAIS':
                cuts = [start,
                        next(i for i in range(start, end) if lines[i] == 'private:'),
                        next(i for i in range(start, end) if 'vector<int> id(n, -1), lms;' in lines[i]), end]
                for part in range(3):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + ('类型与桶内诱导' if part == 1 else 'LMS命名与递归') + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'SAMDocuments':
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in ['SAMDocuments(const', '// Longest suffix']] + [end]
                for j in range(3):
                    if j:
                        body.append('\\newpage')
                        body.append('\\noindent ' + ('文档标记与子树去重' if j == 1 else '阈值后缀长度') + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[j] + 1) + ',lastline=' + str(cuts[j + 1]) + ',firstnumber=' + str(cuts[j] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'AhoCorasick':
                split = next(i for i in range(start, end) if 'void build()' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 构建失败链接与统计出现次数（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'OnlineSAM':
                split = next(i for i in range(start, end) if '// Append c' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 指定状态在线扩展（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'PersistentXorTrie':
                split = next(i for i in range(start, end) if 'bool append(' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 前缀追加与区间单值最大异或（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'convex_tangents_i64':
                split = next(i for i in range(start, end) if 'int a = G::sign' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 选择异态种子边并二分可见边链（接上页同一函数）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'Dominance3D':
                split = next(i for i in range(start, end) if 'auto cdq =' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 三维偏序的 CDQ 归并与原序返回（接上页同一 count 函数）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'ManhattanMST':
                split = next(i for i in range(start, end) if 'map<I, int> sweep;' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 活动点扫描与 Kruskal（接上页同一结构体，仍在四轮循环中）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'AdaptiveSimpson':
                split = next(i for i in range(start, end) if 'auto rec =' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 采样细分与预算合并（接上页同一 integrate 函数）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'GaussReal':
                split = next(i for i in range(start, end) if 'for (int col = 0;' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 主元消元与数值解空间（接上页同一 solve 函数）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'PotentialDSU':
                split = next(i for i in range(start, end) if '// Accept potential' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 约束合并、差值查询与分量大小（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'ModifiedMo':
                split = next(i for i in range(start, end) if 'template <class Add' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name in ('Johnson', 'DominatorTree'):
                split = next(i for i in range(start, end) if ('bool build()' if name == 'Johnson' else 'int eval(') in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent ' + ('势能预处理、单源查询与距离还原' if name == 'Johnson' else '路径查询、半支配点与直接支配点计算') + '（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'Arborescence':
                split = next((i for i in range(start, end) if lines[i].strip() == 'int cnt = 0;'))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 判环与缩点（接上页同一函数）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'StoerWagner':
                split = next((i for i in range(start, end) if 'step + 1 ==' in lines[i]))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 本轮割、合并与继续扩张（接上页同一函数）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'xor_hamming_pairs':
                cuts = [start,
                        next(i for i in range(start, end) if 'int l = 0, r = 0;' in lines[i]),
                        next(i for i in range(start, end) if 'fill(count.begin()' in lines[i]), end]
                captions = ['', '莫队端点移动与前缀事件', '第二次离线与差分还原']
                for part in range(3):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一函数）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'MonotoneStackSeg':
                cuts = [start,
                        next(i for i in range(start, end) if 'll extra(' in lines[i]),
                        next(i for i in range(start, end) if 'void add(int p,' in lines[i]), end]
                captions = ['', '单路扫描、合并与建树', '区间加、双向查询与雨水体积']
                for part in range(3):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'KDTreeSum':
                cuts = [start,
                        next(i for i in range(start, end) if 'void pull(' in lines[i]),
                        next(i for i in range(start, end) if 'int add(int p,' in lines[i]), end]
                captions = ['', '包围盒维护、递归收集与重建', '点权累加与闭矩形查询']
                for part in range(3):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'rectangle_union_area':
                split = next(i for i in range(start, end) if 'auto add =' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 覆盖长度维护与横向面积累加（接上页同一函数）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name in ('PersistentDSU', 'MergeSplitTree'):
                tokens = ['// Queries never'] if name == 'PersistentDSU' else ['void release(', 'int add_node(', 'int meld(', 'pair<int, int> cut(', 'll query(']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                for part in range(len(cuts) - 1):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + cn + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name in ('Fenwick2D', 'RectangleFenwick'):
                token = 'void add(' if name == 'Fenwick2D' else 'T prefix('
                split = next(i for i in range(start, end) if token in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 更新与半开矩形求和（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name in ('MergeSplay', 'BellmanFord', 'Spfa', 'DagLongest', 'Floyd', 'ShortestPathTree', 'DenseDijkstra', 'Kruskal', 'Prim'):
                if name == 'MergeSplay':
                    tokens = ['void rotate(', 'int insert(', '// Change this element']
                    captions = ['', '旋转、伸展与固定编号', '节点插入与小集合合并', '保持编号的改值、名次与第 k 小']
                elif name == 'Prim':
                    tokens = ['    // Rebuild a minimum spanning forest']
                    captions = ['', '矩阵扫描、割边松弛与父点森林']
                elif name == 'Kruskal':
                    tokens = ['    // Rebuild a minimum spanning forest']
                    captions = ['', '边排序、合并与原边方案']
                elif name == 'DenseDijkstra':
                    tokens = ['    void run(']
                    captions = ['', '矩阵扫描、松弛与路径输出']
                elif name == 'ShortestPathTree':
                    tokens = ['// Internal: span', '        bel.assign', '// Forward undirected']
                    captions = ['', '递归辅助与run中的Dijkstra', '继续run：零权块、最轻入口与定向', '读取最短路树中的路径']
                elif name == 'Floyd':
                    tokens = ['// Any negative cycle', '// Forward original-edge']
                    captions = ['', '矩阵初始化与Floyd松弛', '成功运行后的原边路径']
                elif name == 'DagLongest':
                    tokens = ['// s=0 allows', '// Forward original-edge']
                    captions = ['', '全图拓扑序与最长路', '成功运行后的原边路径']
                elif name == 'Spfa':
                    tokens = ['// s=0 checks', '// Forward original-edge']
                    captions = ['', 'FIFO队列与负环判定', '成功运行后的有限路径']
                else:
                    tokens = ['// s=0 initializes', '        if (last != -1)']
                    captions = ['', 'run：逐轮松弛与负环种子', '继续 run：恢复负环并传播；随后为 path']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                for part in range(len(cuts) - 1):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'MonotoneHull':
                cut = next(i for i in range(start, end) if '    pair<I, int> query' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(cut) + ',firstnumber=1]{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 查询（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(cut + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(cut - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name in ('StrictSecondShortest', 'KShortestWalks'):
                token = '    vector<array<ll, 2>> run' if name == 'StrictSecondShortest' else '    vector<ll> run'
                cut = next(i for i in range(start, end) if token in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(cut) + ',firstnumber=1]{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 继续求解（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(cut + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(cut - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name in ('OverallKth', 'TreeIsomorphism'):
                tokens = ['    vector<ll> run() const', '        auto solve ='] if name == 'OverallKth' else ['    pair<int, int> unrooted(']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                for part in range(len(cuts) - 1):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent 继续求解（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name in ('TreeMo', 'RollbackMo'):
                token = '    template <class Add' if name == 'TreeMo' else '        auto empty = snapshot();'
                cut = next(i for i in range(start, end) if token in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(cut) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 查询调度与状态恢复（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(cut + 1) + ',firstnumber=' + str(cut - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'TimeConnectivity':
                cut = next(i for i in range(start, end) if lines[i] == 'private:')
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(cut) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 时间区间插入与回滚递归（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(cut + 1) + ',firstnumber=' + str(cut - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name in ('RealSpace', 'Line3', 'Plane3'):
                token = {'RealSpace': '    static R dot(', 'Line3': '    R distance(', 'Plane3': '    // 1: one point;'}[name]
                cut = next(i for i in range(start, end) if token in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(cut) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 继续三维运算（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(cut + 1) + ',firstnumber=' + str(cut - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'DC3':
                tokens = ['private:', '        vector<int> rank(n + 3);']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                captions = ['', '采样三元组排序与递归命名', '恢复采样排名并合并']
                for part in range(3):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'convolution_mod':
                tokens = ['    const long long p = 167772161']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                captions = ['', '三模卷积与固定逆元CRT重构']
                for part in range(2):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一函数）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'DagDominator':
                tokens = ['    bool build(']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                captions = ['', '全图拓扑检查与逐点构建支配树']
                for part in range(2):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'FibonacciPeriod':
                tokens = ['    u128 prime_period(']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                captions = ['', '素数候选缩减、素数幂逐层检查与互素lcm']
                for part in range(2):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'AssignmentSpectrum':
                tokens = ['int solve(', '            int y;']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                captions = ['', '重置状态与多源松弛', '继续solve：调整顶标与翻转增广路径']
                for part in range(3):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'DynamicPathMax':
                tokens = ['void apply(', 'void splay(', 'bool expose(']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                captions = ['', '递归下传与旋转', '伸展、访问与换根', '连边、两种删边与路径操作']
                for part in range(4):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'SequenceKth':
                tokens = ['void pull(', 'int insert(int u,', 'int less(int u,']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                captions = ['', '内树合并与递归重建', '按位置插入与修改', '区间秩与第k小查询']
                for part in range(4):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'SequenceScapegoat':
                tokens = ['int make(', 'void collect(', 'int insert(int u,', 'int count(int u,']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                captions = ['', '节点复用与频次维护', '递归收集、重建与平衡', '按位置插入与删除', '区间等值计数与右移']
                for part in range(5):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'SequenceSplay':
                tokens = ['void flip(', '// Internal rank', 'void reverse(']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                captions = ['', '翻转下传与伸展旋转', '位置和原编号互查', '区间翻转与完整顺序']
                for part in range(4):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'CentroidDiameter':
                tokens = ['void size_dfs(', '// Fixed tree', 'void set(']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                captions = ['', '递归分解与不同分支的距离', '清空重建与重心候选', '活动点设置与端点查询']
                for part in range(4):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'CentroidNearest':
                tokens = ['void collect(', '// Fixed connected']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                captions = ['', '重心距离与递归分解', '清空重建、活动点增删与最近点查询']
                for part in range(3):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'CentroidSum':
                tokens = ['void size_dfs(', '// Raw distance d', '// Rebuild resets']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                captions = ['', '子树大小、重心与距离记录', '线性构建距离桶和递归分解',
                            '重建、点权赋值与距离球求和']
                for part in range(4):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'SegmentBeats':
                tokens = ['void pull(', 'void apply_add(', 'void push(', 'void chmin(']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                captions = ['', '极值合并与递归建树', '整段加法和单极值组截断',
                            '标记下传与有条件递归更新', '公开修改与区间和查询']
                for part in range(5):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'PersistentOrderedTreap':
                tokens = ['// Only rotate freshly copied nodes', 'int merge(',
                          '// Updates append versions', '// Ranks and k are']
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                captions = ['', '复制路径插入与旋转', '复制路径合并与删除',
                            '版本接口、大小与排名', '第 k 小与严格前驱后继']
                for part in range(5):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'OrderedSplay':
                cuts = [start,
                        next(i for i in range(start, end) if 'void splay(' in lines[i]),
                        next(i for i in range(start, end) if 'void insert(' in lines[i]),
                        next(i for i in range(start, end) if 'int rank(' in lines[i]),
                        next(i for i in range(start, end) if 'optional<ll> prev(' in lines[i]), end]
                captions = ['', '伸展与查找', '插入与删除', '排名与第 k 小', '严格前驱与后继']
                for part in range(5):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'ScapegoatTree':
                first = next(i for i in range(start, end) if 'int balance(' in lines[i])
                second = next(i for i in range(first, end) if 'int less(' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(first) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 重建与插入删除（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(first + 1) + ',lastline=' + str(second) + ',firstnumber=' + str(first - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 排名、第 k 小与严格前驱后继（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(second + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(second - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'SequenceTreap':
                cuts = [start,
                        next(i for i in range(start, end) if 'void apply_reverse(' in lines[i]),
                        next(i for i in range(start, end) if 'int merge(' in lines[i]),
                        next(i for i in range(start, end) if '// Requires every value' in lines[i]), end]
                captions = ['', '顺序反转、懒标记下传与分裂', '合并、插入、删除与顺序反转', '位翻转、加法、查询与输出']
                for part in range(4):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'AffineSequenceTreap':
                cuts = [start,
                        next(i for i in range(start, end) if 'void flip(' in lines[i]),
                        next(i for i in range(start, end) if 'int merge(' in lines[i]),
                        next(i for i in range(start, end) if 'void reverse(' in lines[i]), end]
                captions = ['', '反转、仿射下传与递归分裂', '合并、插入与删除', '区间操作与递归输出']
                for part in range(4):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'GcdSequenceTreap':
                cuts = [start,
                        next(i for i in range(start, end) if 'void pull(' in lines[i]),
                        next(i for i in range(start, end) if 'void rebuild(' in lines[i]),
                        next(i for i in range(start, end) if '// Insert after' in lines[i]), end]
                captions = ['', '聚合与递归分裂合并', '构建、重算与节点回收', '插删、单点修改与分组查询']
                for part in range(4):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'TreePathProducts':
                first = next(i for i in range(start, end) if 'bool is_root(' in lines[i])
                second = next(i for i in range(first, end) if 'void splay(' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(first) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 聚合、翻转、递归下传与旋转（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(first + 1) + ',lastline=' + str(second) + ',firstnumber=' + str(first - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent Splay、虚实边切换与公开接口（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(second + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(second - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'TreePathKth':
                cuts = [start,
                        next(i for i in range(start, end) if 'int insert(' in lines[i]),
                        next(i for i in range(start, end) if 'int lca(' in lines[i]), end]
                captions = ['', '版本插入与递归建树', '最近公共祖先与路径第 k 小']
                for part in range(3):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[part] + 1) + ',lastline=' + str(cuts[part + 1]) + ',firstnumber=' + str(cuts[part] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'FunctionalGraph':
                first = next((i for i in range(start, end) if 'component.assign' in lines[i]))
                second = next((i for i in range(first, end) if re.match('    int (advance|Advance)\\(', lines[i])))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(first) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 环、入环树与倍增表（接上页同一结构体与函数）：')
                body.append('\\lstinputlisting[firstline=' + str(first + 1) + ',lastline=' + str(second) + ',firstnumber=' + str(first - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 跳转与最少步数接口（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(second + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(second - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'SAMLex':
                split = next(i for i in range(start, end) if '// alphabet must be' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 字典序查询（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'TreeDiameter':
                split = next((i for i in range(start, end) if 'void merge(' in lines[i]))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 合并与最远点查询（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'EulerLCA':
                first = next((i for i in range(start, end) if re.match('    void (dfs|Dfs)\\(', lines[i])))
                second = next((i for i in range(first, end) if re.match('    int (lca|Lca)\\(', lines[i])))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(first) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 递归欧拉序与 RMQ（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(first + 1) + ',lastline=' + str(second) + ',firstnumber=' + str(first - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent LCA、边数距离与带权距离（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(second + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(second - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'PersistentRange':
                first = next((i for i in range(start, end) if re.match('    int (change|Change)\\(', lines[i])))
                second = next((i for i in range(first, end) if re.match('    ll (get|Get)\\(', lines[i])))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(first) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 区间加与版本拼接（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(first + 1) + ',lastline=' + str(second) + ',firstnumber=' + str(first - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 只读查询与对外接口（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(second + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(second - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name in ('SubtreeColors', 'VirtualTree', 'CentroidPairs', 'WaveletMatrix', 'GaussXor', 'SecondMST', 'DivisionTree'):
                tokens = {'DivisionTree': ['    void build('], 'SecondMST': ['    // Keep edge IDs', '    Pair path(', '    Result solve('], 'GaussXor': ['        Solution ans{'], 'WaveletMatrix': ['        for (int d = h - 1;', '// Count values'], 'SubtreeColors': ['void solve('],
                          'VirtualTree': ['void dfs(', 'Edge path('],
                          'CentroidPairs': ['int centroid(', '// Input must be a forest.']}[name]
                captions = {'DivisionTree': ['稳定划分与区间查询'], 'SecondMST': ['不同权摘要与递归预处理', '路径查询', 'Kruskal与逐边换入'], 'GaussXor': ['构造特解与零空间基（接上页 solve）'], 'WaveletMatrix': ['逐层稳定划分（接上页构造函数）、rank 与第 k 小', '严格小于计数与频次'], 'SubtreeColors': ['启发式合并与运行入口'],
                            'VirtualTree': ['预处理与最近公共祖先', '压缩路径与虚树构造'],
                            'CentroidPairs': ['重心与分解', '重建与距离计数']}[name]
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                for j, (lo, hi) in enumerate(zip(cuts, cuts[1:])):
                    if j:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[j - 1] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(lo + 1) + ',lastline=' + str(hi) + ',firstnumber=' + str(lo - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'minkowski_sum':
                split = next(i for i in range(start, end) if 'while (i < n || j < m)' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 合并凸包边（接上页同一函数）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'closest_pair_i64':
                split = next(i for i in range(start, end) if 'function<I(int, int)> solve' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 递归分治（接上页同一函数）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'MultipointEvaluation':
                split = next(i for i in range(start, end) if 'void eval(' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 余式下传与求值入口（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'StaticRMQ2D':
                split = next(i for i in range(start, end) if '        for (int k = 0;' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 层表递推、位置比较与四块查询（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'StaticRMQ':
                split = next(i for i in range(start, end) if '        int m = st[0].size();' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 块间表构建、最优位置合并与查询（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'KDMin':
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in ['    int build(', '    void erase(']] + [end]
                for part, (left, right) in enumerate(zip(cuts, cuts[1:])):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + ['', '中位数建树与固定包围盒', '按编号删除与矩形查询'][part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(left + 1) + ',lastline=' + str(right) + ',firstnumber=' + str(left - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'Chain3D':
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in ['        vector<int> order(', '        auto cdq =', '        cdq(cdq,']] + [end]
                captions = ['', '坐标顺序、分组与状态合并', '先转移再右递归（同一构造函数内）', '汇总答案与路径恢复']
                for part, (left, right) in enumerate(zip(cuts, cuts[1:])):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + captions[part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(left + 1) + ',lastline=' + str(right) + ',firstnumber=' + str(left - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'KDRange':
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in ['    bool less(', '    int build(', '    void take(']] + [end]
                for part, (left, right) in enumerate(zip(cuts, cuts[1:])):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + ['', '节点复用与子树维护', '建树、回收与插入', '矩形取出与删除入口'][part] + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(left + 1) + ',lastline=' + str(right) + ',firstnumber=' + str(left - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'KDNearest':
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in ['    int build(', '    void search(']] + [end]
                for part, (left, right) in enumerate(zip(cuts, cuts[1:])):
                    if part:
                        body.append('\\newpage')
                        body.append('\\noindent ' + ('中位数建树与距离界' if part == 1 else '剪枝搜索与查询入口') + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(left + 1) + ',lastline=' + str(right) + ',firstnumber=' + str(left - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'chirp_z':
                split = next((i for i in range(start, end) if 'power = 1;' == lines[i].strip()))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 构造循环卷积并取点值（接上页同一函数）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'SetConvolution':
                split = next((i for i in range(start, end) if 'static Poly ' in lines[i]))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 点乘并逆变换（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'BostanMori':
                split = next((i for i in range(start, end) if '// a[i] =' in lines[i]))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 从初值构造递推生成函数（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'NttConvolution':
                split = next((i for i in range(start, end) if 'for (int half' in lines[i] or 'for ( int half' in lines[i]))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 蝶形变换与卷积（接上页同一结构体与函数）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'CompositeRoots':
                split = next((i for i in range(start, end) if 'static optional<Composite' in lines[i]))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 局部求根与 CRT 系数（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'PrimePowerRoots':
                first = next((i for i in range(start, end) if 'static optional<Prime' in lines[i]))
                second = next((i for i in range(first, end) if lines[i].strip().startswith('ll scale =')))
                cuts = [start, first, second, end]
                for j in range(3):
                    if j:
                        body.append('\\newpage')
                        body.append('\\noindent 接上页同一结构体（第三页继续同一函数）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[j] + 1) + ',lastline=' + str(cuts[j + 1]) + ',firstnumber=' + str(cuts[j] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'CirclePolygon':
                split = next((i for i in range(start, end) if lines[i].strip() == 'R answer = 0;'))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 分段面积与逐边累加（接上页同一结构体与函数）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'EnclosingCircle':
                split = next((i for i in range(start, end) if 'static optional<Circle>' in lines[i]))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 随机增量主过程（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'IntegerTangents':
                split = next(i for i in range(start, end) if '// |coordinates|' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 公切线枚举与精确切点排序（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'CircleTangents':
                split = next((i for i in range(start, end) if lines[i].strip() == 'Result answer;'))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 内外公切线枚举（接上页同一函数）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'ClosestPair':
                split = next((i for i in range(start, end) if lines[i].strip() == 'int m = (l + r) / 2;'))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 分治、归并与跨分界线点对（接上页同一函数）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'odd_induced_partition':
                split = next(i for i in range(start, end) if 'dsu d(n);' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 合并未完成分组（接上页同一函数）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'NegativeCostFlow':
                split = next(i for i in range(start, end) if 'pair<ll, I> solve(' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 需求修复、增广与原边流量还原（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'GeneralSAM':
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in ['void build()', 'long long distinct()']] + [end]
                for j in range(3):
                    if j:
                        body.append('\\newpage')
                        body.append('\\noindent ' + ('BFS 构建' if j == 1 else '不同子串计数') + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[j] + 1) + ',lastline=' + str(cuts[j + 1]) + ',firstnumber=' + str(cuts[j] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'LiChao':
                split = next(i for i in range(start, end) if 'void add(int p' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 插入与查询（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'SegmentLiChao':
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in ['bool better(', 'int query(']] + [end]
                for j in range(3):
                    if j:
                        body.append('\\newpage')
                        body.append('\\noindent ' + ('精确比较与线段插入' if j == 1 else '查询最优线段编号') + '（接上页同一结构体）：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[j] + 1) + ',lastline=' + str(cuts[j + 1]) + ',firstnumber=' + str(cuts[j] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'IntegerHalfplanes':
                first = next((i for i in range(start, end) if re.match('    static I (value|Value)\\(', lines[i])))
                second = next((i for i in range(first, end) if lines[i].strip() == 'deque<Line> q;'))
                cuts = [start, first, second, end]
                for j in range(3):
                    if j:
                        body.append('\\newpage')
                        body.append('\\noindent 接上页同一结构体与函数：')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[j] + 1) + ',lastline=' + str(cuts[j + 1]) + ',firstnumber=' + str(cuts[j] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'garner':
                split = next((i for i in range(start, end) if lines[i].startswith('// Return the least')))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\Needspace{180pt}')
                body.append('\\subsection*{规范解对目标数取模}')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'RealPolarLess':
                split = next(i for i in range(start, end) if 'bool operator()' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 接上页同一结构体：极角比较接口。')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'RealPlane':
                split = next(i for i in range(start, end) if 'enum class Kind' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\Needspace{310pt}')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'BiconnectedCore':
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in ['void dfs(', 'void paint(', 'void run(']] + [end]
                for j, (lo, hi) in enumerate(zip(cuts, cuts[1:])):
                    if j:
                        body.append('\\Needspace{' + str((hi - lo + 2) * 11) + 'pt}')
                    body.append('\\lstinputlisting[firstline=' + str(lo + 1) + ',lastline=' + str(hi) + ',firstnumber=' + str(lo - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'Lucas':
                split = next((i for i in range(start, end) if re.match('    int (choose|Choose)\\(', lines[i])))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\Needspace{270pt}')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'PrimitiveRoot':
                cuts = [start, next((i for i in range(start, end) if re.match('    PrimitiveRoot\\(', lines[i]))), next((i for i in range(start, end) if re.match('    bool (is_root|Is_Root)\\(', lines[i]))), next(i for i in range(start, end) if 'vector<int> all()' in lines[i]), end]
                for j in range(len(cuts) - 1):
                    if j:
                        body.append('\\Needspace{' + str((cuts[j + 1] - cuts[j] + 2) * 11) + 'pt}')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[j] + 1) + ',lastline=' + str(cuts[j + 1]) + ',firstnumber=' + str(cuts[j] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'Binomial':
                split = next((i for i in range(start, end) if re.match('    Z (choose|Choose)\\(', lines[i])))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\Needspace{220pt}')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'LiftingLCA':
                cuts = [start, next((i for i in range(start, end) if re.match('    void (dfs|Dfs)\\(', lines[i]))), next((i for i in range(start, end) if re.match('    int (lca|Lca)\\(', lines[i]))), end]
                for j in range(len(cuts) - 1):
                    if j:
                        body.append('\\newpage')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[j] + 1) + ',lastline=' + str(cuts[j + 1]) + ',firstnumber=' + str(cuts[j] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'XorBasis':
                cuts = [start, next((i for i in range(start, end) if re.match('    bool contains\\(', lines[i]))), next((i for i in range(start, end) if re.match('    optional<U> kth\\(', lines[i]))) - 1, end]
                for j in range(len(cuts) - 1):
                    if j:
                        body.append('\\newpage')
                    body.append('\\lstinputlisting[firstline=' + str(cuts[j] + 1) + ',lastline=' + str(cuts[j + 1]) + ',firstnumber=' + str(cuts[j] - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'SuffixArray':
                split = next((i for i in range(start, end) if re.search('for \\(\\s*int k = 1; k < n;', lines[i])))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
            elif name in ('ExLucas', 'DynamicKth', 'SupportHull', 'SuffixLCP', 'PositionBasis', 'XorWalk', 'Lowlink', 'OfflineLCA', 'EulerLCA', 'DirectedEuler', 'UndirectedEuler', 'mixed_euler_orientation', 'odd_cycle_vertices', 'LexTwoSAT'):
                if name == 'LexTwoSAT':
                    split = next((i for i in range(start, end) if re.match('    bool (paint|Paint)\\(', lines[i])))
                elif name == 'odd_cycle_vertices':
                    split = next((i for i in range(start, end) if 'edges(graph.blocks.size())' in lines[i]))
                elif name == 'mixed_euler_orientation':
                    split = next((i for i in range(start, end) if '!edges.empty()' in lines[i]))
                elif name in ('DirectedEuler', 'UndirectedEuler'):
                    split = next((i for i in range(start, end) if re.match('    bool (run|Run)\\(', lines[i]))) - 1
                elif name == 'EulerLCA':
                    split = next((i for i in range(start, end) if re.match('    void (dfs|Dfs)\\(', lines[i])))
                elif name == 'OfflineLCA':
                    split = next((i for i in range(start, end) if re.match('    int (find|Find)\\(', lines[i])))
                elif name == 'Lowlink':
                    split = next((i for i in range(start, end) if re.match('    void (dfs|Dfs)\\(', lines[i])))
                elif name == 'XorWalk':
                    split = next((i for i in range(start, end) if re.match('    void (add|Insert)\\(', lines[i])))
                elif name == 'PositionBasis':
                    split = next((i for i in range(start, end) if re.match('    void (insert|Insert)\\(', lines[i])))
                elif name == 'SuffixLCP':
                    split = next((i for i in range(start, end) if re.match('    int (query|Query)\\(', lines[i])))
                elif name == 'SupportHull':
                    split = next((i for i in range(start, end) if 'template <class Oracle>' in lines[i])) - 2
                else:
                    split = next((i for i in range(start, end) if re.match('    (?:int (?:choose|Choose)|void (?:set|Set))\\(', lines[i])))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                if name in ('SupportHull', 'PositionBasis', 'XorWalk', 'Lowlink', 'OfflineLCA', 'EulerLCA', 'DirectedEuler', 'UndirectedEuler', 'mixed_euler_orientation', 'odd_cycle_vertices', 'LexTwoSAT'):
                    body.append('\\newpage')
                else:
                    body.append('\\Needspace{' + str((end - split + 2) * 11) + 'pt}')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'lazy_segtree':
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in ['void act(', 'S all()', 'template <class G> int min_left']] + [end]
                for j, (lo, hi) in enumerate(zip(cuts, cuts[1:])):
                    if j:
                        body.append('\\newpage')
                    body.append('\\lstinputlisting[firstline=' + str(lo + 1) + ',lastline=' + str(hi) + ',firstnumber=' + str(lo - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'circle_intersections':
                split = next(i for i in range(start, end) if lines[i].strip() == 'R d = G::norm(v);')
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 默认正容差分支（接上页同一函数）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name in ('ModInt', 'mint'):
                split = next(i for i in range(start, end) if 'optional<' + name + '> try_inv' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                if name == 'ModInt':
                    body.append('\\noindent 求逆与除法（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'PalindromicTree':
                split = next(i for i in range(start, end) if '// Append a lowercase letter' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 接上页同一结构体：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name in ('SpfaFlow', 'SuffixAutomaton', 'Isap', 'ZkwFlow', 'TreeMarket'):
                tokens = (['void collect(', '// Existing markets'] if name == 'TreeMarket' else
                          ['// Internal:', 'bool relabel('] if name == 'ZkwFlow' else
                          ['void bfs(', '// Returns additional'] if name == 'Isap' else
                          ['// Internal:', '// Returns additional'] if name == 'SpfaFlow' else
                          ['void extend(', 'vector<long long> counts()'])
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in tokens] + [end]
                for j, (lo, hi) in enumerate(zip(cuts, cuts[1:])):
                    if j:
                        body.append('\\newpage')
                        body.append('\\noindent 接上页同一结构体：')
                    body.append('\\lstinputlisting[firstline=' + str(lo + 1) + ',lastline=' + str(hi) + ',firstnumber=' + str(lo - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'MinCostFlow':
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in ['// Negative costs allowed', 'if (d[t] == inf)']] + [end]
                for j, (lo, hi) in enumerate(zip(cuts, cuts[1:])):
                    if j:
                        body.append('\\newpage')
                    body.append('\\lstinputlisting[firstline=' + str(lo + 1) + ',lastline=' + str(hi) + ',firstnumber=' + str(lo - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'IntegerPlane':
                split = next(i for i in range(start, end) if 'struct PolarLess' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 极角比较器（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'ComplexFFT':
                split = next(i for i in range(start, end) if 'void transform(' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 正逆变换（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'FpsFunctions':
                split = next(i for i in range(start, end) if 'static Poly exp(' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'Min25':
                split = next(i for i in range(start, end) if 'array<Z, 3> prefix{};' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'dag_path_determinant':
                split = next(i for i in range(start, end) if 'vector<vector<Z>> a(' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'GaussMod':
                split = next(i for i in range(start, end) if 'Solution ans{' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'LinkCutTree':
                cuts = [start] + [next(i for i in range(start, end) if token in lines[i]) for token in ['void rotate(', 'void access(', 'bool connected(']] + [end]
                for j, (lo, hi) in enumerate(zip(cuts, cuts[1:])):
                    if j:
                        body.append('\\newpage')
                    body.append('\\lstinputlisting[firstline=' + str(lo + 1) + ',lastline=' + str(hi) + ',firstnumber=' + str(lo - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'Dinic':
                cuts = [start, next(i for i in range(start, end) if 'bool bfs(' in lines[i]), next(i for i in range(start, end) if '// Returns additional flow' in lines[i]), end]
                for j, (lo, hi) in enumerate(zip(cuts, cuts[1:])):
                    if j:
                        body.append('\\newpage')
                    body.append('\\lstinputlisting[firstline=' + str(lo + 1) + ',lastline=' + str(hi) + ',firstnumber=' + str(lo - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'BoundedMaxFlow':
                split = next(i for i in range(start, end) if 'optional<ll> minimum(' in lines[i])
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\newpage')
                body.append('\\noindent 最小净流与原边流量（接上页同一结构体）：')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'segtree':
                cuts = [start, next(i for i in range(start, end) if 'S prod(' in lines[i]), next(i for i in range(start, end) if 'template <class F> int min_left' in lines[i]), end]
                for j, (lo, hi) in enumerate(zip(cuts, cuts[1:])):
                    if j:
                        body.append('\\newpage')
                    body.append('\\lstinputlisting[firstline=' + str(lo + 1) + ',lastline=' + str(hi) + ',firstnumber=' + str(lo - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            else:
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(end) + ']{../src/' + style + '/' + filename + '.hpp}')
            if name == 'rp':
                body.append(r'\begin{lstlisting}' + '\n' + 'rp<int> a;\na.push_back(3);\na.insert(0, 7);\nrp<int> b = a;\nb.replace(1, 9);\nb.erase(0, 1);\nauto c = a.substr(0, 1);\nint x = a[1];\n' + r'\end{lstlisting}')
            if name == 'pheap':
                body.append(r'\begin{lstlisting}' + '\n' + 'pheap<int> a, b;\nauto h = a.push(7);\na.modify(h, 2);\nb.join(a);\nb.erase(h);\n' + r'\end{lstlisting}')
            for usage in usage_rows:
                if usage['symbol'] != name:
                    if name in usage.get('also_covers', []):
                        body.append('联合使用示例见第~\\pageref{usage-' + usage['id'] + '}~页（' + esc(usage['problem']) + '），其中直接调用本模板。')
                    continue
                if name == 'BoundedMaxFlow' or usage.get('start_new_page'):
                    body.append('\\newpage')
                count = len(usage['snippet'].splitlines())
                if usage['id'] == 'example-354':
                    usage = dict(usage, page_break_before='    vector<int> answer(m);')
                if usage['id'] == 'example-355':
                    usage = dict(usage, page_break_before='    struct Change')
                if usage['id'] == 'example-353':
                    usage = dict(usage, page_break_before='        vector<pair<int, int>> ask(q, {-1, -1});')
                split_lines = 0
                if usage.get('configuration_functions') and count > 48:
                    split_lines = usage['snippet'].splitlines().index('int main()')
                if usage.get('page_break_before'):
                    split_lines = usage['snippet'].splitlines().index(usage['page_break_before'])
                space = min(680, 140 + (split_lines or count) * 11 + len(usage['summary']) / 42 * 14)
                if usage.get('listing_new_page'):
                    space = 200
                body.append('\\Needspace{' + str(round(space)) + 'pt}')
                kind = usage.get('kind', 'template')
                heading = {'template': '模板题使用：', 'application': '应用题补充：', 'api': '接口用法演示：'}[kind]
                body.append('\\subsection*{' + heading + esc(usage['problem']) + '}')
                if not usage.get('listing_new_page'):
                    body.append('\\label{usage-' + usage['id'] + '}')
                body.append(('演示约定：' if kind == 'api' else '题意：') + esc(usage['summary']))
                from template_dependencies import references
                body.append('所需模板：' + references(usage['requires']) + '。以下仅含使用代码，默认已粘贴所需模板并包含标准头文件、使用 std 命名空间。')
                for header in usage.get('extra_headers', []):
                    body.append('额外依赖（不属于标准头文件）：\\nolinkurl{' + header + '}，须由编译环境提供并显式包含。')
                link = '\\url{' + usage['url'] + '}'
                if usage.get('url_label'):
                    link = '\\href{' + usage['url'] + '}{' + esc(usage['url_label']) + '}'
                if usage.get('extra_headers') and not usage.get('url_label'):
                    link = '\\href{' + usage['url'] + '}{参考文档}'
                body.append(('来源：' if kind == 'api' else '题目：') + link)
                if usage.get('listing_new_page'):
                    body.append('\\newpage')
                    body.append('\\subsection*{' + esc(usage['problem']) + '：使用代码}')
                    body.append('\\label{usage-' + usage['id'] + '}')
                listing = usage['snippet_file'].removeprefix('docs/')
                if split_lines:
                    body.append('\\lstinputlisting[lastline=' + str(split_lines) + ']{' + listing + '}')
                    body.append('\\newpage')
                    body.append('\\noindent ' + ('继续处理操作（接上页同一 main）：' if usage.get('page_break_before') else '使用入口（接上页配置函数）：'))
                    if usage.get('continuation_break_before'):
                        listing_lines = usage['snippet'].splitlines()
                        boundary = usage['continuation_break_before']
                        assert listing_lines.count(boundary) == 1
                        second_split = listing_lines.index(boundary)
                        assert split_lines < second_split < count
                        body.append('\\lstinputlisting[firstline=' + str(split_lines + 1) + ',lastline=' + str(second_split) + ',firstnumber=' + str(split_lines + 1) + ']{' + listing + '}')
                        body.append('\\newpage')
                        body.append('\\noindent 继续处理操作（接上页同一 main）：')
                        body.append('\\lstinputlisting[firstline=' + str(second_split + 1) + ',firstnumber=' + str(second_split + 1) + ']{' + listing + '}')
                    else:
                        body.append('\\lstinputlisting[firstline=' + str(split_lines + 1) + ',firstnumber=' + str(split_lines + 1) + ']{' + listing + '}')
                else:
                    body.append('\\lstinputlisting{' + listing + '}')
            if name in ('BurnsideAverage', 'permutation_cycles', 'necklace_colorings', 'MonotoneHull', 'monotone_dp_layer', 'wqs_independent_set', 'StrictSecondShortest', 'KShortestWalks', 'OverallKth', 'TreeIsomorphism', 'TreeMo', 'RollbackMo', 'TimeConnectivity', 'RealSpace', 'Line3', 'Plane3', 'AffineSequenceTreap', 'TarjanSCC', 'AssignmentSpectrum', 'FibonacciPeriod', 'DagDominator', 'DC3', 'convolution_mod'):
                body.append('\\newpage')
            records.append(dict(module=file, symbol=name, title=cn, chapter=title, code='\n'.join(lines[start:end]), latex='\n\n'.join(body[begin:])))
assert {r['symbol'] for r in records} == {r[1] for r in cat}, 'Catalog contains an unprinted module'
(root / 'build').mkdir(exist_ok=True)
from template_dependencies import dependencies, references
copy_dependencies = dependencies(records)
for row in records:
    deps = copy_dependencies[row['symbol']]
    row['dependencies'] = deps
    if deps:
        marker = r'\index{' + row['symbol'].replace('_', r'\_') + '}'
        assert row['latex'].count(marker) == 1, row['symbol']
        row['latex'] = row['latex'].replace(marker, marker + '\n\n' + '代码依赖：' + references(deps) + '。抄写时一并准备；标准库类型不列入算法依赖。', 1)
(root / 'build/book-sections.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
(root / 'docs/template-dependencies.json').write_text(json.dumps(copy_dependencies, ensure_ascii=False, indent=2) + '\n')
from taxonomy_layout import render
from knowledge_layout import classified_fragments, legacy_knowledge
(root / 'docs/generated.tex').write_text(render(records + classified_fragments(), omnibus=True) + '\n')
(root / 'docs/mathematics-legacy.tex').write_text(legacy_knowledge())
print('Generated source-linked book sections')
