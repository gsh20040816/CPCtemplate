# 已核对的模板题入口

本表记录已核对的题面或来源模型与适配约定；原题面不可访问的记录明确标注，不能视为题面核验完成。AC、接口覆盖与速度榜分别记录；空白项不表示完成。完整候选和上游缺项见 [候选清单](template-problems.json)，执行依据为 [issue #1](ISSUE-1.md)。

| 算法 | 模板题 | 边界 | 当前 AC | 速度榜 |
|---|---|---|---|---|
| `ModifiedMo` | [Luogu P1903](https://www.luogu.com.cn/problem/P1903) | n,m<=133333; colors<=1000000 | [记录](https://www.luogu.com.cn/record/297653743) | 待核验 |
| `TarjanSCC` | [QOJ 906](https://qoj.ac/problem/906) | 1<=N,M<=500000; directed multigraph; 0-based vertices | [记录](https://qoj.ac/submission/2940638) | 94 out of 143（CCF_NOI 当前可见的满分提交，按用时并列） |
| `berlekamp_massey` | [QOJ 547](https://qoj.ac/problem/547) | 0<=n<=10000; modulus 998244353 | 待编写驱动/提交 | 待核验 |
| `prefix_function` | [QOJ 464](https://qoj.ac/problem/464) | 1<=\|S\|<=2000000; lowercase; 0.5s | 待编写驱动/提交 | 待核验 |
| `z_function` | [QOJ 786](https://qoj.ac/problem/786) | 1<=\|S\|<=2000000; lowercase; 0.5s | 待编写驱动/提交 | 待核验 |
| `manacher` | [QOJ 787](https://qoj.ac/problem/787) | \|S\|<=1000000; 1s | 待编写驱动/提交 | 待核验 |
| `TwoSAT` | [QOJ 997](https://qoj.ac/problem/997) | 1<=n<=100000; 1<=m<=500000; 1-based variables | 待编写驱动/提交 | 待核验 |
| `NttConvolution::multiply` | [QOJ 618](https://qoj.ac/problem/618) | degrees n,m in [1,1000000]; modulus 998244353; 1s | 待编写驱动/提交 | 待核验 |
| `Polynomial::multiply` | [QOJ 618](https://qoj.ac/problem/618) | degrees n,m<=1000000; modulus 998244353; 1s | 待编写驱动/提交 | 待核验 |
| `Polynomial::inverse` | [QOJ 619](https://qoj.ac/problem/619) | 1<=n<=1000000; modulus 998244353; a[0]!=0; 1.5s | 待编写驱动/提交 | 待核验 |
| `Polynomial::log` | [QOJ 620](https://qoj.ac/problem/620) | 1<=n<=1000000; modulus 998244353; a[0]=1; 1.5s | 待编写驱动/提交 | 待核验 |
| `Polynomial::exp` | [QOJ 621](https://qoj.ac/problem/621) | 1<=n<=1000000; modulus 998244353; a[0]=0; 2.5s | 待编写驱动/提交 | 待核验 |
| `GeneralMultipointEvaluation` | [QOJ 622](https://qoj.ac/problem/622) | 1<=n,m<=1000000; output mod 998244353; 10s | 待实现 | 待核验 |
| `SuffixArray::sa` | [QOJ 956](https://qoj.ac/problem/956) | 1<=n<=1000000; ASCII letters/digits; 3s; 128MB | 待编写驱动/提交 | 待核验 |
| `PalindromicTree::add/occurrences` | [QOJ 801](https://qoj.ac/problem/801) | lowercase string length<=1000000; 1s; 2048MB | 待编写驱动/提交 | 待核验 |
| `SuffixAutomaton::extend/counts` | [Luogu P3804](https://www.luogu.com.cn/problem/P3804) | 1<=\|S\|<=1000000; lowercase | 待编写驱动/提交 | 待核验 |
| `OrderedTreap` | [Luogu P3369](https://www.luogu.com.cn/problem/P3369) | 1<=operations<=100000; \|x\|<=10000000 | [记录](https://www.luogu.com.cn/record/297515150) | 待核验 |
| `OrderedSplay` | [Luogu P3369](https://www.luogu.com.cn/problem/P3369) | 1<=operations<=100000; \|x\|<=10000000 | [记录](https://www.luogu.com.cn/record/297520192) | 待核验 |
| `SequenceTreap` | [Luogu P3391](https://www.luogu.com.cn/problem/P3391) | 1<=n,m<=100000; 1<=l<=r<=n | [记录](https://www.luogu.com.cn/record/297520211) | 待核验 |
| `ost` | [Luogu P3369](https://www.luogu.com.cn/problem/P3369) | operations<=100000; \|x\|<=10000000 | 待编写驱动/提交 | 待核验 |
| `ost` | [Luogu P6136](https://www.luogu.com.cn/problem/P6136) | n<=100000; m<=1000000; values<2^30 | [记录](https://www.luogu.com.cn/record/297800993) | 待核验 |
| `gp_map` | [Library Checker associative_array](https://judge.yosupo.jp/problem/associative_array) | Q<=1000000; 0<=key,value<=10^18; 5s | [记录](https://judge.yosupo.jp/submission/401867) | 956 out of 7334（All AC submissions, all users including anonymous, all languages, Dedup user unchecked. Not all verdicts and not per-user best.） |
| `rp` | [Library Checker persistent_queue](https://judge.yosupo.jp/problem/persistent_queue) | Q<=500000; -1<=t_i<i; 0<=x<=10^9; 5s | [记录](https://judge.yosupo.jp/submission/401871) | 待核验 |
| `dsu` | [Luogu P3367](https://www.luogu.com.cn/problem/P3367) | N<=200000; M<=1000000; 1-based task vertices | [记录](https://www.luogu.com.cn/record/297668102) | 待核验 |
| `Lowlink::add/run/bridge` | [QOJ 995](https://qoj.ac/problem/995) | n<=100000; m<=500000; 1s; 1-based | 待编写驱动/提交 | 待核验 |
| `Lowlink::add/run/cut` | [QOJ 996](https://qoj.ac/problem/996) | n<=20000; m<=100000; 0.5s; 1-based | 待编写驱动/提交 | 待核验 |
| `Dinic::add/flow` | [Luogu P3376](https://www.luogu.com.cn/problem/P3376) | n<=200; m<=5000; 0<=capacity<2^31 | [记录](https://www.luogu.com.cn/record/297501480) | 待核验 |
| `MinCostFlow::slope` | [Luogu P3381](https://www.luogu.com.cn/problem/P3381) | n<=5000; m<=50000; capacity,cost<=1000; result<=2^31-1 | 待编写驱动/提交 | 待核验 |
| `Biconnected::add/run/blocks` | [Luogu P8435](https://www.luogu.com.cn/problem/P8435) | n<=500000; m<=2000000 | [记录](https://www.luogu.com.cn/record/297517446) | 待核验 |
| `Biconnected::add/run/bel` | [Luogu P8436](https://www.luogu.com.cn/problem/P8436) | n<=500000; m<=2000000; multigraph | [记录](https://www.luogu.com.cn/record/297519028) | 待核验 |
| `BipartiteMatching::add/solve` | [Luogu P3386](https://www.luogu.com.cn/problem/P3386) | 1<=n,m<=500; edges<=50000; parallel edges allowed | 待编写驱动/提交 | 待核验 |
| `WeightedMatching::add/solve/r` | [Luogu P6577](https://www.luogu.com.cn/problem/P6577) | n<=500; m<=n^2; -19980731<=weight<=19980731 | [记录](https://www.luogu.com.cn/record/297520123) | 待核验 |
| `OfflineLCA::add/add_query/run/answer` | [Luogu P3379](https://www.luogu.com.cn/problem/P3379) | N,M<=500000; root S; queries may have equal endpoints | [记录](https://www.luogu.com.cn/record/297521009) | 待核验 |
| `EulerLCA::add/build/lca` | [Luogu P3379](https://www.luogu.com.cn/problem/P3379) | N,M<=500000; root S | 待编写驱动/提交 | 待核验 |
| `LiftingLCA::add/build/lca` | [Luogu P3379](https://www.luogu.com.cn/problem/P3379) | N,M<=500000; root S | 待编写驱动/提交 | 待核验 |
| `HLD::add/build/lca` | [Luogu P3379](https://www.luogu.com.cn/problem/P3379) | N,M<=500000; root S | 待编写驱动/提交 | 待核验 |
| `HLD + AffineSegTree` | [Luogu P3384](https://www.luogu.com.cn/problem/P3384) | n,m<=100000; 1<=P<=2^30; int inputs | [记录](https://www.luogu.com.cn/record/297520172) | 待核验 |
| `CentroidPairs::add/build/count_exact` | [Luogu P3806](https://www.luogu.com.cn/problem/P3806) | n<=10000; m<=100; 1<=k<=10^7; 1<=edge_weight<=10000 | [记录](https://www.luogu.com.cn/record/297519137) | 待核验 |
| `PersistentKth::kth` | [Luogu P3834](https://www.luogu.com.cn/problem/P3834) | n,m<=200000; 0<=a[i]<=10^9; valid l,r,k | [记录](https://www.luogu.com.cn/record/297520290) | 待核验 |
| `ost` | [Library Checker ordered_set](https://judge.yosupo.jp/problem/ordered_set) | 0<=N<=500000; 1<=Q<=500000; sorted distinct initial keys; 0<=keys<=10^9; kth query x>=1 | [记录](https://judge.yosupo.jp/submission/401869) | 628 out of 1095（All AC submissions, all users and languages, Dedup user unchecked. Not non-AC verdicts or per-user best.） |
| `segtree` | [Library Checker point_set_range_composite](https://judge.yosupo.jp/problem/point_set_range_composite) | N,Q<=500000; 0<=l<r<=N; coefficients mod998244353 with nonzero slopes | [记录](https://judge.yosupo.jp/submission/402090) | 454 out of 2914（All AC submissions, all users/languages, dedup disabled; excludes non-AC verdicts.） |
| `segtree` | [Library Checker predecessor_problem](https://judge.yosupo.jp/problem/predecessor_problem) | 1<=N<=10000000;1<=Q<=1000000;0<=k<N;initial binary membership string | [记录](https://judge.yosupo.jp/submission/402089) | 687 out of 2582（All users and languages, AC only, user dedup disabled; not all verdicts.） |
| `lazy_segtree` | [Library Checker range_affine_range_sum](https://judge.yosupo.jp/problem/range_affine_range_sum) | N,Q<=500000; coefficients modulo998244353; nonzero multipliers;0<=l<r<=N | 待编写驱动/提交 | 待核验 |
| `mint` | [Luogu P5431](https://www.luogu.com.cn/problem/P5431) | n<=5000000;2<=k<p<=10^9;prime p;1<=a_i<p | 待编写驱动/提交 | 待核验 |
| `convolution_i64` | [Luogu P3803](https://www.luogu.com.cn/problem/P3803) | Degrees n,m<=1000000; coefficients 0..9; exact integer output. | 待编写驱动/提交 | 待核验 |
| `TarjanSCC` | [Library Checker Strongly Connected Components](https://judge.yosupo.jp/problem/scc) | 1<=N,M<=500000; vertices 0..N-1; loops and parallel edges allowed. | 待编写驱动/提交 | 待核验 |
| `TwoSAT` | [Library Checker 2 Sat](https://judge.yosupo.jp/problem/two_sat) | 1<=N,M<=500000; signed DIMACS literals in +/-1..N. | 待编写驱动/提交 | 待核验 |
| `NttConvolution` | [Library Checker convolution_mod](https://judge.yosupo.jp/problem/convolution_mod) | 1<=N,M<=524288; coefficients in [0,998244353). | 待编写驱动/提交 | 待核验 |
| `SetConvolution` | [Library Checker bitwise_and_convolution](https://judge.yosupo.jp/problem/bitwise_and_convolution) | Exponent 0<=N<=20; each array has 2^N residues modulo998244353. | 待编写驱动/提交 | 待核验 |
| `SetConvolution` | [Library Checker bitwise_xor_convolution](https://judge.yosupo.jp/problem/bitwise_xor_convolution) | Exponent 0<=N<=20; each array has 2^N residues modulo998244353. | 待编写驱动/提交 | 待核验 |
| `GaussMod` | [Library Checker system_of_linear_equations](https://judge.yosupo.jp/problem/system_of_linear_equations) | 1<=N,M<=500; all arithmetic in F_998244353. | 待编写驱动/提交 | 待核验 |
| `det_prime` | [Library Checker matrix_det](https://judge.yosupo.jp/problem/matrix_det) | 1<=N<=500; square matrix with residues modulo998244353. | 待编写驱动/提交 | 待核验 |
| `ModMatrix` | [Library Checker matrix_product](https://judge.yosupo.jp/problem/matrix_product) | 1<=N,M,K<=1024; N*M times M*K matrices over modulo998244353. | 待编写驱动/提交 | 待核验 |
| `FpsInverse` | [Library Checker inv_of_formal_power_series](https://judge.yosupo.jp/problem/inv_of_formal_power_series) | 1<=N<=500000; coefficients modulo998244353; a0 nonzero. | 待编写驱动/提交 | 待核验 |
| `FpsFunctions` | [Library Checker log_of_formal_power_series](https://judge.yosupo.jp/problem/log_of_formal_power_series) | 1<=N<=500000; coefficients modulo998244353; a0=1. | 待编写驱动/提交 | 待核验 |
| `FpsFunctions` | [Library Checker exp_of_formal_power_series](https://judge.yosupo.jp/problem/exp_of_formal_power_series) | 1<=N<=500000; coefficients modulo998244353; a0=0. | 待编写驱动/提交 | 待核验 |
| `gp_map` | [Library Checker associative_array (cc_hash_table variant)](https://judge.yosupo.jp/problem/associative_array) | Q<=1000000; key/value in [0,10^18]. | 待编写驱动/提交 | 待核验 |
| `Prime64` | [Library Checker primality_test](https://judge.yosupo.jp/problem/primality_test) | 1<=Q<=100000;1<=N<=10^18. | 待编写驱动/提交 | 待核验 |
| `floor_sum` | [Library Checker sum_of_floor_of_linear](https://judge.yosupo.jp/problem/sum_of_floor_of_linear) | 1<=T<=100000;1<=N,M<=10^9;0<=A,B<M. | 待编写驱动/提交 | 待核验 |
| `pheap` | [Library Checker Shortest Path](https://judge.yosupo.jp/problem/shortest_path) | 2<=N<=500000; 1<=M<=500000; simple directed graph; 0<=w<=1e9; s!=t | 待编写驱动/提交 | 待核验 |
| `enumerate_triangles` | [Library Checker enumerate_triangles](https://judge.yosupo.jp/problem/enumerate_triangles) | 1<=N,M<=100000; undirected simple graph; 0<=x<998244353 | 待编写驱动/提交 | 待核验 |
| `z_function` | [Library Checker zalgorithm](https://judge.yosupo.jp/problem/zalgorithm) | 1<=N<=500000；非空小写字母串。 | 待编写驱动/提交 | 待核验 |
| `manacher` | [Library Checker enumerate_palindromes](https://judge.yosupo.jp/problem/enumerate_palindromes) | 1<=N<=500000；非空小写字母串。 | 待编写驱动/提交 | 待核验 |
| `matrix_inverse` | [Library Checker inverse_matrix](https://judge.yosupo.jp/problem/inverse_matrix) | 1<=N<=500, entries modulo998244353. | 待编写驱动/提交 | 待核验 |
| `matrix_inverse_mod2` | [Library Checker inverse_matrix_mod_2](https://judge.yosupo.jp/problem/inverse_matrix_mod_2) | 1<=N<=4096, each row is a length-N binary string. | 待编写驱动/提交 | 待核验 |
| `prime_count` | [Library Checker counting_primes](https://judge.yosupo.jp/problem/counting_primes) | 1<=N<=10^11; local extension also accepts N=0. | 待编写驱动/提交 | 待核验 |
| `Min25` | [Library Checker sum_of_multiplicative_function](https://judge.yosupo.jp/problem/sum_of_multiplicative_function) | N<=10^11; T<=10000, T>1 implies T sqrt(N)<=100000; modulus469762049 | 待编写驱动/提交 | 待核验 |
| `euler_power` | [Luogu P5091](https://www.luogu.com.cn/problem/P5091) | 1<=a<=1e9, 1<=m<=1e8, 1<=b<=10^20000000; input a,m,b. | 待编写驱动/提交 | 待核验 |
| `euler_phi` | [Luogu P5091](https://www.luogu.com.cn/problem/P5091) | 1<=a<=1e9, 1<=m<=1e8, 1<=b<=10^20000000; input a,m,b. | 待编写驱动/提交 | 待核验 |
| `ScapegoatTree` | [Luogu P3369](https://www.luogu.com.cn/problem/P3369) | 1<=operations<=100000; \|x\|<=10000000; rank/predecessor/successor query key may be absent; kth and neighbors exist. | 待编写驱动/提交 | 待核验 |
| `xor_hamming_pairs` | [Luogu P4887](https://www.luogu.com.cn/problem/P4887) | 1<=n,m<=100000; 0<=a_i,k<2^14. Note k may exceed 14. | 待编写驱动/提交 | 待核验 |
| `MonotoneStackSeg` | [Luogu P12438 / CF1912G](https://www.luogu.com.cn/problem/P12438) | 1<=n,q<=200000; 1<=a_i<=1e9; each closed interval increases by one. | 待编写驱动/提交 | 待核验 |
| `KDTreeSum` | [Luogu P4148](https://www.luogu.com.cn/problem/P4148) | N<=500000, at most 200000 operations, 20 MB memory, positive updates, XOR all arguments with last answer; answers fit int. | 待编写驱动/提交 | 待核验 |
| `cdq_convolution` | [Luogu P4721](https://www.luogu.com.cn/problem/P4721) | 2<=n<=100000; recurrence modulo 998244353, f[0]=1. | 待编写驱动/提交 | 待核验 |
| `PolynomialDivision` | [Luogu P4512](https://www.luogu.com.cn/problem/P4512) | 1<=m<=n<=100000; input degrees, fixed output lengths; mod 998244353 | 待编写驱动/提交 | 待核验 |
| `FpsSqrt` | [Luogu P5205](https://www.luogu.com.cn/problem/P5205) | 1<=n<=100000; a[0]=1; smaller constant root | 待编写驱动/提交 | 待核验 |
| `PolynomialDivision` | [Library Checker division_of_polynomials](https://judge.yosupo.jp/problem/division_of_polynomials) | 1<=N,M<=500000; normalized leading coefficients; zero polynomial output length 0 | 待编写驱动/提交 | 待核验 |
| `FpsSqrt` | [Library Checker sqrt_of_formal_power_series](https://judge.yosupo.jp/problem/sqrt_of_formal_power_series) | 1<=N<=500000; arbitrary coefficients; output any root or -1 | 待编写驱动/提交 | 待核验 |
| `FpsPower` | [Luogu P5245](https://www.luogu.com.cn/problem/P5245) | 1<n<=100000; 0<k<=10^100000; a[0]=1 | 待编写驱动/提交 | 待核验 |
| `FpsPower` | [Luogu P5273](https://www.luogu.com.cn/problem/P5273) | 1<n<=100000; 0<=k<=10^100000; arbitrary coefficients | 待编写驱动/提交 | 待核验 |
| `FpsPower` | [Library Checker pow_of_formal_power_series](https://judge.yosupo.jp/problem/pow_of_formal_power_series) | 1<=N<=500000; 0<=M<=10^18; arbitrary coefficients | 待编写驱动/提交 | 待核验 |
| `BostanMori` | [Library Checker kth_term_of_linearly_recurrent_sequence](https://judge.yosupo.jp/problem/kth_term_of_linearly_recurrent_sequence) | 1<=d<=100000; 0<=k<=10^18; normalized coefficients and initial values modulo 998244353; input initial values before recurrence coefficients | 待编写驱动/提交 | 待核验 |
| `convolution_fft` | [Luogu P3803](https://www.luogu.com.cn/problem/P3803) | 0<=n,m<=1000000; integer coefficients 0..9 | 待编写驱动/提交 | 待核验 |
| `convolution_mod_fft` | [Luogu P4245](https://www.luogu.com.cn/problem/P4245) | 1<=n,m<=100000; coefficients 0..10^9; 2<=mod<=1000000009 | 待编写驱动/提交 | 待核验 |
| `integer_hull` | [Luogu P2742](https://www.luogu.com.cn/problem/P2742) | 3<=n<=100000; \|coordinate\|<=1000000, at most two fractional decimal digits | 待编写驱动/提交 | 待核验 |
| `convex_diameter2` | [Luogu P1452](https://www.luogu.com.cn/problem/P1452) | 2<=n<=50000 distinct points; \|coordinate\|<=10000 | 待编写驱动/提交 | 待核验 |
| `IntegerHalfplanes` | [Luogu P4196](https://www.luogu.com.cn/problem/P4196) | 2<=polygons<=10; 3<=vertices<=50 each; CCW; integer coordinates in [-1000,1000] | 待编写驱动/提交 | 待核验 |
| `IntegerPlane` | [Library Checker sort_points_by_argument](https://judge.yosupo.jp/problem/sort_points_by_argument) | 1<=n<=200000; \|x\|,\|y\|<=10^9; order (-pi,pi], origin angle 0, equal angles arbitrary | 待编写驱动/提交 | 待核验 |
| `SpfaFlow` | [Luogu P3381](https://www.luogu.com.cn/problem/P3381) | n<=5000, m<=50000; nonnegative integer capacity/cost<=1000; no self-loop; flow and minimum cost<=2^31-1; distinct source/sink required by API | 待编写驱动/提交 | 待核验 |
| `BiconnectedCore` | [Library Checker biconnected_components](https://judge.yosupo.jp/problem/biconnected_components) | 1<=N<=500000; 0<=M<=500000; parallel edges allowed, no loops | 待编写驱动/提交 | 待核验 |
| `BiconnectedCore` | [Library Checker two_edge_connected_components](https://judge.yosupo.jp/problem/two_edge_connected_components) | 1<=N<=200000; 1<=M<=200000; parallel edges and loops allowed | 待编写驱动/提交 | 待核验 |
| `manacher` | [Luogu P3805](https://www.luogu.com.cn/problem/P3805) | 1<=n<=11000000; lowercase English letters | 待编写驱动/提交 | 待核验 |
| `SuffixArray` | [Library Checker suffixarray](https://judge.yosupo.jp/problem/suffixarray) | 1<=N<=500000; lowercase English letters | 待编写驱动/提交 | 待核验 |
| `SuffixArray` | [Library Checker longest_common_substring](https://judge.yosupo.jp/problem/longest_common_substring) | 1<=\|S\|,\|T\|<=500000; lowercase | 待编写驱动/提交 | 待核验 |
| `GeneralSAM` | [Luogu P6139](https://www.luogu.com.cn/problem/P6139) | 1<=n<=400000; nonempty lowercase strings; total length<=1000000; 1s/512MB | 待编写驱动/提交 | 待核验 |
| `unit_flow_edges` | [QOJ 10424 / NERC 2024 K](https://qoj.ac/problem/10424) | 1<=k<=n<=2000; sum(n)<=2000; two permutations and partial subsequences; 3s/1024MB | 待编写驱动/提交 | 待核验 |
| `closest_pair_i64` | [Library Checker closest_pair](https://judge.yosupo.jp/problem/closest_pair) | T<=100000; 2<=N; sum(N)<=500000; integer \|x\|,\|y\|<=1e9 | 待编写驱动/提交 | 待核验 |
| `polygon_contains` | [AOJ CGL_3_C](https://onlinejudge.u-aizu.ac.jp/problems/CGL_3_C) | 3<=n<=100; q<=1000; integer coordinates with absolute values<=10000; CCW simple polygon, not necessarily convex | 待编写驱动/提交 | 待核验 |
| `minkowski_sum` | [Luogu P4557 [JSOI2018] 战争](https://www.luogu.com.cn/problem/P4557) | 3<=n,m<=100000; q<=100000; \|coordinates\| and \|translation\|<=1e8; each set noncollinear; all original points distinct | 待编写驱动/提交 | 待核验 |
| `CentroidPairs` | [Luogu P3806](https://www.luogu.com.cn/problem/P3806) | n<=10000,m<=100,k<=1e7,positive edge weights<=10000 | 待编写驱动/提交 | 待核验 |
| `SubtreeColors` | [Codeforces 600E](https://codeforces.com/problemset/problem/600/E) | n<=100000,1<=colors<=n,root=1 | 待编写驱动/提交 | 待核验 |
| `VirtualTree` | [Luogu P2495 [SDOI2011] 消耗战](https://www.luogu.com.cn/problem/P2495) | n<=250000,queries<=500000,sum(keys)<=500000,1<=weights<=100000,keys exclude root1 | 待编写驱动/提交 | 待核验 |
| `WaveletMatrix` | [Library Checker range_kth_smallest](https://judge.yosupo.jp/problem/range_kth_smallest) | 静态数组，查询半开区间[l,r)内第k小，l/r/k均按题面0-based；直接调用kth。n、q至20万，值在0..10⁹。 | 待编写驱动/提交 | 待核验 |
| `WaveletMatrix` | [Library Checker static_range_frequency](https://judge.yosupo.jp/problem/static_range_frequency) | 静态数组，统计半开区间[l,r)中x的出现次数；允许空数组、空查询区间、q=0和未出现的x。n、q至50万，值在0..10⁹。 | 待编写驱动/提交 | 待核验 |
| `WaveletMatrix` | [Luogu P3834](https://www.luogu.com.cn/problem/P3834) | 静态区间第k小；题目为1-based闭区间和1-based k，调用时转换成kth(l-1,r,k-1)。n、q至20万，题面值在0..10⁹；本程序采用小波矩阵，不建立历史版本。 | 待编写驱动/提交 | 待核验 |
| `GaussXor` | [Library Checker system_of_linear_equations_mod_2](https://judge.yosupo.jp/problem/system_of_linear_equations_mod_2) | 给定模2矩阵A和右端b，输出无解-1，或解空间维数、一个特解和全部零空间基。输出维数是变量数减系数秩，不是rank。输入每行是连续01字符，先把b追加到对应行；行列数各至4096。 | 待编写驱动/提交 | 待核验 |
| `SecondMST` | [Luogu P4180](https://www.luogu.com.cn/problem/P4180) | n<=100000,m<=300000,w=0..1e9; self-loops allowed; strict second tree guaranteed. | 待编写驱动/提交 | 待核验 |
| `GaussXor` | [POJ 1681](http://poj.org/problem?id=1681) | Locally tested n<=15,t<=20; w requires toggle, y does not; own cell and four neighbors; enumerate entire affine solution space to minimize presses. | 待编写驱动/提交 | 待核验 |
| `DivisionTree` | [Luogu P3834](https://www.luogu.com.cn/problem/P3834) | N/Q<=200000, values 0..1e9; kth(l-1,r,k-1) converts 1-based closed interval/rank. | 待编写驱动/提交 | 待核验 |
| `DivisionTree` | [Library Checker range_kth_smallest](https://judge.yosupo.jp/problem/range_kth_smallest) | N/Q<=200000, values 0..1e9; directly query half-open [l,r), 0-based k. | 待编写驱动/提交 | 待核验 |
| `maximum_closure` | [Luogu P2762 太空飞行计划问题](https://www.luogu.com.cn/problem/P2762) | 选实验获得收益，配置仪器支付费用，输出最优实验/仪器编号和净收益。m、n至50，单项费用为正且小于2³¹，累计用long long。逐行读取变长依赖，istringstream兼容CRLF；实验i依赖仪器m+j。应用用法，不计非比赛模板覆盖。 | 待编写驱动/提交 | 待核验 |
| `Arborescence` | [Luogu P4716](https://www.luogu.com.cn/problem/P4716) | 给定根的有向最小树形图费用，无解输出-1。n至100、m至10⁴、正权至10⁶；顶点和根从1-based转0-based。optional有值时才解引用，本题总费用可转long long；核心只返回费用，不恢复选边。 | 待编写驱动/提交 | 待核验 |
| `StoerWagner` | [Luogu P5632](https://www.luogu.com.cn/problem/P5632) | 无向连通正权图的全局最小割，n至600、边权总和至10⁹；矩阵按无向边双向累加、自环忽略。核心返回费用与0-based割侧side，本题只输出费用。核心要求n≥2；单点没有非平凡割，驱动额外约定输出0。 | 待编写驱动/提交 | 待核验 |
| `line_circle_i64` | [AOJ CGL_7_D](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_7_D) | 整数圆心/半径及直线，坐标绝对值≤10⁴、半径1..10⁴，q≤1000。题目保证直线非退化且至少一个交点；精确分类后构造坐标，按x/y字典序输出，相切点复制一次。绝对误差要求小于1e-6。 | 待编写驱动/提交 | 待核验 |
| `circle_intersections_i64` | [AOJ CGL_7_E](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_7_E) | 整数圆心/半径，坐标绝对值≤10⁴、半径1..10⁴；不同圆心且至少一个交点。按x/y字典序输出，相切点复制一次；不使用eps排序。绝对误差要求小于1e-6。 | 待编写驱动/提交 | 待核验 |
| `CirclePolygon` | [AOJ CGL_7_H](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_7_H) | 原点圆与逆时针简单多边形的公共面积，允许凹多边形。n为3..100，整数坐标绝对值≤100，半径1..100。直接传入顶点序列，不取凸包；绝对误差小于1e-5。 | 待编写驱动/提交 | 待核验 |
| `circle_overlap_area` | [AOJ CGL_7_I](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_7_I) | 两个圆的公共面积，整数坐标绝对值≤10⁴、半径1..10⁴。覆盖相离、内含、同心与部分相交；输出面积的绝对误差须小于1e-6。 | 待编写驱动/提交 | 待核验 |
| `CircleTangents` | [AOJ CGL_7_F](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_7_F) | 过圆外整数点作切线，输出圆上的两个切点。坐标绝对值≤1000，半径1..1000，保证点严格在圆外。from_point把点作为第一圆，圆上切点在line.b；按x/y字典序输出，每行一个点，绝对误差小于1e-5。 | 待编写驱动/提交 | 待核验 |
| `IntegerTangents` | [AOJ CGL_7_G](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_7_G) | 不同整数圆的公切线，输出第一圆上的全部切点。坐标绝对值≤1000，半径1..1000；可能0..4条，同心不等圆需空输出。整数版已精确排序，直接顺序输出line.a，不再按舍入值排序；绝对误差小于1e-5。 | 待编写驱动/提交 | 待核验 |
| `floor_moments` | [Luogu P5170](https://www.luogu.com.cn/problem/P5170) | 求i=0..n的整除和、整除值平方和、i乘整除值之和，模998244353。t至10⁵，n/a/b/c至10⁹且c>0。核心参数顺序(n+1,c,a,b)，返回顺序是和/带权和/平方和；本题输出索引0、2、1，不能只核对第一项。 | 待编写驱动/提交 | 待核验 |
| `Partitions` | [Library Checker partition_function](https://judge.yosupo.jp/problem/partition_function) | 输出0..N的全部整数分拆数，模998244353，N≤500000。构造Partitions后直接读p；p[0]=1表示空分拆。五边形数递推O(N√N)时间、O(N)空间，不是有序拆分。此用法不调用limited。 | 待编写驱动/提交 | 待核验 |
| `Partitions` | [Luogu P6189 [NOI Online #1 入门组] 跑步](https://www.luogu.com.cn/problem/P6189) | 正整数非增序列的总和为n，等价于n的无序分拆。n≤10⁵，1≤p<2³⁰且不保证素数；直接构造Partitions(n,p)，输出p[n]。这是比赛应用，单独记录，不替代正式模板题。 | 待编写驱动/提交 | 待核验 |
| `recurrence_nth` | [Luogu P5487](https://www.luogu.com.cn/problem/P5487) | 给出n个初值，恢复唯一的最短递推并求第m项，n≤10000、n<m≤10⁹、阶数≤5000，模998244353。BM返回c[j-1]乘a[i-j]，首行仅输出系数、不带阶数；裁取恰好c.size()个初值后调用recurrence_nth。全零序列空递推仍输出空首行和第二行0。复杂度O(nk+k²log m)，O(n+k)空间。 | 待编写驱动/提交 | 待核验 |
| `SCC` | [Library Checker scc (Kosaraju)](https://judge.yosupo.jp/problem/scc) | 给有向图，输出强连通分量并按缩点拓扑序排列；N、M≤500000，可有重边和自环。题面零基点号先加1；SCC.bel为1..cnt且沿跨分量边递增，按1..cnt输出并将点号减1。不要照搬TarjanSCC的逆序循环。时间、空间O(N+M)，DFS递归。 | 待编写驱动/提交 | 待核验 |
| `removal_components` | [AOJ GRL_3_A](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=GRL_3_A&lang=en) | 连通无向简单图，按编号升序输出所有割点，N、M≤100000。输入零基转一基；BiconnectedCore.run后取(before,after)，仅当after[u]>before才输出u-1。本例展示已有点双结果的复用；只求割点优先用更短的Lowlink。时间、空间O(N+M)，递归DFS。该题只核验割点集合，完整删点数量另见UVA10765应用。 | 待编写驱动/提交 | 待核验 |
| `removal_components` | [UVA 10765 Doves and Bombs](https://onlinejudge.org/external/107/10765.pdf) | 分别删去每个站点，按剩余连通块数降序、原编号升序输出前m名；n≤10000，原图连通。m是输出名额而非边数，边表以-1 -1结束，多测以0 0结束，每组末尾空行。after是剩余总块数而非增量，不重复加before。O(n log n+E)时间、O(n+E)空间。应用题不计正式模板覆盖。 | 待编写驱动/提交 | 待核验 |
| `orient_edges` | [Codeforces 118E Bertown roads](https://codeforces.com/problemset/problem/118/E) | 给连通无向简单图，把每条边定向使整图强连通，无解输出0。n≤100000、m≤300000。先用Lowlink.run确认连通且无桥，再调用orient_edges；返回数组与add的原边编号逐项对应，每条逻辑边只加一次。任意可行方向均可。O(n+m)时间、空间，DFS递归；比赛应用不替代正式模板题。 | 待编写驱动/提交 | 待核验 |
| `block_cut_forest` | [Luogu P4630](https://www.luogu.com.cn/problem/P4630) | 无向简单图，可不连通，n≤100000、m≤200000；统计存在经过c的简单s-f路径的有序三元组(s,c,f)，三点互异。原点1..n权为-1，方点n+i+1权为blocks[i].size()，树路径权和就是可选c数。sz仅计原点，每棵树独立累计有序端点对，答案用long long。O(n+m)时间、空间，递归DFS。 | 待编写驱动/提交 | 待核验 |
| `bridge_component_forest` | [Luogu P2860 (bridge forest)](https://www.luogu.com.cn/problem/P2860) | 连通无向图，n≤5000、m≤10000；允许已有重边及新增重边，求最少新增边使任意两点间有两条边不相交路径。run后边双缩点，编号1..cnt，邻接项为(边双号,原桥号)。度1点数为L，答案(L+1)/2；只剩一个边双时为0。该公式要求原图连通，不可对任意森林直接套用。O(n+m)时间、空间。 | 待编写驱动/提交 | 待核验 |
| `bridge_augmentation` | [Luogu P2860 (construct augmentation)](https://www.luogu.com.cn/problem/P2860) | 同题的构造接口：连通非空图run后调用bridge_augmentation，返回最少补边方案的原点端点对，点号1..n，可直接逐对使用；题目只输出方案长度。已有边和新增边都允许平行边。接口不修改graph，若需更新原图须自行add并重新run。O(n+m)时间、空间；DFS顺序收集桥树叶子后对半配对，奇数叶子补首叶。 | 待编写驱动/提交 | 待核验 |
| `SCC` | [QOJ 906 (Kosaraju)](https://qoj.ac/problem/906) | 给有向图，输出强连通分量并按缩点拓扑序排列；N、M≤500000，可有重边和自环。题面零基点号先加1；SCC.bel为1..cnt且沿跨分量边递增，按1..cnt输出并将点号减1。不要照搬TarjanSCC的逆序循环。时间、空间O(N+M)，DFS递归。 | [记录](https://qoj.ac/submission/3061625) | 待核验 |
| `BiconnectedCore` | [QOJ 999 (BiconnectedCore)](https://qoj.ac/problem/999) | 1<=N<=200000; 1<=M<=200000; parallel edges and loops allowed | [记录](https://qoj.ac/submission/3061643) | 待核验 |
| `path_intersection` | [Luogu P3398](https://www.luogu.com.cn/problem/P3398) | n,q<=100000; tree; 1-based vertices | [记录](https://www.luogu.com.cn/record/299972443) | 待核验 |
| `TreeDiameter` | [Codeforces 379F](https://codeforces.com/problemset/problem/379/F) | q<=500000; final n=4+2q; two new leaves per operation | 待编写驱动/提交 | 待核验 |
| `FunctionalGraph` | [CSES 1750](https://cses.fi/problemset/task/1750) | n,q<=200000; 0<=k<=1000000000 | 待编写驱动/提交 | 待核验 |
| `FunctionalGraph` | [CSES 1160](https://cses.fi/problemset/task/1160) | n,q<=200000 | 待编写驱动/提交 | 待核验 |
| `FunctionalGraph` | [Luogu P2921](https://www.luogu.com.cn/problem/P2921) | n<=100000 | [记录](https://www.luogu.com.cn/record/299973954) | 待核验 |
| `PersistentRange` | [SPOJ TTM / Luogu SP11470](https://www.luogu.com.cn/problem/SP11470) | n,m<=100000; abs(initial)<=1e9; abs(delta)<=10000 | 待编写驱动/提交 | 待核验 |
| `PersistentRange` | [QOJ 8240](https://qoj.ac/problem/8240) | n,q<=300000; colors1..n; online XOR endpoints | [记录](https://qoj.ac/submission/2939235) | 待核验 |
| `XorWalk` | [Luogu P4151](https://www.luogu.com.cn/problem/P4151) | n<=50000;m<=100000;0<=w<=1e18;connected;loops/parallel edges | 待编写驱动/提交 | 待核验 |
| `UndirectedEuler` | [Luogu P2731](https://www.luogu.com.cn/problem/P2731) | 1<=m<=1024;vertex labels1..500;Euler trail exists | [记录](https://www.luogu.com.cn/record/299974727) | 待核验 |
| `basis_intersection` | [LC Intersection of F2 Vector Spaces](https://judge.yosupo.jp/problem/intersection_of_f2_vector_spaces) | T<=100000;n,m<=30;independent30-bit generators | 待编写驱动/提交 | 待核验 |
| `basis_sum_intersection` | [LC Intersection / Zassenhaus](https://judge.yosupo.jp/problem/intersection_of_f2_vector_spaces) | T<=100000;n,m<=30;independent30-bit generators | 待编写驱动/提交 | 待核验 |
| `RealPlane` | [AOJ CGL_2_A](https://onlinejudge.u-aizu.ac.jp/problems/CGL_2_A) | integer coordinates \|x\|,\|y\|<=10000; 1<=q<=1000; nondegenerate input lines/segments | 待编写驱动/提交 | 待核验 |
| `line_projection` | [AOJ CGL_1_A](https://onlinejudge.u-aizu.ac.jp/problems/CGL_1_A) | integer coordinates \|x\|,\|y\|<=10000; 1<=q<=1000; nondegenerate input lines/segments | 待编写驱动/提交 | 待核验 |
| `segment_distance_real` | [AOJ CGL_2_D](https://onlinejudge.u-aizu.ac.jp/problems/CGL_2_D) | integer coordinates \|x\|,\|y\|<=10000; 1<=q<=1000; nondegenerate input lines/segments | 待编写驱动/提交 | 待核验 |
| `line_intersection_real` | [AOJ CGL_2_C](https://onlinejudge.u-aizu.ac.jp/problems/CGL_2_C) | integer coordinates \|x\|,\|y\|<=10000; 1<=q<=1000; nondegenerate input lines/segments | 待编写驱动/提交 | 待核验 |
| `polygon_area2` | [AOJ CGL_3_A](https://onlinejudge.u-aizu.ac.jp/problems/CGL_3_A) | integer coordinates \|x\|,\|y\|<=10000; 3<=n<=100; simple CCW polygon | 待编写驱动/提交 | 待核验 |
| `BoundedCirculation` | [LibreOJ 115](https://loj.ac/p/115) | 1<=n<=200; 1<=m<=10200; 1<=u,v<=n; 0<=lower<=upper<3000 | 待编写驱动/提交 | 待核验 |
| `square_counts` | [Luogu P1117 [NOI2016] 优秀的拆分](https://www.luogu.com.cn/problem/P1117) | 1<=T<=10; lowercase strings, length<=30000 | 待编写驱动/提交 | 待核验 |
| `MatrixTreeMod` | [Library Checker Counting Spanning Trees (Undirected)](https://judge.yosupo.jp/problem/counting_spanning_tree_undirected) | 1<=N<=500; 0<=M<=500000; zero-based multigraph; modulus998244353 | 待编写驱动/提交 | 待核验 |
| `MatrixTreeMod` | [Library Checker Counting Spanning Trees (Directed)](https://judge.yosupo.jp/problem/counting_spanning_tree_directed) | 1<=N<=500; 0<=M<=500000; zero-based multigraph; modulus998244353 | 待编写驱动/提交 | 待核验 |
| `pheap` | [Library Checker Double-Ended Priority Queue](https://judge.yosupo.jp/problem/double_ended_priority_queue) | 0<=N<=500000; 1<=Q<=500000; -1e9<=x<=1e9; deletion on nonempty multiset | 待编写驱动/提交 | 待核验 |
| `divisor_sum_power` | [Luogu P1593 因子和](https://www.luogu.com.cn/problem/P1593) | 1<=a<=50000000; 0<=b<=50000000; modulus9901 | 待编写驱动/提交 | 待核验 |

## 适配与证据范围

### Luogu P1903 / ModifiedMo

Official title explicitly labels this as a modifiable-Mo template. Historical source is national-team training / bzoj2120; retained here as a standalone standard-template candidate, not a regional-contest application.



Check fastest-submission leaderboard availability and denominator. This AC does not complete issue #1.

### QOJ 906 / TarjanSCC

Library Checker standard SCC task, reused in template practice contests.

Shift input vertices +1; emit component IDs in reverse order because Tarjan IDs are reverse topological. add/run/bel are covered; dag is not called.

Global full-score count is 578, but linked visible list contains 143 records. Global rank is unresolved; displayed best-per-user table position 66 is not an all-submission rank. dag remains outside this AC scope.

### QOJ 547 / berlekamp_massey

Direct shortest finite-prefix recurrence template; template practice use.

Output returned coefficient count and positive recurrence coefficients. n=0 needs an empty line. Does not test recurrence_nth.

Driver/AC and full-score submission speed-rank audit pending. This is a reviewed task mapping, not a completed verification.

### QOJ 464 / prefix_function

Direct prefix-function template; template practice use.

Print prefix_function output in order. This task does not test kmp_match.

Driver/AC and full-score submission speed-rank audit pending. This is a reviewed task mapping, not a completed verification.

### QOJ 786 / z_function

Direct Z-function template; template practice use.

Problem requires z[0]=0; current library deliberately returns |S|. Driver must replace the first output with 0; do not change the generic contract silently.

Driver/AC and full-score submission speed-rank audit pending. This is a reviewed task mapping, not a completed verification.

### QOJ 787 / manacher

Direct longest-palindrome template; template practice use.

Take maximum of 2*odd[i]-1 and 2*even[i]. The scalar answer does not independently verify every radius.

Driver/AC and full-score submission speed-rank audit pending. This is a reviewed task mapping, not a completed verification.

### QOJ 997 / TwoSAT

Direct Boolean clause assignment template; template practice use.

add(a,b,c,d) encodes the given disjunction; solve then ans[1..n]. Print Yes/No, unlike Luogu POSSIBLE/IMPOSSIBLE.

Driver/AC and full-score submission speed-rank audit pending. This is a reviewed task mapping, not a completed verification.

### QOJ 618 / NttConvolution

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Read n+1 and m+1 coefficients, not n and m. multiply returns n+m+1 coefficients. Transform size is at most 2^21, within the 998244353 capacity. This fixed-modulus task cannot certify all template moduli or primitive roots.

Driver, online evidence and fastest-ranking scope still require verification.

### QOJ 618 / Polynomial

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Same degree-based input adapter, using Polynomial::multiply. Record this implementation separately from NttConvolution and do not transfer AC or speed evidence between the two.

Driver, online evidence and fastest-ranking scope still require verification.

### QOJ 619 / Polynomial

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Here n is coefficient count and truncation order. Call inverse(a,n), print exactly n coefficients. Verify the complete driver and largest non-power-of-two truncation; multiplication AC alone does not prove inverse.

Driver, online evidence and fastest-ranking scope still require verification.

### QOJ 620 / Polynomial

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Call log(a,n), preserving n coefficients including constant zero. Constant-one restriction is essential. Derivative/integral/inverse are dependencies, but only the composed logarithm behavior is directly observed.

Driver, online evidence and fastest-ranking scope still require verification.

### QOJ 621 / Polynomial

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Call exp(a,n), preserving n coefficients with constant one. Do not confuse coefficient count with polynomial degree or ordinary floating-point exponential.

Driver, online evidence and fastest-ranking scope still require verification.

### QOJ 622 / GeneralMultipointEvaluation

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Input has n coefficients followed by m arbitrary nonnegative evaluation points. Distinctness is not promised. General product/remainder-tree evaluation is absent; Chirp Z only handles geometric points and cannot replace this task. Coefficient and point upper bounds are not explicitly stated on the fetched page, so parser bounds need further audit.

Implementation is not present. This is a reviewed target only; performance, driver, AC and ranking remain unverified.

### QOJ 956 / SuffixArray

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Print each sa index plus one. Library sa is zero-based and orders unsigned bytes. This task outputs suffix order only, not the lcp array or range-LCP queries.

Driver, online evidence and fastest-ranking scope still require verification.

### QOJ 801 / PalindromicTree

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Call add(ch) with each lowercase character, obtain occurrences(), then maximize occ[u]*len[u]*len[u] over real nodes u>=2. Promote before multiplication: n^3<=10^18 fits signed 64-bit. This is length squared, unlike common length-times-occurrence tasks. distinct and incremental total are not directly validated.

Driver, online evidence and fastest-ranking scope still require verification.

### Luogu P3804 / SuffixAutomaton

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Use extend and counts; maximize cnt[u]*a[u].len only where cnt[u]>1, otherwise output zero. Use 64-bit multiplication. distinct is not tested. The QOJ217 candidate was not reviewed because the fetch returned HTTP 429; no equivalence to it is claimed.

Independent local frequency oracle and million-letter closed forms passed in normal and sanitizer modes. Online AC and ranking still pending.

### Luogu P3369 / OrderedTreap

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Multiset semantics: erase one copy, rank is number of values <x plus one, kth is one-based, predecessor/successor are strict. x need not already exist for rank/neighbor queries. kth and neighbors have guaranteed answers.

Existing vector AC retained with its archived scope; leaderboard ranking remains unverified.

### Luogu P3369 / OrderedSplay

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Multiset semantics: erase one copy, rank is number of values <x plus one, kth is one-based, predecessor/successor are strict. x need not already exist for rank/neighbor queries. kth and neighbors have guaranteed answers.

Existing vector AC retained with its archived scope; leaderboard ranking remains unverified.

### Luogu P3391 / SequenceTreap

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Initialize values 1..n using zero-based insertion positions; reverse uses the library one-based closed [l,r] interval; output values(). This does not validate range addition or general erase. A plain rope has no lazy reversal API, so it must not inherit this efficiency claim.

Existing vector AC retained with its archived scope; leaderboard ranking remains unverified.

### Luogu P3369 / ost

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Use pair<int,int> with unique positive ID; deletion erases only one equal key, absent deletion ignored. Strict ranks use {x,0}; predecessor lower_bound then prev; successor upper_bound({x,INT_MAX}); kth converted from 1-based.

Separate PBDS multiset driver now passes independent sorted-list oracle and ASan/UBSan. P6136 also checks 100000 initial duplicates and 1000000 online operations. Online AC and ranking still pending.

### Luogu P6136 / ost

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Read an initial multiset, XOR each operand with the last query answer before executing it, and print XOR of all query answers. All operations are legal. Cannot simply reuse P3369 input/output or sort operations offline; require separate maximum-scale performance evidence.

Fastest-submission ranking availability and scope remain to audit. P3369 driver has separate pending online evidence.

### Library Checker associative_array / gp_map

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

uint64_t keys and values; assignment uses operator[], lookup uses find and returns zero without insertion. Official online tests include hash-killer and sparse-key families.

PBDS ordered trees and rope remain separate work. This AC validates assignment/find only; erase/insert/copy/clear have local evidence.

原始题面与参数：[来源 1](https://raw.githubusercontent.com/yosupo06/library-checker-problems/master/data_structure/associative_array/task.md)，[来源 2](https://raw.githubusercontent.com/yosupo06/library-checker-problems/master/data_structure/associative_array/info.toml)

### Library Checker persistent_queue / rp

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Version -1 becomes index 0. Preallocate Q zero cells; copy root and head/tail per version. Push is replace at tail; pop reads head then increments it. This avoids repeated rope concat/erase rebalancing in direct queue implementation.

Ranking pending. General insert/erase/substr have local evidence only; significant version-memory overhead remains.

原始题面与参数：[来源 1](https://raw.githubusercontent.com/yosupo06/library-checker-problems/master/data_structure/persistent_queue/task.md)，[来源 2](https://raw.githubusercontent.com/yosupo06/library-checker-problems/master/data_structure/persistent_queue/info.toml)

### Luogu P3367 / dsu

Explicit standard DSU template. Retained by user exception in issue #2 comment 5646284816.

Construct dsu(n); subtract one from task vertices; merge/same provide the required operations. size/groups are covered by independent local tests, not by this task output. Linking direction follows the supplied user version without union-by-size.

P3367 final source AC: 20 tests, slowest 196ms. size/groups remain independently local-tested; leaderboard ranking pending.

### QOJ 995 / Lowlink

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

保存每条边原始有序端点；add 返回输入顺序边号，run 后按边号扫描 bridge。只输出标记为桥的原端点，不排序端点或按 DFS 发现顺序输出。题目允许重边与自环；该输出不验证 cut 和 delta。

完整驱动、在线验证及速度榜口径仍待核验。

### QOJ 996 / Lowlink

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

run 后扫描 cut[1..n]，先输出数量，再按顶点编号递增输出。必须遍历全部连通分量；根节点割点条件不同。该题不输出桥或删点后的分量增量。

完整驱动、在线验证及速度榜口径仍待核验。

### Luogu P3376 / Dinic

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

读入 n,m,s,t 与有向边，按容量加入后调用 flow(s,t)，使用库约定的不同源汇。总流量可能超过 32 位，需要 long long；不可达或零容量网络输出 0。默认最大流结果不单独验证 limit、used 或 cut。

保留已有 vector 提交的归档验证范围；该模板题的速度榜仍待核验。

### Luogu P3381 / MinCostFlow

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

输出 flow(s,t) 返回的流量、费用，顺序不可反。原始费用非负，且题目不允许自环；不能用此题证明负费用边、负环处理或超大费用范围。库费用累加为 int128，驱动打印须与题目数值界兼容。 新驱动输出 slope 最后一个折点，仅验证终点，不覆盖中间曲线。

完整 slope 终点驱动已通过独立边流枚举，线上和排名待核验。中间折点以独立曲线测试验证。

### Luogu P8435 / Biconnected

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

输出 run 后的 blocks。题目采用“无割点”定义，要包括孤立点及自环场景；库将自环保留在边表但不加入 DFS 邻接表，孤立顶点输出单点块。不同块可能共享割点，不能当作互不相交的顶点分区。此输出不验证圆方树接口。

保留已有 vector 提交的归档验证范围；该模板题的速度榜仍待核验。

### Luogu P8436 / Biconnected

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

按 run 后的 bel[1..n] 分组并输出 cnt 组，点号和分量号均为 1-based；支持重边、自环、孤立点和多个连通分量。不能误用点双 blocks；本题不单独输出桥森林。

保留已有 vector 提交的归档验证范围；该模板题的速度榜仍待核验。

### Luogu P3386 / BipartiteMatching

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

左右点集分别按 1..n 和 1..m 编号，add 后 solve 返回匹配边数，不要把两侧编号混在一个区间。题目只要求数量，不检查 cover 或完整匹配方案；存在重边。

完整驱动、在线验证及速度榜口径仍待核验。

### Luogu P6577 / WeightedMatching

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

构造两侧均为 n 的实例，调用 solve(false)；题目保证完美匹配。权值允许负数，缺边不能当成零权边。第二行要求右点到左点的配对，输出 r[1..n]。此题不验证允许不匹配的分支或矩形点集。

保留已有 vector 提交的归档验证范围；该模板题的速度榜仍待核验。

### Luogu P3379 / OfflineLCA

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

先登记全部 add_query，再 run(S)，按登记顺序输出 answer。点号 1-based；不能把固定根 1 当作题目给定根 S。原离线驱动已有对应记录。

保留已有 vector 提交的归档验证范围；该模板题的速度榜仍待核验。

### Luogu P3379 / EulerLCA

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

按无权树加入边，以 S 建立 Euler 序，再逐条输出 lca(a,b)。该题不验证加权距离、边距离或其它 RMQ 包装接口；不能挪用 OfflineLCA 的 AC。

完整驱动、在线验证及速度榜口径仍待核验。

### Luogu P3379 / LiftingLCA

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

默认单位边权即可，以 S build 后调用 lca。相同端点应返回自身。题目不验证祖先跳转、路径最大边或换根查询；须使用本实现自己的驱动与记录。

完整驱动、在线验证及速度榜口径仍待核验。

### Luogu P3379 / HLD

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

以 S 剖分，输出 lca(a,b)。无需接线段树；该题不检查 path 回调、边权路径的 LCA 排除或子树区间。

完整驱动、在线验证及速度榜口径仍待核验。

### Luogu P3384 / HLD + AffineSegTree

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

以给定根 R 构建 HLD，把初始点权放到 dfn 位置，线段树使用同一模数 P。path 的闭区间直接调用 update(l,r,1,z)；子树区间为 [dfn[u],dfn[u]+siz[u]-1]。这是点权而非边权，包含路径两端。该组合不证明通用乘法更新或在线换根。

保留已有 vector 提交的归档验证范围；该模板题的速度榜仍待核验。

### Luogu P3806 / CentroidPairs

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

静态树 build 后以 count_exact(k)>0 输出 AYE/NAY。题目只观察存在性，不能据此验证所有点对计数值；零权、负查询值等扩展需保留本地证据。多个查询复用同一分解。

保留已有 vector 提交的归档验证范围；该模板题的速度榜仍待核验。

### Luogu P3834 / PersistentKth

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

构造时传入不含占位元素的原数组；kth(l,r,k) 接收 1-based 闭区间和 1-based 名次。内部比较 root[r] 与 root[l-1] 的频次数，并还原离散值。该题不支持在线修改或任意版本拼接，不能给其它可持久化接口背书。

保留已有 vector 提交的归档验证范围；该模板题的速度榜仍待核验。

### Library Checker ordered_set / ost

Official standalone ordered set template task.

Convert 1-based kth to find_by_order(x-1). Inclusive count uses order_of_key(x)+presence, avoiding x+1 overflow. Predecessor is <=x via upper_bound, successor is >=x via lower_bound; missing outputs -1. Duplicates ignored.

Duplicate-key adapters require separate online tests.

### Library Checker point_set_range_composite / segtree

Official standalone generic segment-tree composition template.

0-based point set and half-open prod. op(f,g)=g after f. Evaluate returned affine function at x. This driver does not invoke either boundary-search API.

all() and empty-range output remain local evidence. Boundary searches verified separately by predecessor_problem.

### Library Checker predecessor_problem / segtree

Official standalone dynamic predecessor template task.

Store 0/1 counts; set for insert/erase, get for membership. max_right(k,sum==0) finds inclusive successor, N becomes -1. min_left(k+1,sum==0)-1 finds inclusive predecessor, zero result becomes -1. No overflow of sum at N limit.

prod/all not invoked. Noncommutative boundary order locally verified separately.

### Library Checker range_affine_range_sum / lazy_segtree

Official standalone range-affine/range-sum template.

Node {sum,len}; tag {mul,add}. composition(f,g)=f after g, mapping multiplies sum and adds add*len. Driver calls construction/apply/prod only.

19 official generated cases pass local checker in normal and sanitizer builds; online submit/ranking still pending. Other interfaces retain separate local evidence.

### Luogu P5431 / mint

Official batch inverse template with runtime prime modulus.

mint sets runtime modulus then combines batch_units. Return sum k^i/a_i for i starting at1; fast unsigned reader. Input guarantees units, so nonunit branch is only locally tested.

Online submission pending; existing long-long P5431 AC does not cover this new driver.

### Luogu P3803 / convolution_i64

Standalone polynomial multiplication template.

Read n+1 and m+1 signed64 coefficients; output exact convolution. Maximum coefficient 81*(1000001).

Online result and performance pending; negative and signed64 extremes covered by local cpp_int oracle only.

### Library Checker Strongly Connected Components / TarjanSCC

Official standalone template task.

Shift vertices +1 on input and -1 on output. Tarjan IDs are reverse topological; print component groups from cnt down to1. Output partition and order checked independently by reachability.

Online submission and all-AC ranking pending; local independent driver oracle and official checker evidence are separate from prior OJ AC.

### Library Checker 2 Sat / TwoSAT

Official standalone template task.

Read p cnf N M; each a b 0 maps to add(abs(a),a>0,abs(b),b>0). Output SAT/UNSAT and signed assignment in variable order. Current TwoSAT uses its existing Kosaraju SCC numbering convention.

Online submission and all-AC ranking pending; local independent driver oracle and official checker evidence are separate from prior OJ AC.

### Library Checker convolution_mod / NttConvolution

Official standalone ordinary modular polynomial convolution template.

Read actual lengths N,M; use NttConvolution<998244353>::multiply and output N+M-1 residues. This tests one prime/root only, no empty input or other moduli.

Online AC and all-AC ranking pending. Independent whole-driver coefficient oracles and official local checker results are not online evidence.

### Library Checker bitwise_and_convolution / SetConvolution

Official standalone bitwise AND convolution template.

Read exponent then allocate 1<<N; invoke multiply with '&'. Output k accumulates pairs i&j=k. This driver does not cover OR or composite moduli.

Online AC and all-AC ranking pending. Independent whole-driver coefficient oracles and official local checker results are not online evidence.

### Library Checker bitwise_xor_convolution / SetConvolution

Official standalone bitwise XOR convolution template.

Read exponent then allocate 1<<N; invoke multiply with '^'. Output k accumulates pairs i^j=k. This driver does not cover OR or arbitrary odd composite moduli.

Online AC and all-AC ranking pending. Independent whole-driver coefficient oracles and official local checker results are not online evidence.

### Library Checker system_of_linear_equations / GaussMod

Official standalone linear algebra template task.

Read A then RHS b into augmented rows; solve(a,M). Print -1 if inconsistent, else kernel.size() (nullity, not matrix rank), particular vector and every kernel basis vector.

Online AC and all-AC ranking pending; official local checker uses a 120-second execution timeout, not an OJ time-limit verdict.

### Library Checker matrix_det / det_prime

Official standalone linear algebra template task.

Call det_prime<998244353>(move(a)); print the residue. Zero-dimensional and other prime contracts are not covered by this task.

Online AC and all-AC ranking pending; official local checker uses a 120-second execution timeout, not an OJ time-limit verdict.

### Library Checker matrix_product / ModMatrix

Official standalone linear algebra template task.

Call ModMatrix<998244353>::multiply; print N rows with K coefficients. Does not invoke power or test composite moduli; those retain separate local evidence.

Online AC and all-AC ranking pending; official local checker uses a 120-second execution timeout, not an OJ time-limit verdict.

### Library Checker inv_of_formal_power_series / FpsInverse

Official standalone formal power series template.

Read N coefficients and return exactly N terms with FpsInverse::inverse(a,N). No empty driver input or arbitrary input/output-length mismatch.

Online AC and all-AC ranking pending. Official local runner uses a 120-second execution timeout, not the official 10-second verdict.

### Library Checker log_of_formal_power_series / FpsFunctions

Official standalone formal power series template.

Read N coefficients and return exactly N terms with FpsFunctions::log(a,N). No empty driver input or arbitrary input/output-length mismatch.

Online AC and all-AC ranking pending. Official local runner uses a 120-second execution timeout, not the official 10-second verdict.

### Library Checker exp_of_formal_power_series / FpsFunctions

Official standalone formal power series template.

Read N coefficients and return exactly N terms with FpsFunctions::exp(a,N). No empty driver input or arbitrary input/output-length mismatch.

Online AC and all-AC ranking pending. Official local runner uses a 120-second execution timeout, not the official 10-second verdict.

### Library Checker associative_array (cc_hash_table variant) / gp_map

Official standalone associative-array template.

The combined GNU hash-table entry now includes cc_map; this driver uses cc_map exclusively. Find returns zero for absent keys without inserting; operator[] performs assignments.

CC online AC/ranking pending. Existing GP AC does not cover CC. erase/copy/point stability are tested separately, not by this driver.

### Library Checker primality_test / Prime64

Official standalone number theory template task.

Call Prime64::prime and print exact Yes/No tokens. This task excludes zero and numbers above10^18, so full uint64 behavior retains separate local evidence.

Online AC and all-AC ranking pending; official local checker does not confer an OJ performance verdict.

### Library Checker sum_of_floor_of_linear / floor_sum

Official standalone number theory template task.

Call floor_sum and cast result to long long for output. Every summand is at most i, hence sum<=N(N-1)/2 fits signed64. Negative coefficients and N=0 are outside this driver task.

Online AC and all-AC ranking pending; official local checker does not confer an OJ performance verdict.

### Library Checker Shortest Path / pheap

Standalone Library Checker template; official statement and parameters checked.

非负权简单有向图，0起点号，n和m不超过500000，权≤10⁹，s≠t。输出最短距离和一条有序路径，无解输出-1。小根配对堆存(距离,点)，每个堆内点保存句柄；松弛时已入堆则modify降键，否则push。pop后置in=false，不再访问旧句柄。距离用long long，pre还原原边；零权边允许。这个用法展示push/top/pop/modify，不覆盖join/split。

Online AC and all-submission ranking unresolved; join/split covered only by container tests.

原始题面与参数：[来源 1](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/graph/shortest_path/task.md)，[来源 2](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/graph/shortest_path/info.toml)

### Library Checker enumerate_triangles / enumerate_triangles

Standalone simple-graph triangle weighted-sum template; user issue 11 attachment section 2.9 supplies counting use case.

Degree/id orientation order need not be vertex-number order; product is symmetric. Reduce after each multiplication to stay in signed64.

17 pinned official local cases in normal/ASan+UBSan modes passed; online submission and all-submission ranking pending.

原始题面与参数：[来源 1](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/graph/enumerate_triangles/task.md)，[来源 2](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/graph/enumerate_triangles/info.toml)

### Library Checker zalgorithm / z_function

Standalone string template problem; nonempty lowercase input.

直接输出 z，约定 z[0]=串长。

29 组固定官方本地数据普通及 ASan/UBSan 通过；在线提交及速度排名待核验。

原始题面与参数：[来源 1](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/string/zalgorithm/task.md)，[来源 2](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/string/zalgorithm/info.toml)

### Library Checker enumerate_palindromes / manacher

Standalone string template problem; nonempty lowercase input.

odd[i] 转到位置 2*i 的长度 2*odd[i]-1；even[i] 转到位置 2*i-1 的长度 2*even[i]，只输出 2*n-1 个中心。

24 组固定官方本地数据普通及 ASan/UBSan 通过；在线提交及速度排名待核验。

原始题面与参数：[来源 1](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/string/enumerate_palindromes/task.md)，[来源 2](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/string/enumerate_palindromes/info.toml)

### Library Checker inverse_matrix / matrix_inverse

Official standalone linear algebra template task.

matrix_inverse<998244353>(a); optional matrix or -1.

Online AC and ranking pending; local official checker runs use a 120-second timeout, not an OJ time-limit verdict. Empty matrix extension checked by independent local test.

### Library Checker inverse_matrix_mod_2 / matrix_inverse_mod2

Official standalone linear algebra template task.

matrix_inverse_mod2(a); optional rows of binary strings or -1.

Online AC and ranking pending; local official checker runs use a 120-second timeout, not an OJ time-limit verdict. Empty matrix extension checked by independent local test.

### Library Checker counting_primes / prime_count

Official standalone number theory template task.

See directly executed registered usage and current full driver.

Online AC/ranking pending; local official execution uses 120-second timeout rather than an OJ time-limit verdict.

### Library Checker sum_of_multiplicative_function / Min25

Official standalone number theory template task.

See directly executed registered usage and current full driver.

Online AC/ranking pending. Local timeout is wider than OJ limit. Ordinary Min25 reference is explicitly allow_tle; do not interpret local correctness as a time-limit verdict.

### Luogu P5091 / euler_power

Standalone extended Euler theorem template task.

Explicitly compute euler_phi(m), then euler_power(a,b,m,phi); b is a decimal string.

Online AC and speed ranking pending; full unsigned64 modulus and zero exponent are local API extensions outside P5091.

### Luogu P5091 / euler_phi

Standalone extended Euler theorem template task.

Explicitly compute euler_phi(m), then euler_power(a,b,m,phi); b is a decimal string.

Online AC and speed ranking pending; full unsigned64 modulus and zero exponent are local API extensions outside P5091.

### Luogu P3369 / ScapegoatTree

Standalone ordinary balanced BST template; separate deterministic rebuilding implementation.

Map operations 1..6 to insert/erase/rank/kth/prev/next. Dereference optional only under judge existence guarantee.

Online AC and speed ranking pending. Full signed64 keys, absent-neighbor nullopt, empty tree and deletion failure covered by local API tests.

### Luogu P4887 / xor_hamming_pairs

Official title explicitly labels secondary-offline Mo as a template.



Online submission/ranking pending. Independent local normal and sanitizer evidence in verification/mo-secondary.json.

### Luogu P12438 / CF1912G / MonotoneStackSeg

NERC 2023 G contest application; excluded from noncompetition template coverage.



Independent local validation in verification/monotone-stack-seg.json; online AC and ranking pending. scan and negative values tested separately.

### Luogu P4148 / KDTreeSum

Online dynamic rectangle-sum application; no explicit official noncompetition template designation established, excluded from formal coverage.



Online AC, actual judge memory/time and ranking pending; local normal/sanitizer and allocation records in verification/kd-tree-sum.json.

### Luogu P4721 / cdq_convolution

Official title explicitly labels divide-and-conquer FFT as a template; implementation uses CDQ with NTT convolution.



Online submission/ranking pending; general forcing terms and other prime fields are verified separately by local quadratic DP.

### Luogu P4512 / PolynomialDivision

Official standalone algorithm template; not a regional-contest application.



Online AC and speed ranking pending. Local independent oracles and pinned Library Checker official cases are recorded separately.

### Luogu P5205 / FpsSqrt

Official standalone algorithm template; not a regional-contest application.



Online AC and speed ranking pending. Local independent oracles and pinned Library Checker official cases are recorded separately.

### Library Checker division_of_polynomials / PolynomialDivision

Official standalone algorithm template; not a regional-contest application.



Online AC and speed ranking pending. Local independent oracles and pinned Library Checker official cases are recorded separately.

### Library Checker sqrt_of_formal_power_series / FpsSqrt

Official standalone algorithm template; not a regional-contest application.



Online AC and speed ranking pending. Local independent oracles and pinned Library Checker official cases are recorded separately.

### Luogu P5245 / FpsPower

Official standalone power-of-formal-series template.



Online AC and ranking pending; independent local powers, decimal boundary cases and official LC checker evidence recorded separately.

### Luogu P5273 / FpsPower

Official standalone power-of-formal-series template.



Online AC and ranking pending; independent local powers, decimal boundary cases and official LC checker evidence recorded separately.

### Library Checker pow_of_formal_power_series / FpsPower

Official standalone power-of-formal-series template.



Online AC and ranking pending; independent local powers, decimal boundary cases and official LC checker evidence recorded separately.

### Library Checker kth_term_of_linearly_recurrent_sequence / BostanMori

Official standalone algorithm template; not a regional-contest application.



Online AC and ranking pending. Pinned official local checker evidence is recorded separately; the general rational coefficient entry is covered by independent series oracles.

### Luogu P3803 / convolution_fft

Official standalone polynomial multiplication template.



New FFT implementation: online AC and ranking pending. Local exact references, full-size complete drivers and all-root high-precision checks recorded separately. Numeric preconditions remain part of the contract.

### Luogu P4245 / convolution_mod_fft

Official standalone polynomial multiplication template.



New FFT implementation: online AC and ranking pending. Local exact references, full-size complete drivers and all-root high-precision checks recorded separately. Numeric preconditions remain part of the contract.

### Luogu P2742 / integer_hull

Competition-origin application supplement; does not complete the noncompetition-template requirement.



Online AC and ranking pending. Current vector driver independently verified in both local modes; see geometry-attachment.json.

### Luogu P1452 / convex_diameter2

Competition-origin application supplement; does not complete the noncompetition-template requirement.



Online AC and ranking pending. Current vector driver independently verified in both local modes; see geometry-attachment.json.

### Luogu P4196 / IntegerHalfplanes

Competition-origin application supplement; does not complete the noncompetition-template requirement.



Online AC and ranking pending. Current vector driver independently verified in both local modes; see geometry-attachment.json.

### Library Checker sort_points_by_argument / IntegerPlane

Official standalone integer argument-sort template; tests only Point and PolarLess, not all plane predicates.



Online AC and ranking pending. Pinned official local checker accepts all 21 cases in both modes.

### Luogu P3381 / SpfaFlow

Official standalone minimum-cost maximum-flow template; new SPFA variant tested separately from old potential version.



Online AC and ranking pending. used, limits, continuation, negative edges and global negative-cycle rejection have independent local tests, beyond P3381 scope.

### Library Checker biconnected_components / BiconnectedCore

Library Checker standalone standard template task.

Vertex blocks, singleton isolated vertices; input and output zero-based, adapted to one-based core

Official generated data accepted locally in both modes. No online AC or ranking.

### Library Checker two_edge_connected_components / BiconnectedCore

Library Checker standalone standard template task.

Group vertices by bel after run; input and output zero-based, adapted to one-based core

Official generated data accepted locally in both modes. No online AC or ranking.

### Luogu P3805 / manacher

Luogu explicitly labeled standard Manacher template.

Take max of 2*odd[i]-1 and 2*even[i]; no transformed-string radius convention.

Local independent and maximum-length verification only; online AC and ranking pending.

### Library Checker suffixarray / SuffixArray

Library Checker standalone standard string task.



Official generated data accepted locally in normal and sanitizer modes; no online AC or ranking.

### Library Checker longest_common_substring / SuffixArray

Library Checker standalone standard string task.



Official generated data accepted locally in normal and sanitizer modes; no online AC or ranking.

### Luogu P6139 / GeneralSAM

Official generalized suffix automaton template; official sample 1 requires endpos state count 10, not suffix-union minimal partial DFA count 7.



Online submission/hidden tests and ranking unverified. Interpret second output according to official sample endpos-class convention.

### QOJ 10424 / NERC 2024 K / unit_flow_edges

Regional contest application, not a standalone template problem; excluded from formal template coverage.



Online AC/ranking unverified; general unit-edge kernel evidence retained independently.

### Library Checker closest_pair / closest_pair_i64

Official standalone geometry template; outputs original point IDs, including duplicate coordinates.



Online AC and speed ranking pending. Local official-checker acceptance is not online acceptance.

### AOJ CGL_3_C / polygon_contains

Aizu Library of Computational Geometry standalone polygon-point containment task.



Online AC and speed ranking pending. Extended clockwise/degenerate core checks are separate from official input constraints.

### Luogu P4557 [JSOI2018] 战争 / minkowski_sum

Competition application, not standalone template coverage. Minkowski difference plus logarithmic convex containment.



Online AC pending. Does not finish formal template matching for Minkowski sum or convex containment.

### Luogu P3806 / CentroidPairs

Explicit standalone centroid-decomposition template; tests existence of distinct pairs at exact distance. count_leq and broader forest/zero-weight contracts separately checked locally.



No new online submission this batch. Historical snapshots remain separately audited; formal coverage/ranking not inferred from local tests.

### Codeforces 600E / SubtreeColors

Competition application; formal noncompetition template matching remains pending.



No new online submission this batch. Historical snapshots remain separately audited; formal coverage/ranking not inferred from local tests.

### Luogu P2495 [SDOI2011] 消耗战 / VirtualTree

Provincial competition application despite current template-labelled title; formal noncompetition template matching remains pending.



No new online submission this batch. Historical snapshots remain separately audited; formal coverage/ranking not inferred from local tests.

### Library Checker range_kth_smallest / WaveletMatrix

Standalone template problem; local validation only



Online AC and speed ranking pending; extra core APIs and extended inputs have separate local tests.

### Library Checker static_range_frequency / WaveletMatrix

Standalone template problem; local validation only



Online AC and speed ranking pending; extra core APIs and extended inputs have separate local tests.

### Luogu P3834 / WaveletMatrix

Standalone template problem; local validation only



Online AC and speed ranking pending; extra core APIs and extended inputs have separate local tests.

### Library Checker system_of_linear_equations_mod_2 / GaussXor

Standalone template problem; local validation only



Online AC and speed ranking pending; extra core APIs and extended inputs have separate local tests.

### Luogu P4180 / SecondMST

BJWC2010 contest application; not formal standalone template coverage.



No online AC or ranking; local validation only.

### POJ 1681 / GaussXor

Source-model application from kuangbin; original statement access pending.



Original POJ/Bailian statement unavailable; model checked against pinned kuangbin pp37–39 only. No online AC or ranking.

### Luogu P3834 / DivisionTree

Standalone template problem; local validation only.



No online AC or ranking; local validation only.

### Library Checker range_kth_smallest / DivisionTree

Standalone template problem; local validation only.



No online AC or ranking; local validation only.

### Luogu P2762 太空飞行计划问题 / maximum_closure

Application; not formal template coverage



Online AC and rankings pending. P5632 driver prints only the weight; original-side certificate is covered by separate core tests. Arborescence has no edge reconstruction.

### Luogu P4716 / Arborescence

Officially titled standalone template problem



Online AC and rankings pending. P5632 driver prints only the weight; original-side certificate is covered by separate core tests. Arborescence has no edge reconstruction.

### Luogu P5632 / StoerWagner

Officially titled standalone template problem



Online AC and rankings pending. P5632 driver prints only the weight; original-side certificate is covered by separate core tests. Arborescence has no edge reconstruction.

### AOJ CGL_7_D / line_circle_i64

AOJ Computational Geometry standard library exercise; standalone template problem.

Complete vector-style driver in verify/aoj; integer predicates for D/E, original area functions for H/I.

Local verification only; online AC and ranking remain pending.

原始题面与参数：[来源 1](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_7_D)

### AOJ CGL_7_E / circle_intersections_i64

AOJ Computational Geometry standard library exercise; standalone template problem.

Complete vector-style driver in verify/aoj; integer predicates for D/E, original area functions for H/I.

Local verification only; online AC and ranking remain pending.

原始题面与参数：[来源 1](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_7_E)

### AOJ CGL_7_H / CirclePolygon

AOJ Computational Geometry standard library exercise; standalone template problem.

Complete vector-style driver in verify/aoj; integer predicates for D/E, original area functions for H/I.

Local verification only; online AC and ranking remain pending.

原始题面与参数：[来源 1](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_7_H)

### AOJ CGL_7_I / circle_overlap_area

AOJ Computational Geometry standard library exercise; standalone template problem.

Complete vector-style driver in verify/aoj; integer predicates for D/E, original area functions for H/I.

Local verification only; online AC and ranking remain pending.

原始题面与参数：[来源 1](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_7_I)

### AOJ CGL_7_F / CircleTangents

Official standalone library/template problem.

过圆外整数点作切线，输出圆上的两个切点。坐标绝对值≤1000，半径1..1000，保证点严格在圆外。from_point把点作为第一圆，圆上切点在line.b；按x/y字典序输出，每行一个点，绝对误差小于1e-5。

Local verification only; online AC and speed ranking pending.

原始题面与参数：[来源 1](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_7_F)

### AOJ CGL_7_G / IntegerTangents

Official standalone library/template problem.

不同整数圆的公切线，输出第一圆上的全部切点。坐标绝对值≤1000，半径1..1000；可能0..4条，同心不等圆需空输出。整数版已精确排序，直接顺序输出line.a，不再按舍入值排序；绝对误差小于1e-5。

Local verification only; online AC and speed ranking pending.

原始题面与参数：[来源 1](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=CGL_7_G)

### Luogu P5170 / floor_moments

Official standalone library/template problem.

求i=0..n的整除和、整除值平方和、i乘整除值之和，模998244353。t至10⁵，n/a/b/c至10⁹且c>0。核心参数顺序(n+1,c,a,b)，返回顺序是和/带权和/平方和；本题输出索引0、2、1，不能只核对第一项。

Local verification only; online AC and speed ranking pending.

原始题面与参数：[来源 1](https://www.luogu.com.cn/problem/P5170)

### Library Checker partition_function / Partitions

Official standalone template/library problem.

输出0..N的全部整数分拆数，模998244353，N≤500000。构造Partitions后直接读p；p[0]=1表示空分拆。五边形数递推O(N√N)时间、O(N)空间，不是有序拆分。此用法不调用limited。

Online AC and speed ranking pending. Partitions::limited is not exercised by these usages.

原始题面与参数：[来源 1](https://judge.yosupo.jp/problem/partition_function)，[来源 2](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/enumerative_combinatorics/partition_function/task.md)

### Luogu P6189 [NOI Online #1 入门组] 跑步 / Partitions

NOI Online contest application; not formal-template coverage.

正整数非增序列的总和为n，等价于n的无序分拆。n≤10⁵，1≤p<2³⁰且不保证素数；直接构造Partitions(n,p)，输出p[n]。这是比赛应用，单独记录，不替代正式模板题。

Online AC and speed ranking pending. Partitions::limited is not exercised by these usages.

原始题面与参数：[来源 1](https://www.luogu.com.cn/problem/P6189)

### Luogu P5487 / recurrence_nth

Official standalone template/library problem.

给出n个初值，恢复唯一的最短递推并求第m项，n≤10000、n<m≤10⁹、阶数≤5000，模998244353。BM返回c[j-1]乘a[i-j]，首行仅输出系数、不带阶数；裁取恰好c.size()个初值后调用recurrence_nth。全零序列空递推仍输出空首行和第二行0。复杂度O(nk+k²log m)，O(n+k)空间。

Online AC and speed ranking pending.

原始题面与参数：[来源 1](https://www.luogu.com.cn/problem/P5487)

### Library Checker scc (Kosaraju) / SCC

Official standalone library/template problem.

给有向图，输出强连通分量并按缩点拓扑序排列；N、M≤500000，可有重边和自环。题面零基点号先加1；SCC.bel为1..cnt且沿跨分量边递增，按1..cnt输出并将点号减1。不要照搬TarjanSCC的逆序循环。时间、空间O(N+M)，DFS递归。

Online AC and speed ranking pending.

原始题面与参数：[来源 1](https://judge.yosupo.jp/problem/scc)

### AOJ GRL_3_A / removal_components

Official standalone library/template problem.

连通无向简单图，按编号升序输出所有割点，N、M≤100000。输入零基转一基；BiconnectedCore.run后取(before,after)，仅当after[u]>before才输出u-1。本例展示已有点双结果的复用；只求割点优先用更短的Lowlink。时间、空间O(N+M)，递归DFS。该题只核验割点集合，完整删点数量另见UVA10765应用。

Online AC and speed ranking pending. AOJ checks articulation threshold; UVA application checks complete removal counts and ranking.

原始题面与参数：[来源 1](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=GRL_3_A&lang=en)

### UVA 10765 Doves and Bombs / removal_components

Contest/application usage; not formal-template coverage.

分别删去每个站点，按剩余连通块数降序、原编号升序输出前m名；n≤10000，原图连通。m是输出名额而非边数，边表以-1 -1结束，多测以0 0结束，每组末尾空行。after是剩余总块数而非增量，不重复加before。O(n log n+E)时间、O(n+E)空间。应用题不计正式模板覆盖。

Online AC and speed ranking pending. AOJ checks articulation threshold; UVA application checks complete removal counts and ranking.

原始题面与参数：[来源 1](https://onlinejudge.org/external/107/10765.pdf)

### Codeforces 118E Bertown roads / orient_edges

Contest/application usage; not formal-template coverage.

给连通无向简单图，把每条边定向使整图强连通，无解输出0。n≤100000、m≤300000。先用Lowlink.run确认连通且无桥，再调用orient_edges；返回数组与add的原边编号逐项对应，每条逻辑边只加一次。任意可行方向均可。O(n+m)时间、空间，DFS递归；比赛应用不替代正式模板题。

Contest application only; standalone formal-template problem, online AC and speed ranking pending.

原始题面与参数：[来源 1](https://codeforces.com/problemset/problem/118/E)

### Luogu P4630 / block_cut_forest

Contest/application usage; not formal-template coverage.

无向简单图，可不连通，n≤100000、m≤200000；统计存在经过c的简单s-f路径的有序三元组(s,c,f)，三点互异。原点1..n权为-1，方点n+i+1权为blocks[i].size()，树路径权和就是可选c数。sz仅计原点，每棵树独立累计有序端点对，答案用long long。O(n+m)时间、空间，递归DFS。

Contest application; formal-template coverage, online AC and speed ranking pending. Independent simple-path triple enumeration and large closed-form cases checked locally.

原始题面与参数：[来源 1](https://www.luogu.com.cn/problem/P4630)

### Luogu P2860 (bridge forest) / bridge_component_forest

Contest/application usage; not formal-template coverage.

连通无向图，n≤5000、m≤10000；允许已有重边及新增重边，求最少新增边使任意两点间有两条边不相交路径。run后边双缩点，编号1..cnt，邻接项为(边双号,原桥号)。度1点数为L，答案(L+1)/2；只剩一个边双时为0。该公式要求原图连通，不可对任意森林直接套用。O(n+m)时间、空间。

Online AC and speed ranking pending. P2860 only outputs cardinality; returned endpoint certificates and original bridge IDs separately checked by local interface tests.

原始题面与参数：[来源 1](https://www.luogu.com.cn/problem/P2860)

### Luogu P2860 (construct augmentation) / bridge_augmentation

Contest/application usage; not formal-template coverage.

同题的构造接口：连通非空图run后调用bridge_augmentation，返回最少补边方案的原点端点对，点号1..n，可直接逐对使用；题目只输出方案长度。已有边和新增边都允许平行边。接口不修改graph，若需更新原图须自行add并重新run。O(n+m)时间、空间；DFS顺序收集桥树叶子后对半配对，奇数叶子补首叶。

Online AC and speed ranking pending. P2860 only outputs cardinality; returned endpoint certificates and original bridge IDs separately checked by local interface tests.

原始题面与参数：[来源 1](https://www.luogu.com.cn/problem/P2860)

### QOJ 906 (Kosaraju) / SCC

Official standalone library/template problem.

给有向图，输出强连通分量并按缩点拓扑序排列；N、M≤500000，可有重边和自环。题面零基点号先加1；SCC.bel为1..cnt且沿跨分量边递增，按1..cnt输出并将点号减1。不要照搬TarjanSCC的逆序循环。时间、空间O(N+M)，DFS递归。

Online AC on CCF_NOI: 226ms / 76512kb, 11 accepted tests, C++20. Global all-submission speed ranking unresolved; bundled unused algorithms and dag are not covered.

原始题面与参数：[来源 1](https://qoj.ac/problem/906/statement/zh_cn)

### QOJ 999 (BiconnectedCore) / BiconnectedCore

Library Checker standalone standard template task.

Group vertices by bel after run; input and output zero-based, adapted to one-based core

CCF_NOI online AC: 87ms / 42352kb, C++20, 20 accepted tests. Only the edge-biconnected partition is checked; other outputs and global speed ranking remain separate.

原始题面与参数：[来源 1](https://qoj.ac/problem/999)

### Luogu P3398 / path_intersection

Contest application; not a formal template problem.

EulerLCA depth counts edges and shares its root with lca. Boolean intersection only; full endpoints/count independently checked locally.

Global speed rank unverified. Online verdict checks only whether vertices is nonzero; endpoints/count remain local evidence. Contest application does not supply formal-template coverage.

### Codeforces 379F / TreeDiameter

Contest application; not a formal template problem.

Build final tree offline using HLD, then insert vertices in appearance order. Future leaf additions cannot change old pair distances. merge/farthest not called.

Luogu submission form rejected on 2026-09-29: Codeforces RemoteJudge temporarily unavailable. No submission ID or online verdict. Global speed rank unverified.

### CSES 1750 / FunctionalGraph

Standalone direct successor-jump exercise; CSES problem-set task, not a regional contest application.

Convert 1-based vertices to zero-based and add1 to returned vertex. The API supports unsigned64 steps, but CSES only tests up to1e9.

Global speed rank unverified; only stated APIs are covered. Local acceptance does not confer an online AC.

### CSES 1160 / FunctionalGraph

Standalone direct functional-graph reachability/minimum-step exercise.

Subtract1 from both vertices; result is a distance or -1 and must not be shifted. Same component alone does not imply reachability.

Global speed rank unverified; only stated APIs are covered. Local acceptance does not confer an online AC.

### Luogu P2921 / FunctionalGraph

USACO2008 December contest application, not formal-template coverage.

Number of distinct visited vertices equals tail depth plus cycle length; start included. Does not call advance/steps.

Online AC covers decomposition fields only; advance/steps and global speed ranking are not covered.

### SPOJ TTM / Luogu SP11470 / PersistentRange

Direct range-update/history task; origin not established as a non-contest template, conservatively application-only.

Store only changes in zero-initialized tree, add initial prefix sum to every query. ver[logical_time] maps to append-only template IDs; after B, next C overwrites logical slot without mutating old roots. splice not called.

Global speed rank unverified; only stated APIs are covered. Local acceptance does not confer an online AC.

### QOJ 8240 / PersistentRange

2023 ICPC Asia Hangzhou K Card Game; contest application, not formal-template coverage.

Version indexed by left endpoint, coordinate is right endpoint. Range add1 then suffix splice; output point query. Signed increments, arbitrary splice ranges and range sums require separate tests.

Global speed rank unverified; only stated APIs are covered. Local acceptance does not confer an online AC.

### Luogu P4151 / XorWalk

WC2011 competition application, not formal-template coverage.

无向连通带权图，求1到n可重复经过点边的最大异或和；n≤50000，m≤100000，权值≤10^18，允许重边、自环。点号保留1-based，build(1)后query(1,n)。题目保证连通才可直接解引用；通用图先检查optional。此题验证行走，不能改成简单路径。O((n+m)·64)，DFS递归。

Online AC and global speed rank pending; local tests cover only their stated scopes.

原始题面与参数：[来源 1](https://www.luogu.com.cn/problem/P4151)

### Luogu P2731 / UndirectedEuler

USACO Training Section3.3; non-contest training task directly specifying lexicographic undirected Euler trail.

USACO Training：无向多重图保证有欧拉路，输出字典序最小顶点序列。m≤1024，点号1..500；直接构造500个点，不把孤立点1强设为起点。run()自动选较小奇点，若全偶选最小非孤立点，并按邻点排序。输出vertices，共m+1项；本题不输出edge_ids，边编号与方向另验。DFS递归，最深可达m+1。

AC covers automatic-start lexicographic vertex sequence on promised valid inputs. Edge-ID output, rejected inputs and other modes only locally checked. Global speed rank pending.

原始题面与参数：[来源 1](https://www.luogu.com.cn/problem/P2731)

### LC Intersection of F2 Vector Spaces / basis_intersection

Library Checker standalone non-contest template problem.

多组给两个F2向量空间的基，输出交空间的一组基。T≤100000，n,m≤30，输入独立且小于2^30。把输入插入两个XorBasis，调用求交，输出rank和a中的非零主元；答案不唯一，不能逐字比较不同实现输出。模板本身支持64位和相关生成元，属于题外扩展。零维输出0。

Online AC and global speed rank pending; local tests cover only their stated scopes.

原始题面与参数：[来源 1](https://judge.yosupo.jp/problem/intersection_of_f2_vector_spaces)，[来源 2](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/linear_algebra/intersection_of_f2_vector_spaces/task.md)，[来源 3](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/linear_algebra/intersection_of_f2_vector_spaces/info.toml)

### LC Intersection / Zassenhaus / basis_sum_intersection

Library Checker standalone non-contest template problem; only intersection component output.

同一线性空间求交题，约束与前例相同。Zassenhaus返回{和空间,交空间}，本题仅输出second的rank和非零主元，不能据此声称first也获线上验证。和空间由独立本地测试检查。两部分均为独立生成元；无需对输入枚举全部异或值。

Online AC and global speed rank pending; local tests cover only their stated scopes.

原始题面与参数：[来源 1](https://judge.yosupo.jp/problem/intersection_of_f2_vector_spaces)，[来源 2](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/linear_algebra/intersection_of_f2_vector_spaces/task.md)，[来源 3](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/linear_algebra/intersection_of_f2_vector_spaces/info.toml)

### AOJ CGL_2_A / RealPlane

AOJ Library of Computational Geometry standalone template exercise, not a regional-contest application.

每组给两条非退化直线，平行输出2，垂直输出1，否则输出0。输入为绝对值不超过10000的整数，点积与叉积在此范围可由浮点精确表示，所以直接比较0；这不适用于一般实数或更大整数。只演示点向量与dot/cross，不涵盖圆及Result分类。

Online submission and all-submission ranking unresolved; local tests are not online AC.

### AOJ CGL_1_A / line_projection

AOJ Library of Computational Geometry standalone template exercise, not a regional-contest application.

固定直线两端点，对每个点输出其在无限直线上的投影。题目保证两端点不同，整数坐标绝对值不超过10000，q不超过1000；投影可在线段外。接口参数为(p,a,b)，不截断到线段；a=b时模板返回a属于额外边界。

Online submission and all-submission ranking unresolved; local tests are not online AC.

### AOJ CGL_2_D / segment_distance_real

AOJ Library of Computational Geometry standalone template exercise, not a regional-contest application.

求两条闭线段间距离，q不超过1000，整数坐标绝对值不超过10000。先用IntegerPlane精确判相交（含接触和共线重叠），相交输出0；否则取四个端点到另一线段距离的最小值。单点距离接口参数为(p,a,b)。题目线段非退化，点线段属于额外接口边界。

Online submission and all-submission ranking unresolved; local tests are not online AC.

### AOJ CGL_2_C / line_intersection_real

AOJ Library of Computational Geometry standalone template exercise, not a regional-contest application.

输出两条线段的唯一交点；题目保证非平行且相交，q不超过1000，整数坐标绝对值不超过10000，因此可直接取one结果。模板计算支撑直线交点，不自动检查交点在线段内；一般输入须先检查kind。整数方向叉积非零时绝对值至少1，大于本题范围下默认相对阈值。

Online submission and all-submission ranking unresolved; local tests are not online AC.

### AOJ CGL_3_A / polygon_area2

AOJ Library of Computational Geometry standalone template exercise, not a regional-contest application.

给出逆时针简单多边形，3至100点，整数坐标绝对值不超过10000，输出面积并保留一位小数。无需凸包，凹多边形也适用。接口返回有向二倍面积，逆时针为正；取绝对值后按奇偶精确打印.0或.5。本题范围允许将半面积转为long long；一般int128结果不可任意缩窄。

Online submission and all-submission ranking unresolved; local tests are not online AC.

### LibreOJ 115 / BoundedCirculation

Official statement explicitly identifies this as a standalone template problem.

Read each directed edge once; solve a circulation without an artificial t-to-s edge. A feasible result outputs used(i) for the original input-edge IDs, including the lower bound. solve is one-shot and used requires feasibility.

Online AC and all-submission ranking are pending. Local feasible certificates do not prove an online time bound.

原始题面与参数：[来源 1](https://loj.ac/p/115)，[来源 2](https://api.loj.ac/api/problem/getProblem)

### Luogu P1117 [NOI2016] 优秀的拆分 / square_counts

NOI2016 competition application; does not satisfy the noncompetition template requirement.

统计所有子串的非空AABB拆分，不同出现位置、不同A/B长度分别计数，允许A=B。T为1至10，每组小写串长度不超过30000。正向与反向SuffixLCP必须来自同一字符串；start[i]和finish[i]分别计开始/结束于字符i的AA。每个分界点贡献finish[i]*start[i+1]，以long long累加。此为NOI比赛应用题，尚未计入独立模板题覆盖。

Online AC and all-submission ranking unresolved. Local evidence is distinct from online judge acceptance.

### Library Checker Counting Spanning Trees (Undirected) / MatrixTreeMod

Standalone Library Checker template; official statement and parameter metadata checked.

无向多重图生成树计数，模998244353；点号0..n-1，1≤n≤500、0≤m≤500000，允许自环和重边。每条原边权重设1，自环不参与树，重边是不同选择。删去任意根的拉普拉斯行列，这里取根0；n=1的空树计1，断连计0。此接口也支持合数模数，复杂度O(n³ log mod)，本题固定质数亦可选更快的MatrixTree版本。

Online AC and all-submission ranking unresolved. Local evidence is distinct from online judge acceptance.

原始题面与参数：[来源 1](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/graph/counting_spanning_tree_undirected/task.md)，[来源 2](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/graph/counting_spanning_tree_undirected/info.toml)

### Library Checker Counting Spanning Trees (Directed) / MatrixTreeMod

Standalone Library Checker template; official statement and parameter metadata checked.

有向多重图生成树计数，模998244353，要求指定根r能到达所有点，使用away_from_root。n不超过500、m不超过500000，点号及根为0起；每条原边权1，自环忽略，重边分别计数。每个非根点恰有一个入边，根无入边；toward_root表示所有点到达根，不能替代。n=1计空树1，无外向生成树计0。

Online AC and all-submission ranking unresolved. Local evidence is distinct from online judge acceptance.

原始题面与参数：[来源 1](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/graph/counting_spanning_tree_directed/task.md)，[来源 2](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/graph/counting_spanning_tree_directed/info.toml)

### Library Checker Double-Ended Priority Queue / pheap

Standalone Library Checker template; official statement and parameters checked.

多重集合支持插入和删除一个最小/最大值；0≤n≤500000、1≤q≤500000，值在[-10⁹,10⁹]，删除时保证非空。用两个大根配对堆分别保存(-值,id)/(值,id)，同次插入保存两份句柄；删除时先erase另一堆的句柄，再pop当前堆。id每次新插入都递增，重复值也可区分。删除后两份句柄失效，禁止再次使用。本题取负在int范围内；全int64值不能直接照搬取负。

Online AC and all-submission ranking unresolved; join/split covered only by container tests.

原始题面与参数：[来源 1](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/data_structure/double_ended_priority_queue/task.md)，[来源 2](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/data_structure/double_ended_priority_queue/info.toml)

### Luogu P1593 因子和 / divisor_sum_power

Independent divisor-sum template task; Luogu statement and bounds checked. No contest prefix in current title.

给定1≤a≤50000000、0≤b≤50000000，求a^b的所有正约数之和模9901。只分解a，质因子重数e对应e*b+1项几何级数，无需构造a^b或求逆元。a=1或b=0输出1。PollardRho可复用；本题模数固定，但核心允许任意正uint64模数，长度以uint128计算。

Online AC and all-submission ranking unresolved. Independent generated local cases do not constitute official judge data or online acceptance.

原始题面与参数：[来源 1](https://www.luogu.com.cn/problem/P1593)

## 榜单口径

QOJ statistics 的“最快”表会合并同一用户的提交，不能把榜单行号配上全体满分提交数。已核对同一用户三条 AC 的反例，详见 ranking-audits.json。用户要求的所有提交速度排名需另行枚举或找到可靠筛选接口；没有核验前保持待查。读取时间、相邻排名与并列用时范围必须随排名一起保存。
