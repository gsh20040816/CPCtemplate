#include "../src/compact/graph.hpp"
#include <iostream>
#include <cassert>

int main()
{
    std::mt19937 rng(20260918);
    for (int it = 0; it < 1000; it++)
    {
        int n = 1 + rng() % 9, m = rng() % 20;
        Lowlink g(n);
        std::vector<std::pair<int, int>> e;
        for (int j = 0; j < m; j++)
        {
            int u = 1 + rng() % n, v = 1 + rng() % n;
            e.push_back({u, v});
            g.add(u, v);
        }
        auto components = [&](int vertex, int edge)
        {
            std::vector<int> vis(n + 1);
            int cnt = 0;
            for (int s = 1; s <= n; s++)
                if (s != vertex && !vis[s])
                {
                    cnt++;
                    std::vector<int> q{s};
                    vis[s] = 1;
                    for (int k = 0; k < (int)q.size(); k++)
                    {
                        int u = q[k];
                        for (int id = 0; id < m; id++)
                            if (id != edge)
                            {
                                auto [a, b] = e[id];
                                if (b == u) std::swap(a, b);
                                if (a == u && b != vertex && !vis[b])
                                {
                                    vis[b] = 1;
                                    q.push_back(b);
                                }
                            }
                    }
                }
            return cnt;
        };
        int base = components(-1, -1);
        g.run();
        assert(g.components == base);
        for (int u = 1; u <= n; u++)
        {
            assert(g.components + g.delta[u] == components(u, -1));
            bool want = components(u, -1) > base;
            assert(g.cut[u] == want);
        }
        for (int id = 0; id < m; id++)
        {
            bool want = components(-1, id) > base;
            assert(g.bridge[id] == want);
        }
    }
    Lowlink chain(200000);
    for (int u = 1; u < chain.n; u++) chain.add(u, u + 1);
    chain.run();
    for (int u = 1; u <= chain.n; u++) assert(chain.cut[u] == (u > 1 && u < chain.n));
    chain.add(chain.n, 1);
    chain.run();
    assert(chain.components == 1);
    for (int u = 1; u <= chain.n; u++) assert(!chain.cut[u] && !chain.delta[u]);
    for (int b : chain.bridge) assert(!b);
    std::cout << "Lowlink: 1000 multigraph deletion oracles including component "
                 "deltas; 200000-node chain, cycle and rebuild PASS\n";
}
