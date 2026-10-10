#include "../src/compact/cactus.hpp"
#include <random>

using Edge = tuple<int, int, long long>;
void check(int n, const vector<Edge> &edges)
{
    Cactus a(n);
    const long long inf = LLONG_MAX / 3;
    vector<vector<long long>> d(n + 1, vector<long long>(n + 1, inf));
    for (int i = 1; i <= n; i++) d[i][i] = 0;
    for (auto [u, v, w] : edges)
    {
        a.add(u, v, w);
        d[u][v] = d[v][u] = w;
    }
    for (int k = 1; k <= n; k++)
        for (int i = 1; i <= n; i++)
            for (int j = 1; j <= n; j++)
                d[i][j] = min(d[i][j], d[i][k] + d[k][j]);
    a.build();
    for (int repeat = 0; repeat < 3; repeat++)
    {
        auto b = a;
        for (int i = 1; i <= n; i++)
            for (int j = 1; j <= n; j++)
                if (b.distance(i, j) != (d[i][j] == inf ? -1 : d[i][j]))
                {
                    cerr << "Mismatch " << n << ' ' << i << ' ' << j << '\n';
                    abort();
                }
        a.build();
    }
}

// Independent definition check: enumerate simple cycles and count edge use.
bool cactus(int n, const vector<Edge> &edges)
{
    vector<vector<pair<int, int>>> g(n + 1);
    for (int id = 0; id < int(edges.size()); id++)
    {
        auto [u, v, w] = edges[id];
        g[u].push_back({v, id});
        g[v].push_back({u, id});
    }
    vector<int> used(edges.size()), path;
    auto dfs = [&](auto &&self, int s, int u, int mask) -> void
    {
        for (auto [v, id] : g[u])
        {
            if (v == s && path.size() >= 2)
            {
                // Each undirected simple cycle is encountered twice.
                used[id]++;
                for (int e : path) used[e]++;
            }
            else if (v > s && !(mask >> v & 1))
            {
                path.push_back(id);
                self(self, s, v, mask | (1 << v));
                path.pop_back();
            }
        }
    };
    for (int s = 1; s <= n; s++) dfs(dfs, s, s, 1 << s);
    return all_of(used.begin(), used.end(), [](int x) { return x <= 2; });
}

int main()
{
    check(0, {});
    int exhaustive = 0;
    for (int n = 1; n <= 6; n++)
    {
        vector<pair<int, int>> possible;
        for (int u = 1; u <= n; u++)
            for (int v = u + 1; v <= n; v++) possible.push_back({u, v});
        for (int mask = 0; mask < (1 << possible.size()); mask++)
        {
            vector<Edge> edges;
            for (int k = 0; k < int(possible.size()); k++)
            {
                auto [u, v] = possible[k];
                if (mask >> k & 1) edges.push_back({u, v, (k * 17 + mask) % 13});
            }
            if (!cactus(n, edges)) continue;
            check(n, edges);
            exhaustive++;
        }
    }
    mt19937 rng(5236);
    for (int trial = 0; trial < 3000; trial++)
    {
        int n = 1 + rng() % 40;
        vector<Edge> edges;
        int now = 1;
        while (now < n)
        {
            int u = 1 + rng() % now;
            int take = min<int>(n - now, 1 + rng() % 6);
            int v = u;
            for (int j = 0; j < take; j++)
            {
                int x = ++now;
                edges.push_back({v, x, rng() % 1000});
                v = x;
            }
            if (take >= 2 && rng() % 2) edges.push_back({v, u, rng() % 1000});
        }
        vector<int> perm(n + 1);
        iota(perm.begin(), perm.end(), 0);
        shuffle(perm.begin() + 1, perm.end(), rng);
        for (auto &[u, v, w] : edges)
        {
            u = perm[u];
            v = perm[v];
            if (rng() % 2) swap(u, v);
        }
        shuffle(edges.begin(), edges.end(), rng);
        check(n, edges);
        if (!edges.empty()) edges.erase(edges.begin() + rng() % edges.size());
        check(n, edges);
    }
    check(4, {{1, 2, LLONG_MAX / 16}, {2, 3, LLONG_MAX / 16},
              {3, 1, 1}, {3, 4, LLONG_MAX / 16}});
    Cactus a(4);
    a.add(1, 2, 5);
    a.build();
    a.add(2, 3, 7);
    a.add(3, 1, 1);
    a.build();
    if (a.distance(2, 3) != 6 || a.distance(1, 4) != -1) abort();
    cout << "PASS: " << exhaustive << " exhaustive cactus forests, 3000 randomized graphs and deletions, rebuild/copy/add, 64-bit bounds\n";
}
