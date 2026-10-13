# WIDA 在线模板：简洁版头文件

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `b65beaf95791c63fad526c7f5be34fbcc130c43d`，路径 `01 - 常用在线模板汇总/01 - 初始与杂类/01 - 在线头文件（简洁版）.cpp`。它不是可包含的头，而是一份带 `signed main` 的程序。

没有定义 `ONLINE_JUDGE` 时，它包含 `<bits/wida.h>`。本机没有这个文件，编译失败。加上 `-DONLINE_JUDGE` 后可以编译。`main` 先读 `Task`，再按次数执行空循环。空输入、`0` 和 `4` 都正常退出，并且没有输出。循环体是空的，所以全局初始化里的 12 位小数格式没有被运行结果观察到。`Task` 为负数时条件一直为真，这轮没有跑。

`python3 tests/wida_header_short.py` 在普通 `-O2` 和 ASan/UBSan 下通过这三组输入。没有新的在线 AC，也没有新增模板。来源保持 partial。
