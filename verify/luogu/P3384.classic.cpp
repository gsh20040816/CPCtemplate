#include "../../src/classic/tree.hpp"
#include "../../src/classic/affine_segment_tree.hpp"
#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m, root, mod;
    std::cin >> n >> m >> root >> mod;
    std::vector<long long> values(n + 1);
    for ( int u = 1; u <= n; u++ )
        std::cin >> values[u];
    static Heavy_Light_Decomposition<100000> h;
    h.Init(n);
    for ( int i = 1; i < n; i++ )
    {
        int u, v;
        std::cin >> u >> v;
        h.Insert(u, v);
    }
    h.Build(root);
    std::vector<long long> ordered(n);
    for ( int u = 1; u <= n; u++ )
        ordered[h.dfn[u] - 1] = values[u];
    static Affine_Segment_Tree<100000> seg;
    seg.Init(ordered, mod);
    while ( m-- )
    {
        int op, u;
        std::cin >> op >> u;
        if ( op == 1 )
        {
            int v;
            long long x;
            std::cin >> v >> x;
            h.Path(u,
                   v,
                   [&](int l, int r)
                   {
                       seg.Update(l, r, 1, x);
                   });
        }
        else if ( op == 2 )
        {
            int v;
            std::cin >> v;
            long long answer = 0;
            h.Path(u,
                   v,
                   [&](int l, int r)
                   {
                       answer = (answer + seg.Query(l, r)) % mod;
                   });
            std::cout << answer << '\n';
        }
        else if ( op == 3 )
        {
            long long x;
            std::cin >> x;
            seg.Update(h.dfn[u], h.dfn[u] + h.siz[u] - 1, 1, x);
        }
        else
            std::cout << seg.Query(h.dfn[u], h.dfn[u] + h.siz[u] - 1) << '\n';
    }
}
