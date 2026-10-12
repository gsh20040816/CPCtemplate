# 素数模 Gaussian 二项式

新增q_binomial及完整API用法443。与分数组件一起，当前327组件、443份完整用法。对应WIDA树cfdb12db6792eb2303798541fb5c760ed2bc618b的`03 - jiangly模板收集/03 - 数论、几何与多项式/13B - 生成函数（q-Binomial）.cpp`，原稿blob 714c557a289286e67617ff4cd5b4725c32dde767，精确字节保存在tests/fixtures/wida_q_binomial/13B.cpp。

## 语义

Gaussian二项式是多项式[n choose k]_q，不是在模p后强行用可能为0的分母相除。q=1取普通组合数；q=0且0≤k≤n时取1；k>n为0。n/k支持完整unsigned long long，q支持整个int范围，p必须是[2,INT_MAX]内的素数。返回规范余数，函数不检测素性。

设非零q的乘法阶为r。使用q-Lucas：结果等于普通C(floor(n/r),floor(k/r))乘以低位Gaussian二项式[n mod r choose k mod r]。低位k>n为0；其余分子、分母因子的指数均严格小于r，因此非零，可以求逆。高位普通组合数再用p进制Lucas。r=1时低位为空积，自然覆盖q=1。

q-Lucas多项式同余可见Meštrović综述[式(101)，第36页](https://arxiv.org/pdf/1409.3820)：以第r分圆多项式取模。因为r整除p-1，r与p互素，F_p中阶恰为r的元素是该分圆多项式的根，因此可代入。本实现还通过不调用q-Lucas的独立生成积系数方法验证。

## 复杂度与整数边界

先试除p-1的不同素因子，再逐次尝试缩小阶；O(sqrt(p))试除，至多O(log p)次模幂，每次O(log p)。低位乘积只循环min(k0,n0-k0)次，维护上下幂的递增/递减，避免原稿每个因子各做模幂。普通Lucas各位循环min(ki,ni-ki)次；空间O(1)。这仍可能在大素数的中间数字上很慢，不声称O(log n)或适用于任意大模数的大量询问。

全部模乘提升为long long。最大临时因子为2p-2，乘积上界2(p-1)^2，在p≤INT_MAX时严格小于LLONG_MAX。试除终止用d≤rest/d，避免d*d的int溢出。n、k不相加，处理ULLONG_MAX无溢出；负q用取余后加p归一化。

## 验证与保留事项

普通和ASan/UBSan各689695项检查：素数2、3、5、7、11、17、31、43的全部q余数，n≤60所有k，用独立Gaussian递推、未修改原稿及新核心三方对照；还覆盖负q、INT_MIN/INT_MAX、ULLONG_MAX端点。原稿可能返回负余数，对照时规范化，不据此冒称数学错误。

完整头文件与纸面程序分别通过NDEBUG普通版和ASan/UBSan。980组大参数真值采用生成积product(1+q^i*x)的周期块多项式快速幂，截断到所需次数，再除去q^(k(k-1)/2)，不调用任何普通或q-Lucas函数；覆盖64位n、靠近0或n的k、0/1/负q与单位根。

本次没有线上AC、原QOJ164128完整题面或排名证据。13B为local-tested，不能由此宣称原题已验收。WIDA13A的q-int返回p进阶数及单位部分，语义不同，仍保持pending；本函数不返回该信息。
