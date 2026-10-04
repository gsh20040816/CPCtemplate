# SA-IS：与倍增并列的线性后缀数组

依据 issue #3 的 ACL 对照缺项新增独立 `SAIS`。保留 `SuffixArray` 的倍增实现与已有使用者，不将已有后缀数组功能重复算作缺失。赛时一般规模可以继续抄较熟悉的倍增版；需要线性构造或大量重复串时可选择本版，实际常数与机器有关，不宣称性能排名。

## 契约

- `SAIS(s, alphabet)` 接受整数向量，`1 <= alphabet < INT_MAX`，每个符号在 `[0, alphabet)`，`n < INT_MAX`
- `SAIS(string)` 将每个字节转成 `unsigned char`，字母表为256，支持嵌入零字节和128..255
- 不附加公开哨兵，不把空后缀放入结果。`sa/rk/lcp` 都长 n：`sa[k]` 是第 k 小非空后缀的起点，`rk[sa[k]]=k`，`lcp[0]=0`，`lcp[k]` 是 `sa[k-1]` 与 `sa[k]` 的公共前缀长度
- 空输入产生三个空向量；所有下标0-based。输入不被修改，可通过赋值重新构造。内部递归仅用于缩小后的命名串
- 前提由调用方保证；断言不是 NDEBUG 下的输入校验。内存分配失败可抛出标准异常

时间及额外空间均为 `O(n+alphabet)`。alphabet 是实际分配大小，不是仅作范围注释；例如稀疏整数不能直接给一个巨大 alphabet。先进行保序离散化需要额外 `O(n log n)`，不能把包含排序预处理的全过程仍写成线性。

## 诱导排序的三个阶段

这里使用 ACL 的无显式哨兵约定：末位置是 L 型，`type[n-1]=false`。向前分类，相邻字符相等时继承后一位置的类型；否则当前字符较小是 S 型。LMS 是前一位置 L、当前位置 S 的转折点。末位置既不当作 S 型哨兵，也不加入 LMS。

同字符桶内，L 型后缀排在 S 型之前。`lo[c]` 是桶首，`hi[c]` 是 S 区首，`lo[c+1]` 是桶尾的后一位置。两个计数数组都有 alphabet+1 项；`hi[alphabet]` 不使用。

一次 induce：
1. 将给定 LMS 顺序放到各桶 S 区；清空其余位置
2. 显式放入末后缀 n-1，从左到右扫描已有后缀，将 L 型前驱放入相应桶头。相同首字符的前驱次序由其后一后缀次序决定，因此稳定诱导得到 L 顺序
3. 重置桶游标，从右到左扫描，将 S 型前驱从桶尾向前放入。反向扫描加反向写入维持同样的稳定次序

第一轮 LMS 仅按原位置投入，能够排好 LMS 子串，尚不保证完整 LMS 后缀排序。按第一轮结果给 LMS 子串命名，名称写回 LMS 的原位置顺序；递归排序名称串，再按递归结果恢复 LMS 顺序并最终诱导。

## LMS 相等与递归

一段 LMS 子串从当前 LMS 到下一 LMS，比较包括下一 LMS 的字符。首先比较两段的端点距离；相等时比较内部及下一端点。共同的 S 型右端点与字符序列反向确定内部类型。最后一段以 n 为结束标志，不能与普通子串合并；代码在读取端点前同时检查两个下标仍小于 n。

相同名字对应相同长度和内容的块。名称串的第一个不同名字决定原后缀的先后；相同名字可同时跳过等长块，因此递归给出完整 LMS 后缀顺序。名称串的最后一个名称不保证最小，例如 `[3,0,3,2,3]` 的 LMS 名称为 `[0,1]`；递归必须沿用无哨兵约定，不能偷换成假定末尾最小的版本。

LMS 不相邻且两个端点都不是 LMS，数量至多 `floor((n-1)/2)`。每层扫描和诱导线性；相邻 LMS 子串比较使每段最多参与两次，总比较量也线性。递归规模不断减半，后续字母表不大于当前名称串长度，故总时间和空间 `O(n+alphabet)`，递归深度 `O(log n)`。

## LCP、界与配合

构造完 sa 后用 Kasai 的相邻前驱版本求 lcp：位置前进一格时已有公共前缀至少减少一，遇到 rk=0 清零。数组下标加法先由 `k<n-i && k<n-j` 保护。桶计数和游标至多 n，所有 next-LMS 端点由现成下标或 n 提供，长度用减法计算，不需要额外的 n≤INT_MAX/2 限制。

本版输出语义与倍增相同，但 `SuffixLCP` 的构造函数目前显式接受 `const SuffixArray&`，不能直接传 SAIS。不要仅凭字段相同就声称自动兼容。需要桥接时可以先构造空 `SuffixArray(vector<int>{},1)`，复制三个结果向量，再传给 SuffixLCP；这个步骤有 O(n) 复制成本。本轮不改变原组件的构造语义，也不把桥接当作新增受测接口。

## 正式用例与验证范围

example-241 使用 Library Checker `suffixarray` 协议：长度1..500000的小写串，输出0-based起点。驱动、打包程序和最小抄写形式分别接受独立 Python 后缀枚举与50万字符闭式数据；核心测试还覆盖空串、全字节、整数稀疏字母表、重新构造、LCP区间最小值与百万字符周期串。

测试断言不依赖 NDEBUG；头文件与正文复制形式分别在断言开/关模式运行，并加入错误结果、LCP偏移等负对照。报告绑定实际源码与编译器。旧倍增实现的线上 AC 和旧官方数据记录保持历史含义，不转记为本版成绩；不声明新的线上 AC、跨平台性能或 LeakSanitizer 结论。

## 来源

诱导排序由 [固定 ACL string.hpp](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/string.hpp) 改写，许可 [CC0-1.0](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/LICENSE)。移除了小规模 naive/doubling 分支，改成 alphabet 的半开范围、显式端点保护与本库 n 长度 LCP；不复制上游 string 入口的有符号 char 转换。

理论参考：Nong、Zhang、Chan，[Two Efficient Algorithms for Linear Time Suffix Array Construction](https://www.cin.ufpe.br/~paguso/courses/if767/bib/Nong_2011.pdf)。正式题目的 [固定题面](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/string/suffixarray/task.md) 与 [规模参数](https://github.com/yosupo06/library-checker-problems/blob/e64660561a995c357cdc61ddee1bde68b80528db/string/suffixarray/info.toml) 独立于算法来源。
