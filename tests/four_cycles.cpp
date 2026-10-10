#include "../src/compact/four_cycles.hpp"
#include <bits/stdc++.h>
using namespace std;

#define CHECK(x) do { if (!(x)) { cerr << "line " << __LINE__ << '\n'; abort(); } } while (0)

long long brute(int n, const vector<pair<int, int>> &edges)
{
    vector<vector<bool>> g(n, vector<bool>(n));
    for (auto [u, v] : edges) g[u][v] = g[v][u] = true;
    long long ans = 0;
    for (int a = 0; a < n; a++)
        for (int b = a + 1; b < n; b++)
            for (int c = b + 1; c < n; c++)
                for (int d = c + 1; d < n; d++)
                {
                    ans += g[a][b] && g[b][c] && g[c][d] && g[d][a];
                    ans += g[a][b] && g[b][d] && g[d][c] && g[c][a];
                    ans += g[a][c] && g[c][b] && g[b][d] && g[d][a];
                }
    return ans;
}

int main()
{
    int total = 0;
    for (int n = 0; n <= 6; n++)
    {
        vector<pair<int, int>> all;
        for (int u = 0; u < n; u++)
            for (int v = u + 1; v < n; v++) all.emplace_back(u, v);
        for (int mask = 0; mask < (1 << all.size()); mask++)
        {
            vector<pair<int, int>> edges;
            for (int i = 0; i < (int)all.size(); i++)
                if (mask >> i & 1) edges.push_back(all[i]);
            CHECK(count_four_cycles(n, edges) == brute(n, edges));
            total++;
        }
    }
    mt19937 rng(367189);
    for (int trial = 0; trial < 3000; trial++)
    {
        int n = rng() % 20 + 1;
        vector<pair<int, int>> edges;
        for (int u = 0; u < n; u++)
            for (int v = u + 1; v < n; v++)
                if (rng() % 3 == 0) edges.emplace_back(u, v);
        long long want = brute(n, edges);
        CHECK(count_four_cycles(n, edges) == want);
        vector<int> label(n);
        iota(label.begin(), label.end(), 0);
        shuffle(label.begin(), label.end(), rng);
        for (auto &[u, v] : edges)
        {
            u = label[u];
            v = label[v];
            if (rng() & 1) swap(u, v);
        }
        shuffle(edges.begin(), edges.end(), rng);
        auto old = edges;
        CHECK(count_four_cycles(n, edges) == want);
        CHECK(edges == old);
        CHECK(count_four_cycles(n + 3, edges) == want);
    }
    vector<pair<int, int>> edges;
    int n = 632;
    for (int u = 0; u < n; u++)
        for (int v = u + 1; v < n; v++) edges.emplace_back(u, v);
    CHECK(count_four_cycles(n, edges) == 1LL * n * (n - 1) * (n - 2) * (n - 3) / 8);
    edges.clear();
    for (int u = 2; u < 100000; u++)
    {
        edges.emplace_back(0, u);
        edges.emplace_back(1, u);
    }
    CHECK(count_four_cycles(100000, edges) == 1LL * 99998 * 99997 / 2);
    edges.clear();
    for (int u = 0; u < 400; u++)
        for (int v = 400; v < 900; v++) edges.emplace_back(u, v);
    CHECK(count_four_cycles(100000, edges) == 1LL * 400 * 399 / 2 * 500 * 499 / 2);
    edges.clear();
    for (int u = 1; u < 100000; u++) edges.emplace_back(0, u);
    CHECK(count_four_cycles(100000, edges) == 0);
    CHECK(count_four_cycles(100000, {}) == 0);
    cout << total << " exhaustive graphs; 3000 relabelled graphs; K632/K2,99998/K400,500/star/isolates PASS\n";
}
