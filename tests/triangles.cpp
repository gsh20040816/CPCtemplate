#include "../src/compact/enumerate_triangles.hpp"
#include <algorithm>
#include <array>
#include <iostream>
#include <set>
using namespace std;

int main()
{
    for (int n = 0; n <= 6; n++)
    {
        vector<pair<int, int>> all;
        for (int u = 0; u < n; u++)
            for (int v = u + 1; v < n; v++) all.push_back({u, v});
        for (unsigned mask = 0; mask < (1U << all.size()); mask++)
        {
            bool adj[6][6]{};
            vector<pair<int, int>> edges;
            for (int i = 0; i < int(all.size()); i++)
                if (mask >> i & 1)
                {
                    auto [u, v] = all[i];
                    adj[u][v] = adj[v][u] = true;
                    edges.push_back(i & 1 ? pair{u, v} : pair{v, u});
                }
            set<array<int, 3>> want, got;
            for (int u = 0; u < n; u++)
                for (int v = u + 1; v < n; v++)
                    for (int w = v + 1; w < n; w++)
                        if (adj[u][v] && adj[u][w] && adj[v][w]) want.insert({u, v, w});
            reverse(edges.begin(), edges.end());
            enumerate_triangles(n, edges, [&](int u, int v, int w)
            {
                array<int, 3> t{u, v, w};
                sort(t.begin(), t.end());
                assert(got.insert(t).second);
            });
            assert(got == want);
        }
    }
    auto count = [](int n, const vector<pair<int, int>> &edges)
    {
        long long result = 0;
        enumerate_triangles(n, edges, [&](int, int, int) { result++; });
        return result;
    };
    vector<pair<int, int>> edges;
    for (int u = 0; u < 300; u++)
        for (int v = u + 1; v < 300; v++) edges.push_back({u, v});
    assert(count(300, edges) == 300LL * 299 * 298 / 6);
    edges.clear();
    for (int v = 1; v < 200000; v++) edges.push_back({0, v});
    assert(count(200000, edges) == 0);
    edges.clear();
    for (int u = 0; u < 200; u++)
        for (int v = 200; v < 500; v++) edges.push_back({u, v});
    assert(count(500, edges) == 0);
    cout << "Triangles: exhaustive simple graphs through six vertices, unique callback certificates, reversed inputs, dense clique, 200000-vertex star and complete bipartite graph PASS\n";
}
