# WIDA 分数模板：原稿审计起点

这是原稿缺陷发现时的历史记录。后续已补Rational及两份用法，最新范围与验证见[FRACTION.md](FRACTION.md)；下文的pending描述保留为当时状态。

来源树 cfdb12db6792eb2303798541fb5c760ed2bc618b，路径 `03 - jiangly模板收集/04 - 数据结构/09 - 分数四则运算（Frac）.cpp`，blob 7b4036c7e2601bf74a360f7f4ed662c8a993811a。GPL-3.0 原稿逐字节保存于 tests/fixtures/wida_fraction/Frac.cpp；来源注释引用 QOJ498911，本次未取得该原题完整协议。

原稿可复现的自除别名问题：`Frac<long long> x(2,3); x /= x;` 得到1/3，而用非修改运算 `x / x` 得到1。原因是 `/=` 首先把num乘以rhs.den，rhs与自身别名时rhs.num随之变化，下一句den再乘rhs.num就使用了新分子。这个反例不涉及整数溢出或除零；普通和ASan/UBSan均复现。测试断言的是原稿已知行为，不代表该结果数学正确。

后续新增公开模板必须明确非零除数、正分母及约分规则；复合运算应先计算临时结果再赋值，保证自加、自减、自乘、自除均成立。固定宽度整数需要说明中间积和符号边界，尤其不能把最终结果能表示等同于中间积不溢出。原稿在输出时才约分，反复运算的数值范围还需要单独审计。另一份分数来源及一般分数组件尚未完成，覆盖表保持pending；不把此反例报告算成已补齐模板。

复现：`python3 tests/wida_fraction_source.py`。证据：verification/wida-fraction-source.json。
