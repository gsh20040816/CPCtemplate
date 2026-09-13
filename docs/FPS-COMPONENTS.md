# FPS 组件与兼容入口

原 Polynomial 条目含 NTT、形式幂级数、FWT、BM、线性递推。它们已有不同的 OI Wiki 页面和独立模板，现按职责复用：

- FpsInverse 继承 NttConvolution<998244353>，只增加 Newton 求逆，归多项式牛顿迭代。
- FpsFunctions 继承 FpsInverse，增加微分、积分、log、exp，归多项式初等函数。抄写链为 NttConvolution → FpsInverse → FpsFunctions；只求逆时不需抄后者。
- Polynomial 留作兼容入口，FWT 调 SetConvolution，BM/递推转换到已维护的整数系数接口。手册不再重复打印这些算法。

固定模数998244353。逆级数要求常数非零，log要求常数1，exp要求常数0（允许空输入），截断长度n正。积分要求输入长度小于模数。每次内部卷积必须满足NTT容量2^23；n≤2^22且输入长度≤n是统一充分界，并非宣称大于该界一律不能算。log仍按原接口对完整输入求导，过长输入需另核对容量。

旧recurrence允许给出多于递推阶数的初值：查询落在已给前缀中时原样返回；超出前缀才用最前k项和递推式外推。兼容入口保留此约定，不能直接将完整init传给要求恰好k项的recurrence_nth。

独立检查在tests/fps_components.cpp。逆级数、log、exp分别使用逐系数三角递推参考：ab=1、a'=a(log a)'、(exp a)'=a'exp a，未通过互相套用log/exp来验证彼此。覆盖随机输入、输入长短与截断、微积分常数项、空指数输入，以及131072项的几何级数、log(1-x)、exp(x)解析系数。兼容入口额外核对给定前缀、空递推、BM与Fibonacci外推。

上述测试和现有property/algebra回归均在普通与ASan/UBSan下通过，日志为verification/fps-components-*.txt和verification/fps-split-regression-*.txt。历史基线只放在临时构建目录。独立组件尚未获得新的线上AC；既有NTT/FWT的局部证据不扩张成FPS全接口线上验证。
