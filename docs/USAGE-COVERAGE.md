# 模板题使用示例覆盖

每个条目需要最简题意、所需模板和使用代码；代码只含必要配置与 main 调用部分，不重复算法。
示例与现有完整驱动共用源文件；模板依赖展开后的源码哈希改变时，原执行记录不再视为当前验证。示例执行通过不等于在线 AC。

locally_checked_example 表示至少有一份正式模板题用法；locally_checked_application 表示没有正式模板题、但有已验证的应用用法；locally_checked_api 表示只有已验证的接口演示。后两者均不计正式模板题覆盖。generated_unverified 表示执行证据缺失或源码指纹已失配。

| 模板 | 示例 | 状态 |
|---|---|---|
| dsu | [example-7](usage/example-7.cpp) | generated_unverified |
| RollbackDSU | [example-84](usage/example-84.cpp) | generated_unverified |
| Fenwick | [example-210](usage/example-210.cpp) | generated_unverified |
| XorBasis | [example-36](usage/example-36.cpp) | generated_unverified |
| Dinic | [example-1](usage/example-1.cpp), [example-318（接口演示）](usage/example-318.cpp), [example-319（应用补充）](usage/example-319.cpp) | generated_unverified |
| maximum_closure | [example-148（应用补充）](usage/example-148.cpp) | generated_unverified |
| MinCostFlow | [example-55](usage/example-55.cpp) | generated_unverified |
| Dijkstra | [example-59](usage/example-59.cpp) | generated_unverified |
| SCC | [example-161](usage/example-161.cpp) | generated_unverified |
| TwoSAT | [example-3](usage/example-3.cpp), [example-128](usage/example-128.cpp) | generated_unverified |
| BipartiteMatching | [example-35](usage/example-35.cpp), [example-311（应用补充）](usage/example-311.cpp) | generated_unverified |
| HLD | [example-231](usage/example-231.cpp), [example-281（接口演示）](usage/example-281.cpp), [example-282（应用补充）](usage/example-282.cpp), [example-324（接口演示）](usage/example-324.cpp) | generated_unverified |
| prefix_function | [example-91](usage/example-91.cpp), [example-344（接口演示）](usage/example-344.cpp) | generated_unverified |
| kmp_match | [example-91](usage/example-91.cpp) | generated_unverified |
| z_function | [example-22](usage/example-22.cpp) | generated_unverified |
| manacher | [example-23](usage/example-23.cpp), [example-129](usage/example-129.cpp), [example-252（接口演示）](usage/example-252.cpp) | generated_unverified |
| minimum_rotation | [example-209](usage/example-209.cpp) | generated_unverified |
| AhoCorasick | [example-70](usage/example-70.cpp), [example-262](usage/example-262.cpp), [example-265（接口演示）](usage/example-265.cpp), [example-266（接口演示）](usage/example-266.cpp) | generated_unverified |
| SuffixArray | [example-19](usage/example-19.cpp), [example-131](usage/example-131.cpp) | generated_unverified |
| SuffixAutomaton | [example-71](usage/example-71.cpp), [example-130](usage/example-130.cpp), [example-325（接口演示）](usage/example-325.cpp) | generated_unverified |
| Mod64 | [example-234（接口演示）](usage/example-234.cpp) | generated_unverified |
| Prime64 | [example-13](usage/example-13.cpp) | generated_unverified |
| extended_gcd | [example-221](usage/example-221.cpp) | generated_unverified |
| mod_inverse | [example-219（应用补充）](usage/example-219.cpp) | generated_unverified |
| crt_merge | [example-15](usage/example-15.cpp) | generated_unverified |
| floor_sum | [example-14](usage/example-14.cpp) | locally_checked_example |
| linear_congruence | [example-207（应用补充）](usage/example-207.cpp) | generated_unverified |
| segmented_primes | [example-208（应用补充）](usage/example-208.cpp) | generated_unverified |
| batch_inverse | [example-197](usage/example-197.cpp) | generated_unverified |
| inverse_table | [example-196](usage/example-196.cpp) | generated_unverified |
| garner | [example-213](usage/example-213.cpp) | generated_unverified |
| PollardRho | [example-43](usage/example-43.cpp) | generated_unverified |
| LinearSieve | [example-218（应用补充）](usage/example-218.cpp) | generated_unverified |
| ModInt | [example-216（应用补充）](usage/example-216.cpp) | generated_unverified |
| Binomial | [example-216（应用补充）](usage/example-216.cpp) | generated_unverified |
| PrimitiveRoot | [example-48](usage/example-48.cpp) | generated_unverified |
| floor_moments | [example-157](usage/example-157.cpp) | generated_unverified |
| euler_phi | [example-106](usage/example-106.cpp) | generated_unverified |
| Partitions | [example-158](usage/example-158.cpp), [example-159（应用补充）](usage/example-159.cpp) | locally_checked_example |
| Lucas | [example-40](usage/example-40.cpp) | locally_checked_example |
| ExLucas | [example-41](usage/example-41.cpp) | locally_checked_example |
| mod_sqrt | [example-42](usage/example-42.cpp) | locally_checked_example |
| KthResidue | 待补 | pending_example |
| Lagrange | [example-17](usage/example-17.cpp) | locally_checked_example |
| ComplexFFT | [example-222](usage/example-222.cpp), [example-412（应用补充）](usage/example-412.cpp) | locally_checked_example |
| convolution_mod_fft | [example-122](usage/example-122.cpp) | locally_checked_example |
| NttConvolution | [example-16](usage/example-16.cpp), [example-455（接口演示）](usage/example-455.cpp) | generated_unverified |
| stirling_second_row | [example-53](usage/example-53.cpp) | generated_unverified |
| stirling_first_row | [example-54](usage/example-54.cpp) | generated_unverified |
| FpsInverse | [example-18](usage/example-18.cpp) | generated_unverified |
| FpsFunctions | [example-28](usage/example-28.cpp), [example-29](usage/example-29.cpp) | generated_unverified |
| GaussMod | [example-24](usage/example-24.cpp), [example-414（应用补充）](usage/example-414.cpp) | generated_unverified |
| ModMatrix | [example-26](usage/example-26.cpp) | generated_unverified |
| matrix_inverse | [example-100](usage/example-100.cpp), [example-101](usage/example-101.cpp) | generated_unverified |
| determinant_mod | [example-77](usage/example-77.cpp) | locally_checked_example |
| MatrixTreeMod | [example-187](usage/example-187.cpp), [example-188](usage/example-188.cpp) | locally_checked_example |
| DuJiao | [example-85](usage/example-85.cpp), [example-86](usage/example-86.cpp) | generated_unverified |
| DiscreteLog | [example-47](usage/example-47.cpp) | generated_unverified |
| IntegerPlane | [example-126](usage/example-126.cpp) | generated_unverified |
| integer_hull | [example-64](usage/example-64.cpp), [example-123（应用补充）](usage/example-123.cpp) | generated_unverified |
| polygon_area2 | [example-184](usage/example-184.cpp), [example-238（应用补充）](usage/example-238.cpp) | generated_unverified |
| polygon_contains | [example-135](usage/example-135.cpp) | generated_unverified |
| convex_contains_i64 | [example-136（应用补充）](usage/example-136.cpp) | generated_unverified |
| convex_diameter2 | [example-65](usage/example-65.cpp), [example-124（应用补充）](usage/example-124.cpp) | generated_unverified |
| RealPlane | [example-180](usage/example-180.cpp) | generated_unverified |
| RealPolarLess | [example-228（接口演示）](usage/example-228.cpp) | generated_unverified |
| line_projection | [example-181](usage/example-181.cpp) | generated_unverified |
| segment_distance_real | [example-182](usage/example-182.cpp) | generated_unverified |
| line_intersection_real | [example-183](usage/example-183.cpp) | generated_unverified |
| line_circle_intersections | [example-229](usage/example-229.cpp) | generated_unverified |
| circle_intersections | [example-230](usage/example-230.cpp) | generated_unverified |
| circle_overlap_area | [example-154](usage/example-154.cpp) | generated_unverified |
| MaxPlusMatrix | [example-223（应用补充）](usage/example-223.cpp) | locally_checked_application |
| LiChao | [example-89](usage/example-89.cpp) | locally_checked_example |
| PersistentKth | [example-37](usage/example-37.cpp) | locally_checked_example |
| DynamicKth | [example-63](usage/example-63.cpp) | locally_checked_example |
| Hungarian | [example-80](usage/example-80.cpp) | locally_checked_example |
| Arborescence | [example-149](usage/example-149.cpp) | locally_checked_example |
| StoerWagner | [example-150](usage/example-150.cpp) | locally_checked_example |
| gomory_hu | [example-56](usage/example-56.cpp) | generated_unverified |
| BoundedCirculation | [example-185](usage/example-185.cpp) | generated_unverified |
| IntegerHalfplanes | [example-125（应用补充）](usage/example-125.cpp) | locally_checked_application |
| CirclePolygon | [example-153](usage/example-153.cpp) | generated_unverified |
| EnclosingCircle | [example-61](usage/example-61.cpp) | generated_unverified |
| CircleTangents | [example-155](usage/example-155.cpp) | generated_unverified |
| ClosestPair | [example-60](usage/example-60.cpp) | locally_checked_example |
| minkowski_sum | [example-136（应用补充）](usage/example-136.cpp) | generated_unverified |
| IntegerGeometry3D | [example-225（接口演示）](usage/example-225.cpp) | generated_unverified |
| LinkCutTree | [example-45](usage/example-45.cpp) | locally_checked_example |
| OrderedTreap | [example-8](usage/example-8.cpp) | locally_checked_example |
| PersistentOrderedTreap | [example-199](usage/example-199.cpp) | locally_checked_example |
| SequenceTreap | [example-10](usage/example-10.cpp), [example-109（应用补充）](usage/example-109.cpp) | locally_checked_example |
| OrderedSplay | [example-9](usage/example-9.cpp) | locally_checked_example |
| Blossom | [example-72](usage/example-72.cpp) | locally_checked_example |
| berlekamp_massey | [example-81](usage/example-81.cpp), [example-160](usage/example-160.cpp) | locally_checked_example |
| recurrence_nth | [example-160](usage/example-160.cpp) | locally_checked_example |
| BiconnectedCore | [example-4](usage/example-4.cpp), [example-5](usage/example-5.cpp) | locally_checked_example |
| block_cut_forest | [example-165（应用补充）](usage/example-165.cpp) | locally_checked_application |
| bridge_component_forest | [example-166（应用补充）](usage/example-166.cpp) | locally_checked_application |
| PalindromicTree | [example-20](usage/example-20.cpp), [example-21（应用补充）](usage/example-21.cpp) | locally_checked_example |
| CentroidPairs | [example-137](usage/example-137.cpp) | locally_checked_example |
| CentroidSum | [example-201](usage/example-201.cpp) | generated_unverified |
| SubtreeColors | [example-138（应用补充）](usage/example-138.cpp) | locally_checked_application |
| SegmentBeats | [example-200](usage/example-200.cpp) | locally_checked_example |
| VirtualTree | [example-139（应用补充）](usage/example-139.cpp) | locally_checked_application |
| SuffixLCP | [example-343（接口演示）](usage/example-343.cpp) | generated_unverified |
| PositionBasis | [example-39（应用补充）](usage/example-39.cpp) | locally_checked_application |
| basis_intersection | [example-178](usage/example-178.cpp) | generated_unverified |
| basis_sum_intersection | [example-179](usage/example-179.cpp) | generated_unverified |
| LiftingLCA | [example-34](usage/example-34.cpp), [example-283（应用补充）](usage/example-283.cpp) | locally_checked_example |
| path_intersection | 待补 | pending_example |
| DirectedEuler | [example-57](usage/example-57.cpp) | locally_checked_example |
| UndirectedEuler | [example-177](usage/example-177.cpp) | locally_checked_example |
| mixed_euler_orientation | [example-206（接口演示）](usage/example-206.cpp) | generated_unverified |
| mixed_euler_trail | [example-206（接口演示）](usage/example-206.cpp) | generated_unverified |
| BostanMori | [example-49](usage/example-49.cpp) | generated_unverified |
| SetConvolution | [example-27](usage/example-27.cpp) | generated_unverified |
| subset_convolution | [example-51](usage/example-51.cpp) | generated_unverified |
| polynomial_shift | [example-30](usage/example-30.cpp) | generated_unverified |
| chirp_z | [example-31](usage/example-31.cpp) | generated_unverified |
| PersistentRange | [example-174（应用补充）](usage/example-174.cpp), [example-175（应用补充）](usage/example-175.cpp) | locally_checked_application |
| TreeDiameter | [example-170（应用补充）](usage/example-170.cpp) | generated_unverified |
| FunctionalGraph | [example-171](usage/example-171.cpp), [example-172](usage/example-172.cpp), [example-173（应用补充）](usage/example-173.cpp) | locally_checked_example |
| ModifiedMo | [example-168](usage/example-168.cpp) | generated_unverified |
| gp_map | [example-68](usage/example-68.cpp), [example-69](usage/example-69.cpp) | generated_unverified |
| ost | [example-67](usage/example-67.cpp) | generated_unverified |
| rp | [example-66](usage/example-66.cpp) | generated_unverified |
| segtree | [example-78](usage/example-78.cpp) | locally_checked_example |
| lazy_segtree | [example-79](usage/example-79.cpp) | locally_checked_example |
| mint | [example-198](usage/example-198.cpp) | generated_unverified |
| pheap | [example-189](usage/example-189.cpp), [example-190](usage/example-190.cpp) | generated_unverified |
| enumerate_triangles | [example-6](usage/example-6.cpp) | locally_checked_example |
| LeftistHeap | [example-50](usage/example-50.cpp) | generated_unverified |
| DominatorTree | [example-82](usage/example-82.cpp), [example-83](usage/example-83.cpp) | locally_checked_example |
| SegmentLiChao | [example-87](usage/example-87.cpp), [example-88（应用补充）](usage/example-88.cpp) | locally_checked_example |
| GeneralSAM | [example-90](usage/example-90.cpp), [example-132](usage/example-132.cpp), [example-257（接口演示）](usage/example-257.cpp), [example-261（应用补充）](usage/example-261.cpp) | locally_checked_example |
| BoundedMaxFlow | [example-93（应用补充）](usage/example-93.cpp), [example-99（应用补充）](usage/example-99.cpp) | generated_unverified |
| matching_edges | [example-95（应用补充）](usage/example-95.cpp) | generated_unverified |
| mincut_edges | [example-94（应用补充）](usage/example-94.cpp) | generated_unverified |
| Min25 | [example-104](usage/example-104.cpp), [example-105](usage/example-105.cpp) | generated_unverified |
| euler_power | [example-106](usage/example-106.cpp) | generated_unverified |
| dag_path_determinant | [example-107（应用补充）](usage/example-107.cpp) | generated_unverified |
| xor_hamming_pairs | [example-111](usage/example-111.cpp) | locally_checked_example |
| MonotoneStackSeg | [example-112（应用补充）](usage/example-112.cpp), [example-113（应用补充）](usage/example-113.cpp) | locally_checked_application |
| KDTreeSum | [example-114（应用补充）](usage/example-114.cpp), [example-269（接口演示）](usage/example-269.cpp) | locally_checked_application |
| cdq_convolution | [example-115](usage/example-115.cpp) | generated_unverified |
| PolynomialDivision | [example-116](usage/example-116.cpp), [example-118](usage/example-118.cpp) | generated_unverified |
| FpsSqrt | [example-117](usage/example-117.cpp), [example-119](usage/example-119.cpp), [example-450（接口演示）](usage/example-450.cpp) | generated_unverified |
| FpsPower | [example-120](usage/example-120.cpp) | generated_unverified |
| GaussXor | [example-143](usage/example-143.cpp), [example-145（应用补充）](usage/example-145.cpp) | locally_checked_example |
| SecondMST | [example-144（应用补充）](usage/example-144.cpp) | generated_unverified |
| line_circle_i64 | [example-151](usage/example-151.cpp) | generated_unverified |
| circle_intersections_i64 | [example-152](usage/example-152.cpp) | generated_unverified |
| rectangle_union_area | [example-202](usage/example-202.cpp) | locally_checked_example |
| MultipointEvaluation | [example-211](usage/example-211.cpp) | generated_unverified |
| polynomial_interpolation | [example-212](usage/example-212.cpp) | generated_unverified |
| PotentialDSU | [example-232](usage/example-232.cpp) | generated_unverified |
| GaussReal | [example-233（接口演示）](usage/example-233.cpp) | locally_checked_api |
| AdaptiveSimpson | [example-235（接口演示）](usage/example-235.cpp) | locally_checked_api |
| ManhattanMST | [example-236](usage/example-236.cpp) | generated_unverified |
| Dominance3D | [example-237](usage/example-237.cpp) | generated_unverified |
| PersistentXorTrie | [example-239（应用补充）](usage/example-239.cpp) | locally_checked_application |
| convex_tangents_i64 | [example-240（接口演示）](usage/example-240.cpp), [example-242（应用补充）](usage/example-242.cpp) | generated_unverified |
| SAIS | [example-241](usage/example-241.cpp) | locally_checked_example |
| ExactCover | [example-243](usage/example-243.cpp) | locally_checked_example |
| MinimumCover | [example-244（接口演示）](usage/example-244.cpp) | locally_checked_api |
| offline_rectangle_sum | [example-436](usage/example-436.cpp) | generated_unverified |
| RectangleFenwick | [example-247](usage/example-247.cpp) | locally_checked_example |
| PersistentDSU | [example-248](usage/example-248.cpp) | locally_checked_example |
| MergeSplitTree | [example-249](usage/example-249.cpp), [example-289（应用补充）](usage/example-289.cpp), [example-438（接口演示）](usage/example-438.cpp) | generated_unverified |
| exkmp | [example-250](usage/example-250.cpp) | generated_unverified |
| SAMLex | [example-253（应用补充）](usage/example-253.cpp), [example-255（接口演示）](usage/example-255.cpp) | generated_unverified |
| sam_lcs | [example-254（应用补充）](usage/example-254.cpp), [example-255（接口演示）](usage/example-255.cpp) | generated_unverified |
| SAMDocuments | [example-259（应用补充）](usage/example-259.cpp), [example-260（接口演示）](usage/example-260.cpp) | generated_unverified |
| KDNearest | [example-267（接口演示）](usage/example-267.cpp), [example-268（应用补充）](usage/example-268.cpp) | locally_checked_application |
| BellmanFord | [example-293](usage/example-293.cpp), [example-294（应用补充）](usage/example-294.cpp), [example-295（接口演示）](usage/example-295.cpp) | generated_unverified |
| Spfa | [example-296](usage/example-296.cpp), [example-297](usage/example-297.cpp), [example-298（应用补充）](usage/example-298.cpp), [example-299（接口演示）](usage/example-299.cpp) | generated_unverified |
| Floyd | [example-304](usage/example-304.cpp), [example-305（应用补充）](usage/example-305.cpp), [example-306（接口演示）](usage/example-306.cpp) | generated_unverified |
| independent_set | [example-309（应用补充）](usage/example-309.cpp), [example-310（接口演示）](usage/example-310.cpp) | generated_unverified |
| Kruskal | [example-314](usage/example-314.cpp), [example-315（接口演示）](usage/example-315.cpp) | generated_unverified |
| Prim | [example-316](usage/example-316.cpp), [example-317（接口演示）](usage/example-317.cpp) | generated_unverified |
| RealSpace | [example-348（接口演示）](usage/example-348.cpp) | generated_unverified |
| Line3 | [example-349（接口演示）](usage/example-349.cpp) | generated_unverified |
| Plane3 | [example-350（接口演示）](usage/example-350.cpp), [example-351（接口演示）](usage/example-351.cpp) | generated_unverified |
| TimeConnectivity | [example-352（应用补充）](usage/example-352.cpp), [example-353（接口演示）](usage/example-353.cpp), [example-393](usage/example-393.cpp) | generated_unverified |
| TreeMo | [example-354（应用补充）](usage/example-354.cpp) | generated_unverified |
| RollbackMo | [example-355](usage/example-355.cpp) | generated_unverified |
| OverallKth | [example-356（应用补充）](usage/example-356.cpp) | generated_unverified |
| TreeIsomorphism | [example-357](usage/example-357.cpp) | locally_checked_example |
| StrictSecondShortest | [example-358（应用补充）](usage/example-358.cpp) | locally_checked_application |
| KShortestWalks | [example-359（应用补充）](usage/example-359.cpp) | locally_checked_application |
| MonotoneHull | [example-360（应用补充）](usage/example-360.cpp) | locally_checked_application |
| monotone_dp_layer | [example-361（应用补充）](usage/example-361.cpp), [example-363（应用补充）](usage/example-363.cpp) | locally_checked_application |
| wqs_independent_set | [example-362（应用补充）](usage/example-362.cpp) | locally_checked_application |
| BurnsideAverage | [example-365（应用补充）](usage/example-365.cpp) | locally_checked_application |
| permutation_cycles | [example-367（接口演示）](usage/example-367.cpp) | locally_checked_api |
| necklace_colorings | [example-364](usage/example-364.cpp), [example-366（接口演示）](usage/example-366.cpp) | locally_checked_example |
| StringHash | [example-368](usage/example-368.cpp), [example-369（接口演示）](usage/example-369.cpp) | locally_checked_example |
| KruskalTree | [example-370（应用补充）](usage/example-370.cpp), [example-371（接口演示）](usage/example-371.cpp) | generated_unverified |
| lyndon | [example-372](usage/example-372.cpp), [example-373（接口演示）](usage/example-373.cpp) | locally_checked_example |
| MinCycle | [example-374](usage/example-374.cpp), [example-375（接口演示）](usage/example-375.cpp) | locally_checked_example |
| LongChain | [example-376](usage/example-376.cpp), [example-377（接口演示）](usage/example-377.cpp) | locally_checked_example |
| count_four_cycles | [example-378](usage/example-378.cpp), [example-379（接口演示）](usage/example-379.cpp) | locally_checked_example |
| minimum_mean_cycle | [example-380](usage/example-380.cpp), [example-381（接口演示）](usage/example-381.cpp) | locally_checked_example |
| Cactus | [example-382](usage/example-382.cpp) | locally_checked_example |
| HLPP | [example-383](usage/example-383.cpp), [example-384（接口演示）](usage/example-384.cpp) | locally_checked_example |
| DynamicDiameter | [example-388](usage/example-388.cpp) | locally_checked_example |
| regular_matching | [example-389](usage/example-389.cpp) | locally_checked_example |
| tutte | [example-390](usage/example-390.cpp) | locally_checked_example |
| SteinerTree | [example-391](usage/example-391.cpp) | locally_checked_example |
| CartesianTree | [example-392](usage/example-392.cpp) | locally_checked_example |
| Mo | [example-394](usage/example-394.cpp), [example-415（应用补充）](usage/example-415.cpp) | generated_unverified |
| grid_cycle | [example-396](usage/example-396.cpp) | locally_checked_example |
| Simplex | [example-397](usage/example-397.cpp) | locally_checked_example |
| circle_union_area | [example-398](usage/example-398.cpp), [example-403](usage/example-403.cpp) | generated_unverified |
| polygon_union_area | [example-399](usage/example-399.cpp) | generated_unverified |
| Hull3D | [example-400](usage/example-400.cpp) | locally_checked_example |
| WeightedBlossom | [example-401](usage/example-401.cpp), [example-402（接口演示）](usage/example-402.cpp) | locally_checked_example |
| grid_cycles | [example-404（应用补充）](usage/example-404.cpp), [example-405（接口演示）](usage/example-405.cpp) | generated_unverified |
| manhattan_order | [example-416（应用补充）](usage/example-416.cpp) | generated_unverified |
| minimum_rectangle | [example-418](usage/example-418.cpp) | generated_unverified |
| convex_cut | [example-419](usage/example-419.cpp) | generated_unverified |
| polygon_centroid | [example-420（接口演示）](usage/example-420.cpp) | generated_unverified |
| triangle_incircle | [example-426](usage/example-426.cpp) | generated_unverified |
| BigInteger | [example-421](usage/example-421.cpp), [example-422](usage/example-422.cpp), [example-423](usage/example-423.cpp), [example-424（接口演示）](usage/example-424.cpp), [example-425（接口演示）](usage/example-425.cpp) | locally_checked_example |
| convolution_i64 | [example-52](usage/example-52.cpp) | generated_unverified |
| NegativeCostFlow | [example-98](usage/example-98.cpp) | generated_unverified |
| CentroidDiameter | [example-284（应用补充）](usage/example-284.cpp), [example-285（接口演示）](usage/example-285.cpp) | locally_checked_application |
| circle_coverage_area | [example-417](usage/example-417.cpp) | generated_unverified |
