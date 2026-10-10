# SIMD 原生验证

Issue #17 第二章。印刷源码直接读取 examples/infra/simd.hpp 与 simd_demo.cpp。Linux测试：`python3 tests/infra_simd.py`；要求测试CPU支持AVX2和AVX512F，且已安装GCC、objdump。测试器先检查CPU能力，示例本身采用赛场已确认指令集的前提，不提供运行时分派。

本轮在用户desktop主机的隔离临时目录执行：AMD Ryzen 7 9700X、Linux x86_64、GCC16.2.1 20260810。完整CPU信息、命令、输出、源文件SHA-256、自动向量化报告、目标函数反汇编及9次原始样本保存在 verification/infra-simd.json。远端绝对路径保留为执行现场记录。

O2 -mavx2 与 ASan/UBSan 两配置均通过：加法遍历长度0至1024，三个数组分别紧贴不可访问保护页，检查无过读和过写；输入含随机32位整数，按无符号模加法与标量比较。比较函数覆盖上述长度及INT_MIN、-1、0、1、INT_MAX阈值。演示额外检查UINT_MAX回绕、INT_MIN、逆序及3项掩码尾部。比较数组用普通vector，其尾部由ASan检查。大于1024的全部长度并未穷举；循环条件改为i<=n-width，避免接近INT_MAX时加法溢出，尾部位移限制在1至15。

性能组：2^20项uint32加法，100次调用，每轮编译器内存屏障，计时外初始化和全量核验。9个进程交错运行，各中位数为自动循环8.538231ms、AVX2 8.204672ms、AVX512F 7.852265ms。未绑核、固定频率或排除其他负载，不把小差异解释为稳定优势。自动循环使用不别名的restrict约定，与手写版本契约一致；反汇编目标函数确有ymm vpaddd。未新增算法组件或OJ AC。

依据：
- [GCC向量化报告](https://gcc.gnu.org/onlinedocs/gcc-12.5.0/gcc/Developer-Options.html)
- [GCC函数选项pragma](https://gcc.gnu.org/onlinedocs/gcc/Function-Specific-Option-Pragmas.html)
- [Intel指令参考](https://www.intel.com/content/dam/develop/external/us/en/documents/319433-024-697869.pdf)
- [Intel逻辑操作intrinsics](https://www.intel.com/content/www/us/en/docs/cpp-compiler/developer-guide-reference/2021-9/intrinsics-for-logical-operations.html)

常用指令表是接口速查，不声称每个表项都由本测试执行。实际执行示例与检查范围以上述收据为准。
