# Issue 10：赛时码风调整

执行依据：[issue #10](https://github.com/gsh20040816/CPCtemplate/issues/10)。最新要求允许相关短语句合并；无意义的封装与修饰应减少。

## 函数 inline

第一批去除 31 个头文件中 42 处显式函数 inline。按单个 C++ 源文件抄写、打包与提交，函数体及其他非空白文本保持不变；记录见 verification/inline-style.json。这些片段不承诺直接供多个翻译单元重复包含并链接，inline 的 ODR 作用与优化器是否展开调用是不同问题。

保留 DynamicModInt 的 static inline 数据成员：它使类内初始化的可变静态变量成为定义，并非函数内联提示。number_theory_detail/polynomial_detail 的 inline constexpr 函数指针变量暂保留，后续与兼容层一起检查。

## init 到构造函数的待办核对

| 类型 | 当前用途与待改范围 |
| --- | --- |
| PrimitiveRoot、Lucas | 构造仅转调 init；可直接并入构造函数，重置调用改为重新构造赋值 |
| SuffixLCP | 单一来源构造转调 init；可合并，核对重建空串及不同长度测试 |
| Binomial | 默认大小与扩缩容测试、QOJ 8237 驱动使用 init；须同步适配 |
| SuffixArray | 字符串与整数序列共用初始化逻辑；需保留共用实现，避免复制算法体 |
| XorWalk | init 同时清图、访问数组、线性基及 built；构造改写须验证重新构造后的状态 |
| Lagrange | 当前先声明后初始化；需同步 P4781 驱动与调用示例 |
| PalindromicTree | 空构造调用 init；需适配重复建树测试 |
| XorBasis、PositionBasis | init 是清空操作；须核对使用方后决定改名/替换方式 |

以上为实际调用审计，尚未宣称构造函数迁移完成。短语句压缩随具体算法审阅进行，不批量引入逗号副作用或改变执行顺序。
