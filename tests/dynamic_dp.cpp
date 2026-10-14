#include "../src/compact/dynamic_dp.hpp"
#include <iostream>
#include <random>

// Dynamic DP versus a fresh O(n) tree DP after every update.
using ll = long long;
mt19937_64 rng(4719);

ll brute(const vector<vector<int>> &g, const vector<ll> &w, int root)
{
    int n = (int)g.size() - 1;
    vector<int> fa(n + 1), q{root};
    fa[root] = 0;
    for (int i = 0; i < (int)q.size(); i++)
        for (int v : g[q[i]])
            if (v != fa[q[i]]) fa[v] = q[i], q.push_back(v);
    vector<ll> f0(n + 1), f1(n + 1);
    for (int i = n - 1; i >= 0; i--)
    {
        int u = q[i];
        f1[u] += w[u];
        if (fa[u]) f0[fa[u]] += max(f0[u], f1[u]), f1[fa[u]] += f0[u];
    }
    return max(f0[root], f1[root]);
}

int main()
{
    long long checks = 0;
    for (int it = 0; it < 2000; it++)
    {
        int n = 1 + rng() % 30, root = 1 + rng() % n;
        HLD h(n);
        vector<vector<int>> g(n + 1);
        for (int v = 2; v <= n; v++)
        {
            int u = 1 + rng() % (rng() % 2 ? v - 1 : min(v - 1, 2));
            h.add(u, v), g[u].push_back(v), g[v].push_back(u);
        }
        h.build(root);
        vector<ll> w(n + 1);
        for (int i = 1; i <= n; i++) w[i] = (ll)(rng() % 21) - 10;
        DynamicDP d(h, w);
        assert(d.answer() == brute(g, w, root));
        for (int q = 0; q < 40; q++)
        {
            int u = 1 + rng() % n;
            w[u] = (ll)(rng() % 21) - 10;
            if (rng() % 8 == 0) w[u] = (ll)1e9;
            d.set(u, w[u]);
            assert(d.answer() == brute(g, w, root));
            checks++;
        }
    }
    // long chain: alternating picks
    int n = 100000;
    HLD h(n);
    vector<vector<int>> g(n + 1);
    for (int v = 2; v <= n; v++) h.add(v - 1, v), g[v - 1].push_back(v), g[v].push_back(v - 1);
    h.build(1);
    vector<ll> w(n + 1, 1);
    DynamicDP d(h, w);
    assert(d.answer() == n / 2);
    for (int q = 0; q < 1000; q++)
    {
        int u = 1 + rng() % n;
        w[u] = rng() % 100;
        d.set(u, w[u]);
    }
    assert(d.answer() == brute(g, w, 1));
    cout << "DynamicDP: 2000 random trees x 40 updates vs O(n) tree DP, large weights and a "
            "100000-vertex chain PASS (" << checks << " checks)\n";
}
