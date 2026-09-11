#include "../src/compact/tree_path_kth.hpp"
#include "../src/classic/tree_path_kth.hpp"
#include <climits>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <pthread.h>
using ll = long long;

vector<int> parents(const vector<vector<int>> &g, int r)
{
    vector<int> p(g.size(), -1), q{r};
    p[r] = 0;
    for (int i = 0; i < int(q.size()); i++)
        for (int v : g[q[i]])
            if (p[v] == -1)
            {
                p[v] = q[i];
                q.push_back(v);
            }
    return p;
}

void run_tests()
{
    mt19937_64 rng(2633);
    static Tree_Path_Kth<50, 400, 6> classic;
    for (int trial = 0; trial < 100; trial++)
    {
        int n = 1 + rng() % 50;
        vector<ll> weights(n);
        vector<ll> choices{LLONG_MIN, LLONG_MAX, -1, 0, 1, 7};
        for (ll &w : weights)
            w = choices[rng() % choices.size()];
        TreePathKth dynamic(weights);
        classic.Init(weights);
        vector<vector<int>> g(n + 1);
        for (int v = 2; v <= n; v++)
        {
            int u = trial % 3 == 0 ? v - 1 : 1 + rng() % (v - 1);
            g[u].push_back(v);
            g[v].push_back(u);
            dynamic.add(u, v);
            classic.Insert(u, v);
        }
        for (int root : {1, n})
        {
            dynamic.build(root);
            classic.Build(root);
            auto p = parents(g, root);
            for (int u = 1; u <= n; u++)
            {
                auto from_u = parents(g, u);
                vector<bool> ancestors(n + 1);
                for (int x = u; x; x = p[x])
                    ancestors[x] = true;
                for (int v = 1; v <= n; v++)
                {
                    int z = v;
                    while (!ancestors[z])
                        z = p[z];
                    assert(dynamic.lca(u, v) == z);
                    assert(classic.Lca(u, v) == z);
                    vector<ll> values;
                    for (int x = v; x; x = from_u[x])
                        values.push_back(weights[x - 1]);
                    sort(values.begin(), values.end());
                    for (int k = 1; k <= int(values.size()); k++)
                    {
                        assert(dynamic.kth(u, v, k) == values[k - 1]);
                        assert(classic.Kth(u, v, k) == values[k - 1]);
                    }
                }
            }
        }
    }
    constexpr int n = 200000;
    vector<ll> a(n);
    iota(a.begin(), a.end(), 0);
    TreePathKth dynamic(a);
    static Tree_Path_Kth<n, n * 20, 18> large;
    large.Init(a);
    for (int u = 1; u < n; u++)
    {
        dynamic.add(u, u + 1);
        large.Insert(u, u + 1);
    }
    for (int root : {1, n})
    {
        dynamic.build(root);
        large.Build(root);
        assert(large.tot <= n * 19);
        assert(dynamic.t.size() <= size_t(n) * 19 + 1);
        for (int k : {1, 2, n / 2, n - 1, n})
        {
            assert(dynamic.kth(1, n, k) == k - 1);
            assert(large.Kth(1, n, k) == k - 1);
        }
        assert(dynamic.kth(99999, 100005, 4) == 100001);
        assert(large.Kth(99999, 100005, 4) == 100001);
    }
    large.Init({LLONG_MIN});
    large.Build();
    assert(large.Kth(1, 1, 1) == LLONG_MIN && large.tot == 1);
    cout << "Tree-path kth dual all-path sorted oracle, LCA, reroot and 200000-node recursion PASS\n";
}

void *entry(void *)
{
    run_tests();
    return nullptr;
}

int main()
{
    pthread_attr_t attr;
    assert(pthread_attr_init(&attr) == 0);
    assert(pthread_attr_setstacksize(&attr, 256ULL << 20) == 0);
    pthread_t worker;
    assert(pthread_create(&worker, &attr, entry, nullptr) == 0);
    assert(pthread_attr_destroy(&attr) == 0);
    assert(pthread_join(worker, nullptr) == 0);
}
