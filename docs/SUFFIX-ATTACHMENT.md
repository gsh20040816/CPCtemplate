# 附件后缀数组与 SAM

核对 issue #11 实际 5–8、10–11 页（1.2.1/1.2.2、1.4.1）。保留已有 vector 核心，
新增 P3804 与 LC 最长公共子串完整用法，另增加 LC 后缀数组适配。

## 倍增与整数序列

附件两份都是倍增计数排序，不是 DC3 或 SA-IS。第一份初始字符映射 a..z 为1..26；
第二份直接以 A[i] 作桶下标，初始 lim=len，要求编码在已分配和初始化的桶范围内。
不能将任意负数或大整数直接代入。两份均使用1-based后缀起点和排名。

本库 SuffixArray(s) 按 unsigned char 的0..255排序，支持内嵌零字节；
SuffixArray(a,alphabet) 接受0..alphabet-1，内部加一给越界第二关键字保留零。
任意有符号值先排序去重、lower_bound保序压缩；相等值必须得到同一编码。
空间O(n+alphabet)，时间O(n log n+alphabet)，不要为了稀疏大值按最大原值开桶。
空串/空整数序列合法，不输出空后缀；重新赋值可重建。

sa[k]是第k个非空后缀起点，rk为其逆排列，lcp[k]比较sa[k-1]和sa[k]，lcp[0]=0。
[Luogu P3809](https://www.luogu.com.cn/problem/P3809) 当前长度至100万，大小写字母和数字按ASCII排序；输出起点需加一。
Kasai跨到最小排名时将滚动长度清零，避免留下上一次前缀长度。
本库倍增宽度在越过n前已经区分全部非空后缀，因此n<INT_MAX条件下不会执行溢出的下一次倍增。

## 附件的分隔符截止 LCP

第二份附件的height扩展还检查`A[pos]<=save_total_map`，并非无条件普通LCP。
这意味着特殊编码只参加后缀排序，不能被公共前缀跨过；同一分隔符可能重复。
本库先正常构造，再令remain[i]为位置i向右、遇到第一个分隔符前的普通字符数，分隔符处为零：

```cpp
vector<int> remain(n + 1);
for (int i = n - 1; i >= 0; i--)
    if (a[i] < ordinary) remain[i] = remain[i + 1] + 1;
auto height = suffix.lcp;
for (int k = 1; k < n; k++)
    height[k] = min({height[k], remain[suffix.sa[k - 1]], remain[suffix.sa[k]]});
```

ordinary是普通编码个数；分隔符统一编码到其后，其它已离散化编码亦可用独立标记数组判断。
截断后的height是分段LCP，原suffix.lcp仍保留普通LCP语义，不能混用。
证明只需观察两种阻止扩展的条件：字符不同，或者任意一端到达分隔符。
两者共同决定的最大长度就是三个上界之最小值。

LC longest_common_substring 用两个小写字符串加编码26的分隔符拼接，alphabet=27。
扫描相邻、分别属于两串的后缀；跳过分隔符起点，并按两个原串的剩余长度截断。
最长公共前缀的后缀在SA中形成连续区间，包含两种来源时必有相邻异色对，所以相邻扫描足够。
输出两串各自0-based半开区间；没有公共字符时输出两个空区间。当前各串长度至50万。

## SAM 的种子、克隆和计数

附件endpos[now]=id是插入时存放的位置/外部标记，克隆置零；它不是已经汇总的出现次数。
本库occ仅作计数种子：每次真实extend的新状态为1，克隆为0。
如果题目需要每个前缀结束位置所对应的状态，调用者在extend后保存last，不能把计数当位置。
附件还声明了link树edge，但所示代码未使用，也未在Clear中清空那些vector；不能当作已经维护好的树接口。

真实非根状态u代表长度区间(len[link[u]],len[u]]，这些子串拥有相同endpos集合。
因此不同子串数量是所有区间长度之和；出现次数是沿link从长向短汇总种子。
克隆可能晚于其子状态创建，不能仿照PAM直接按节点编号逆序传播；counts按len计数排序后倒序传播。
counts返回副本，不改occ，重复查询、查询后继续extend安全；根返回输入长度n，不是空串的n+1个出现位置。
仅在非根节点上解释子串频次；清空使用重新赋值SuffixAutomaton()。
字符输入是0..25的小写编码。固定26字母表构建O(n)，counts/distinct均O(n)，空间O(26n)。

[Luogu P3804](https://www.luogu.com.cn/problem/P3804) 只考虑次数大于1的子串，最大化长度乘次数。
同一状态内次数相同，取最长长度len即可；乘积为long long。没有重复子串时输出零。
本题不要求最小DFA或广义SAM状态数，不能据此替代那些独立问题的验证。

## 独立证据

- tests/suffix_array.cpp移除classic依赖：三字节表长度至9全部串、1000任意字节串、稀疏整数、空序列、重建，
  由逐字符比较排序后缀并暴力LCP；全部后缀对区间最小值核对。百万周期串闭式和1500分隔符截断图例也通过。
- tests/suffix_automaton.cpp：全部3280个三字母表长度至7的字符串逐前缀枚举所有子串及实际结束位置集合。
  核对同一状态等价、不同状态集合不同、长度区间完整、次数、原始种子、不同子串数量、重复查询/继续追加/清空；
  百万相同字符逐状态频次闭式检查。
- P3809完整驱动105个Python后缀排序参考和百万同字符输出。
  P3804/最长公共子串各200个独立子串频次/集合参考，另百万SAM输入、两串各50万的LCS区间证书。
- 固定上游版本LC suffixarray全部50组、longest_common_substring全部28组，各普通和ASan/UBSan官方checker接受；
  故意错误输出被拒绝。原number_of_substrings驱动源码指纹与已有官方本地证据匹配。

均为本地验证，不新增线上AC或OJ速度排名。报告 verification/suffix-attachment.json、sa-official*.json、lcs-official*.json。
