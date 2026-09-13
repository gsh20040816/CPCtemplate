# Library Checker 逐题覆盖队列

固定官方仓库版本：[`e64660561a99`](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db)。

从所有非 test/ 的 info.toml 提取，核对 categories.toml，无分类缺失文件。未列入分类的题也保留，是否已部署需逐题核对。仅按用户要求排除官方 Sample 类；没有按实现难度缩小范围。

这是逐题工作队列，不是已审题或 AC 清单。参数为上游原始元数据，完整输入条件仍需阅读题面和 verifier。候选驱动只按显式题目 URL 或精确文件名关联；其他 OJ 的同源题 AC 不冒充 Library Checker 在线 AC。

| 分类 | 总数 | 纳入 |
| --- | ---: | ---: |
| Big Integer | 6 | 6 |
| Convolution | 15 | 15 |
| Data Structure | 43 | 43 |
| Enumerative Combinatorics | 17 | 17 |
| Geometry | 8 | 8 |
| Graph | 36 | 36 |
| Linear Algebra | 17 | 17 |
| Number Theory | 22 | 22 |
| Other | 7 | 7 |
| Polynomial | 26 | 26 |
| Sample | 3 | 0 |
| Set Power Series | 4 | 4 |
| String | 11 | 11 |
| Tree | 20 | 20 |
| Unlisted | 17 | 17 |

