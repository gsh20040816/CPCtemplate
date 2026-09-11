# 待在线评测

以下提交驱动尚无本库的新 AC 记录；列表由当前 verify/luogu 与 oj.json 对照生成。

- `verify/luogu/CF600E.classic.cpp`
- `verify/luogu/CF600E.compact.cpp`
- `verify/luogu/P3369.classic.cpp`
- `verify/luogu/P3369.splay.classic.cpp`
- `verify/luogu/P3369.splay.compact.cpp`
- `verify/luogu/P3373.classic.cpp`
- `verify/luogu/P3391.classic.cpp`
- `verify/luogu/P3391.compact.cpp`
- `verify/luogu/P3649.classic.cpp`
- `verify/luogu/P3649.compact.cpp`
- `verify/luogu/P5496.classic.cpp`
- `verify/luogu/P6113.classic.cpp`
- `verify/luogu/P6113.compact.cpp`

## 已解决的提交异常

- P8436、P3806 曾在旧页面的文件及文本提交入口返回 `The route object cannot be resolved`。2026-09-12 在新标签页重新提交后，两套版本均 AC；具体记录在 oj.json。错误原因尚未确定。
- P6113 动态版之前因 10 秒请求超时未生成记录，可在新标签页重试。
- 当前无待确认的验证码。后续出现验证码仍按工具要求当次确认。

OJ 只验证驱动实际调用的接口。点分治 P3806 只核验距离存在性，完整计数与零权等扩展仍由本地独立测试提供证据。
