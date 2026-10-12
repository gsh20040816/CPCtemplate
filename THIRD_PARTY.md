# Reference attribution

Most implementation files in `src/` were written for this project. The explicitly
attributed adaptation below retains its upstream MIT notice. The project
uses kuangbin's 2018 template, WIDA's XCPC collection, OI Wiki, and contest
editorials to identify required topics. It does not copy an upstream author's
AC status onto the new implementation.

- kuangbin: https://kuangbin.github.io/2018/08/01/ACM-template/
- WIDA (GPL-3.0 upstream): https://github.com/hh2048/XCPC
- OI Wiki: https://oi-wiki.org/math/
- Colin Percival, *Rapid multiplication modulo the sum and difference of highly
  composite numbers*, Mathematics of Computation 72 (2003), Theorem 5.1:
  https://www.daemonology.net/papers/fft.pdf (FFT error analysis; implementation
  and parameter choices are this project's own).

The MIT license applies to this project's newly written code and documentation;
it does not relicense linked third-party material. Reference inventories retain
original topic titles. Contest-specific provenance and page locations are in
`docs/SOURCES.md`. Do not import third-party code without preserving its license
and attribution.

## Weighted blossom adaptation

`src/compact/weighted_blossom.hpp` is adapted from Shahjalal Shohag, commit
0884be6ab81fce26b8bba76d6013b3fcaadd92fd, Graph Theory/Blossom Algorithm Weighted.cpp.
Source: https://github.com/ShahjalalShohag/code-library

Copyright (c) 2021 Shahjalal Shohag
License: MIT

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
