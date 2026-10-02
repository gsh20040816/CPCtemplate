# 有限状态计数到线性递推：知识与验证

`knowledge-state-recurrence.tex` 在固定 OI 导航的“数学 / 线性代数 / 特征多项式”下补充两页知识：固定有限维线性状态、列转移的方向与重数、Cayley–Hamilton 的伴随矩阵系数消去证明、标量序列阶数≤d，以及目标素数域中前2d项为何足以支持BM外推。

模型使用不含连续子串101的二进制串，说明状态构造、空串、初值与现有接口。对比直接DP、矩阵幂、BM+二次递推求项和NTT版Bostan–Mori，显式计入采样及求逆成本。保留合数模数、NTT容量、标量与矩阵最小多项式区别、2d−1项不足、幂零初始瞬态及尾零不能删除等边界。

分类增至七份知识源文件、18个带标签节。算法207、完整题目用法221、正式模板覆盖153不变，没有新增特征多项式/矩阵最小多项式算法或线上AC。历史附录和相关OI页面的其余范围仍待审计。

## 测试入口

- `python3 tests/state_recurrence_knowledge.py`：精确数学、状态建模与真实C++接口流水线
- `python3 tests/state_recurrence_snippet.py`：提取正文唯一lstlisting原样编译执行
- 两者支持 `--mode normal|sanitizer` 和 `--report`；不指定mode时读取SANITIZE/CPC_SANITIZE，默认普通模式。默认生成物/报告写入新的build子目录；导入不会运行测试，拒绝Python -O
- `tests/state_recurrence_usage.cpp` 只使用已有 `berlekamp_massey`、`recurrence_nth`、`BostanMori` 核心，不另写BM参考实现

## 独立参考及范围

Python用排列展开计算小整数矩阵的特征多项式，再以任意精度整数验证χ(A)=0。穷举所有1–3顶点带自环Boolean有向图，共530张，4674对起终点；显式枚举长度0–4的路径，23370次核对。另枚举长度0–12的全部8191个二进制串，直接检查子串101，与状态转移独立比对。

图模型及命名边界案例在4个素数（2、3、5、998244353）和6个合数（4、6、8、9、12、1000）下共46800组。真实C++二次递推求项1638000次，其中468000次使用只看前2d项的BM系数；NTT版Bostan–Mori在998244353下另234000次。合数只测试独立已知特征递推，不传给BM或NTT。

每组查询下标0–20、21、64、10^18及ULLONG_MAX，参考是独立矩阵向量迭代/矩阵幂，不由被测递推生成。包含零输出、不可达状态、重复特征值、幂零瞬态与标量阶数更小的情况。文中两状态λ=0/1反例也用真实BM验证，保留[0,0]和[0,1]的长度；diag(1,2)投影反例在F2仍有效。

正文原样listing额外检查17个下标，包括长度0–12和上述远项。包装仅声明unsigned long long N、输入N和输出answer；列表中的BM/递推调用保持原样。

这些有限精确检查支撑实现和模型，不替代正文的一般证明，也不声称计算了所有矩阵或任意状态规模。

## 可复核证据

- `verification/state-recurrence-normal.json`
- `verification/state-recurrence-sanitizer.json`
- `verification/state-recurrence-snippet-normal.json`
- `verification/state-recurrence-snippet-sanitizer.json`

报告绑定前后测试、正文、递归头文件、编译器驱动及cc1plus哈希，记录生成输入/程序/可执行文件与输出；不把这些哈希称为整个系统工具链的完整绑定。使用默认PIE和ASan默认quarantine，当前环境关闭LSan。普通/ASan+UBSan分别运行；耗时只记录执行过程，不用作性能比较或OJ时限证明。

文档分类/正文保留/引用检查为18节；最终PDF布局和实际页面检查见 `verification/state-recurrence-layout.json`、`verification/state-recurrence-visual.json`。字体字号不改。旧52d81d1整库回执仍只对它当时的源快照有效，不能计入本次新增文件；已知浮点几何判题限制继续保留。
