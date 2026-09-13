# 分册构建与分类

运行 `tools/build_pdf.sh` 同时生成总册与六本独立分册，输出在 `output/pdf/`：

| 大类 | 文件 |
| --- | --- |
| 数据结构 | xcpc-data-structures.pdf |
| 图论 | xcpc-graphs.pdf |
| 杂项 | xcpc-misc.pdf |
| 字符串 | xcpc-strings.pdf |
| 数学 | xcpc-mathematics.pdf |
| 计算几何 | xcpc-geometry.pdf |
| 总册 | xcpc-template.pdf |

分册顶层及中、小层级取自固定 OI Wiki 官方导航；实际深度随上游分支变化。本库实现列在对应知识点下。树上问题归图论，动态树归数据结构，原树上算法独立分册停止生成，可在 Git 历史找回。各册独立编译目录、页码引用与索引，不从总册截页。`docs/volumes.json` 记录每个项目的主分类及额外收录的跨类依赖。每个现有项目只归属一个主分类；依赖可跨册重复，方便配套抄写。

`tools/book.py` 把来源代码的行范围与既有分页规则写入临时 `build/book-sections.json`，总册和分册共享这些片段。`tools/taxonomy_layout.py` 按 `docs/oi-taxonomy.json` 排序与生成层级，`tools/volumes.py` 生成分册，生成的分册 LaTeX 不提交，避免重复维护代码及文字；公共排版在 `docs/preamble.tex`。新增模块未归类时生成器报错。

跨类依赖按已收录标识符在代码、注释及接口说明中的引用求传递闭包，可能保守地多收录条目。它不是 C++ 依赖分析器；抄写时仍需核对头文件依赖。页码引用若缺少目标则构建前报错。

几何册同时包含 `geometry-notes.tex` 和数学速查中的数值算法与几何内容，精确判定、退化情形、精度前提与算法代码位于同册。数学速查中原有的图、树与数据结构应用说明分别随对应分册收录。历史静态版 AC 只作归档证据。

4个复合条目仍需进一步拆分，3个相关挂靠仍需正文定位，详见 `OI-TAXONOMY.md`；因此 issue #7 的严格分类尚未全部完成。分册是现有内容的组织改进，不表示上游目录、Library Checker 或近三年赛题已全量覆盖。

用户 issue #8 覆盖默认导航：PBDS 和 GNU rope 归平衡树板块。原语言基础册已无主条目，停止生成；旧版保留在 Git 历史。平衡树与哈希表提供双向自动页码引用，gp/cc 的选择建议与源码放在哈希表条目。
