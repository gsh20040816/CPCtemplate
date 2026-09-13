#!/usr/bin/env python3
"""Build category books from the same source-linked sections as the omnibus."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
rows = json.loads((root / 'build/book-sections.json').read_text())
groups = {
    'data-structures': ('数据结构', 'segtree rope ordered_set hash_table data_structure modified_mo position_basis basis_intersection affine_segment_tree persistent_array persistent_range dynamic_kth persistent_distinct treap splay gcd_sequence'),
    'graphs': ('图论', 'tarjan functional_graph biconnected odd_cycle_vertices vertex_removal edge_components bridge_augmentation flow maximum_closure graph release_bfs lex_two_sat directed_euler word_chain undirected_euler mixed_euler xor_walk graph_advanced gomory_hu cut_tree_queries weighted_matching blossom'),
    'trees': ('树上算法', 'tree offline_lca euler_lca tree_diameter lifting_lca path_intersection centroid dsu_on_tree virtual_tree tree_path_kth dynamic_tree'),
    'strings': ('字符串', 'string suffix_lcp palindromic_tree'),
    'mathematics': ('数学', 'number_theory linear_equation linear_congruence segmented_sieve batch_inverse inverse_table garner primitive_root coprime_pairs floor_moments divisor_sum euler_phi carmichael partitions lucas exlucas modular_sqrt kth_residue prime_power_roots root_factors composite_roots interpolation ntt_convolution polynomial_shift chirp_z stirling set_convolution subset_convolution polynomial algebra determinant_mod matrix_tree matrix_tree_mod recurrence bostan_mori'),
    'geometry': ('计算几何', 'geometry halfplanes circle_polygon enclosing_circle circle_tangents closest_pair geometry_extra support_hull'),
}
owner = {m: k for k, (_, modules) in groups.items() for m in modules.split()}
for r in rows:
    r['volume'] = ('mathematics' if r['symbol'] == 'MaxPlusMatrix' else 'data-structures') if r['module'] == 'optimization' else owner[r['module']]
by_name = {r['symbol']: r for r in rows}
assert len(by_name) == len(rows)
notes = {k: [] for k in groups}
parts = re.split(r'(?=\\section\{)', (root / 'docs/mathematics.tex').read_text())[1:]
for part in parts:
    title = part.split('\n', 1)[0]
    if 'ACL 的组合约定' in title:
        # General ACL comparison stays in the omnibus, not every category.
        continue
    key = 'mathematics'
    if '数值算法与几何' in title:
        key = 'geometry'
    elif any(x in title for x in ['可持久化区间', '杭州 2023 K', '带修莫队', '并查集模板题']):
        key = 'data-structures'
    elif '非负权树' in title:
        key = 'trees'
    elif any(x in title for x in ['函数图', '杭州 2023 H', '杭州 2023 G', 'SCC 模板题']):
        key = 'graphs'
    notes[key].append(part)
notes['geometry'].append((root / 'docs/geometry-notes.tex').read_text())

manifest = []
for key, (title, _) in groups.items():
    primary = [r for r in rows if r['volume'] == key]
    included = {r['symbol'] for r in primary}
    knowledge = '\n'.join(notes[key])
    # Exact catalog identifiers conservatively include dependencies mentioned in
    # code/comments or interface notes; close transitively before emitting labels.
    pending = knowledge + '\n' + '\n'.join(r['code'] + r['latex'] for r in primary)
    while True:
        tokens = set(re.findall(r'\b[A-Za-z_]\w*\b', pending))
        added = (tokens & by_name.keys()) - included
        if not added:
            break
        included.update(added)
        pending = '\n'.join(by_name[n]['code'] + by_name[n]['latex'] for n in added)
    dependencies = [r for r in rows if r['symbol'] in included and r not in primary]
    body = [r'\input{preamble.tex}', r'\begin{document}', r'\raggedbottom',
            r'\hypersetup{pageanchor=false}', r'\begin{titlepage}\centering\vspace*{35mm}',
            r'{\Huge\bfseries ' + title + r'\par}\vspace{15mm}',
            r'{\LARGE Morning Flower and Evening Oath\par}\vspace{15mm}',
            r'{\Large XCPC vector 模板分册\par}\vfill',
            r'建设稿：验证状态与适用边界见各条目及仓库 verification/。',
            r'\end{titlepage}\hypersetup{pageanchor=true}', r'\frontmatter\tableofcontents',
            r'\chapter{使用约定}',
            r'C++20，默认包含 bits/stdc++.h 并使用 std 命名空间。下标、区间及数值范围以各条目说明为准。DFS 保持递归，需满足题目栈空间条件。',
            r'本册按“大类（分册）—种类（章）—项目（节）”组织。跨类引用的已收录组件附在依赖部分；源头文件中的依赖仍须一并检查。',
            r'本册尚非全量完成稿；传统版评测仅为历史档案，当前只维护 vector 代码。', r'\mainmatter']
    def emit(entries):
        last = None
        for r in entries:
            if r['module'] != last:
                body.append('\\chapter{' + r['chapter'] + '}')
                last = r['module']
            body.append(r['latex'])
    emit(primary)
    if knowledge.strip():
        body += [r'\chapter{配套知识与验证范围}', knowledge]
    if dependencies:
        body.append(r'\appendix')
        body.append(r'\part{跨类依赖}')
        emit(dependencies)
    body += [r'\backmatter\printindex', r'\end{document}']
    source = '\n\n'.join(body) + '\n'
    labels = set(re.findall(r'\\label\{([^}]+)\}', source))
    refs = set(re.findall(r'\\(?:page)?ref\{([^}]+)\}', source))
    assert not refs - labels, (key, refs - labels)
    (root / f'docs/volume-{key}.tex').write_text(source)
    manifest.append(dict(id=key, title=title, entries=[r['symbol'] for r in primary], dependencies=[r['symbol'] for r in dependencies]))
assert sum(len(v['entries']) for v in manifest) == len(rows)
(root / 'docs/volumes.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print('Generated six volumes; every catalog entry has exactly one primary category')
