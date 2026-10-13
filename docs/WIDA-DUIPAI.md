# WIDA 在线模板：对拍说明

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `632a72ec2ef746f054de87c894848f8474587237`，路径 `01 - 常用在线模板汇总/01 - 初始与杂类/03 - 对拍相关.md`。这是一份 Windows 对拍笔记，不是可收录的算法模板。

C++ 循环调用 `Juruo.exe`、`Shenben.exe`、`Ask.exe`，再用 `fc` 比较输出。在这台机器上这三个程序都不存在，`system("fc ...")` 三秒内没有返回，所以没有走到打印 `Wrong Answer` 的分支。源码里那个分支使用 `exit(0)`，即使走到了，进程状态也是成功。`clock` 的差值被标成毫秒，但这台机器的 `CLOCKS_PER_SEC` 是 1000000。

bat 片段写成 `if errorlevel==1`，不是 `if errorlevel 1`。这里没有运行它。

样例程序在没有 `ONLINE_JUDGE` 时包含 `<bits/wida.h>`，本机编译失败。加上该宏后可以编译。`main` 是空的，初始化把标准输出改到 `Ask.txt`，运行后文件是空的。

两段 `freopen` 分别把 `Ask.txt` 读入并写到 `Shenben.out` 和 `Juruo.out`。放入 `ping` 后，两个输出文件都是 `ping`。

`python3 tests/wida_duipai.py` 记录了这些结果。没有新的在线 AC，也没有新增模板。来源保持 partial。
