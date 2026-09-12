#include "../../src/compact/tree.hpp"
#include "../../src/compact/affine_segment_tree.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m, root, mod;
    std::cin >> n >> m >> root >> mod;
    std::vector<long long> values(n + 1);
    for (int u = 1; u <= n; u++) std::cin >> values[u];
    HLD h(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        std::cin >> u >> v;
        h.add(u, v);
    }
    h.build(root);
    std::vector<long long> ordered(n);
    for (int u = 1; u <= n; u++) ordered[h.dfn[u] - 1] = values[u];
    AffineSegTree seg(ordered, mod);
    while (m--)
    {
        int op, u;
        std::cin >> op >> u;
        if (op == 1)
        {
            int v;
            long long x;
            std::cin >> v >> x;
            h.path(u, v, [&](int l, int r) { seg.update(l, r, 1, x); });
        }
        else if (op == 2)
        {
            int v;
            std::cin >> v;
            long long answer = 0;
            h.path(
                u, v, [&](int l, int r) { answer = (answer + seg.query(l, r)) % mod; });
            std::cout << answer << '\n';
        }
        else if (op == 3)
        {
            long long x;
            std::cin >> x;
            seg.update(h.dfn[u], h.dfn[u] + h.siz[u] - 1, 1, x);
        }
        else
            std::cout << seg.query(h.dfn[u], h.dfn[u] + h.siz[u] - 1) << '\n';
    }
}
