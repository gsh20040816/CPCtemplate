# 编译检查与 GNU 扩展示例

Issue #17 第二章的两项增补。印刷稿直接包含 examples/infra 下的 int128_io.cpp、type_probe.cpp、gnu_bits.cpp、diagnostics.cpp 和 warnings.cpp。前3个是可运行示例；diagnostics.cpp 故意含4种错误，每次只在对应检测选项下运行；warnings.cpp 仅编译观察警告，不能执行其格式不匹配的 printf。

## 验证

运行 `python3 tests/infra_checks.py`，收据 `verification/infra-checks.json` 记录命令、编译输出、运行退出状态、诊断与源码哈希。当前宿主为macOS arm64、Homebrew GCC16.2.0、libstdc++，不是原生Linux验证。

- int128读写使用Python整数作为参考，含3000个固定种子随机值、±边界、前导零/正号、只有符号、非数字、超范围及500位输入；strict C++20和GNU++20均分别用O2、ASan/UBSan运行。
- 额外检查空字符串及其他解析失败不改变输出参数。最小负数解析经`-i128(value-1)-1`构造，输出经无符号幅值转换，避免直接对最小负数取负。
- 位集合低位遍历检查65536个掩码、64个单置位边界；bitset查找覆盖130个位置及无下一位的size哨兵。
- 运行4项对应错误，要求非零退出且诊断类型匹配；检查4类编译警告。
- GCC16在strict C++20与GNU++20下的`is_integral_v<__int128>`均为true，strict宏分别1/0；这修正了不能套用旧版本trait结果的假设。`-pedantic-errors`拒绝本例直接使用`__int128`的写法。标准、GNU模式和pedantic是不同维度。

测试不会在无检查器的配置下运行故意越界或UB样例，也不将检查器能捕获这些例子推论成捕获所有错误。没有执行CI。

## 资料依据

标准链接保留在开发文档，不进入印刷正文。

- [GCC检查器选项](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html)
- [libstdc++ debug模式与ABI约束](https://gcc.gnu.org/onlinedocs/libstdc++/manual/debug_mode_using.html)
- [libstdc++断言宏](https://gcc.gnu.org/onlinedocs/libstdc++/manual/using_macros.html)
- [GCC警告选项](https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html)
- [GCC 128位整数扩展](https://gcc.gnu.org/onlinedocs/gcc/_005f_005fint128.html)
- [GCC位内建函数](https://gcc.gnu.org/onlinedocs/gcc/Bit-Operation-Builtins.html)

bitset扩展行为同时以本机libstdc++实现及实际运行验证；后续换比赛工具链应重新执行探针。
