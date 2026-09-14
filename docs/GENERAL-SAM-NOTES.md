# 广义 SAM 的状态数口径

`GeneralSAM` 用 Trie BFS 原地构造，维护按 `(文档编号, 结束位置)` 定义的 endpos 等价类。支持不同非空子串计数及沿转移判定子串；不自动提供终态标记、文档出现次数或最小 DFA 化。

[OI Wiki 的广义 SAM 构造](https://oi-wiki.org/string/general-sam/)与 issue #11 附件的逐串扩展版本都需要将“构造出的状态数”和“仅接受后缀并集的最小 DFA 状态数”分开考虑。

[洛谷 P6139](https://www.luogu.com.cn/problem/P6139) 当前题面要求第二行输出后者，并表示可认为是广义 SAM 的状态数。以下小例子说明二者在字面定义下不同：输入 `ab`、`b`，不同非空子串为 `a`、`b`、`ab`。其 endpos 集合分别为 `{(0,0)}`、`{(0,1),(1,0)}`、`{(0,1)}`，加初态共 4 个广义 SAM 状态。

仅识别后缀并集时，部分 DFA 可用 3 个状态：初态 R 在 `a` 上转向 A，在 `b` 上转向 B；A 在 `b` 上转向 B，B 为终态，其他转移拒绝。若包含空后缀，R 也标为终态。B 和读完 `ab` 的状态可合并。这里省略拒绝汇点，与通常 SAM 的表示一致。

`tests/suffix_state_semantics.py` 独立建立所有后缀的 Trie，按终态和转移签名自底向上合并；另直接枚举文档 endpos 集合。结果保存在 `verification/general-sam-semantics.json`。

`verify/luogu/P6139.compact.cpp` 仅是候选驱动，第二行遵循常见广义 SAM 的 endpos 状态数；尚未验证线上评测实际采用的口径。它不进入已验证使用示例清单，也不据此声称符合题面第二行要求。广义 SAM 本体的子串集合、endpos 等价类与转移语言另有独立多串对拍；LC `number_of_substrings` 官方本地数据只验证单串特例。
