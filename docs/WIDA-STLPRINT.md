# WIDA 打印稿：STL 与库函数

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `13987c4c523997325bba88a0f9888aefac06808a`，路径 `02 - 打印稿模板汇总/12 - STL与库函数.md`。

已排序数组 `1,2,2,4` 里，第一个大于等于 2 的下标是 1，2 出现 2 次。`binary_search` 能找到 4，找不到 3。`iota` 从 3 填到 6。排序后 `unique` 再 `erase`，`2,2,1,1` 变成 `1,2`。

`__builtin_popcount(15)` 是 4，`__builtin_ffs(8)` 是 4，`__builtin_ffs(26)` 是 2，`__builtin_ctz(8)` 是 3。`bit_width(9)` 和 `bit_width(26)` 是 4 和 5。它是标准库函数，不是在名字后面加 `ll` 的内建函数。

`stoi("1010", nullptr, 2)` 是 10，`stoi("c", nullptr, 16)` 是 12，`stoi("0x3f3f3f3f", nullptr, 0)` 是 1061109567。`atoi` 对三个例子分别是 12、-12 和 0。`1,2,3` 的 `next_permutation` 一共 6 个排列。`is_sorted` 和 `accumulate` 与对照一致。`bitset<8>("11101001")` 异或 `"11101000"` 的数值是 1，1 的个数是 5。`to_string(12.12)` 实际是 `12.120000`。

下面这些原文不能编译：`itoa` 在这份标准库里没有；元组初始化写成了 `45000)`；`deque::pop_front` 不接受参数；`lower_cound` 不是成员名；`pair` 没有 `fi`。`gp_hash_table` 还依赖没有定义的 `myhash`。

结构体哈希的相等判断用的是或。只要有一个字段相同就算相等，不能当作键的相等关系。`set` 里删除小于 500 的循环，遇到大于等于 500 的元素会停在原地。优先队列默认是大根堆，原文写成了升序。快速 IO 的构造函数把读文件写成 `out.txt`、写文件写成 `in.txt`。

`python3 tests/wida_stlprint.py` 在普通 `-O2` 和 ASan/UBSan 下通过上面这些例子。没有新的在线 AC，也没有新增模板。来源保持 partial。
