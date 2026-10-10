# 赛场编译与对拍脚本

这是 [issue #17](https://github.com/gsh20040816/CPCtemplate/issues/17) 第三章的已执行素材。四章手册、PDF更名和其余示例仍在推进；当前PDF暂未改版。

目标环境：Linux、Bash、GNU g++ 支持 C++23、GNU coreutils（timeout）、Python 3。脚本不做平台和编译器探测。测试环境另记在文末。

## 编译后运行

保存 [compile.sh](../examples/infra/compile.sh)，在代码所在目录运行：

```bash
bash compile.sh main < input.txt > actual.txt
bash compile.sh main.cpp -O2 < input.txt > actual.txt
bash compile.sh main.cpp -O2 -o solution
./solution < input.txt
```

默认用 O1、调试信息和 ASan/UBSan；检测到未定义行为立即退出。加 -O2 改为优化构建，不带 sanitizer。两者都用 C++23，保留警告；成功信息写 stderr，不混入答案。

-o 必须接输出路径，指定后只编译、不运行。省略它则输出文件名为源文件去掉.cpp，并立即运行。不支持多源文件、以减号开头的文件名、任意透传编译参数或程序参数，需要时直接写g++命令。路径含空格必须加引号。

已有输出仅允许覆盖普通可执行文件，拒绝符号链接、目录、普通文本和源文件本身。编译失败时即使旧可执行文件仍在，也不执行它。程序非零退出状态原样传出。脚本只保护常见误操作，不是并发文件修改环境中的安全隔离工具。

与issue里的短脚本相比，修正了缺失参数、源文件误覆盖、目录/链接目标、绝对输出路径和UBSan默认继续执行的问题；结尾的百分号不属于脚本。

## 固定种子对拍

完整示例文件：[生成器](../examples/infra/gen.py)、[暴力](../examples/infra/brute.py)、[待测程序](../examples/infra/main.cpp)、[对拍脚本](../examples/infra/stress.sh)。示例问题为**非空**最大子段和，生成器含负数；暴力枚举全部区间，待测程序使用线性递推。这里只示范工具串联，不新增基础算法模板。

在独立目录复制这五个文件，再执行：

```bash
cp gen.py gen
cp brute.py brute
chmod +x gen brute
bash compile.sh main.cpp -O2 -o main
bash stress.sh 1000
```

生成器接收一个整数种子，同一Python环境下可以复现输入。stress.sh依次执行gen、brute、main和diff，任一步失败立即停止。每次运行创建独立stress.XXXXXX目录；每轮先清空输出槽，避免第二轮生成失败却留下上一轮答案。目录内保留seed、input、expected、actual、diff和三个stderr文件；成功则保留最后一组，失败保留第一组反例。

三个程序分别限时2秒，TERM发出后1秒仍不退出则KILL。timeout的124通常表示限时耗尽；137可能表示KILL，其他非零退出也必须检查stderr。diff逐字节比较，返回1表示有差异，其他错误也停止；特殊浮点误差或输出方案问题应换成专用checker。

复现时替换下面目录名：

```bash
cat stress.XXXXXX/seed
./main < stress.XXXXXX/input > retry.txt
diff -u stress.XXXXXX/expected retry.txt
cat stress.XXXXXX/main.err
```

## Bash抄写要点

- "$1"为第一个参数，"$#"为参数个数，shift移除首参数；case选择选项。
- flags=(...)是数组，"${flags[@]}"逐项传参；不能用单个字符串拼编译参数。
- [[ ... ]]判断文件和字符串；(( ... ))做整数条件。循环计数要区分算术返回状态和数值，set -e下不能随意把((i++))当作必成功语句。
- <输入，>覆盖输出，2>错误输出，>>追加；输入文件不能同时重定向为输出。
- set -euo pipefail要求普通命令失败、未设置变量和失败管道尽早停止。条件测试、&&/||链等有例外，不能以为它能自动覆盖所有控制流。
- 正常状态0，失败非0；先检查状态再比较输出。不要只把最后一个echo成功当作整个脚本成功。

## 执行证据和来源

运行 `python3 tests/infra_scripts.py`。实际源码哈希、GNU编译器、Bash、timeout版本和宿主系统见 [收据](../verification/infra-scripts.json)。测试在当前macOS宿主执行，通过测试专用PATH将g++绑定到GNU g++-16；脚本本体没有跨平台适配，尚不能据此声称完成原生Linux或整本手册验证。

检查调试/优化编译与运行、绝对路径及空格、文件保护、错误参数、编译失败、非零运行退出、UBSan溢出、30组独立暴力、五类失败与第二轮失败残留。未做全库回归或CI操作。

语义依据：[GCC instrumentation options](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html)、[Bash set](https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html)、[GNU timeout](https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html)；后两者在线读取失败，当前执行行为已用本机命令验证，完整版本说明仍需后续核对。
