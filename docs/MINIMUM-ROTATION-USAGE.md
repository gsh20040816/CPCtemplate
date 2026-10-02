# 最小表示法模板题用法

对应 issue #1 / #12，正式模板题使用 [Luogu P13270【模板】最小表示法](https://www.luogu.com.cn/problem/P13270)，登记为 `example-209`、`kind=template`。2026-10-02 核对官方题面：输入为长度 `1..10^7` 的小写英文字母串，输出字典序最小的循环位移。原题 [P1368 工艺](https://www.luogu.com.cn/problem/P1368) 也明确指向这道新模板题；P13270 可直接使用现有字符串接口，无须修改算法或添加整数编码适配。

- 模板：`minimum_rotation`，位于 [string.hpp](../src/compact/string.hpp)
- 完整驱动：[P13270.compact.cpp](../verify/luogu/P13270.compact.cpp)
- 使用片段：由同一驱动的 `main` 生成，不重复打印算法
- 独立测试：[minimum_rotation_usage.py](../tests/minimum_rotation_usage.py)

## 调用、边界与复杂度

输入一组 `n` 和字符串 `s`，题面保证 `s.size()==n`。调用 `p=minimum_rotation(s)` 得到从 `0` 开始的起点，再用标准库 `rotate(s.begin(), s.begin()+p, s.end())` 原地移位并输出整个字符串，末尾恰有一个换行。`p` 不需要加减 `1`，也不能当成字符值输出。重复字符、周期串可以有多个等价的最小起点，题目只要求输出对应的最小字符串。

函数不修改输入、不维护跨调用状态；多测时每组重新读串并调用即可。算法和输出重排均为 `O(n)` 时间，算法本体以及原地重排使用 `O(1)` 额外空间；输入字符串本身占 `O(n)` 空间。官方最大长度下，核心中的 `int` 长度、候选下标及下标和均在范围内。

`minimum_rotation` 的实际接口是 `const string &`。核心显式将参与比较的字符转成 `unsigned char`，因而采用 `0..255` 的字节顺序，不依赖编译器默认的 `char` 符号性。二进制零字节和高位字节属于核心可处理的字符串内容；空串返回 `0`。这些是接口边界，不是 P13270 的合法输入，也不是整数数组或负整数接口。驱动的 `cin >> s` 仅用于官方小写字母输入，不用于读取任意二进制串。未修改现有核心。

## 本地证据

```sh
python3 tests/minimum_rotation_usage.py
python3 tests/minimum_rotation_usage.py --sanitizer
```

测试也识别 `SANITIZE=1`，便于接入现有回归。普通与 ASan/UBSan 模式分别生成 [normal 报告](../verification/minimum-rotation-usage-normal.json) 和 [sanitizer 报告](../verification/minimum-rotation-usage-sanitizer.json)。每份报告绑定输入源码、完整展开程序、核心、精简抄写程序、测试脚本和语料哈希，记录实际编译器、平台、命令和运行环境；运行前后核对源文件未变。默认 `ASAN_OPTIONS=detect_leaks=0`，只声明地址/未定义行为检查，不声明泄漏检查。

每种模式包含：

- 216 组完整驱动测试：8 组固定输入、200 组随机串、4 组长相等前缀/周期串，以及 4 组 `n=10^7` 的合法最大规模输入
- 最大规模分别为全相等、最后一位唯一最小、交替周期和长相等前缀；预期答案来自各自结构，不调用第二份最小表示法
- 8 组只粘贴 `minimum_rotation`、标准头及原驱动 `main` 的检查，确认所列依赖足够
- 3,944 组核心接口输入：空串 1 组、字母表 `{0,127,255}` 上长度 `1..7` 的完全枚举 3,279 组、所有单字节 256 组、固定二进制边界 8 组、随机字节串 400 组
- 核心接口语料分别在 `-fsigned-char` 与 `-funsigned-char` 下执行，每模式共 7,888 次调用，且检查调用后输入串未被修改

所有小规模预期答案均直接枚举全部循环位移并比较 Python 字节串，不复用 Booth、Duval 或后缀结构。驱动逐字节比较完整输出及末尾换行；接口检查返回下标范围与该下标生成的最小字符串，不额外要求某个未承诺的等价起点。

中央 `tests/usage_examples.py --only example-209` 仍负责同一打印片段的固定双模式证据及覆盖状态。本地测试通过不等于官方完整数据通过；没有在线提交，也不声明 OJ AC 或速度排名。