| 题目 | 分类 | 状态 | 候选驱动 |
| --- | --- | --- | --- |
| [Addition of Big Integers](https://judge.yosupo.jp/problem/addition_of_big_integers) | Big Integer | 待逐题审题、适配与在线验证 | — |
| [Addition of Hex Big Integers](https://judge.yosupo.jp/problem/addition_of_hex_big_integers) | Big Integer | 待逐题审题、适配与在线验证 | — |
| [Division of Big Integers](https://judge.yosupo.jp/problem/division_of_big_integers) | Big Integer | 待逐题审题、适配与在线验证 | — |
| [Division of Hex Big Integers](https://judge.yosupo.jp/problem/division_of_hex_big_integers) | Big Integer | 待逐题审题、适配与在线验证 | — |
| [Multiplication of Big Integers](https://judge.yosupo.jp/problem/multiplication_of_big_integers) | Big Integer | 待逐题审题、适配与在线验证 | — |
| [Multiplication of Hex Big Integers](https://judge.yosupo.jp/problem/multiplication_of_hex_big_integers) | Big Integer | 待逐题审题、适配与在线验证 | — |
| [Bitwise And Convolution](https://judge.yosupo.jp/problem/bitwise_and_convolution) | Convolution | 待逐题审题、适配与在线验证 | — |
| [Bitwise Xor Convolution](https://judge.yosupo.jp/problem/bitwise_xor_convolution) | Convolution | 待逐题审题、适配与在线验证 | — |
| [Convolution](https://judge.yosupo.jp/problem/convolution_mod) | Convolution | 待逐题审题、适配与在线验证 | — |
| [Convolution (Mod 1,000,000,007)](https://judge.yosupo.jp/problem/convolution_mod_1000000007) | Convolution | 待逐题审题、适配与在线验证 | — |
| [Convolution (Mod 2^64)](https://judge.yosupo.jp/problem/convolution_mod_2_64) | Convolution | 待逐题审题、适配与在线验证 | — |
| [Convolution (Large)](https://judge.yosupo.jp/problem/convolution_mod_large) | Convolution | 待逐题审题、适配与在线验证 | — |
| [Gcd Convolution](https://judge.yosupo.jp/problem/gcd_convolution) | Convolution | 待逐题审题、适配与在线验证 | — |
| [Lcm Convolution](https://judge.yosupo.jp/problem/lcm_convolution) | Convolution | 待逐题审题、适配与在线验证 | — |
| [Min Plus Convolution (Concave and Arbitrary)](https://judge.yosupo.jp/problem/min_plus_convolution_concave_arbitrary) | Convolution | 待逐题审题、适配与在线验证 | — |
| [Min Plus Convolution (Convex and Arbitrary)](https://judge.yosupo.jp/problem/min_plus_convolution_convex_arbitrary) | Convolution | 待逐题审题、适配与在线验证 | — |
| [Min Plus Convolution (Convex and Convex)](https://judge.yosupo.jp/problem/min_plus_convolution_convex_convex) | Convolution | 待逐题审题、适配与在线验证 | — |
| [Convolution on the Multiplicative Monoid of $\mathbb{Z} / 2^N\mathbb{Z}$](https://judge.yosupo.jp/problem/mul_mod2n_convolution) | Convolution | 待逐题审题、适配与在线验证 | — |
| [Convolution on the Multiplicative Monoid of $\mathbb{Z} / P\mathbb{Z}$](https://judge.yosupo.jp/problem/mul_modp_convolution) | Convolution | 待逐题审题、适配与在线验证 | — |
| [Multidimensional Convolution (Truncated)](https://judge.yosupo.jp/problem/multivariate_convolution) | Convolution | 待逐题审题、适配与在线验证 | — |
| [Multidimensional Convolution (Circular)](https://judge.yosupo.jp/problem/multivariate_convolution_cyclic) | Convolution | 待逐题审题、适配与在线验证 | — |
| [Area of Union of Rectangles](https://judge.yosupo.jp/problem/area_of_union_of_rectangles) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Associative Array](https://judge.yosupo.jp/problem/associative_array) | Data Structure | 已有本库 Library Checker AC，接口范围仍须核对 | [associative_array.compact.cpp](../verify/library_checker/associative_array.compact.cpp) |
| [Deque Operate All Composite](https://judge.yosupo.jp/problem/deque_operate_all_composite) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Double-Ended Priority Queue](https://judge.yosupo.jp/problem/double_ended_priority_queue) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Dynamic Point Rectangle Affine Rectangle Sum](https://judge.yosupo.jp/problem/dynamic_point_set_rectangle_affine_rectangle_sum) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Dynamic Sequence Range Affine Range Sum](https://judge.yosupo.jp/problem/dynamic_sequence_range_affine_range_sum) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Line Add Get Min](https://judge.yosupo.jp/problem/line_add_get_min) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Ordered Set](https://judge.yosupo.jp/problem/ordered_set) | Data Structure | 已有本库 Library Checker AC，接口范围仍须核对 | [ordered_set.compact.cpp](../verify/library_checker/ordered_set.compact.cpp) |
| [Persistent Queue](https://judge.yosupo.jp/problem/persistent_queue) | Data Structure | 已有本库 Library Checker AC，接口范围仍须核对 | [persistent_queue.compact.cpp](../verify/library_checker/persistent_queue.compact.cpp) |
| [Persistent Range Affine Range Sum](https://judge.yosupo.jp/problem/persistent_range_affine_range_sum) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Persistent Unionfind](https://judge.yosupo.jp/problem/persistent_unionfind) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Point Add Range Sum](https://judge.yosupo.jp/problem/point_add_range_sum) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Point Add Rectangle Sum](https://judge.yosupo.jp/problem/point_add_rectangle_sum) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Point Set Range Composite](https://judge.yosupo.jp/problem/point_set_range_composite) | Data Structure | 已有本库 Library Checker AC，接口范围仍须核对 | [point_set_range_composite.compact.cpp](../verify/library_checker/point_set_range_composite.compact.cpp) |
| [Point Set Range Composite (Large Array)](https://judge.yosupo.jp/problem/point_set_range_composite_large_array) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Point Set Range Frequency](https://judge.yosupo.jp/problem/point_set_range_frequency) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Point Set Range Sort Range Composite](https://judge.yosupo.jp/problem/point_set_range_sort_range_composite) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Predecessor Problem](https://judge.yosupo.jp/problem/predecessor_problem) | Data Structure | 已有本库 Library Checker AC，接口范围仍须核对 | [predecessor_problem.compact.cpp](../verify/library_checker/predecessor_problem.compact.cpp) |
| [Queue Operate All Composite](https://judge.yosupo.jp/problem/queue_operate_all_composite) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Range Affine Point Get](https://judge.yosupo.jp/problem/range_affine_point_get) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Range Affine Range Sum](https://judge.yosupo.jp/problem/range_affine_range_sum) | Data Structure | 待逐题审题、适配与在线验证 | [range_affine_range_sum.compact.cpp](../verify/library_checker/range_affine_range_sum.compact.cpp) |
| [Range Affine Range Sum (Large Array)](https://judge.yosupo.jp/problem/range_affine_range_sum_large_array) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Range Chmin Chmax Add Range Sum](https://judge.yosupo.jp/problem/range_chmin_chmax_add_range_sum) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Range Kth Smallest](https://judge.yosupo.jp/problem/range_kth_smallest) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Range Linear Add Range Min](https://judge.yosupo.jp/problem/range_linear_add_range_min) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Range Parallel Unionfind](https://judge.yosupo.jp/problem/range_parallel_unionfind) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Range Reverse Range Sum](https://judge.yosupo.jp/problem/range_reverse_range_sum) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Range Set Range Composite](https://judge.yosupo.jp/problem/range_set_range_composite) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Rectangle Add Point Get](https://judge.yosupo.jp/problem/rectangle_add_point_get) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Rectangle Sum](https://judge.yosupo.jp/problem/rectangle_sum) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Segment Add Get Min](https://judge.yosupo.jp/problem/segment_add_get_min) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Set Xor-Min](https://judge.yosupo.jp/problem/set_xor_min) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Static Range Count Distinct](https://judge.yosupo.jp/problem/static_range_count_distinct) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Static Range Frequency](https://judge.yosupo.jp/problem/static_range_frequency) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Static Range Inversions Query](https://judge.yosupo.jp/problem/static_range_inversions_query) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Static Range LIS Query](https://judge.yosupo.jp/problem/static_range_lis_query) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Static Range Mode Query](https://judge.yosupo.jp/problem/static_range_mode_query) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Static Range Sum](https://judge.yosupo.jp/problem/static_range_sum) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Static Rectangle Add Rectangle Sum](https://judge.yosupo.jp/problem/static_rectangle_add_rectangle_sum) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Static RMQ](https://judge.yosupo.jp/problem/staticrmq) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Unionfind](https://judge.yosupo.jp/problem/unionfind) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Unionfind with Potential](https://judge.yosupo.jp/problem/unionfind_with_potential) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Unionfind with Potential (Non-Commutative Group)](https://judge.yosupo.jp/problem/unionfind_with_potential_non_commutative_group) | Data Structure | 待逐题审题、适配与在线验证 | — |
| [Bell Number](https://judge.yosupo.jp/problem/bell_number) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [Binomial Coefficient](https://judge.yosupo.jp/problem/binomial_coefficient) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [Binomial Coefficient (Prime Mod)](https://judge.yosupo.jp/problem/binomial_coefficient_prime_mod) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [Factorial](https://judge.yosupo.jp/problem/factorial) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [Many Factorials](https://judge.yosupo.jp/problem/many_factorials) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [Montmort Number](https://judge.yosupo.jp/problem/montmort_number_mod) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [Number of Increasing Sequences Between Two Sequences](https://judge.yosupo.jp/problem/number_of_increasing_sequences_between_two_sequences) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [Number of Subsequences ](https://judge.yosupo.jp/problem/number_of_subsequences) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [Partition Function](https://judge.yosupo.jp/problem/partition_function) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [$q$-Binomial Coefficient (Prime Mod)](https://judge.yosupo.jp/problem/q_binomial_coefficient_prime_mod) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [$\#_p$ Subset Sum](https://judge.yosupo.jp/problem/sharp_p_subset_sum) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [Stirling Number of the First Kind](https://judge.yosupo.jp/problem/stirling_number_of_the_first_kind) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [Stirling Number of the First Kind (Fixed K)](https://judge.yosupo.jp/problem/stirling_number_of_the_first_kind_fixed_k) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [Stirling Number of the First Kind (Small p, Large n)](https://judge.yosupo.jp/problem/stirling_number_of_the_first_kind_small_p_large_n) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [Stirling Number of the Second Kind](https://judge.yosupo.jp/problem/stirling_number_of_the_second_kind) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [Stirling Number of the Second Kind (Fixed K)](https://judge.yosupo.jp/problem/stirling_number_of_the_second_kind_fixed_k) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [Stirling Number of the Second Kind (Small p, Large n)](https://judge.yosupo.jp/problem/stirling_number_of_the_second_kind_small_p_large_n) | Enumerative Combinatorics | 待逐题审题、适配与在线验证 | — |
| [Closest Pair of Points](https://judge.yosupo.jp/problem/closest_pair) | Geometry | 待逐题审题、适配与在线验证 | — |
| [Convex Layers](https://judge.yosupo.jp/problem/convex_layers) | Geometry | 待逐题审题、适配与在线验证 | — |
| [Count Points in Triangles](https://judge.yosupo.jp/problem/count_points_in_triangle) | Geometry | 待逐题审题、适配与在线验证 | — |
| [Euclidean MST](https://judge.yosupo.jp/problem/euclidean_mst) | Geometry | 待逐题审题、适配与在线验证 | — |
| [Furthest Pair of Points](https://judge.yosupo.jp/problem/furthest_pair) | Geometry | 待逐题审题、适配与在线验证 | — |
| [Manhattan MST](https://judge.yosupo.jp/problem/manhattanmst) | Geometry | 待逐题审题、适配与在线验证 | — |
| [Sort Points by Argument](https://judge.yosupo.jp/problem/sort_points_by_argument) | Geometry | 待逐题审题、适配与在线验证 | — |
| [Static Convex Hull](https://judge.yosupo.jp/problem/static_convex_hull) | Geometry | 待逐题审题、适配与在线验证 | — |
| [Assignment Problem](https://judge.yosupo.jp/problem/assignment) | Graph | 待逐题审题、适配与在线验证 | — |
| [Biconnected Components](https://judge.yosupo.jp/problem/biconnected_components) | Graph | 待逐题审题、适配与在线验证 | — |
| [Edge Coloring of Bipartite Graph](https://judge.yosupo.jp/problem/bipartite_edge_coloring) | Graph | 待逐题审题、适配与在线验证 | — |
| [Matching on Bipartite Graph](https://judge.yosupo.jp/problem/bipartitematching) | Graph | 待逐题审题、适配与在线验证 | — |
| [Chordal Graph Recognition](https://judge.yosupo.jp/problem/chordal_graph_recognition) | Graph | 待逐题审题、适配与在线验证 | — |
| [Chromatic Number](https://judge.yosupo.jp/problem/chromatic_number) | Graph | 待逐题审题、适配与在线验证 | — |
| [Chromatic Polynomial](https://judge.yosupo.jp/problem/chromatic_polynomial) | Graph | 待逐题审题、适配与在线验证 | — |
| [Connected Components of Complement Graph](https://judge.yosupo.jp/problem/connected_components_of_complement_graph) | Graph | 待逐题审题、适配与在线验证 | — |
| [Counting $C _ 4$'s](https://judge.yosupo.jp/problem/counting_c4) | Graph | 待逐题审题、适配与在线验证 | — |
| [Counting Eulerian Circuits](https://judge.yosupo.jp/problem/counting_eulerian_circuits) | Graph | 待逐题审题、适配与在线验证 | — |
| [Counting Spanning Trees (Directed)](https://judge.yosupo.jp/problem/counting_spanning_tree_directed) | Graph | 待逐题审题、适配与在线验证 | — |
| [Counting Spanning Trees (Undirected)](https://judge.yosupo.jp/problem/counting_spanning_tree_undirected) | Graph | 待逐题审题、适配与在线验证 | — |
| [Cycle Detection (Directed)](https://judge.yosupo.jp/problem/cycle_detection) | Graph | 待逐题审题、适配与在线验证 | — |
| [Cycle Detection (Undirected)](https://judge.yosupo.jp/problem/cycle_detection_undirected) | Graph | 待逐题审题、适配与在线验证 | — |
| [Directed MST](https://judge.yosupo.jp/problem/directedmst) | Graph | 待逐题审题、适配与在线验证 | — |
| [Dominator Tree](https://judge.yosupo.jp/problem/dominatortree) | Graph | 待逐题审题、适配与在线验证 | — |
| [Dynamic Graph Vertex Add Component Sum](https://judge.yosupo.jp/problem/dynamic_graph_vertex_add_component_sum) | Graph | 待逐题审题、适配与在线验证 | — |
| [Enumerate Cliques](https://judge.yosupo.jp/problem/enumerate_cliques) | Graph | 待逐题审题、适配与在线验证 | — |
| [Enumerate Triangles](https://judge.yosupo.jp/problem/enumerate_triangles) | Graph | 待逐题审题、适配与在线验证 | — |
| [Eulerian Trail (Directed)](https://judge.yosupo.jp/problem/eulerian_trail_directed) | Graph | 待逐题审题、适配与在线验证 | — |
| [Eulerian Trail (Undirected)](https://judge.yosupo.jp/problem/eulerian_trail_undirected) | Graph | 待逐题审题、适配与在线验证 | — |
| [Matching on General Graph](https://judge.yosupo.jp/problem/general_matching) | Graph | 待逐题审题、适配与在线验证 | — |
| [General Weighted Matching](https://judge.yosupo.jp/problem/general_weighted_matching) | Graph | 待逐题审题、适配与在线验证 | — |
| [Global Minimum Cut of Dynamic Star Augmented Graph](https://judge.yosupo.jp/problem/global_minimum_cut_of_dynamic_star_augmented_graph) | Graph | 待逐题审题、适配与在线验证 | — |
| [Strongly Connected Components (Incremental)](https://judge.yosupo.jp/problem/incremental_scc) | Graph | 待逐题审题、适配与在线验证 | — |
| [K-Shortest Walk](https://judge.yosupo.jp/problem/k_shortest_walk) | Graph | 待逐题审题、适配与在线验证 | — |
| [Maximum Independent Set](https://judge.yosupo.jp/problem/maximum_independent_set) | Graph | 待逐题审题、适配与在线验证 | — |
| [Minimum Cost b-flow](https://judge.yosupo.jp/problem/min_cost_b_flow) | Graph | 待逐题审题、适配与在线验证 | — |
| [Minimum Diameter Spanning Tree](https://judge.yosupo.jp/problem/minimum_diameter_spanning_tree) | Graph | 待逐题审题、适配与在线验证 | — |
| [Minimum Spanning Tree](https://judge.yosupo.jp/problem/minimum_spanning_tree) | Graph | 待逐题审题、适配与在线验证 | — |
| [Strongly Connected Components](https://judge.yosupo.jp/problem/scc) | Graph | 待逐题审题、适配与在线验证 | — |
| [Shortest Path](https://judge.yosupo.jp/problem/shortest_path) | Graph | 待逐题审题、适配与在线验证 | — |
| [st-Numbering](https://judge.yosupo.jp/problem/st_numbering) | Graph | 待逐题审题、适配与在线验证 | — |
| [Three-Edge-Connected Components](https://judge.yosupo.jp/problem/three_edge_connected_components) | Graph | 待逐题审题、适配与在线验证 | — |
| [Tree Decomposition (Width 2)](https://judge.yosupo.jp/problem/tree_decomposition_width_2) | Graph | 待逐题审题、适配与在线验证 | — |
| [Two-Edge-Connected Components](https://judge.yosupo.jp/problem/two_edge_connected_components) | Graph | 待逐题审题、适配与在线验证 | — |
| [Adjugate Matrix](https://judge.yosupo.jp/problem/adjugate_matrix) | Linear Algebra | 待逐题审题、适配与在线验证 | — |
| [Characteristic Polynomial](https://judge.yosupo.jp/problem/characteristic_polynomial) | Linear Algebra | 待逐题审题、适配与在线验证 | — |
| [Hafnian of Matrix](https://judge.yosupo.jp/problem/hafnian_of_matrix) | Linear Algebra | 待逐题审题、适配与在线验证 | — |
| [Intersection of $\mathbb{F}_{2}$ vector spaces](https://judge.yosupo.jp/problem/intersection_of_f2_vector_spaces) | Linear Algebra | 待逐题审题、适配与在线验证 | [intersection_intersection.compact.cpp](../verify/library_checker/intersection_intersection.compact.cpp)<br>[intersection_zassenhaus.compact.cpp](../verify/library_checker/intersection_zassenhaus.compact.cpp) |
| [Inverse Matrix](https://judge.yosupo.jp/problem/inverse_matrix) | Linear Algebra | 待逐题审题、适配与在线验证 | — |
| [Inverse Matrix (Mod 2)](https://judge.yosupo.jp/problem/inverse_matrix_mod_2) | Linear Algebra | 待逐题审题、适配与在线验证 | — |
| [Determinant of Matrix](https://judge.yosupo.jp/problem/matrix_det) | Linear Algebra | 待逐题审题、适配与在线验证 | — |
| [Determinant of Matrix (Arbitrary Mod)](https://judge.yosupo.jp/problem/matrix_det_arbitrary_mod) | Linear Algebra | 待逐题审题、适配与在线验证 | — |
| [Determinant of Matrix (Mod 2)](https://judge.yosupo.jp/problem/matrix_det_mod_2) | Linear Algebra | 待逐题审题、适配与在线验证 | — |
| [Matrix Product](https://judge.yosupo.jp/problem/matrix_product) | Linear Algebra | 待逐题审题、适配与在线验证 | — |
| [Matrix Product (Mod 2)](https://judge.yosupo.jp/problem/matrix_product_mod_2) | Linear Algebra | 待逐题审题、适配与在线验证 | — |
| [Rank of Matrix](https://judge.yosupo.jp/problem/matrix_rank) | Linear Algebra | 待逐题审题、适配与在线验证 | — |
| [Rank of Matrix (Mod 2)](https://judge.yosupo.jp/problem/matrix_rank_mod_2) | Linear Algebra | 待逐题审题、适配与在线验证 | — |
| [Pow of Matrix](https://judge.yosupo.jp/problem/pow_of_matrix) | Linear Algebra | 待逐题审题、适配与在线验证 | — |
| [Determinant of Sparse Matrix](https://judge.yosupo.jp/problem/sparse_matrix_det) | Linear Algebra | 待逐题审题、适配与在线验证 | — |
| [System of Linear Equations](https://judge.yosupo.jp/problem/system_of_linear_equations) | Linear Algebra | 待逐题审题、适配与在线验证 | — |
| [System of Linear Equations (Mod 2)](https://judge.yosupo.jp/problem/system_of_linear_equations_mod_2) | Linear Algebra | 待逐题审题、适配与在线验证 | — |
| [Bernoulli Number](https://judge.yosupo.jp/problem/bernoulli_number) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Counting Primes](https://judge.yosupo.jp/problem/counting_primes) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Counting Square-free Integers](https://judge.yosupo.jp/problem/counting_squarefrees) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Discrete Logarithm](https://judge.yosupo.jp/problem/discrete_logarithm_mod) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Enumerate Primes](https://judge.yosupo.jp/problem/enumerate_primes) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Enumerate Quotients](https://judge.yosupo.jp/problem/enumerate_quotients) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Factorize](https://judge.yosupo.jp/problem/factorize) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Gcd of Gaussian Integers](https://judge.yosupo.jp/problem/gcd_of_gaussian_integers) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Kth Root (Integer)](https://judge.yosupo.jp/problem/kth_root_integer) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Kth Root (Mod)](https://judge.yosupo.jp/problem/kth_root_mod) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Min of Mod of Linear](https://judge.yosupo.jp/problem/min_of_mod_of_linear) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Nim Product ($\mathbb{F}_{2^{64}}$)](https://judge.yosupo.jp/problem/nim_product_64) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Primality Test](https://judge.yosupo.jp/problem/primality_test) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Primitive Root](https://judge.yosupo.jp/problem/primitive_root) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Rational Approximation](https://judge.yosupo.jp/problem/rational_approximation) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Sqrt Mod](https://judge.yosupo.jp/problem/sqrt_mod) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Stern–Brocot Tree](https://judge.yosupo.jp/problem/stern_brocot_tree) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Sum of Floor of Linear](https://judge.yosupo.jp/problem/sum_of_floor_of_linear) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Sum of Multiplicative Function(Large)](https://judge.yosupo.jp/problem/sum_of_multiplicative_function_large) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Sum of Totient Function](https://judge.yosupo.jp/problem/sum_of_totient_function) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Tetration Mod](https://judge.yosupo.jp/problem/tetration_mod) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Represent A Number As Two Square Sum](https://judge.yosupo.jp/problem/two_square_sum) | Number Theory | 待逐题审题、适配与在线验证 | — |
| [Consecutive Terms of Linear Recurrent Sequence](https://judge.yosupo.jp/problem/consecutive_terms_of_linear_recurrent_sequence) | Other | 待逐题审题、适配与在线验证 | — |
| [Find Linear Recurrence](https://judge.yosupo.jp/problem/find_linear_recurrence) | Other | 待逐题审题、适配与在线验证 | — |
| [Kth term of Linearly Recurrent Sequence](https://judge.yosupo.jp/problem/kth_term_of_linearly_recurrent_sequence) | Other | 待逐题审题、适配与在线验证 | — |
| [Longest Increasing Subsequence](https://judge.yosupo.jp/problem/longest_increasing_subsequence) | Other | 待逐题审题、适配与在线验证 | — |
| [$\sum_{i=0}^{n-1} r^i i^d$](https://judge.yosupo.jp/problem/sum_of_exponential_times_polynomial) | Other | 待逐题审题、适配与在线验证 | — |
| [$\sum_{i=0}^{\infty} r^i i^d$](https://judge.yosupo.jp/problem/sum_of_exponential_times_polynomial_limit) | Other | 待逐题审题、适配与在线验证 | — |
| [2 Sat](https://judge.yosupo.jp/problem/two_sat) | Other | 待逐题审题、适配与在线验证 | — |
| [Composition of Formal Power Series](https://judge.yosupo.jp/problem/composition_of_formal_power_series) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Composition of Formal Power Series (Large)](https://judge.yosupo.jp/problem/composition_of_formal_power_series_large) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Compositional Inverse of Formal Power Series](https://judge.yosupo.jp/problem/compositional_inverse_of_formal_power_series) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Compositional Inverse of Formal Power Series (Large)](https://judge.yosupo.jp/problem/compositional_inverse_of_formal_power_series_large) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Conversion from Monomial Basis to Newton Basis](https://judge.yosupo.jp/problem/conversion_from_monomial_basis_to_newton_basis) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Division of Polynomials](https://judge.yosupo.jp/problem/division_of_polynomials) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Exp of Formal Power Series](https://judge.yosupo.jp/problem/exp_of_formal_power_series) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Exp of Formal Power Series (Sparse)](https://judge.yosupo.jp/problem/exp_of_formal_power_series_sparse) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Factorization of Polynomial (Mod)](https://judge.yosupo.jp/problem/factorization_of_polynomials) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Inv of Formal Power Series](https://judge.yosupo.jp/problem/inv_of_formal_power_series) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Inv of Formal Power Series (Sparse)](https://judge.yosupo.jp/problem/inv_of_formal_power_series_sparse) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Inv of Polynomials](https://judge.yosupo.jp/problem/inv_of_polynomials) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Log of Formal Power Series](https://judge.yosupo.jp/problem/log_of_formal_power_series) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Log of Formal Power Series (Sparse)](https://judge.yosupo.jp/problem/log_of_formal_power_series_sparse) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Multipoint Evaluation](https://judge.yosupo.jp/problem/multipoint_evaluation) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Multipoint Evaluation (Geometric Sequence)](https://judge.yosupo.jp/problem/multipoint_evaluation_on_geometric_sequence) | Polynomial | 待逐题审题、适配与在线验证 | [multipoint_evaluation_on_geometric_sequence.compact.cpp](../verify/library_checker/multipoint_evaluation_on_geometric_sequence.compact.cpp) |
| [Polynomial Interpolation](https://judge.yosupo.jp/problem/polynomial_interpolation) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Polynomial Interpolation (Geometric Sequence)](https://judge.yosupo.jp/problem/polynomial_interpolation_on_geometric_sequence) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Polynomial Root Finding (Mod 998244353)](https://judge.yosupo.jp/problem/polynomial_root_finding) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Polynomial Taylor Shift](https://judge.yosupo.jp/problem/polynomial_taylor_shift) | Polynomial | 待逐题审题、适配与在线验证 | [polynomial_taylor_shift.compact.cpp](../verify/library_checker/polynomial_taylor_shift.compact.cpp) |
| [Pow of Formal Power Series](https://judge.yosupo.jp/problem/pow_of_formal_power_series) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Pow of Formal Power Series (Sparse)](https://judge.yosupo.jp/problem/pow_of_formal_power_series_sparse) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Product of Polynomial Sequence](https://judge.yosupo.jp/problem/product_of_polynomial_sequence) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Shift of Sampling Points of Polynomial](https://judge.yosupo.jp/problem/shift_of_sampling_points_of_polynomial) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Sqrt of Formal Power Series](https://judge.yosupo.jp/problem/sqrt_of_formal_power_series) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [Sqrt of Formal Power Series (Sparse)](https://judge.yosupo.jp/problem/sqrt_of_formal_power_series_sparse) | Polynomial | 待逐题审题、适配与在线验证 | — |
| [A + B](https://judge.yosupo.jp/problem/aplusb) | Sample | 排除：官方 Sample | — |
| [Many A + B](https://judge.yosupo.jp/problem/many_aplusb) | Sample | 排除：官方 Sample | — |
| [Many A + B (128 bit)](https://judge.yosupo.jp/problem/many_aplusb_128bit) | Sample | 排除：官方 Sample | — |
| [Exp of Set Power Series](https://judge.yosupo.jp/problem/exp_of_set_power_series) | Set Power Series | 待逐题审题、适配与在线验证 | — |
| [Polynomial Composite Set Power Series](https://judge.yosupo.jp/problem/polynomial_composite_set_power_series) | Set Power Series | 待逐题审题、适配与在线验证 | — |
| [Power Projection of Set Power Series](https://judge.yosupo.jp/problem/power_projection_of_set_power_series) | Set Power Series | 待逐题审题、适配与在线验证 | — |
| [Subset Convolution](https://judge.yosupo.jp/problem/subset_convolution) | Set Power Series | 待逐题审题、适配与在线验证 | — |
| [Eertree](https://judge.yosupo.jp/problem/eertree) | String | 待逐题审题、适配与在线验证 | — |
| [Enumerate Palindromes](https://judge.yosupo.jp/problem/enumerate_palindromes) | String | 待逐题审题、适配与在线验证 | — |
| [Longest Common Substring](https://judge.yosupo.jp/problem/longest_common_substring) | String | 待逐题审题、适配与在线验证 | — |
| [Lyndon Factorization](https://judge.yosupo.jp/problem/lyndon_factorization) | String | 待逐题审题、适配与在线验证 | — |
| [Number of Substrings](https://judge.yosupo.jp/problem/number_of_substrings) | String | 待逐题审题、适配与在线验证 | — |
| [Palindromes in Deque](https://judge.yosupo.jp/problem/palindromes_in_deque) | String | 待逐题审题、适配与在线验证 | — |
| [Prefix-Substring LCS](https://judge.yosupo.jp/problem/prefix_substring_lcs) | String | 待逐题审题、适配与在线验证 | — |
| [Run Enumerate](https://judge.yosupo.jp/problem/runenumerate) | String | 待逐题审题、适配与在线验证 | — |
| [Suffix Array](https://judge.yosupo.jp/problem/suffixarray) | String | 待逐题审题、适配与在线验证 | — |
| [Wildcard Pattern Matching](https://judge.yosupo.jp/problem/wildcard_pattern_matching) | String | 待逐题审题、适配与在线验证 | — |
| [Z Algorithm](https://judge.yosupo.jp/problem/zalgorithm) | String | 待逐题审题、适配与在线验证 | — |
| [Cartesian Tree](https://judge.yosupo.jp/problem/cartesian_tree) | Tree | 待逐题审题、适配与在线验证 | — |
| [Common Interval Decomposition Tree](https://judge.yosupo.jp/problem/common_interval_decomposition_tree) | Tree | 待逐题审题、适配与在线验证 | — |
| [Dynamic Tree Subtree Add Subtree Sum](https://judge.yosupo.jp/problem/dynamic_tree_subtree_add_subtree_sum) | Tree | 待逐题审题、适配与在线验证 | — |
| [Dynamic Tree Vertex Add Path Sum](https://judge.yosupo.jp/problem/dynamic_tree_vertex_add_path_sum) | Tree | 待逐题审题、适配与在线验证 | — |
| [Dynamic Tree Vertex Add Subtree Sum](https://judge.yosupo.jp/problem/dynamic_tree_vertex_add_subtree_sum) | Tree | 待逐题审题、适配与在线验证 | — |
| [Dynamic Tree Vertex Set Path Composite](https://judge.yosupo.jp/problem/dynamic_tree_vertex_set_path_composite) | Tree | 待逐题审题、适配与在线验证 | — |
| [Frequency Table of Tree Distance](https://judge.yosupo.jp/problem/frequency_table_of_tree_distance) | Tree | 待逐题审题、适配与在线验证 | — |
| [Jump on Tree](https://judge.yosupo.jp/problem/jump_on_tree) | Tree | 待逐题审题、适配与在线验证 | — |
| [Lowest Common Ancestor](https://judge.yosupo.jp/problem/lca) | Tree | 待逐题审题、适配与在线验证 | — |
| [Point Set Tree Path Composite Sum](https://judge.yosupo.jp/problem/point_set_tree_path_composite_sum) | Tree | 待逐题审题、适配与在线验证 | — |
| [Point Set Tree Path Composite Sum (Fixed Root)](https://judge.yosupo.jp/problem/point_set_tree_path_composite_sum_fixed_root) | Tree | 待逐题审题、适配与在线验证 | — |
| [Rooted Tree Isomorphism Classification](https://judge.yosupo.jp/problem/rooted_tree_isomorphism_classification) | Tree | 待逐题审题、适配与在线验证 | — |
| [Rooted Tree Topological Order with Minimum Inversions](https://judge.yosupo.jp/problem/rooted_tree_topological_order_with_minimum_inversions) | Tree | 待逐题审题、适配与在线验证 | — |
| [Tree Diameter](https://judge.yosupo.jp/problem/tree_diameter) | Tree | 待逐题审题、适配与在线验证 | — |
| [Tree Path Composite Sum](https://judge.yosupo.jp/problem/tree_path_composite_sum) | Tree | 待逐题审题、适配与在线验证 | — |
| [Vertex Add Path Sum](https://judge.yosupo.jp/problem/vertex_add_path_sum) | Tree | 待逐题审题、适配与在线验证 | — |
| [Vertex Add Range Contour Sum on Tree](https://judge.yosupo.jp/problem/vertex_add_range_contour_sum_on_tree) | Tree | 待逐题审题、适配与在线验证 | — |
| [Vertex Add Subtree Sum](https://judge.yosupo.jp/problem/vertex_add_subtree_sum) | Tree | 待逐题审题、适配与在线验证 | — |
| [Vertex Get Range Contour Add on Tree](https://judge.yosupo.jp/problem/vertex_get_range_contour_add_on_tree) | Tree | 待逐题审题、适配与在线验证 | — |
| [Vertex Set Path Composite](https://judge.yosupo.jp/problem/vertex_set_path_composite) | Tree | 待逐题审题、适配与在线验证 | — |
| [Aho Corasick](https://judge.yosupo.jp/problem/aho_corasick) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |
| [Convolution ($\mathbb{F}_{2^{64}}$)](https://judge.yosupo.jp/problem/convolution_F_2_64) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |
| [Deque](https://judge.yosupo.jp/problem/deque) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |
| [Dirichlet Convolution and Prefix Sums](https://judge.yosupo.jp/problem/dirichlet_convolution_and_prefix_sums) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |
| [Dirichlet Inverse and Prefix Sums](https://judge.yosupo.jp/problem/dirichlet_inverse_and_prefix_sums) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |
| [Discrete Logarithm (Fixed Mod)](https://judge.yosupo.jp/problem/discrete_logarithm_fixed_mod) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |
| [Incremental Minimum Spanning Forest](https://judge.yosupo.jp/problem/incremental_minimum_spanning_forest) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |
| [Inv of Bivariate Formal Power Series](https://judge.yosupo.jp/problem/inv_of_formal_power_series_2d) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |
| [Log of Set Power Series](https://judge.yosupo.jp/problem/log_of_set_power_series) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |
| [Majority Voting](https://judge.yosupo.jp/problem/majority_voting) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |
| [Minimum Enclosing Circle](https://judge.yosupo.jp/problem/minimum_enclosing_circle) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |
| [Minimum Steiner Tree](https://judge.yosupo.jp/problem/minimum_steiner_tree) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |
| [Pfaffian of Matrix](https://judge.yosupo.jp/problem/pfaffian_of_matrix) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |
| [Prefix Sum of Polynomial](https://judge.yosupo.jp/problem/prefix_sum_of_polynomial) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |
| [Range Add Range Min](https://judge.yosupo.jp/problem/range_add_range_min) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |
| [Static Range Sum with Upper Bound](https://judge.yosupo.jp/problem/static_range_sum_with_upper_bound) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |
| [Sum of Multiplicative Function](https://judge.yosupo.jp/problem/sum_of_multiplicative_function) | Unlisted | 待逐题审题、适配与在线验证；尚未列入分类 | — |

机器清单： [library-checker-inventory.json](library-checker-inventory.json)，包含参数、测试生成数量、题面/校验器摘要及固定版本链接。

重建：`python3 tools/library_checker_inventory.py /path/to/clean/library-checker-problems`。更换上游版本时需审查增删；本工具不删除现有模板，也不自动迁移历史评测证据。
