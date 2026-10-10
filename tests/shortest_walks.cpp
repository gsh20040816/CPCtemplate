#include "../src/compact/shortest_walks.hpp"
#include <cstdlib>
#include <iostream>
#include <random>
using namespace std;

void check(bool ok)
{
    if (!ok) abort();
}

int main()
{
    mt19937 rng(29012865);
    for (int test = 0; test < 1200; test++)
    {
        int n = 1 + rng() % 7;
        StrictSecondShortest strict(n);
        KShortestWalks walks(n);
        for (int e = rng() % 25; e > 0; e--)
        {
            int u = 1 + rng() % n;
            int v = 1 + rng() % n;
            int w = rng() % 5;
            strict.add(u, v, w);
            walks.add(u, v, w + 1);
        }
        for (int s = 1; s <= n; s++)
        {
            int limit = 4 * n * 5;
            vector<vector<bool>> reach(limit + 1, vector<bool>(n + 1));
            reach[0][s] = true;
            for (int d = 0; d <= limit; d++)
            {
                // Independent fixed-point closure for zero-weight edges.
                for (int pass = 0; pass < n; pass++)
                {
                    for (int u = 1; u <= n; u++)
                    {
                        if (!reach[d][u]) continue;
                        for (auto [v, w] : strict.g[u])
                        {
                            if (d + w <= limit) reach[d + w][v] = true;
                        }
                    }
                }
            }
            auto got = strict.run(s);
            for (int v = 1; v <= n; v++)
            {
                array<long long, 2> want = {StrictSecondShortest::inf, StrictSecondShortest::inf};
                int count = 0;
                for (int d = 0; d <= limit && count < 2; d++)
                {
                    if (reach[d][v]) want[count++] = d;
                }
                check(got[v] == want);
            }
            int k = 8;
            limit = n * (k + 1) * 5;
            vector<vector<int>> ways(limit + 1, vector<int>(n + 1));
            ways[0][s] = 1;
            for (int d = 0; d <= limit; d++)
            {
                for (int u = 1; u <= n; u++)
                {
                    for (auto [v, w] : walks.g[u])
                    {
                        if (d + w <= limit)
                        {
                            ways[d + w][v] = min(k, ways[d + w][v] + ways[d][u]);
                        }
                    }
                }
            }
            for (int t = 1; t <= n; t++)
            {
                vector<long long> want;
                for (int d = 0; d <= limit && int(want.size()) < k; d++)
                {
                    for (int c = 0; c < ways[d][t] && int(want.size()) < k; c++)
                    {
                        want.push_back(d);
                    }
                }
                check(walks.run(s, t, k) == want);
                check(walks.run(s, t, 0).empty());
            }
        }
    }
    StrictSecondShortest a(3);
    a.add(1, 2, LLONG_MAX - 2);
    a.add(2, 3, 1);
    a.add(3, 3, 1);
    check(a.run(1)[3][0] == LLONG_MAX - 1);
    check(a.run(1)[3][1] == a.inf);
    a.add(1, 3, 0);
    check(a.run(1)[3][1] == 1);
    KShortestWalks b(3);
    b.add(1, 2, LLONG_MAX - 2);
    b.add(2, 3, 1);
    b.add(3, 3, 1);
    check(b.run(1, 3, 2) == vector<long long>{LLONG_MAX - 1});
    b.add(1, 3, 1);
    check(b.run(1, 3, 3) == (vector<long long>{1, 2, 3}));
    cout << "PASS 1200 multigraphs, all sources/targets, length-layer truth and signed64 boundary\n";
}
