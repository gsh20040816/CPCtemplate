# WIDA 在线模板：__int128 输入输出

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `29f875f2fe00ce7f1ef7232860d394784af4f738`，路径 `01 - 常用在线模板汇总/01 - 初始与杂类/07 - int128输入输出流控制.cpp`。它使用 `istream`、`string`、`reverse` 和 `function`，但没有头文件，单独编译失败。

读入先把整个单词反转，再从末尾逐个弹出。数字用完之后，循环的更新部分仍会调用 `string::back()`。普通 `-O2` 下，输入 `-12 34` 输出 `-12 34`，`my128::abs(-12)` 是 12。打开 UBSan 后，同一输入到达不可达点并中止。所以这个结果不能当成安全读入。

文件末尾有 `using namespace my128`。它和 `std` 同时可见时，`abs(__int128)` 有多份候选，调用不明确。输出最小的负数时要取负，UBSan 报 negation。

`python3 tests/wida_i128.py` 记录了普通构建的输出和两处中止。没有新的在线 AC，也没有新增模板。来源保持 partial。
