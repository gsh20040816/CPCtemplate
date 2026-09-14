# Issue 10：赛时码风调整

执行依据：[issue #10](https://github.com/gsh20040816/CPCtemplate/issues/10)。最新要求允许相关短语句合并；无意义的封装与修饰应减少。

## 函数 inline

第一批去除 31 个头文件中 42 处显式函数 inline。按单个 C++ 源文件抄写、打包与提交，函数体及其他非空白文本保持不变；记录见 verification/inline-style.json。这些片段不承诺直接供多个翻译单元重复包含并链接，inline 的 ODR 作用与优化器是否展开调用是不同问题。

保留 DynamicModInt 的 static inline 数据成员：它使类内初始化的可变静态变量成为定义，并非函数内联提示。number_theory_detail/polynomial_detail 的 inline constexpr 函数指针变量暂保留，后续与兼容层一起检查。

## init 到构造函数的逐项核对

| 类型 | 当前用途与待改范围 |
| --- | --- |
| PrimitiveRoot、Lucas | 已直接并入构造函数，重置测试改为重新构造赋值 |
| SuffixLCP | 已合并入构造函数，保留重建空串及不同长度测试 |
| Binomial | 默认大小与扩缩容测试、QOJ 8237 驱动使用 init；须同步适配 |
| SuffixArray | 整数序列构造函数直接构建；字符串按无符号字节转换后复用它，重建改为重新构造赋值 |
| XorWalk | 已直接构造空图；重新构造赋值清图、访问数组、线性基及 built，验证重建后的状态 |
| Lagrange | 已改为任意点/连续点两个构造函数；P4781 驱动与重建调用同步适配 |
| PalindromicTree | 已直接构造两根与哨兵；重复建树测试改为重新构造赋值 |
| XorBasis、PositionBasis | init 是清空操作；须核对使用方后决定改名/替换方式 |

以上为实际调用审计，尚未宣称构造函数迁移完成。短语句压缩随具体算法审阅进行，不批量引入逗号副作用或改变执行顺序。

PrimitiveRoot、Lucas、SuffixLCP 的首批迁移已通过原有独立枚举/对拍测试的普通及 ASan/UBSan 两种模式，源码哈希与证据见 verification/constructors.json。后缀 LCP 在原字号下一页展示完整结构，原根在方法边界分页。其余类型继续按上表处理。

回文树与异或行走的直接构造已通过普通及 ASan/UBSan 原有对拍；20 万规模和重新构造测试保留。证据见 verification/state-constructors.json。e739d1d 的全量普通及消毒器回归均已通过；后续改动按对应专项测试记录。

Lagrange 的任意点/连续点构造与原有多项式对拍在普通、ASan/UBSan 模式均通过；P4781 驱动另执行 100 组独立多项式求值，含 2000 点规模。见 verification/lagrange-constructors.json；旧在线 AC 不迁移为当前驱动的在线验证。

SuffixArray 的整数构造已承接共用算法体，字符串入口保留 unsigned char 转换后复用构造结果；不复制倍增实现。完整字节集、整数字母表、空串重建、百万周期串与下游 SuffixLCP 在普通及 ASan/UBSan 模式通过，见 verification/suffix-constructors.json。
