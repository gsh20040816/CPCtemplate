#include "../src/compact/johnson.hpp"
#include <climits>
#include <random>
using namespace std;

int main()
{
    using I = Johnson::I;
    auto check = [&](int n, const vector<tuple<int, int, long long>> &edges)
    {
        Johnson graph(n);
        vector<vector<I>> d(n + 1, vector<I>(n + 1, Johnson::inf));
        for (int u = 1; u <= n; u++) d[u][u] = 0;
        for (auto [u, v, w] : edges)
        {
            graph.add(u, v, w);
            d[u][v] = min(d[u][v], I(w));
        }
        for (int k = 1; k <= n; k++)
            for (int u = 1; u <= n; u++)
                for (int v = 1; v <= n; v++)
                    if (d[u][k] != Johnson::inf && d[k][v] != Johnson::inf)
                        d[u][v] = min(d[u][v], d[u][k] + d[k][v]);
        bool valid = true;
        for (int u = 1; u <= n; u++) valid &= d[u][u] >= 0;
        assert(graph.build() == valid);
        assert(graph.ready == valid);
        if (valid)
        {
            for (int u = 1; u <= n; u++) assert(graph.distances(u) == d[u]);
            for (auto [u, v, w] : edges) assert(I(w) + graph.h[u] - graph.h[v] >= 0);
        }
        assert(graph.build() == valid);
    };
    for (int mask = 0; mask < 81; mask++)
    {
        vector<tuple<int, int, long long>> edges;
        int x = mask;
        for (int u = 1; u <= 2; u++)
            for (int v = 1; v <= 2; v++)
            {
                int state = x % 3;
                x /= 3;
                if (state) edges.push_back({u, v, state == 1 ? -1 : 2});
            }
        check(2, edges);
    }
    mt19937 rng(5905);
    for (int trial = 0; trial < 3000; trial++)
    {
        int n = rng() % 8 + 1;
        vector<tuple<int, int, long long>> edges;
        for (int i = 0, m = rng() % 25; i < m; i++)
            edges.push_back(
                {int(rng() % n + 1), int(rng() % n + 1), int(rng() % 17) - 6});
        check(n, edges);
    }
    check(4, {{1, 2, LLONG_MIN}, {2, 3, LLONG_MIN}, {3, 4, LLONG_MAX}});
    check(3, {{1, 2, LLONG_MAX}, {2, 3, LLONG_MAX}});
    check(3, {{2, 3, LLONG_MIN}, {3, 2, LLONG_MAX}});
    Johnson changed(3);
    assert(changed.build());
    changed.add(3, 3, -1);
    assert(!changed.ready && !changed.build());
    const int n = 3000;
    Johnson large(n);
    for (int u = 2; u <= n; u++)
    {
        large.add(u, u - 1, -3);
        large.add(u, u - 1, 0);
    }
    large.add(1, 1, 0);
    large.add(n, n, 0);
    assert(large.build());
    for (int s = 1; s <= n; s++)
    {
        auto d = large.distances(s);
        for (int v = 1; v <= n; v++)
            assert(d[v] == (v <= s ? I(-3) * (s - v) : Johnson::inf));
    }
    cout << "Johnson: Floyd oracle, disconnected negative cycles, parallel/self edges, "
            "int64 extremes, rebuild and 3000x6000 all-source chain PASS\n";
}
