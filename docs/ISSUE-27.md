# 四边形不等式：定义、适用 DP 与优化条件（issue 27）

总册与杂项分册“四边形不等式优化”一节现按 定义与性质 → 分组 DP 的条件与证明 → `monotone_dp_layer` 代码 → P4767 用法 → 区间 DP Knuth 条件与证明 → `knuth_interval_dp` 代码 → AtCoder AWC0100 O 用法 相邻编排，正文为 `docs/knowledge-quadrangle.tex`，排序由 `tools/taxonomy_layout.py` 固定。

## 内容

- 定义：最小化方向的四边形不等式、Monge 矩阵解释、只需验证相邻格的推导；区间包含单调性；最优决策单调性是 DP 决策的性质且依赖并列取法。三者互不等同，并给出两个互不蕴含的反例。
- 分组 DP：状态、合法下标、初值与不可达状态；四边形不等式推出 `opt_g(i)≤opt_g(i+1)`（取最小最优决策）的证明；分治每层 O(n log n)，K 层 O(Kn log n)；与 `monotone_dp_layer` 参数逐一对应，并说明不能用于依赖同层未算状态的转移。
- Knuth：`f(i,i)=0`、w 只在长度≥2 时使用；Yao 引理（f 满足四边形不等式）的归纳证明，指出包含单调性只在 b=c 一步使用；双侧决策关系的推导及并列规则；O(n^2) 的相消计数；两种优化的对照表与 `w=-[l=1]` 反例。

## 代码与验证

新增 `knuth_interval_dp`（`src/compact/monotone_dp.hpp`），`monotone_dp_layer` 函数体未改动；同一头文件新增了函数，所以 P4767 的洛谷 AC 记录对应的打包源码哈希与当前打包不同，记录只证明该函数体。测试见 [DP-OPTIMIZATION.md](DP-OPTIMIZATION.md)。AtCoder 驱动 `verify/atcoder/awc0100_o.compact.cpp` 本地通过全部官方样例与枚举对拍，在线提交待完成。
