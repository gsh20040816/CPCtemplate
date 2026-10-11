#include "../src/compact/regular_matching.hpp"

void check(const vector<vector<int>> &g, uint64_t seed)
{
    auto original = g;
    auto match = regular_matching(g, seed);
    int n = g.size();
    if (g != original || (int)match.size() != n) abort();
    vector<int> used(n);
    for (int u = 0; u < n; u++)
    {
        int v = match[u];
        if (v < 0 || v >= n || used[v]++) abort();
        if (find(g[u].begin(), g[u].end(), v) == g[u].end()) abort();
    }
}

int main()
{
    check({}, 0);
    int exhaustive = 0;
    for (int n = 1; n <= 3; n++)
    {
        int limit = 1;
        for (int i = 0; i < n * n; i++) limit *= 3;
        for (int mask = 0; mask < limit; mask++)
        {
            vector<vector<int>> g(n);
            vector<int> degree(n);
            int cur = mask;
            for (int u = 0; u < n; u++)
                for (int v = 0; v < n; v++)
                {
                    int count = cur % 3;
                    cur /= 3;
                    degree[v] += count;
                    while (count--) g[u].push_back(v);
                }
            int d = g[0].size();
            bool regular = d > 0;
            for (int u = 0; u < n; u++) regular &= (int)g[u].size() == d && degree[u] == d;
            if (!regular) continue;
            for (uint64_t seed = 0; seed < 20; seed++) check(g, seed);
            exhaustive++;
        }
    }
    mt19937 rng(265);
    for (int test = 0; test < 3000; test++)
    {
        int n = rng() % 100 + 1;
        int d = rng() % 100 + 1;
        vector<vector<int>> g(n);
        vector<int> p(n);
        iota(p.begin(), p.end(), 0);
        for (int j = 0; j < d; j++)
        {
            if (test % 3 || j == 0) shuffle(p.begin(), p.end(), rng);
            for (int u = 0; u < n; u++) g[u].push_back(p[u]);
        }
        for (auto &row : g) shuffle(row.begin(), row.end(), rng);
        for (int seed = 0; seed < 4; seed++) check(g, rng());
    }
    cout << "PASS: " << exhaustive << " regular multiplicity-0..2 matrices with 20 seeds; 3000 permutation unions with 4 seeds\n";
}
