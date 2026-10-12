# 64位异或仿射变换

WIDA的15 - 矩阵（Matrix）并非普通模矩阵。精确blob 5f16c4a7f59a95446ac34c183fcb6c75b21cfcec使用65个uint64行表示GF(2)上的64位仿射映射：前64项为输入各位的贡献，最后一项是偏置。其QOJ353771原应用页面本轮无法读取，只核对精确片段，不将示例冒充原题协议。

新组件XorAffine64使用vector保存64个线性列及独立bias；可直接赋值col[i]与bias，但col长度必须保持64。默认构造为零变换，XorAffine64(true)为恒等变换。输入/输出都是完整unsigned64位串，不是模某个整数的加法。共有335组件、457份完整用法。

## 应用与复合

apply(x)=bias XOR Σ_XOR(col[i]，其中x第i位为1)。linear只算线性部分。实现遍历置位位号，仅在x非零时调用ctz，不存在ctz(0)。所有移位最大为63。

f.then(g)表示先f后g，即g(f(x))。新列为g.linear(f.col[i])，新偏置为g.apply(f.bias)。列不能调用g.apply，否则会把偏置错误地混入每一列。原稿矩阵乘法与这一顺序一致，测试逐项核对65项结果。

power(k)将同一变换重复k次；k=0返回恒等映射，即使原变换不可逆或为常量也成立。指数支持uint64最大值。二进制幂只需要复合，不需要逆矩阵。

单次应用O(popcount(x))，复合最坏O(64²)，幂最坏O(64² log(k+1))，辅助空间O(64)。这里64位是固定任务域；若大量查询同一变换，可由调用者预存64层倍增结果，示例456为清楚起见逐询问求幂。col与bias是可直接使用的表示，复制对象会复制vector，不共享存储。

## 原稿旋转表达式

readMatrix读取若干项，每项是rotl(x,s) OR A或rotl(x,s) AND A，最后将所有项异或，再异或B。所有项作用于同一个x，不是依次修改x。

AND项对每个输入基向量留下旋转后被A选择的位。OR项满足y OR A=(y AND NOT A) XOR A，所以线性部分取补掩码，偏置异或A。示例457按这个等式构造模板，再做迭代；shift约定0..63，operation=0为OR、1为AND。偏置与系数都可含第63位。

这不是带进位整数仿射运算，也不支持任意非线性布尔表达式。原稿在命名上仅称Matrix，不能据此映射到ModMatrix后就认为覆盖。

## 验证

核心普通NDEBUG、ASan/UBSan各8432项检查：独立64×64逐位矩阵应用，随机稠密变换的复合与小指数反复应用，恒等/常量变换和复制独立性；最大uint64指数用单比特旋转和异或偏置的闭式答案核对。原稿operator*、标量作用及readMatrix都实际调用，并核对独立位旋转AND/OR真值。

两份API的准确纸面程序和头文件驱动，在普通及ASan/UBSan下各84组Python独立真值通过。检查包括同一变换的多次询问、旋转表达式直接计算，以及最大uint64指数的异或开关解析结果。集中用法检查另覆盖456、457，所有当前纸面程序都有匹配哈希。

源代码证据tests/xor_affine64.cpp、tests/xor_affine_protocols.py，运行记录verification/xor-affine64.json、verification/xor-affine-protocols.json。原稿精确字节与GPL-3.0许可在tests/fixtures/wida_matrix。没有新线上AC或OJ性能排名，覆盖条目保留partial，待原应用协议与线上验证补齐。
