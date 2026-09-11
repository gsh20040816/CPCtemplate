#include "../src/compact/tarjan.hpp"
#include "../src/classic/tarjan.hpp"
#include <iostream>
#include <random>

void check(const std::vector<std::vector<int>> &g)
{
    int n = g.size() - 1;
    TarjanSCC a(n);
    static Tarjan_SCC<30> b;
    b.Init(n);
    std::vector<std::vector<bool>> reach(n + 1, std::vector<bool>(n + 1));
    for (int u = 1; u <= n; u++)
    {
        reach[u][u] = true;
        for (int v : g[u])
        {
            a.add(u, v);
            b.Insert(u, v);
            reach[u][v] = true;
        }
    }
    for (int k = 1; k <= n; k++)
        for (int u = 1; u <= n; u++)
            for (int v = 1; v <= n; v++)
                reach[u][v] = reach[u][v] || (reach[u][k] && reach[k][v]);
    for (int repeat = 0; repeat < 2; repeat++)
    {
        a.run();
        b.Run();
        assert(a.cnt == b.cnt);
        assert(a.st.empty() && b.st.empty());
        for (int u = 1; u <= n; u++)
        {
            assert(1 <= a.bel[u] && a.bel[u] <= a.cnt);
            assert(1 <= b.bel[u] && b.bel[u] <= b.cnt);
            for (int v = 1; v <= n; v++)
            {
                bool same = reach[u][v] && reach[v][u];
                assert((a.bel[u] == a.bel[v]) == same);
                assert((b.bel[u] == b.bel[v]) == same);
            }
        }
        auto da = a.dag();
        auto db = b.Dag();
        std::vector<std::vector<int>> ea(a.cnt + 1), eb(b.cnt + 1);
        for (int u = 1; u <= n; u++)
        {
            for (int v : g[u])
            {
                if (a.bel[u] != a.bel[v])
                {
                    assert(a.bel[u] > a.bel[v]);
                    assert(b.bel[u] > b.bel[v]);
                    ea[a.bel[u]].push_back(a.bel[v]);
                    eb[b.bel[u]].push_back(b.bel[v]);
                }
            }
        }
        assert(da == ea && db == eb);
    }
}

int main()
{
    check(std::vector<std::vector<int>>(1));
    for (unsigned mask = 0; mask < (1U << 16); mask++)
    {
        std::vector<std::vector<int>> g(5);
        for (int u = 1; u <= 4; u++)
            for (int v = 1; v <= 4; v++)
                if (mask >> ((u - 1) * 4 + v - 1) & 1)
                    g[u].push_back(v);
        check(g);
    }
    std::mt19937 rng(655274);
    for (int trial = 0; trial < 1000; trial++)
    {
        int n = 1 + rng() % 30;
        std::vector<std::vector<int>> g(n + 1);
        for (int i = 0; i < 100; i++)
            g[1 + rng() % n].push_back(1 + rng() % n);
        check(g);
    }
    std::cout << "Tarjan SCC exhaustive digraphs, reachability and condensation oracle PASS\n";
}
