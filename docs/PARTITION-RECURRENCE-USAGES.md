# 整数分拆与短阶递推完整用法

新增158–160，不改动两个核心头文件。

- [Library Checker partition_function](https://judge.yosupo.jp/problem/partition_function)：输出p(0)..p(N)，N≤500000，模998244353。Partitions为五边形数递推，O(N√N)时间、O(N)空间；输出p[0]=1。固定官方仓库e64660561a995c357cdc61ddee1bde68b80528db的题面/元数据、11份生成数据及checker均在本地核对。
- [Luogu P6189](https://www.luogu.com.cn/problem/P6189)：非增正整数序列求和为n，对应无序分拆。n≤100000，模数1≤p<2³⁰，不保证素数。该题是NOI Online比赛应用，另记application，不借它关闭正式模板题要求。
- [Luogu P5487](https://www.luogu.com.cn/problem/P5487)：n≤10000，n<m≤10⁹，最短阶数≤5000且唯一。首行只输出递推系数，不能仿照Library Checker find_linear_recurrence额外输出阶数。官方两个样例为[1,1]及第10项89、[3,2]及第10项691707。BM系数c[j-1]乘a[i-j]，裁取恰好k个初值给recurrence_nth，保持两行输出；空系数时首行仍为空行。

## 验证方法

`tests/partition_recurrence_applications.py` 编译三份完整驱动；设CPC_SANITIZE=1运行ASan/UBSan。

- 8份全分拆表与Python任意精度完全背包对照到1000。
- 42份P6189输入含n=100000、模数1/2/6/97/1000000006/1073741823。另用`tests/partition_split_oracle.cpp`独立对照：小于等于B的部分用完全背包；大于B的部分按恰好count个维护，删去一个最小部分或所有部分同时减1得到转移，最后与小部分方案卷积。B=floor(sqrt(n))，不使用被测五边形数递推。该参考在小输入上再与任意精度背包交叉核对。
- 289份P5487输入，包含官方样例、全零、有限初始段、穷举低阶参数和随机输入。小规模参考逐阶高斯消元建立所有递推方程，确认最短性和唯一解，伴随矩阵幂求远项；五个负例拒绝多余阶数、错误系数方向、错误远项及丢失空首行。
- 最大5000阶由`tests/recurrence_vandermonde.cpp`构造s[n]=Σ(t^n),t=1..k。特征多项式∏(X-t)给出全部系数；Hankel矩阵为VVᵀ，底数在素数域中互异，故Vandermonde矩阵可逆，确证最短阶数恰为k。第10⁹项直接把每个底数快速幂相加，与被测多项式求余方法独立。小阶同构造还与高斯/矩阵参考核对。

`tools/official_cases.py` 用固定官方11份partition_function输入/答案和checker测试普通与消毒器模式，并确认故意错误输出被拒绝。官方参考使用NTT多项式方法，与本库五边形递推不同。报告为verification/partition-official*.json；不是线上提交记录。

同时重跑`tests/partitions.cpp`和`tests/recurrence.cpp`：有界重数枚举、任意精度背包、BM小域穷举最短性、保留项验证，以及合数模数/完整uint64下标的独立矩阵幂。历史classic只在固定提交1a9fa3e91d7dff58915341040be069611370054c的临时测试目录出现，不恢复第二套库。

本轮不宣称Partitions::limited已有正式题用法，不把P5487的素数域BM扩展到合数。recurrence_nth单独给定递推系数时可用合数模数。三份书册精确拼装程序有各自双模式执行记录；线上AC和速度排名仍待完成。CI保持停用。
