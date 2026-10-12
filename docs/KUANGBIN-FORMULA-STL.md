# kuangbin 公式与 STL 来源核对

固定来源：`build/source-audit/kuangbin.pdf`，SHA256 `f1c90eae0c3fb309d58a14b050fe12b239efb474b033299a547b55646c2768ad`。本批目视核对物理56–57、258–260页，对应印刷54–55、256–258页；仅核对指定章节，不把同页其他代码算作完成。

## 2.19 其它公式

此节只有子节2.19.1 Pólya，没有另一组未实现的公式或代码。全部内容为有限置换群的命名颜色染色数、旋转与翻转的循环数。

- 一般公式由 `BurnsideAverage`、`permutation_cycles` 和用法367覆盖；完整群作用的假设、模群阶乘目标模数后整除见 [POLYA.md](POLYA.md)。不得只输入群生成元。
- 旋转/翻转由 `necklace_colorings` 与用法366覆盖；用法364为旋转模板题，365为固定颜色用量应用。保留已有两条在线记录，不把旋转AC当作翻转AC。
- 原稿奇数情形写成 n/2+1，未标整数除法或下取整。数学表达应为 (n+1)/2；本库整数n对应代码n/2+1正确。n=1、2时采用抽象二面体群的作用，不因置换重复而错误去掉重数。
- 新增独立检查：n=1..200的每个旋转与翻转，把置换视作无向图，合并连通分量求循环数，40200个置换通过。此检查针对原稿公式；完整计数另重新运行原有轨道代表枚举、宽整数、实际用法等测试，普通与ASan/UBSan均通过。

该来源条目记为local-tested；不是新增组件，不改变完整OI Wiki数学覆盖结论。

## 8.5 STL（含两个子节）

8.5.1列出默认大根堆、greater小根堆、整型自定义比较器、结构体operator<按x反序以及empty/pop/push/size/top。8.5.2列出set/multiset、降序整数比较器、x升序/y降序结构体比较器，以及begin/clear/count/empty/end/erase/find/insert/size/lower_bound/upper_bound/equal_range。

本批在基础分册原有章节补齐比较器、降序边界与结构体用法，按实际印刷代码编译测试，没有另造容器封装。`tests/kuangbin_stl.cpp`转写原稿四个比较器的功能语句，重命名避免同名冲突、统一缩进；原稿重复声明与中文说明不作为完整翻译单元。独立有序vector对照69545次堆/集合操作，包含重复值、空集合、按值/迭代器删除、降序边界、等价区间、结构体排序及set去重；原稿功能片段与四块实际打印代码都在O2及ASan/UBSan通过。

核对后明确以下边界：

1. 原稿将end写成最后元素，错误；应是不能解引用的尾后位置。空集合begin==end。
2. 原稿lower_bound/upper_bound的数值描述仅适用于默认升序；降序时按比较器解释。本册用{7,5,5,2}演示查询5分别得到5和2。
3. 原稿提醒同时重载<和>“可能编译错误”，不是语言上的禁止。另编译同时提供合法<和>的结构体并验证大根堆；本册优先用独立比较器或pair，减少全局含义混淆。
4. 原稿外部数组p[x]比较器不能理解成自动降键接口。改变外部键不会自动维护已有堆，本册说明采用快照加过期过滤或可修改堆。
5. 结构体末尾是分号，原稿称“逗号”是文字笔误；本册代码使用分号。
6. 等价键由比较器两方向均为假定义，不必等于所有字段逐一相同。不能直接修改树中键来破坏排序。

语义核对使用[C++关联容器要求](https://eel.is/c++draft/associative.reqmts)、[容器通用要求](https://eel.is/c++draft/container.requirements.general)、[priority_queue](https://eel.is/c++draft/priority.queue)。只使用C++20已有接口，不采用当前草案新增的constexpr或range接口。比较器要求、边界、操作成本以这些规范为依据，有限测试不替代标准保证。

8.5父条目及两个子条目均记local-tested，范围仅为原稿两节，不代表STL百科或OI Wiki语言基础全覆盖；无新增OJ提交或性能排名。

## 8.4 栈设置：已读，保持partial

原稿没有完整DFS模板；它先建议BFS或模拟栈，再给出MSVC链接器/STACK选项及修改32位esp的三行GCC汇编。模拟栈建议与用户的递归DFS要求冲突，不采用。直接写esp依赖平台和调用约定，不能当作当前Apple Silicon或任意64位GCC的通用开栈代码，未编译或执行该汇编。

[微软/STACK文档](https://learn.microsoft.com/en-us/cpp/build/reference/stack-stack-allocations?view=msvc-170)说明reserve与commit属于链接器参数，不能推导为GNU平台通用功能。本库沿用基础分册的环境检查及现有本地测试栈配置，DFS仍递归。此处仅完成原稿阅读与不采用原因记录，没有测试其MSVC/32位运行环境，因此来源保持partial，不伪装成已验证可移植实现。

## 验证记录

`verification/kuangbin-formula-stl.json`记录公式与容器测试、原稿校验和及印刷片段校验和；`verification/polya-normal.json`和`polya-sanitizer.json`是本批重新运行的完整Pólya本地测试。8.3读入、8.6输入输出外挂、8.8Vim仍另行处理。

基础分册最终印刷14–17页已渲染检查；新增比较器与示例均完整，原有排序与复数示例也调整为完整分页。用途索引第35页已检查。最终编译无警告，18处跨册跳转检查通过。本批仅重建基础分册，其他七份PDF没有修改。
