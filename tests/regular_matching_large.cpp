#include "../src/compact/regular_matching.hpp"

int main()
{
    for (auto [n, d] : vector<pair<int, int>>{{2000000, 1}, {1000000, 2}, {100000, 20}, {1000, 2000}})
    {
        for (int shape = 0; shape < 3; shape++)
        {
            vector<vector<int>> g(n);
            for (int u = 0; u < n; u++)
                for (int j = 0; j < d; j++)
                {
                    int shift = shape == 0 ? j : (shape == 1 ? 0 : (j == d - 1));
                    g[u].push_back((u + shift) % n);
                }
            for (int seed = 0; seed < 3; seed++)
            {
                auto start = chrono::steady_clock::now();
                auto p = regular_matching(g, seed);
                vector<int> used(n);
                for (int u = 0; u < n; u++)
                {
                    if (p[u] < 0 || p[u] >= n || used[p[u]]++) abort();
                    if (find(g[u].begin(), g[u].end(), p[u]) == g[u].end()) abort();
                }
                double time = chrono::duration<double>(chrono::steady_clock::now() - start).count();
                cout << "PASS n=" << n << " d=" << d << " shape=" << shape << " seed=" << seed << " seconds=" << time << endl;
            }
        }
    }
}
