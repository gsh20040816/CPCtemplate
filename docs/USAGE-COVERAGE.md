# 模板题使用示例覆盖

每个条目需要最简题意、所需模板和使用代码；代码只含必要配置与 main 调用部分，不重复算法。
示例与现有完整驱动共用源文件；模板依赖展开后的源码哈希改变时，原执行记录不再视为当前验证。示例执行通过不等于在线 AC。

locally_checked_example 表示至少有一份正式模板题用法；locally_checked_application 表示没有正式模板题、但有已验证的应用用法；locally_checked_api 表示只有已验证的接口演示。后两者均不计正式模板题覆盖。generated_unverified 表示执行证据缺失或源码指纹已失配。

| 模板 | 示例 | 状态 |
|---|---|---|
| dsu | [example-7](usage/example-7.cpp) | locally_checked_example |
| RollbackDSU | [example-84](usage/example-84.cpp) | locally_checked_example |
| Fenwick | [example-210](usage/example-210.cpp) | locally_checked_example |
| LazySeg | [example-220](usage/example-220.cpp) | locally_checked_example |
| XorBasis | [example-36](usage/example-36.cpp) | locally_checked_example |
| Dinic | [example-1](usage/example-1.cpp) | locally_checked_example |
| maximum_closure | [example-148（应用补充）](usage/example-148.cpp) | locally_checked_application |
| MinCostFlow | [example-55](usage/example-55.cpp) | locally_checked_example |
| SpfaFlow | [example-127](usage/example-127.cpp) | locally_checked_example |
| Dijkstra | [example-59](usage/example-59.cpp) | locally_checked_example |
| SCC | [example-161](usage/example-161.cpp) | locally_checked_example |
| TwoSAT | [example-3](usage/example-3.cpp), [example-128](usage/example-128.cpp) | locally_checked_example |
| BipartiteMatching | [example-35](usage/example-35.cpp) | locally_checked_example |
| Lowlink | [example-58](usage/example-58.cpp) | locally_checked_example |
| HLD | [example-44](usage/example-44.cpp), [example-231](usage/example-231.cpp) | locally_checked_example |
| prefix_function | [example-91](usage/example-91.cpp) | locally_checked_example |
| kmp_match | [example-91](usage/example-91.cpp) | locally_checked_example |
| z_function | [example-22](usage/example-22.cpp) | locally_checked_example |
| manacher | [example-23](usage/example-23.cpp), [example-129](usage/example-129.cpp) | locally_checked_example |
| minimum_rotation | [example-209](usage/example-209.cpp) | locally_checked_example |
| AhoCorasick | [example-70](usage/example-70.cpp) | locally_checked_example |
| SuffixArray | [example-19](usage/example-19.cpp), [example-131](usage/example-131.cpp) | locally_checked_example |
| SuffixAutomaton | [example-71](usage/example-71.cpp), [example-130](usage/example-130.cpp) | locally_checked_example |
| Mod64 | [example-234（接口演示）](usage/example-234.cpp) | locally_checked_api |
| Prime64 | [example-13](usage/example-13.cpp) | locally_checked_example |
| extended_gcd | [example-221](usage/example-221.cpp) | locally_checked_example |
| mod_inverse | [example-219（应用补充）](usage/example-219.cpp) | locally_checked_application |
| crt_merge | [example-15](usage/example-15.cpp) | locally_checked_example |
| floor_sum | [example-14](usage/example-14.cpp) | locally_checked_example |
| linear_equation | [example-75](usage/example-75.cpp) | locally_checked_example |
| linear_congruence | [example-207（应用补充）](usage/example-207.cpp) | locally_checked_application |
| segmented_primes | [example-208（应用补充）](usage/example-208.cpp) | locally_checked_application |
| batch_inverse | [example-197](usage/example-197.cpp) | locally_checked_example |
| inverse_table | [example-196](usage/example-196.cpp) | locally_checked_example |
| garner | [example-213](usage/example-213.cpp) | locally_checked_example |
| PollardRho | [example-43](usage/example-43.cpp) | locally_checked_example |
| LinearSieve | [example-218（应用补充）](usage/example-218.cpp) | locally_checked_application |
| ModInt | [example-216（应用补充）](usage/example-216.cpp) | locally_checked_application |
| Binomial | [example-216（应用补充）](usage/example-216.cpp) | locally_checked_application |
| PrimitiveRoot | [example-48](usage/example-48.cpp) | locally_checked_example |
| CoprimePairs | [example-195（应用补充）](usage/example-195.cpp) | locally_checked_application |
| floor_moments | [example-157](usage/example-157.cpp) | locally_checked_example |
| power_sum | [example-193（应用补充）](usage/example-193.cpp) | locally_checked_application |
| divisor_sum_power | [example-191](usage/example-191.cpp) | locally_checked_example |
| euler_phi | [example-106](usage/example-106.cpp) | locally_checked_example |
| carmichael | [example-192（应用补充）](usage/example-192.cpp) | locally_checked_application |
| Partitions | [example-158](usage/example-158.cpp), [example-159（应用补充）](usage/example-159.cpp) | locally_checked_example |
| Lucas | [example-40](usage/example-40.cpp) | locally_checked_example |
| ExLucas | [example-41](usage/example-41.cpp) | locally_checked_example |
| mod_sqrt | [example-42](usage/example-42.cpp) | locally_checked_example |
| KthResidue | [example-194](usage/example-194.cpp) | locally_checked_example |
| PrimePowerRoots | [example-194](usage/example-194.cpp) | locally_checked_example |
| root_factors | [example-194](usage/example-194.cpp) | locally_checked_example |
| CompositeRoots | [example-194](usage/example-194.cpp) | locally_checked_example |
| Lagrange | [example-17](usage/example-17.cpp) | locally_checked_example |
| ComplexFFT | [example-222](usage/example-222.cpp) | locally_checked_example |
| convolution_fft | [example-121](usage/example-121.cpp) | locally_checked_example |
| convolution_mod_fft | [example-122](usage/example-122.cpp) | locally_checked_example |
| NttConvolution | [example-16](usage/example-16.cpp) | locally_checked_example |
| stirling_second_row | [example-53](usage/example-53.cpp) | locally_checked_example |
| stirling_first_row | [example-54](usage/example-54.cpp) | locally_checked_example |
| FpsInverse | [example-18](usage/example-18.cpp) | locally_checked_example |
| FpsFunctions | [example-28](usage/example-28.cpp), [example-29](usage/example-29.cpp) | locally_checked_example |
| GaussMod | [example-24](usage/example-24.cpp) | locally_checked_example |
| det_prime | [example-25](usage/example-25.cpp) | locally_checked_example |
| ModMatrix | [example-26](usage/example-26.cpp) | locally_checked_example |
| matrix_inverse | [example-100](usage/example-100.cpp), [example-101](usage/example-101.cpp) | locally_checked_example |
| matrix_inverse_mod2 | [example-102](usage/example-102.cpp) | locally_checked_example |
| determinant_mod | [example-77](usage/example-77.cpp) | locally_checked_example |
| MatrixTree | [example-76](usage/example-76.cpp) | locally_checked_example |
| MatrixTreeMod | [example-187](usage/example-187.cpp), [example-188](usage/example-188.cpp) | locally_checked_example |
| DuJiao | [example-85](usage/example-85.cpp), [example-86](usage/example-86.cpp) | locally_checked_example |
| DiscreteLog | [example-47](usage/example-47.cpp) | locally_checked_example |
| IntegerPlane | [example-126](usage/example-126.cpp) | locally_checked_example |
| integer_hull | [example-64](usage/example-64.cpp), [example-123（应用补充）](usage/example-123.cpp) | locally_checked_example |
| polygon_area2 | [example-184](usage/example-184.cpp), [example-238（应用补充）](usage/example-238.cpp) | locally_checked_example |
| polygon_contains | [example-135](usage/example-135.cpp) | locally_checked_example |
| convex_contains_i64 | [example-136（应用补充）](usage/example-136.cpp) | locally_checked_application |
| convex_diameter2 | [example-65](usage/example-65.cpp), [example-124（应用补充）](usage/example-124.cpp) | locally_checked_example |
| RealPlane | [example-180](usage/example-180.cpp) | locally_checked_example |
| RealPolarLess | [example-228（接口演示）](usage/example-228.cpp) | locally_checked_api |
| line_projection | [example-181](usage/example-181.cpp) | locally_checked_example |
| segment_distance_real | [example-182](usage/example-182.cpp) | locally_checked_example |
| line_intersection_real | [example-183](usage/example-183.cpp) | locally_checked_example |
| line_circle_intersections | [example-229](usage/example-229.cpp) | locally_checked_example |
| circle_intersections | [example-230](usage/example-230.cpp) | locally_checked_example |
| circle_overlap_area | [example-154](usage/example-154.cpp) | locally_checked_example |
| MaxPlusMatrix | [example-223（应用补充）](usage/example-223.cpp) | locally_checked_application |
| LiChao | [example-89](usage/example-89.cpp) | locally_checked_example |
| PersistentKth | [example-37](usage/example-37.cpp) | locally_checked_example |
| TreePathKth | [example-38](usage/example-38.cpp) | locally_checked_example |
| DynamicKth | [example-63](usage/example-63.cpp) | locally_checked_example |
| PersistentDistinct | [example-46（应用补充）](usage/example-46.cpp) | locally_checked_application |
| Hungarian | [example-80](usage/example-80.cpp) | locally_checked_example |
| WeightedMatching | [example-73](usage/example-73.cpp) | locally_checked_example |
| Arborescence | [example-149](usage/example-149.cpp) | locally_checked_example |
| StoerWagner | [example-150](usage/example-150.cpp) | locally_checked_example |
| gomory_hu | [example-56](usage/example-56.cpp) | locally_checked_example |
| cut_tree_values | [example-56](usage/example-56.cpp) | locally_checked_example |
| BoundedCirculation | [example-185](usage/example-185.cpp) | locally_checked_example |
| IntegerHalfplanes | [example-125（应用补充）](usage/example-125.cpp) | locally_checked_application |
| CirclePolygon | [example-153](usage/example-153.cpp) | locally_checked_example |
| EnclosingCircle | [example-61](usage/example-61.cpp) | locally_checked_example |
| CircleTangents | [example-155](usage/example-155.cpp) | locally_checked_example |
| ClosestPair | [example-60](usage/example-60.cpp) | locally_checked_example |
| closest_pair_i64 | [example-62](usage/example-62.cpp), [example-134](usage/example-134.cpp) | locally_checked_example |
| minkowski_sum | [example-136（应用补充）](usage/example-136.cpp) | locally_checked_application |
| IntegerGeometry3D | [example-225（接口演示）](usage/example-225.cpp) | locally_checked_api |
| LinkCutTree | [example-45](usage/example-45.cpp) | locally_checked_example |
| TreePathProducts | [example-108（应用补充）](usage/example-108.cpp) | locally_checked_application |
| OrderedTreap | [example-8](usage/example-8.cpp) | locally_checked_example |
| PersistentOrderedTreap | [example-199](usage/example-199.cpp) | locally_checked_example |
| SequenceTreap | [example-10](usage/example-10.cpp), [example-109（应用补充）](usage/example-109.cpp) | locally_checked_example |
| OrderedSplay | [example-9](usage/example-9.cpp) | locally_checked_example |
| ScapegoatTree | [example-110](usage/example-110.cpp) | locally_checked_example |
| GcdSequenceTreap | [example-224（接口演示）](usage/example-224.cpp) | locally_checked_api |
| Blossom | [example-72](usage/example-72.cpp) | locally_checked_example |
| berlekamp_massey | [example-81](usage/example-81.cpp), [example-160](usage/example-160.cpp) | locally_checked_example |
| recurrence_nth | [example-160](usage/example-160.cpp) | locally_checked_example |
| TarjanSCC | [example-2](usage/example-2.cpp) | locally_checked_example |
| BiconnectedCore | [example-4](usage/example-4.cpp), [example-5](usage/example-5.cpp) | locally_checked_example |
| block_cut_forest | [example-165（应用补充）](usage/example-165.cpp) | locally_checked_application |
| bridge_component_forest | [example-166（应用补充）](usage/example-166.cpp) | locally_checked_application |
| PalindromicTree | [example-20](usage/example-20.cpp), [example-21（应用补充）](usage/example-21.cpp) | locally_checked_example |
| CentroidPairs | [example-137](usage/example-137.cpp) | locally_checked_example |
| CentroidSum | [example-201](usage/example-201.cpp) | locally_checked_example |
| SubtreeColors | [example-138（应用补充）](usage/example-138.cpp) | locally_checked_application |
| AffineSegTree | [example-12](usage/example-12.cpp) | locally_checked_example |
| SegmentBeats | [example-200](usage/example-200.cpp) | locally_checked_example |
| VirtualTree | [example-139（应用补充）](usage/example-139.cpp) | locally_checked_application |
| PersistentArray | [example-11](usage/example-11.cpp) | locally_checked_example |
| SupportHull | [example-226（接口演示）](usage/example-226.cpp) | locally_checked_api |
| SuffixLCP | [example-205（接口演示）](usage/example-205.cpp) | locally_checked_api |
| prefix_lcs | [example-205（接口演示）](usage/example-205.cpp) | locally_checked_api |
| square_counts | [example-186（应用补充）](usage/example-186.cpp) | locally_checked_application |
| PositionBasis | [example-39（应用补充）](usage/example-39.cpp) | locally_checked_application |
| basis_intersection | [example-178](usage/example-178.cpp) | locally_checked_example |
| basis_sum_intersection | [example-179](usage/example-179.cpp) | locally_checked_example |
| XorWalk | [example-176（应用补充）](usage/example-176.cpp) | locally_checked_application |
| removal_components | [example-162](usage/example-162.cpp), [example-163（应用补充）](usage/example-163.cpp) | locally_checked_example |
| EdgeCompression | [example-227（应用补充）](usage/example-227.cpp) | locally_checked_application |
| orient_edges | [example-164（应用补充）](usage/example-164.cpp) | locally_checked_application |
| bridge_augmentation | [example-167（应用补充）](usage/example-167.cpp) | locally_checked_application |
| OfflineLCA | [example-32](usage/example-32.cpp) | locally_checked_example |
| EulerLCA | [example-33](usage/example-33.cpp) | locally_checked_example |
| LiftingLCA | [example-34](usage/example-34.cpp) | locally_checked_example |
| path_intersection | [example-169（应用补充）](usage/example-169.cpp) | locally_checked_application |
| DirectedEuler | [example-57](usage/example-57.cpp) | locally_checked_example |
| UndirectedEuler | [example-177](usage/example-177.cpp) | locally_checked_example |
| word_chain | [example-217（应用补充）](usage/example-217.cpp) | locally_checked_application |
| mixed_euler_orientation | [example-206（接口演示）](usage/example-206.cpp) | locally_checked_api |
| mixed_euler_trail | [example-206（接口演示）](usage/example-206.cpp) | locally_checked_api |
| odd_cycle_vertices | [example-204（应用补充）](usage/example-204.cpp) | locally_checked_application |
| LexTwoSAT | [example-203（应用补充）](usage/example-203.cpp) | locally_checked_application |
| BostanMori | [example-49](usage/example-49.cpp) | locally_checked_example |
| SetConvolution | [example-27](usage/example-27.cpp) | locally_checked_example |
| subset_convolution | [example-51](usage/example-51.cpp) | locally_checked_example |
| polynomial_shift | [example-30](usage/example-30.cpp) | locally_checked_example |
| chirp_z | [example-31](usage/example-31.cpp) | locally_checked_example |
| PersistentRange | [example-174（应用补充）](usage/example-174.cpp), [example-175（应用补充）](usage/example-175.cpp) | locally_checked_application |
| TreeDiameter | [example-170（应用补充）](usage/example-170.cpp) | locally_checked_application |
| FunctionalGraph | [example-171](usage/example-171.cpp), [example-172](usage/example-172.cpp), [example-173（应用补充）](usage/example-173.cpp) | locally_checked_example |
| release_bfs | [example-215（应用补充）](usage/example-215.cpp) | locally_checked_application |
| ModifiedMo | [example-168](usage/example-168.cpp) | locally_checked_example |
| gp_map | [example-68](usage/example-68.cpp), [example-69](usage/example-69.cpp) | locally_checked_example |
| ost | [example-67](usage/example-67.cpp) | locally_checked_example |
| rp | [example-66](usage/example-66.cpp) | locally_checked_example |
| segtree | [example-78](usage/example-78.cpp) | locally_checked_example |
| lazy_segtree | [example-79](usage/example-79.cpp) | locally_checked_example |
| mint | [example-198](usage/example-198.cpp) | locally_checked_example |
| batch_units | [example-198](usage/example-198.cpp) | locally_checked_example |
| convolution_i64 | [example-52](usage/example-52.cpp) | locally_checked_example |
| pheap | [example-189](usage/example-189.cpp), [example-190](usage/example-190.cpp) | locally_checked_example |
| enumerate_triangles | [example-6](usage/example-6.cpp) | locally_checked_example |
| LeftistHeap | [example-50](usage/example-50.cpp) | locally_checked_example |
| Johnson | [example-74](usage/example-74.cpp) | locally_checked_example |
| DominatorTree | [example-82](usage/example-82.cpp), [example-83](usage/example-83.cpp) | locally_checked_example |
| SegmentLiChao | [example-87](usage/example-87.cpp), [example-88（应用补充）](usage/example-88.cpp) | locally_checked_example |
| GeneralSAM | [example-90](usage/example-90.cpp), [example-132](usage/example-132.cpp) | locally_checked_example |
| ac_shortest | [example-92（应用补充）](usage/example-92.cpp) | locally_checked_application |
| BoundedMaxFlow | [example-93（应用补充）](usage/example-93.cpp), [example-99（应用补充）](usage/example-99.cpp) | locally_checked_application |
| matching_edges | [example-95（应用补充）](usage/example-95.cpp) | locally_checked_application |
| mincut_edges | [example-94（应用补充）](usage/example-94.cpp) | locally_checked_application |
| odd_induced_partition | [example-96（应用补充）](usage/example-96.cpp) | locally_checked_application |
| unit_flow_edges | [example-97（应用补充）](usage/example-97.cpp), [example-133（应用补充）](usage/example-133.cpp) | locally_checked_application |
| NegativeCostFlow | [example-98](usage/example-98.cpp) | locally_checked_example |
| prime_count | [example-103](usage/example-103.cpp) | locally_checked_example |
| Min25 | [example-104](usage/example-104.cpp), [example-105](usage/example-105.cpp) | locally_checked_example |
| euler_power | [example-106](usage/example-106.cpp) | locally_checked_example |
| dag_path_determinant | [example-107（应用补充）](usage/example-107.cpp) | locally_checked_application |
| xor_hamming_pairs | [example-111](usage/example-111.cpp) | locally_checked_example |
| MonotoneStackSeg | [example-112（应用补充）](usage/example-112.cpp), [example-113（应用补充）](usage/example-113.cpp) | locally_checked_application |
| KDTreeSum | [example-114（应用补充）](usage/example-114.cpp) | locally_checked_application |
| cdq_convolution | [example-115](usage/example-115.cpp) | locally_checked_example |
| PolynomialDivision | [example-116](usage/example-116.cpp), [example-118](usage/example-118.cpp) | locally_checked_example |
| FpsSqrt | [example-117](usage/example-117.cpp), [example-119](usage/example-119.cpp) | locally_checked_example |
| FpsPower | [example-120](usage/example-120.cpp) | locally_checked_example |
| WaveletMatrix | [example-140](usage/example-140.cpp), [example-141](usage/example-141.cpp), [example-142](usage/example-142.cpp) | locally_checked_example |
| GaussXor | [example-143](usage/example-143.cpp), [example-145（应用补充）](usage/example-145.cpp) | locally_checked_example |
| SecondMST | [example-144（应用补充）](usage/example-144.cpp) | locally_checked_application |
| DivisionTree | [example-146](usage/example-146.cpp), [example-147](usage/example-147.cpp) | locally_checked_example |
| line_circle_i64 | [example-151](usage/example-151.cpp) | locally_checked_example |
| circle_intersections_i64 | [example-152](usage/example-152.cpp) | locally_checked_example |
| IntegerTangents | [example-156](usage/example-156.cpp) | locally_checked_example |
| rectangle_union_area | [example-202](usage/example-202.cpp) | locally_checked_example |
| MultipointEvaluation | [example-211](usage/example-211.cpp) | locally_checked_example |
| polynomial_interpolation | [example-212](usage/example-212.cpp) | locally_checked_example |
| AffineSequenceTreap | [example-214](usage/example-214.cpp) | locally_checked_example |
| PotentialDSU | [example-232](usage/example-232.cpp) | locally_checked_example |
| GaussReal | [example-233（接口演示）](usage/example-233.cpp) | locally_checked_api |
| AdaptiveSimpson | [example-235（接口演示）](usage/example-235.cpp) | locally_checked_api |
| ManhattanMST | [example-236](usage/example-236.cpp) | locally_checked_example |
| Dominance3D | [example-237](usage/example-237.cpp) | locally_checked_example |
| PersistentXorTrie | [example-239（应用补充）](usage/example-239.cpp) | locally_checked_application |
| convex_tangents_i64 | [example-240（接口演示）](usage/example-240.cpp), [example-242（应用补充）](usage/example-242.cpp) | locally_checked_application |
| SAIS | [example-241](usage/example-241.cpp) | locally_checked_example |
| ExactCover | [example-243](usage/example-243.cpp) | locally_checked_example |
| MinimumCover | [example-244（接口演示）](usage/example-244.cpp) | locally_checked_api |
| CentroidNearest | [example-245（应用补充）](usage/example-245.cpp) | locally_checked_application |
| Fenwick2D | [example-246](usage/example-246.cpp) | locally_checked_example |
| RectangleFenwick | [example-247](usage/example-247.cpp) | locally_checked_example |
| PersistentDSU | [example-248](usage/example-248.cpp) | locally_checked_example |
| MergeSplitTree | [example-249](usage/example-249.cpp) | locally_checked_example |
| exkmp | [example-250](usage/example-250.cpp) | locally_checked_example |
