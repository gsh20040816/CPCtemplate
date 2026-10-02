# CF732F Tourist Reform

Source: https://codeforces.com/problemset/problem/732/F (official statement, checked 2026-10-02).

The official sample output is only one optimal orientation. The test checks its objective and every input edge identity, and validates generated outputs by reachability, never by copying the sample directions.

Let K be the largest bridge-free component size. Every orientation has a sink SCC S, whose vertices reach exactly S. An SCC cannot cross an undirected bridge, so |S| <= K and the objective is at most K. Existing DFS orientation strongly orients each bridge-free component. Root the bridge tree at a largest component and orient bridges toward it. Every vertex reaches all K root vertices, and root vertices reach exactly those K, attaining the upper bound.

Compressed edges retain original endpoint order and IDs, not parent-child order. The driver builds both adjacency directions, roots the tree, and uses the original endpoints and component labels when directing each bridge.

Official-domain cases are separated from wider connected multigraph API checks. Disconnected and empty graphs are outside this application's input contract. Loops, parallel edges and n=1 robustness cases are not official CF732F evidence. EdgeCompression.inside is unused here.

Recursion is unchanged. A sufficiently large stack is an explicit precondition: 8 MiB fails for the n=400000 path locally. Maximum-size tests change only each child soft stack limit, capped at its unchanged hard limit. No driver wrapper, hard/global limit changes, judge-stack claim or online AC claim is made. Resource receipts include actual limits, compiler, runtime and child RSS; sanitizer measurements include instrumentation overhead.

The instrumented -O1 ASan/UBSan path also overflowed a 256 MiB child soft stack. Normal tests request 256 MiB; instrumented tests request 1 GiB, capped by the unchanged hard limit. This is explicit test-only resource provisioning, not a driver change or judge-memory claim. The failure receipt is retained in scratch build output.
