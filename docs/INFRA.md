# Infra 构建与验证

`output/pdf/infra.pdf` 汇总 OI Wiki 的比赛相关、工具软件、语言基础三板块中与当前模板相关的内容。正文源为 `docs/infra-body.tex`；`tools/infra.py` 生成封面与跨册索引。

GNU配对堆在数据结构册详细介绍，并在infra集中索引。标准库部分整理当前常用容器、排序/查找、optional、回调、位操作与随机数，并专节解释std::move。它不是整个C++标准库的完整替代品；还需对照实际使用记录继续补齐未登记细项，issue #9保持开放。

## 依赖

除既有XeLaTeX、latexmk、中文字体、Poppler外，跨文件链接审计需要pypdf 6.0.0。首次本地可建立项目工具环境：

```bash
python3 -m venv build/tools-env
build/tools-env/bin/pip install clang-format==23.1.1 pypdf==6.0.0
tools/build_pdf.sh
```

CI显式安装同版本pypdf。构建器先生成算法各册，随后用xr-hyper读取最终aux，再构建infra；不能先生成infra而引用旧页码。所有PDF放在同一目录，链接采用GoToR命名目的地，不手写页码。

`tools/infra_audit.py` 读取infra实际链接，核对目标文件、命名目的地及目标页的印刷页码。当前10项跳转包含PBDS堆、有序树、rope、GP/CC哈希表及标准库典型使用场景；报告为 `verification/infra-links.json`。原来的字体、溢出、索引与页码检查不放松。

## 示例检查

`tests/infra_examples.cpp` 检查move表达式不执行构造、随后move/copy重载选择、const容器复制、移动后合法复用、STL区间操作及PBDS句柄迁移。`tests/infra_examples.py` 执行Python大整数/取整/模逆与Bash带空格路径、字面美元符号例子。

来源包括C++标准草案的[move定义](https://eel.is/c++draft/forward)、[移动后状态](https://eel.is/c++draft/lib.types.movedfrom)，以及[GCC PBDS说明](https://gcc.gnu.org/onlinedocs/libstdc++/manual/policy_data_structures_using.html)。本册只使用已声明的C++20接口，不因参考当前草案而引入更新标准的API。
