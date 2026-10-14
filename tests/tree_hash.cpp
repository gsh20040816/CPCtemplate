#include "../src/compact/tree_isomorphism.hpp"
#include <chrono>
#include <iostream>
#include <random>
#include <string>
#include <unordered_map>

// Deterministic AHU canonical strings are the oracle for the probabilistic Mix13 hash.
using u64 = unsigned long long;
mt19937_64 rng(24);

string canon(const vector<vector<int>> &g, int u, int p)
{
    vector<string> parts;
    for (int v : g[u])
        if (v != p) parts.push_back(canon(g, v, u));
    sort(parts.begin(), parts.end());
    string s = "(";
    for (auto &x : parts) s += x;
    return s + ")";
}

vector<vector<int>> random_tree(int n)
{
    vector<vector<int>> g(n);
    for (int v = 1; v < n; v++)
    {
        int u = rng() % (rng() % 3 ? v : min(v, 3)); // mix of bushy and repeated shapes
        g[u].push_back(v), g[v].push_back(u);
    }
    for (auto &a : g) shuffle(a.begin(), a.end(), rng);
    return g;
}

int main()
{
    u64 s1 = rng() | 1, s2 = rng() | 1;
    if (s1 == s2) s2 ^= 2;
    unordered_map<u64, string> seen1;       // first hash -> canonical form, across all trees
    map<pair<u64, u64>, string> seen;       // full pair -> canonical form
    long long checks = 0;
    for (int it = 0; it < 3000; it++)
    {
        int n = 1 + rng() % 14;
        auto g = random_tree(n);
        int root = rng() % n;
        auto h = tree_hash(g, root, s1, s2);
        // parent array for the oracle
        vector<int> fa(n, -1), q{root};
        for (int i = 0; i < (int)q.size(); i++)
            for (int v : g[q[i]])
                if (v != fa[q[i]]) fa[v] = q[i], q.push_back(v);
        for (int u = 0; u < n; u++)
        {
            string c = canon(g, u, fa[u]);
            auto [p, fresh] = seen.emplace(h[u], c);
            assert(p->second == c); // equal hash => isomorphic (no collision observed)
            auto [p1, f1] = seen1.emplace(h[u].first, c);
            assert(p1->second == c);
            checks++;
        }
        // isomorphic => equal hash: relabel and reshuffle, compare the root hash
        vector<int> perm(n);
        iota(perm.begin(), perm.end(), 0);
        shuffle(perm.begin(), perm.end(), rng);
        vector<vector<int>> g2(n);
        for (int u = 0; u < n; u++)
            for (int v : g[u]) g2[perm[u]].push_back(perm[v]);
        for (auto &a : g2) shuffle(a.begin(), a.end(), rng);
        auto h2 = tree_hash(g2, perm[root], s1, s2);
        for (int u = 0; u < n; u++) assert(h2[perm[u]] == h[u]), checks++;
        // rerooting agrees with direct recomputation at every root
        auto f = tree_hash_reroot(g, root, h);
        for (int u = 0; u < n; u++) assert(f[u] == tree_hash(g, u, s1, s2)[u]), checks++;
    }
    // single vertex: hash is the seed pair
    auto one = tree_hash(vector<vector<int>>(1), 0, s1, s2);
    assert(one[0] == make_pair(s1, s2));
    // million-vertex chain and star, iterative traversal
    for (int shape = 0; shape < 2; shape++)
    {
        int n = 1000000;
        vector<vector<int>> g(n);
        for (int v = 1; v < n; v++)
        {
            int u = shape ? 0 : v - 1;
            g[u].push_back(v), g[v].push_back(u);
        }
        auto t = chrono::steady_clock::now();
        auto h = tree_hash(g, 0, s1, s2);
        auto f = tree_hash_reroot(g, 0, h);
        double sec = chrono::duration<double>(chrono::steady_clock::now() - t).count();
        assert(sec < 3);
        if (shape) // every leaf of the star has the same hash; centre differs
        {
            for (int v = 2; v < n; v++) assert(h[v] == h[1] && f[v] == f[1]);
            assert(h[0] != h[1]);
        }
        else // chain: all distinct subtree hashes
        {
            vector<pair<u64, u64>> s = h;
            sort(s.begin(), s.end());
            assert(unique(s.begin(), s.end()) == s.end());
        }
        checks++;
    }
    cout << "Tree hash: AHU canonical oracle (no collisions, relabel/shuffle invariant), reroot vs direct, "
            "single vertex and million-vertex chain/star PASS (" << checks << " checks)\n";
}
