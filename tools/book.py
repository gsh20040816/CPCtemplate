#!/usr/bin/env python3
import json, re
from pathlib import Path
root = Path(__file__).resolve().parents[1]
cat = json.loads((root / 'docs/catalog.json').read_text())

def esc(s):
    for a, b in [('\\', '\\textbackslash{}'), ('&', '\\&'), ('%', '\\%'), ('$', '\\$'), ('#', '\\#'), ('_', '\\_'), ('{', '\\{'), ('}', '\\}')]:
        if a != '\\':
            s = s.replace(a, b)
    s = s.replace('^', '\\textasciicircum{}')
    s = re.sub('[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+', lambda m: '$^{' + m[0].translate(str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁻', '0123456789-')) + '}$', s)
    for a, b in {'⊆': '$\\subseteq$', 'λ': '$\\lambda$', 'ω': '$\\omega$', '≡': '$\\equiv$', '≤': '$\\le$', '≥': '$\\ge$', '≠': '$\\ne$', 'Σ': '$\\sum$', 'α': '$\\alpha$', 'μ': '$\\mu$', 'φ': '$\\varphi$', '²': '$^2$', '³': '$^3$', '⁹': '$^9$', '⁶': '$^6$', '⁻¹²': '$^{-12}$', '¹²': '$^{12}$', '¹¹': '$^{11}$', '√': '$\\sqrt{\\vphantom x}$', '–': '--'}.items():
        s = s.replace(a, b)
    return s
chapters = {'tarjan': 'Tarjan 与缩点', 'functional_graph': '函数图', 'biconnected': '双连通分量与圆方树', 'odd_cycle_vertices': '奇环顶点判定', 'vertex_removal': '删点连通性', 'edge_components': '边双缩点与边定向', 'bridge_augmentation': '桥树最少加边', 'data_structure': '数据结构', 'position_basis': '带位置线性基', 'basis_intersection': '线性空间求交', 'affine_segment_tree': '线段树常用修改', 'flow': '网络流', 'maximum_closure': '最大权闭合子图', 'graph': '图论', 'release_bfs': '开放时间最短路', 'lex_two_sat': '字典序最小 2-SAT', 'directed_euler': '有向欧拉路', 'word_chain': '字典序单词链', 'undirected_euler': '无向欧拉路', 'mixed_euler': '混合图欧拉定向', 'xor_walk': '图上异或行走', 'tree': '树上算法', 'offline_lca': '离线最近公共祖先', 'euler_lca': '在线最近公共祖先', 'tree_diameter': '树上点集摘要', 'lifting_lca': '倍增祖先与路径最值', 'path_intersection': '树上路径交', 'centroid': '点分治', 'dsu_on_tree': '树上启发式合并', 'virtual_tree': '虚树', 'string': '字符串', 'suffix_lcp': '后缀查询与重复子串', 'palindromic_tree': '回文树', 'number_theory': '数论', 'linear_equation': '二元一次不定方程', 'linear_congruence': '线性同余方程', 'segmented_sieve': '区间筛素数', 'batch_inverse': '批量模逆元', 'inverse_table': '连续整数逆元表', 'garner': '混合进制中国剩余定理', 'primitive_root': '乘法阶与原根', 'coprime_pairs': '矩形 GCD 计数', 'floor_moments': '带权类欧几里德', 'divisor_sum': '模几何级数与约数和', 'euler_phi': '单个数的欧拉函数', 'carmichael': 'Carmichael 函数', 'partitions': '整数分拆', 'lucas': '素数模数组合数', 'exlucas': '合数模数组合数', 'modular_sqrt': '二次剩余', 'kth_residue': '素数模高次剩余', 'prime_power_roots': '素数幂模高次剩余', 'root_factors': '合数求根的准备', 'composite_roots': '合数模高次剩余', 'interpolation': '多项式插值', 'ntt_convolution': '参数化 NTT 卷积', 'polynomial_shift': '多项式平移', 'chirp_z': '等比点求值', 'stirling': '斯特林数整行计算', 'set_convolution': '集合变换与卷积', 'subset_convolution': '不相交子集卷积', 'polynomial': '多项式', 'algebra': '代数与数论进阶', 'determinant_mod': '任意模数行列式', 'matrix_tree': '带权生成树计数', 'matrix_tree_mod': '合数模生成树计数', 'geometry': '计算几何', 'optimization': '优化与可持久化', 'persistent_array': '可持久化数组', 'persistent_range': '可持久化区间操作', 'tree_path_kth': '树上路径第 k 小', 'dynamic_kth': '动态区间顺序统计', 'persistent_distinct': '区间不同数统计', 'graph_advanced': '图论进阶', 'gomory_hu': '最小割树', 'cut_tree_queries': '最小割树查询', 'weighted_matching': '带权二分图匹配', 'halfplanes': '精确有界半平面交', 'circle_polygon': '圆与多边形面积', 'enclosing_circle': '最小覆盖圆', 'circle_tangents': '圆的切线', 'closest_pair': '浮点最近点对', 'geometry_extra': '精确几何进阶', 'support_hull': '凸包支撑点查询', 'dynamic_tree': '动态树', 'treap': '随机平衡树', 'splay': '伸展树', 'gcd_sequence': '状态序列维护', 'blossom': '一般图匹配', 'recurrence': '线性递推', 'bostan_mori': '快速线性递推'}
body = []
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
            if name == 'LexTwoSAT':
                split = next((i for i in range(start, end) if re.match('    bool (paint|Paint)\\(', lines[i])))
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'odd_cycle_vertices':
                split = next((i for i in range(start, end) if 'edges(graph.blocks.size())' in lines[i]))
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'mixed_euler_orientation':
                split = next((i for i in range(start, end) if '!edges.empty()' in lines[i]))
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
            if name == 'release_bfs':
                body.append('\\newpage')
            if name in ('DirectedEuler', 'UndirectedEuler'):
                split = next((i for i in range(start, end) if re.match('    bool (run|Run)\\(', lines[i]))) - 1
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
            if name == 'SuffixLCP':
                split = next((i for i in range(start, end) if re.match('    int (query|Query)\\(', lines[i])))
                estimate = (split - start) * 10.2 + 70 + len(info) / 65 * 12
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
            if estimate < 680:
                body.append('\\Needspace{' + str(round(estimate)) + 'pt}')
            if name in ('SuffixArray', 'XorBasis', 'IntegerGeometry3D'):
                body.append('\\newpage')
            body.append('\\section{' + cn + '}\\label{' + style + '-' + name + '}\\index{' + target.replace('_', '\\_') + '}')
            body.append(esc(info))
            if name == 'Arborescence':
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
            elif name == 'Lucas':
                split = next((i for i in range(start, end) if re.match('    int (choose|Choose)\\(', lines[i])))
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(split) + ']{../src/' + style + '/' + filename + '.hpp}')
                body.append('\\Needspace{270pt}')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            elif name == 'PrimitiveRoot':
                cuts = [start, next((i for i in range(start, end) if re.match('    void (init|Init)\\(', lines[i]))), next((i for i in range(start, end) if re.match('    bool (is_root|Is_Root)\\(', lines[i]))), end]
                for j in range(len(cuts) - 1):
                    if j:
                        body.append('\\newpage')
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
                if name in ('SupportHull', 'SuffixLCP', 'PositionBasis', 'XorWalk', 'Lowlink', 'OfflineLCA', 'EulerLCA', 'DirectedEuler', 'UndirectedEuler', 'mixed_euler_orientation', 'odd_cycle_vertices', 'LexTwoSAT'):
                    body.append('\\newpage')
                else:
                    body.append('\\Needspace{' + str((end - split + 2) * 11) + 'pt}')
                body.append('\\lstinputlisting[firstline=' + str(split + 1) + ',lastline=' + str(end) + ',firstnumber=' + str(split - start + 1) + ']{../src/' + style + '/' + filename + '.hpp}')
            else:
                body.append('\\lstinputlisting[firstline=' + str(start + 1) + ',lastline=' + str(end) + ']{../src/' + style + '/' + filename + '.hpp}')
(root / 'docs/generated.tex').write_text('\n\n'.join(body) + '\n')
print('Generated source-linked book sections')
