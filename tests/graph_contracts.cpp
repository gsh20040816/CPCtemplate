#include "../src/compact/graph.hpp"
#include "../src/classic/graph.hpp"
#include <iostream>
#include <random>
#include <tuple>

using Clause = std::tuple<int, bool, int, bool>;

void sat_check(int n, const std::vector<Clause> &clauses)
{
    TwoSAT a(n);
    Two_SAT b(n);
    std::vector<Clause> current;
    for (int stage = 0; stage < 2; stage++)
    {
        int size = stage ? clauses.size() : clauses.size() / 2;
        while ((int)current.size() < size)
        {
            auto [x, u, y, v] = clauses[current.size()];
            current.push_back({x, u, y, v});
            a.add(x, u, y, v);
            b.Insert(x, u, y, v);
        }
        auto valid = [&](const std::vector<int> &values)
        {
            for (auto [x, u, y, v] : current)
                if ((values[x] != u) && (values[y] != v))
                    return false;
            return true;
        };
        bool exists = false;
        for (int mask = 0; mask < (1 << n); mask++)
        {
            std::vector<int> values(n + 1);
            for (int x = 1; x <= n; x++)
                values[x] = mask >> (x - 1) & 1;
            exists |= valid(values);
        }
        for (int repeat = 0; repeat < 2; repeat++)
        {
            assert(a.solve() == exists && b.Solve() == exists);
            if (exists)
            {
                assert(valid(a.ans) && valid(b.ans));
                for (int x = 1; x <= n; x++)
                    assert((a.ans[x] == 0 || a.ans[x] == 1) &&
                           (b.ans[x] == 0 || b.ans[x] == 1));
            }
        }
    }
}

void shortest_check(int n, const std::vector<std::tuple<int, int, long long>> &edges)
{
    using I = __int128_t;
    const I inf = I(1) << 120;
    std::vector<std::vector<I>> weight(n + 1, std::vector<I>(n + 1, inf));
    Dijkstra a(n);
    Shortest_Path b(n);
    for (auto [u, v, w] : edges)
    {
        a.add(u, v, w);
        b.Insert(u, v, w);
        weight[u][v] = std::min(weight[u][v], I(w));
    }
    auto d = weight;
    for (int u = 1; u <= n; u++)
        d[u][u] = 0;
    for (int k = 1; k <= n; k++)
        for (int u = 1; u <= n; u++)
            for (int v = 1; v <= n; v++)
                d[u][v] = std::min(d[u][v], d[u][k] + d[k][v]);
    for (int source = 1; source <= n; source++)
    {
        a.run(source);
        b.Run(source);
        for (int target = 1; target <= n; target++)
        {
            long long expected =
                d[source][target] == inf ? LLONG_MAX : (long long)d[source][target];
            assert(a.dis[target] == expected && b.dis[target] == expected);
            for (auto path : {a.path(target), b.Path(target)})
            {
                if (expected == LLONG_MAX)
                {
                    assert(path.empty());
                    continue;
                }
                assert(!path.empty() && path.front() == source &&
                       path.back() == target);
                std::vector<int> seen(n + 1);
                I sum = 0;
                for (int i = 0; i < (int)path.size(); i++)
                {
                    assert(1 <= path[i] && path[i] <= n && !seen[path[i]]);
                    seen[path[i]] = 1;
                    if (i)
                        sum += weight[path[i - 1]][path[i]];
                }
                assert(sum == d[source][target]);
            }
        }
    }
}

int main()
{
    sat_check(0, {});
    for (int n = 1; n <= 2; n++)
    {
        std::vector<Clause> all;
        for (int x = 0; x < 2 * n; x++)
            for (int y = x; y < 2 * n; y++)
                all.push_back({x / 2 + 1, bool(x % 2), y / 2 + 1, bool(y % 2)});
        for (unsigned mask = 0; mask < (1U << all.size()); mask++)
        {
            std::vector<Clause> clauses;
            for (int i = 0; i < (int)all.size(); i++)
                if (mask >> i & 1)
                    clauses.push_back(all[i]);
            sat_check(n, clauses);
        }
    }
    std::mt19937_64 rng(734117);
    for (int trial = 0; trial < 1000; trial++)
    {
        int n = 1 + rng() % 8;
        std::vector<Clause> clauses;
        for (int i = rng() % 40; i; i--)
            clauses.push_back(
                {1 + rng() % n, bool(rng() % 2), 1 + rng() % n, bool(rng() % 2)});
        sat_check(n, clauses);
        std::vector<std::tuple<int, int, long long>> edges;
        for (int i = rng() % 50; i; i--)
            edges.push_back({1 + rng() % n, 1 + rng() % n, rng() % 1000000000000ULL});
        shortest_check(n, edges);
    }
    shortest_check(4,
                   {{1, 2, LLONG_MAX - 2},
                    {2, 3, 1},
                    {2, 3, 3},
                    {1, 3, LLONG_MAX},
                    {1, 4, 0},
                    {4, 1, 0}});
    std::cout << "Dual Dijkstra distances/routes and 2-SAT exhaustive assignment "
                 "oracle PASS\n";
}
