# 赛场环境与调试：执行记录

Issue #17 第四章，源码 examples/infra/{environment.cpp,debug_local.cpp,debug.gdb,memory.cpp,interactive.cpp,interactor.py} 直接用于印刷。测试入口 `python3 tests/infra_environment.py`，要求Linux x86/GCC、GDB、GNU time/coreutils及Python3；这是一套限定环境的赛场例子，不做跨平台探测和回退。

在用户desktop的隔离目录执行，原生Linux x86_64，AMD Ryzen 7 9700X、GCC16.2.1。命令、完整stdout/stderr、返回码、文件SHA-256见 verification/infra-environment.json。

已执行：
- 基础目标O2编译环境探针，输出编译器、语言标准、PBDS实际查询、int128大小、栈软硬上限、CPU支持和带校验输出的速度循环。此次只探测本地Linux机器，没有声称已在任何OJ或比赛评测机运行。
- O0 -g -DLOCAL示例输入7，stdout为49、stderr为x=7；输入负数产生断言失败。GDB在square断点观察x=7、result=49与main调用帧，并单步、运行到行号、finish及continue。
- GNU time两种格式、Bash time、/proc/self/status、clock、子shell软栈/虚拟内存限制；memory示例累加结果499999500000。timeout对sleep返回124。未据此宣称RSS与OJ口径相同。
- 交互选手在1至100的所有秘密值下通过，裁判限制最多7次询问，记录双方消息。五份故意损坏的选手分别模拟错误答案、畸形协议、不刷新、多余输出、非零退出；前后四种返回失败，不刷新由外部timeout得到124。裁判要用正常Python，不能用删除assert的-O模式。单行小协议示例不是通用恶意进程隔离器。

开发过程发现当前GCC16的bits/stdc++.h没有提供本例需要的assert，已显式包含cassert并重新验证。GDB脚本中的until行号随最终源码调整；印刷示例保持同源。

未执行编辑器GUI快捷键操作，正文只是现场检查清单。键位可能被桌面或扩展改写，需使用者热身确认。探针不能从__VERSION__/__cplusplus还原所有评测编译选项；完整命令须查比赛说明。

依据：
- [GDB单步、继续与返回](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Continuing-and-Stepping.html)
- [Linux内核/proc文档](https://www.kernel.org/doc/html/latest/filesystems/proc.html)
- GNU time本机`--help`、Bash本机`help ulimit`及实际运行输出；参数与单位以Linux/GNU环境为准。

所有例子都是基础设施演示，没有新增算法组件和OJ AC。后续调整源码要重新生成对应执行收据，不能沿用旧哈希。
