# WIDA polynomial source fixtures

12A.cpp is the exact upstream file (including CRLF), blob c493616c750062b41d1daf07028ee21047ae155a, from hh2048/XCPC tree cfdb12db6792eb2303798541fb5c760ed2bc618b.
Path: 03 - jiangly模板收集/03 - 数论、几何与多项式/12A - 多项式（Poly 手写取模）.cpp.

This third-party reference fixture retains the upstream GPL-3.0 license in LICENSE; it is not relicensed by the root MIT license. It is compiled in a separate namespace only for source behavior comparisons. New production components and independent tests are in src/compact/ntt_2d.hpp, src/compact/bivariate_inverse.hpp, and tests/bivariate*.

12D-multiply.cpp is exact blob 4c51d1709859104bb84e086e0d6d275691b6f81f, upstream path 03 - jiangly模板收集/03 - 数论、几何与多项式/12D - 多项式乘法.cpp.

12D-mint.cpp is exact blob f2063c0206f44f664a04090a48f9dea4c3054879, upstream path 03 - jiangly模板收集/03 - 数论、几何与多项式/12D - 多项式（Poly, with MInt）.cpp. Both retain exact original CRLF bytes and the GPL-3.0 license in LICENSE. The MInt fixture is currently tested only through its tail get(n,m); this is not a complete audit of every member.

12B.cpp is exact blob 2d80d827265a8179b2b20af1775820170dc41346, upstream path 03 - jiangly模板收集/03 - 数论、几何与多项式/12B - 多项式（Poly, with Z）.cpp. It retains the original CRLF and the same upstream GPL-3.0 license. See docs/WIDA-Z-POLY.md for scoped evidence and remaining work.
