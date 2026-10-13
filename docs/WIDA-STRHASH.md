# WIDA 在线模板：字符串哈希

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `a099684db509fe70a03bf9ab0eadb4e4c8bb8c54`，路径 `01 - 常用在线模板汇总/04 - 串与数据结构/35 - 字符串哈希.cpp`。它使用 `vector` 和 `string`，但没有头文件，单独编译失败。

`val[i]` 存的是 `BASE` 的 `i` 次幂，不是字符串前缀哈希。模数 1000、进制 10 时，前四项是 1、10、100、0。`get` 把每个字符加进整串哈希。`"ab"` 得到 68，空串得到 0。`modify` 按这个幂替换一个字符，改首字符或末字符都与重新计算一致。没有子串查询。

文件末尾的 `mod` 是 `1000000007`，`base` 是 127，结构体本身不用它们。用这组参数替换一个字符时，幂和差值的乘积超过 `int`，UBSan 报 signed integer overflow。

`python3 tests/wida_strhash.py` 在普通 `-O2` 和 ASan/UBSan 下通过小模数例子，并记录了大幂溢出。没有新的在线 AC，也没有新增模板。来源保持 partial。
