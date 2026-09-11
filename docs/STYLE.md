# 码风依据

署名：Morning Flower and Evening Oath。QOJ `ucup-team7502`，2026-09-11 已通过 Firefox 登录页面核对。

仅抽取风格特征，不公开浏览器页面快照、登录状态或队员整份训练代码。

| 风格 | 已观察的队伍提交 | 特征 |
|---|---|---|
| compact | [2932575](https://qoj.ac/submission/2932575) | Allman 大括号、紧凑运算符、`vector<int>a`、小写短名、`cin/cout`、1-based 数组 |
| classic | [2930805](https://qoj.ac/submission/2930805)、[2931279](https://qoj.ac/submission/2931279) | 分列头文件、静态数组、Allman 大括号、`Push_Up`/`Insert`/`Query`、`for ( int i = ... )`、`scanf/printf` |

提交账号为共用队号，证据尚不足以把每份代码归属到具体队员，故不擅自给风格冠以个人姓名。两套实现分别维护、分别测试；静态版本须明确容量，规模大的对象应为全局或 static，避免栈溢出。

已看到的训练场次包括 QOJ 912、2826、2691、1987、3169、2693、2527、1886 等。它们用于选择使用示例，不能据此断言队伍不会某算法或某份 WA 的原因。
