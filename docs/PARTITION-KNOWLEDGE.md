# 整数分拆：限制转换与既有接口

本批以084cb44为基线，将原有“整数分拆：重数限制的差一问题”移入固定的“数学 → 组合数学 → 整数分拆”（math/combinatorics/partition.md），补比赛建模中容易混淆的限制。知识分类现为24节/11份源（数学22、图论2），历史附录72节；算法208、用法228不变。

## 新增内容与边界

- Ferrers共轭：每个部分≤k与至多k个部分等势，但不是同一集合
- 恰好k个正部分：每项减1，转为n−k的至多k部分分拆
- 恰好k个互异正部分：减阶梯k,k−1,…,1，转为n−k(k+1)/2的至多k部分分拆
- 每个值出现≤k次：等于只允许非(k+1)倍数部分的分拆数，由生成函数消因子得到；k=1为互异/奇数部分特例
- 空分拆、k=0、负目标和、k≥n及先扩宽阶梯乘法均明确

n=5,k=2时，至多两部分/每部分≤2均为3，恰好两部分为2，而重数限制的整数计数为5，limited返回它对构造模数的余数。n=6,k=2的恰好两部分与互异恰好两部分分别为3和2。Partitions.p仍仅是不限制重数的计数；limited仍只控制每种值的次数，不能替代A_k。A_k可由允许部分1..k的完全背包计算，未新增成员函数或正式用法。

原五边形数定理作为已引用定理保留，本批不宣称补全Franklin对合证明。原来源、HDU页面不可读的说明、历史双版本记录和线上证据边界均保留。原片段及明确修改清单见tests/fixtures/partition-knowledge/，测试逐行重建迁移后的完整正文，防止无记录删改；实现和两份完整用法补齐节号/页号。

## 检查范围

新tests/partition_knowledge.py通过直接递归枚举n≤30的28629个分拆，逐个验证共轭为自身逆；1023组(n,k)核对共轭、减1和阶梯的集合双射与独立完全背包计数。逐个数值的重数统计对照排除(k+1)倍数部分的背包；8432个当前compact limited调用覆盖8种模数、模1、合数、INT_MAX模数和INT_MAX重数上界。有限枚举是核对，不替代理论证明，也不等于验证整个int输入空间。

定向回归另外复用tests/partitions.cpp与tests/partition_recurrence_applications.py。后者原本同时测试分拆完整程序和P5487递推应用，因此保留其实际附带覆盖，不把它伪称为仅分拆或全库测试；它的两个独立参考程序按原脚本保持-O2，在消毒器模式也不启用消毒器。被测分拆/递推程序按该模式编译。

回执verification/partition-knowledge-{normal,sanitizer}.json为cpc-targeted-partition-knowledge-v1，结果以status为准；包含固定classic基线、当前/暂存输入、编译器、辅助运行脚本、日志和生成文件指纹。GNU14.2/Boost、默认PIE/quarantine、LSan关闭；子进程软栈不改变硬限制。不是新的全库回归、线上AC或CI结果。

分类、跨册归属及此前迁移检查继续执行。PDF实际页面和布局记录见verification/partition-knowledge-{visual,layout}.json；字体不变。旧全库回执只覆盖其原始输入，不自动覆盖本批。

## 数学依据

生成函数、有限系数截断及互异/奇数部分恒等式参考MIT18.212第20讲：
https://ocw.mit.edu/courses/18-212-algebraic-combinatorics-spring-2019/resources/mit18_212s19_lec20/

正文给出共轭、平移、阶梯及一般k消因子的具体推导，说明各转换的对象和逆变换，不靠公式名称代替适用条件。
