#include "../src/compact/graph.hpp"
#include <cassert>

int main()
{
    mt19937 rng(293074);
    for (int trial = 0; trial < 2500; trial++)
    {
        int n = rng() % 10;
        TwoSAT sat(n);
        vector<array<int, 4>> clauses;
        for (int stage = 0; stage < 6; stage++)
        {
            if (n)
            {
                int x = rng() % n + 1, y = rng() % n + 1;
                int a = rng() % 2, b = rng() % 2;
                clauses.push_back({x, a, y, b});
                sat.add(x, a, y, b);
            }
            auto valid = [&](int mask)
            {
                for (auto [x, a, y, b] : clauses)
                {
                    if (((mask >> (x - 1)) & 1) != a && ((mask >> (y - 1)) & 1) != b)
                        return false;
                }
                return true;
            };
            bool expected = false;
            for (int mask = 0; mask < (1 << n); mask++) expected |= valid(mask);
            for (int repeat = 0; repeat < 2; repeat++)
            {
                assert(sat.solve() == expected);
                // Kosaraju labels are topological; the assignment inequality depends on
                // this.
                for (int u = 1; u <= 2 * n; u++)
                    for (int v : sat.g.g[u]) assert(sat.g.bel[u] <= sat.g.bel[v]);
                if (!expected) continue;
                assert(sat.ans.size() == n + 1);
                int mask = 0;
                for (int x = 1; x <= n; x++)
                {
                    assert(sat.ans[x] == 0 || sat.ans[x] == 1);
                    mask |= sat.ans[x] << (x - 1);
                }
                assert(valid(mask));
            }
        }
    }
    for (int a = 0; a < 2; a++)
    {
        TwoSAT sat(1);
        sat.add(1, a, 1, a);
        assert(sat.solve() && sat.ans[1] == a);
        sat.add(1, !a, 1, !a);
        assert(!sat.solve());
    }
    cout << "TwoSAT: 2500 truth-table oracles, six clause additions, repeated solve, "
            "empty formula, units and contradictory units PASS\n";
}
