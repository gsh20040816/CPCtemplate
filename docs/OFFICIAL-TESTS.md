# 官方数据的本地验证

`tools/official_cases.py` 接受已生成数据的 Library Checker 固定版本仓库、题目 ID、驱动文件和 JSON 报告路径。它不会提交 OJ，也不把本地用时当作线上排名。

```sh
CXX=g++-16 python3 build/library-checker-reference/generate.py -p range_affine_range_sum
python3 tools/official_cases.py build/library-checker-reference range_affine_range_sum verify/library_checker/range_affine_range_sum.compact.cpp verification/lazy-official-local.json
python3 tools/official_cases.py build/library-checker-reference range_affine_range_sum verify/library_checker/range_affine_range_sum.compact.cpp verification/lazy-official-sanitizer.json --sanitize
```

仓库必须停在待审查的固定 commit，且不能修改已跟踪参考文件。测试生成和参考答案由上游 `generate.py` 完成。脚本检查各输入名字与 `info.toml` 中生成器/次数完全一致，防止只跑部分数据便宣称全过。

每组数据分别运行当前驱动打包文件，再调用该题 checker。报告保存固定版本、元数据、checker 源码和二进制、打包源码、输入、标准答案与输出的 SHA256。另用故意错误的答案验证 checker 返回拒绝状态。失败或超时不会写出通过报告。

macOS 记录每组进程的 resident bytes 和墙钟时间，包含启动开销；这些数值受本机负载、编译器、系统和测试运行顺序影响，不能与 OJ 的 Linux 用时直接比较。Sanitizer 报告必须和普通报告区分。

## 已执行

通用递归懒标记线段树的 `range_affine_range_sum` 驱动，在参考版本 `e64660561a995c357cdc61ddee1bde68b80528db` 的 19 组官方数据上，普通和 ASan/UBSan 都通过官方 checker，包括最大随机数据。普通本轮最大墙钟时间 0.831 秒、最大 resident 74481664 字节。

- [普通报告](../verification/lazy-official-local.json)
- [ASan/UBSan 报告](../verification/lazy-official-sanitizer.json)

范围仅为构造、apply、prod 和此处的模仿射作用。不覆盖没有调用的 set/get、all、左右边界搜索，也不替代非交换字符串与独立扫描测试。线上 AC 与排名仍待补齐。
