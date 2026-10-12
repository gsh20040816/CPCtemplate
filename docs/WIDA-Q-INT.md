# WIDA q-int 原题审计

本次不新增独立 q-int 组件。WIDA 13A 原稿的实际用途是计算 Gaussian 二项式，改由现有 `q_binomial` 完成，并新增完整用法 444。当前仍是 327 个组件，完整用法增加到 444 份。

## 来源与原题

精确原稿保存于 `tests/fixtures/wida_q_int/13A.cpp`，Git blob 为 `1e9fba7eaa91e176b6e53d6d80d8514d767a7909`。2026-10-12 在 Firefox 的 CCF_NOI 账号中读取了 [原提交 163986](https://qoj.ac/submission/163986)；页面结果为 TL，不能当作 AC 参考代码。完整 main 对 qint(q,n-i+1,p) 与 qint(q,i,p) 的第一分量分别相乘、第二分量相减，最后尝试消去模 p 的零因子。

对应 [QOJ 4281 Subspace](https://qoj.ac/contest/1341/problem/4281)，输入依次为 q、n、k、p；q 和 p 均为素数，2≤q≤10^9，1≤k≤n≤10^9，2≤p≤200000。求 F_q^n 的 k 维子空间个数模 p。原题样例 `2 3 2 100003` 输出 7。此题是 ICPCCamp 2015 的比赛应用，不计为非比赛模板题，也不据此声称最快排名。

## 确认的错误与替代范围

满足原题全部约束的输入 `3 2 2 2`，答案必须为 1：整个二维空间只有一个二维子空间。但原稿在 q mod p=1、n=p 时返回 `(0,1)`，使原 main 的分子和分母同时变成 0。最终阶数相消为 0，原程序仍输出 0。此反例使用未修改原稿、原 main 的算术逻辑在本地复现；测试只添加批量输入外壳与必要头文件。

因此不能把该二元组直接描述成已验证的通用 p 进阶数与非零单位部分。先前文档对这一语义的肯定表述已修正。也不需要为覆盖该来源而编写一个与原题无关的新接口：原题所需的 Gaussian 二项式已有 `q_binomial`。覆盖表记录的是**原应用的正确替代**，不是证明原 qint 返回二元组正确，更不是通用 p 进运算覆盖。

子空间数为有序线性无关 k 元组数除以每个 k 维子空间的有序基数：

`product(q^n-q^i, i=0..k-1) / product(q^k-q^i, i=0..k-1)`。

这个整数就是 Gaussian 二项式。新实现使用 q-Lucas，在单位根处避免直接除零；原题 p≤200000，乘法阶低位和普通 Lucas 数字的乘积循环均在原题规模内。

## 验收

`tests/wida_q_int.py` 校验原稿 blob，保存样例及反例实际输出；用 Python 任意精度整数按上述有序基计数公式整除，再模 p，独立验证完整 `verify/qoj/4281.compact.cpp`。普通 NDEBUG 版和 ASan/UBSan 版各 2700 组，包括小素数 q=p、q≡1、单位根与 k=n 等情况。完整纸面用法另由 `tests/usage_examples.py --only example-444` 检查。

本次真实提交 [3166447](https://qoj.ac/submission/3166447) 获得 AC，CCF_NOI，C++20，1ms，3876kb。提交使用相同核心和输入协议，输出换行在浏览器中写作 `endl`，仓库驱动为 `'\n'`；算法代码相同。结果记录在 `verification/qoj-4281.json`，本地证据在 `verification/wida-q-int.json`。

此次原题验收补足 13A 实际应用的来源核对，也为已有 13B 替代核心增加线上证据；没有对尚未核对的其他 WIDA 来源作覆盖推断。

同时读取了[13B原提交164128](https://qoj.ac/submission/164128)：同为QOJ4281，原作者2023-09-04提交为AC（41ms）。其main先执行q%=p，再调用qBinomial(n,k,q,p)。这补足了先前无法读取的来源协议；历史AC与本次3166447的AC分别记录，不混用。
