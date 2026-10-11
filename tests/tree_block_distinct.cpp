#include "../src/compact/tree_block_distinct.hpp"
#include <random>

void check(int n, const vector<pair<int, int>> &edges, const vector<long long> &values, int block, int root)
{
    TreeBlockDistinct a(n);
    for (auto [u, v] : edges) a.add(u, v);
    a.build(values, block, root);
    if (a.k > n / block + 1) abort();
    for (int u = 1; u <= n; u++)
        if (a.dep[u] - a.dep[a.near[u]] >= block) abort();
    vector<vector<int>> want(n + 1, vector<int>(n + 1));
    auto dfs = [&](auto &&self, int s, int u, int p, multiset<long long> &path) -> void
    {
        path.insert(values[u]);
        want[s][u] = set<long long>(path.begin(), path.end()).size();
        for (int v : a.g[u])
            if (v != p) self(self, s, v, u, path);
        path.erase(path.find(values[u]));
    };
    for (int s = 1; s <= n; s++)
    {
        multiset<long long> path;
        dfs(dfs, s, s, 0, path);
    }
    for (int repeat = 0; repeat < 2; repeat++)
    {
        auto b = a;
        for (int u = 1; u <= n; u++)
            for (int v = 1; v <= n; v++)
                if (b.query(u, v) != want[u][v]) abort();
        a.build(values, block, n + 1 - root);
    }
}

int main()
{
    int exhaustive = 0;
    for (int n = 1; n <= 6; n++)
    {
        int total = 1;
        for (int i = 0; i < n - 2; i++) total *= n;
        for (int code = 0; code < total; code++)
        {
            vector<pair<int, int>> edges;
            vector<int> degree(n + 1, 1), seq;
            int value = code;
            for (int i = 0; i < n - 2; i++)
            {
                int x = value % n + 1;
                value /= n;
                seq.push_back(x);
                degree[x]++;
            }
            for (int v : seq)
            {
                int u = 1;
                while (degree[u] != 1) u++;
                edges.push_back({u, v});
                degree[u]--;
                degree[v]--;
            }
            if (n > 1)
            {
                int u = 1;
                while (degree[u] != 1) u++;
                int v = u + 1;
                while (degree[v] != 1) v++;
                edges.push_back({u, v});
            }
            vector<long long> colors(n + 1);
            for (int u = 1; u <= n; u++) colors[u] = (u * 7 + code) % 3;
            for (int block : {1, 2, 3, n + 1})
                check(n, edges, colors, block, 1 + code % n);
            exhaustive++;
        }
    }
    mt19937_64 rng(6177);
    for (int trial = 0; trial < 1500; trial++)
    {
        int n = 1 + rng() % 65;
        vector<int> perm(n + 1);
        iota(perm.begin(), perm.end(), 0);
        shuffle(perm.begin() + 1, perm.end(), rng);
        vector<pair<int, int>> edges;
        for (int v = 2; v <= n; v++) edges.push_back({perm[v], perm[1 + rng() % (v - 1)]});
        shuffle(edges.begin(), edges.end(), rng);
        vector<long long> colors(n + 1);
        for (int u = 1; u <= n; u++) colors[u] = trial % 2 ? rng() % 7 : static_cast<long long>(rng());
        check(n, edges, colors, 1 + rng() % (n + 3), 1 + rng() % n);
    }
    for (int n : {63, 64, 65, 127, 128, 129})
    {
        vector<pair<int, int>> edges;
        vector<long long> colors(n + 1);
        for (int u = 1; u <= n; u++)
        {
            colors[u] = u;
            if (u > 1) edges.push_back({u - 1, u});
        }
        colors[1] = LLONG_MIN;
        colors[n] = LLONG_MAX;
        check(n, edges, colors, 7, n);
    }
    TreeBlockDistinct a(3);
    a.add(1, 2);
    a.add(2, 3);
    a.build({0, 5, 5, 5}, 2);
    if (a.query(1, 3) != 1) abort();
    a.build({0, 5, 6, 7}, 2);
    if (a.query(1, 3) != 3) abort();
    cout << "PASS: " << exhaustive << " labelled trees, 1500 random trees, block sizes/root/rebuild/copy/64-bit colors/bit-word boundaries\n";
}
