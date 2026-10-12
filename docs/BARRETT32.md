# Barrett 32 位约减与动态模整数

新增 `Barrett32`，并把已有 `mint<tag>` 的乘法接入该核心。当前 329 个组件、447 份完整用法；独立 API 为 447，动态 mint 的已有用法 198、232 已重新验证。普通固定模数 ModInt 保留原接口。

## 使用范围

`Barrett32(m)` 要求 1≤m≤UINT32_MAX，`mul(a,b)` 要求 0≤a,b<m，返回规范 uint32 余数。构造含一次 64 位除法，后续模乘没有除法或浮点运算；构造与每次查询均 O(1)，空间 O(1)。可以同时保留多个不同模数的对象，不能直接修改 mod 或 reciprocal。依赖 GNU/Clang 的 unsigned int128。64 位模数请继续使用已有 Mod64。

`mint<tag>` 的范围仍是 1≤p≤INT_MAX。使用 set_mod(p) 同时更新模数和 Barrett 对象；不同 tag 互不影响，同 tag 切换后旧对象和缓存失效。构造支持完整 long long；加法用 long long 求和后最多减一次模数，减法最多加一次模数，乘法直接写入已规范的 Barrett 结果。避免把已规范结果再送回构造函数做重复除法。合数逆元、非负 uint64 次幂、模 1、自运算和 Fenwick 组合语义保持不变。

新增依赖在纸面清单中明确列出，必须先抄 Barrett32 再抄 mint。代码已展开为正常多行函数，不增加一行多语句的压缩写法。

## 正确性与溢出边界

令 R=2^64。m>1 时预计算 I=ceil(R/m)。对 z=a*b，有 0≤z≤(m-1)^2<R，故 zI/R 相比 z/m 的误差在 [0,1) 内，估计商只可能是实际商或多 1。估计商至多 m-1，所以 y=估计商×m<R，不发生 64 位乘积回绕。比较 z<y 可判定是否多减一次；此时 unsigned64 的减法回绕再补 m，最终得到 [0,m) 内的余数。

m=1 时唯一合法输入是 a=b=0；I 的 unsigned64 加法回绕为 0，全部中间值为 0，结果仍正确。uint128 只用于两个 uint64 数相乘取高位。

算法依据也可对照 [AtCoder Library 的整数约减实现](https://github.com/atcoder/ac-library/blob/master/atcoder/internal_math.hpp)。本版本保留 m=1 和完整 uint32 模数的处理；没有用 long double 估计商。

## WIDA 来源范围

精确 07E 原稿保存为 `tests/fixtures/wida_mod_reduction/07E.cpp`，blob 为 `c5af9ebd28047a3c6bd7023cbe26150761c8e86b`。原稿先把 z-y 截为 uint32，再用 m≤v 判断校正；这个判断在 int 模数范围对照通过，但不能无条件扩展到所有 uint32 模数。

已复现：m=4294967291、a=2137899609、b=3861224214，原稿 Barrett 返回 2982428172，精确余数为 2982428167。新实现先在 uint64 上判断 z<y，正确返回后者。这是独立 Barrett 的大模数边界，不据此声称原题使用的 int 模数场景失败。

07E 还包括固定模数 32/64 位包装、long double 模乘及三个原题引用；这些部分尚未完整审计，覆盖仍为 partial。07D Montgomery、其平方根及原根辅助函数也没有因本次工作而计为完成。

## 验证

普通与 ASan/UBSan 各 3136516 项 uint64 整数余数对照，包含 107004 次估计商修正；小模数全枚举、随机完整 uint32 模数和靠近 UINT32_MAX 的边界均覆盖。原稿仅在 int 安全域作为额外对照，大模数使用独立整数真值。

动态 mint 通过既有穷举合数逆元、int128 算术、别名自运算、独立 tag、完整 signed64 构造和 Fenwick 组合测试；批量逆元通过全部单位/非单位与独立乘积证书检查。头文件和纸面 Barrett 程序分别通过 NDEBUG 普通与消毒器模式，各 7714 项 Python 任意精度乘积真值。用法 198、232、447 已重新编译执行并更新哈希。

同机旧版/新版交替三轮的乘加链压力计时见 `verification/barrett32-performance.json`。这些是本地指定工作负载的性能比较，不是所有算法都会加速的保证，更不是 OJ 成绩或 SOTA。本次没有新增线上 AC；旧提交用时不能当作修改后版本的用时。
