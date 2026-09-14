#include "../src/compact/odd_induced_partition.hpp"
#include <iostream>
#include <random>
using namespace std;

void check(int n, const vector<pair<int, int>> &edges)
{
    vector<vector<int>> g(n);
    for (auto [u, v] : edges)
    {
        g[u].push_back(v);
        g[v].push_back(u);
    }
    vector<bool> seen(n);
    bool possible = true;
    for (int s = 0; s < n; s++)
        if (!seen[s])
        {
            queue<int> q;
            q.push(s);
            seen[s] = true;
            int size = 0;
            while (!q.empty())
            {
                int u = q.front();
                q.pop();
                size++;
                for (int v : g[u])
                    if (!seen[v])
                    {
                        seen[v] = true;
                        q.push(v);
                    }
            }
            possible &= size % 2 == 0;
        }
    auto ans = odd_induced_partition(n, edges);
    assert(bool(ans) == possible);
    if (!ans) return;
    vector<int> degree(n);
    for (auto [u, v] : edges)
        if ((*ans)[u] == (*ans)[v]) degree[u]++, degree[v]++;
    for (int u = 0; u < n; u++)
        assert(1 <= (*ans)[u] && (*ans)[u] <= n && degree[u] % 2 == 1);
}

int main(int argc, char **argv)
{
    int max_n = argc > 1 ? stoi(argv[1]) : 6;
    check(0, {});
    for (int n = 1; n <= max_n; n++)
    {
        vector<pair<int, int>> all;
        for (int u = 0; u < n; u++)
            for (int v = u + 1; v < n; v++) all.push_back({u, v});
        for (int mask = 0; mask < (1 << all.size()); mask++)
        {
            vector<pair<int, int>> edges;
            for (int i = 0; i < (int)all.size(); i++)
                if (mask >> i & 1) edges.push_back(all[i]);
            check(n, edges);
        }
    }
    mt19937 rng(215);
    for (int trial = 0; trial < 10000; trial++)
    {
        int n = rng() % 70 + 1;
        vector<pair<int, int>> edges;
        int rate = rng() % 101;
        for (int u = 0; u < n; u++)
            for (int v = u + 1; v < n; v++)
                if (int(rng() % 100) < rate) edges.push_back({u, v});
        shuffle(edges.begin(), edges.end(), rng);
        check(n, edges);
    }
    const int n = 100000;
    vector<pair<int, int>> edges;
    for (int u = 1; u < n; u++) edges.push_back({u - 1, u});
    check(n, edges);
    edges.clear();
    for (int u = 1; u < n; u++) edges.push_back({0, u});
    check(n, edges);
    edges.clear();
    const int q = (n - 2) / 2;
    for (int u = 1; u < q; u++) edges.push_back({u - 1, u});
    for (int u = 0; u < q; u++) edges.push_back({u, 2 * q});
    for (int u = 0; u < q; u++) edges.push_back({u, q + u});
    edges.push_back({0, 2 * q + 1});
    check(n, edges);
    edges.clear();
    for (int u = 0; u < 600; u++)
        for (int v = u + 1; v < 600; v++) edges.push_back({u, v});
    check(600, edges);
    cout << "Odd induced partition: all simple graphs through n=" << max_n
         << ", 10000 shuffled random graphs, induced-degree certificates; "
            "100000-node path/star/repeated-reparent fan and 600-clique PASS\n";
}
