#include "../src/compact/blossom.hpp"
#include "../src/classic/blossom.hpp"
#include <iostream>
#include <random>

int brute(const std::vector<unsigned> &g, unsigned mask, std::vector<int> &dp)
{
    if (!mask)
        return 0;
    int &answer = dp[mask];
    if (answer != -1)
        return answer;
    int u = __builtin_ctz(mask);
    unsigned rest = mask ^ (1U << u);
    answer = brute(g, rest, dp);
    for (unsigned candidates = g[u] & rest; candidates; candidates &= candidates - 1)
    {
        int v = __builtin_ctz(candidates);
        answer = std::max(answer, 1 + brute(g, rest ^ (1U << v), dp));
    }
    return answer;
}

void check(const std::vector<unsigned> &g, std::mt19937 &rng)
{
    int n = g.size();
    Blossom a(n);
    static General_Matching<20> b;
    b.Init(n);
    std::vector<std::pair<int, int>> edges;
    for (int u = 0; u < n; u++)
    {
        edges.push_back({u, u});
        for (int v = u + 1; v < n; v++)
        {
            if (g[u] >> v & 1)
            {
                edges.push_back({u, v});
                if (rng() % 3 == 0)
                    edges.push_back({u, v});
            }
        }
    }
    std::shuffle(edges.begin(), edges.end(), rng);
    for (auto [u, v] : edges)
    {
        a.add(u, v);
        b.Insert(u, v);
    }
    std::vector<int> dp(1U << n, -1);
    int expected = brute(g, (1U << n) - 1, dp);
    for (int repeat = 0; repeat < 2; repeat++)
    {
        assert(a.solve() == expected);
        assert(b.Solve() == expected);
        for (int style = 0; style < 2; style++)
        {
            int count = 0;
            for (int u = 0; u < n; u++)
            {
                int v = style ? b.mate[u] : a.mate[u];
                if (v == -1)
                    continue;
                assert(0 <= v && v < n && u != v);
                assert((style ? b.mate[v] : a.mate[v]) == u);
                assert(g[u] >> v & 1);
                count++;
            }
            assert(count == 2 * expected);
        }
    }
}

int main()
{
    std::mt19937 rng(132477);
    for (int n = 0; n <= 6; n++)
    {
        int m = n * (n - 1) / 2;
        for (unsigned mask = 0; mask < (1U << m); mask++)
        {
            std::vector<unsigned> g(n);
            int bit = 0;
            for (int u = 0; u < n; u++)
            {
                for (int v = u + 1; v < n; v++)
                {
                    if (mask >> bit & 1)
                    {
                        g[u] |= 1U << v;
                        g[v] |= 1U << u;
                    }
                    bit++;
                }
            }
            check(g, rng);
        }
    }
    for (int trial = 0; trial < 3000; trial++)
    {
        int n = 7 + rng() % 12;
        int density = rng() % 101;
        std::vector<unsigned> g(n);
        for (int u = 0; u < n; u++)
        {
            for (int v = u + 1; v < n; v++)
            {
                if ((int)(rng() % 100) < density)
                {
                    g[u] |= 1U << v;
                    g[v] |= 1U << u;
                }
            }
        }
        check(g, rng);
    }
    Blossom a(501);
    static General_Matching<501> b;
    b.Init(501);
    for (int u = 0; u < 501; u++)
    {
        for (int v = u + 1; v < 501; v++)
        {
            a.add(u, v);
            b.Insert(u, v);
        }
    }
    assert(a.solve() == 250);
    assert(b.Solve() == 250);
    std::cout << "Blossom exhaustive n<=6, subset DP, duplicate edges and dense graph PASS\n";
}
