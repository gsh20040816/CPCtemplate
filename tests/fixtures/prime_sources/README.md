# kuangbin §2.1 source fixtures

Complete fragments of 17, 16 and 58 numbered lines, printed25–27 / physical27–29. All three physical pages visually inspected. Locked PDF SHA256: f1c90eae0c3fb309d58a14b050fe12b239efb474b033299a547b55646c2768ad. Original attribution remains kuangbin, not relicensed as new project code.

Only print numbers/indentation removed, mathematical minus and visible string-space glyphs normalized, and the wrapped comment in table line12 and printf arguments in distance line55 joined. No algorithm repairs. table.cpp and list.cpp are included in independent namespaces; distance.cpp retains its actual global main, so its implicit return0 remains valid.

The first table excludes MAXN=1000010; the second includes MAXN=10000 and stores its count at prime[0]. Tests do not interpret the rest of the second array as a boolean prime table. The third source prose supplies 1<=L<U<=INT_MAX and width<=1000000; these are source-prose bounds, not a fresh verification of the original judge statement.
