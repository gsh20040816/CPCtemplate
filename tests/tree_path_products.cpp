#include "../src/compact/tree_path_products.hpp"
#include <cassert>
#include <iostream>
#include <random>

// Independent DFS enumerates each endpoint and multiplies along its unique path.
template <int mod>
long long oracle(const vector<vector<int>> &g, const vector<int> &w, int root)
{
    long long answer = 0;
    auto dfs = [&](auto &&self, int u, int parent, long long product) -> void
    {
        product = product * w[u] % mod;
        answer = (answer + product) % mod;
        for (int v : g[u])
            if (v != parent) self(self, v, u, product);
    };
    dfs(dfs, root, -1, 1);
    return answer;
}

template <int mod> void random_tests()
{
    using Z = ModInt<mod>;
    mt19937 rng(4339);
    for (int test = 0; test < 1000; test++)
    {
        int n = rng() % 35 + 1;
        vector<vector<int>> g(n);
        vector<int> w(n);
        vector<Z> weight(n);
        for (int u = 1; u < n; u++)
        {
            int v = rng() % u;
            g[u].push_back(v);
            g[v].push_back(u);
        }
        for (int u = 0; u < n; u++) weight[u] = w[u] = rng() % mod;
        TreePathProducts<mod> tree(g, weight);
        for (int step = 0; step < 100; step++)
        {
            int u = rng() % n;
            if (step % 3 == 0)
            {
                int value = step % 9 == 0 ? 0 : rng() % mod;
                tree.set(u, Z(value));
                w[u] = value;
            }
            else
                assert(tree.query(u).v == oracle<mod>(g, w, u));
        }
        for (int u = 0; u < n; u++) assert(tree.query(u).v == oracle<mod>(g, w, u));
    }
}

int main()
{
    random_tests<998244353>();
    random_tests<8>();
    using Z = ModInt<998244353>;
    int n = 200000;
    for (bool star : {false, true})
    {
        vector<vector<int>> g(n);
        for (int u = 1; u < n; u++)
        {
            int v = star ? 0 : u - 1;
            g[u].push_back(v);
            g[v].push_back(u);
        }
        TreePathProducts<998244353> tree(g, vector<Z>(n, 1));
        for (int u : {0, n - 1, n / 2, 1}) assert(tree.query(u).v == n);
        tree.set(n / 2, 0);
        assert(tree.query(n / 2).v == 0);
        assert(tree.query(0).v == (star ? n - 1 : n / 2));
        assert(tree.query(n - 1).v == (star ? n - 1 : n - n / 2 - 1));
        tree.set(n / 2, 1);
        tree.set(0, 0);
        assert(tree.query(n - 1).v == (star ? 1 : n - 1));
        tree.set(0, 1);
        for (int i = 0; i < 20000; i++)
        {
            int u = i % 2 ? 0 : n - 1;
            assert(tree.query(u).v == n);
        }
    }
    cout << "TreePathProducts: 2000 random trees, independent endpoint paths, zeros, "
            "composite modulus, 200000 chain/star and repeated reroot PASS\n";
}
