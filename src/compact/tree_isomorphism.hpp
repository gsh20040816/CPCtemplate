#pragma once
#include <algorithm>
#include <cassert>
#include <map>
#include <utility>
#include <vector>
using namespace std;

struct TreeIsomorphism
{
    map<vector<int>, int> codes;

    int rooted(const vector<vector<int>> &g, int root)
    {
        assert(0 <= root && root < int(g.size()));
        auto dfs = [&](auto &&self, int u, int p) -> int
        {
            vector<int> children;
            for (int v : g[u])
            {
                if (v == p) continue;
                children.push_back(self(self, v, u));
            }
            sort(children.begin(), children.end());
            int next = int(codes.size()) + 1;
            return codes.emplace(children, next).first->second;
        };
        return dfs(dfs, root, -1);
    }

    pair<int, int> unrooted(const vector<vector<int>> &g)
    {
        int n = g.size();
        assert(n > 0);
        vector<int> centers;
        auto dfs = [&](auto &&self, int u, int p) -> int
        {
            int size = 1, largest = 0;
            for (int v : g[u])
            {
                if (v == p) continue;
                int child = self(self, v, u);
                size += child;
                largest = max(largest, child);
            }
            largest = max(largest, n - size);
            if (largest <= n / 2) centers.push_back(u);
            return size;
        };
        dfs(dfs, 0, -1);
        int a = rooted(g, centers[0]);
        if (centers.size() == 1) return {a, 0};
        int b = rooted(g, centers[1]);
        if (a > b) swap(a, b);
        return {a, b};
    }
};

// BEGIN tree_hash
// Double 64-bit random rooted-tree hash (Mix13); h[u] equal <=> subtrees isomorphic w.h.p.
// 0-based tree, any root. Trees compared together must share the same nonzero seeds s1 != s2.
unsigned long long mix13(unsigned long long x)
{
    x ^= x >> 30, x *= 0xbf58476d1ce4e5b9ULL;
    x ^= x >> 27, x *= 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}

vector<pair<unsigned long long, unsigned long long>>
tree_hash(const vector<vector<int>> &g, int root, unsigned long long s1, unsigned long long s2)
{
    int n = g.size();
    vector<int> fa(n, -1), q{root};
    for (int i = 0; i < (int)q.size(); i++)
        for (int v : g[q[i]])
            if (v != fa[q[i]]) fa[v] = q[i], q.push_back(v);
    vector<pair<unsigned long long, unsigned long long>> h(n, {s1, s2});
    for (int i = n - 1; i > 0; i--)
    {
        int u = q[i];
        h[fa[u]].first += mix13(h[u].first);
        h[fa[u]].second += mix13(h[u].second);
    }
    return h;
}
// END tree_hash

// BEGIN tree_hash_reroot
// f[u] = hash of the whole tree rooted at u, from h = tree_hash(g, root, s1, s2). O(n).
vector<pair<unsigned long long, unsigned long long>>
tree_hash_reroot(const vector<vector<int>> &g, int root, const vector<pair<unsigned long long, unsigned long long>> &h)
{
    int n = g.size();
    vector<int> fa(n, -1), q{root};
    for (int i = 0; i < (int)q.size(); i++)
        for (int v : g[q[i]])
            if (v != fa[q[i]]) fa[v] = q[i], q.push_back(v);
    auto f = h;
    for (int i = 1; i < n; i++)
    {
        int u = q[i], p = fa[u];
        // the parent side seen from u is f[p] without u's own contribution
        f[u].first += mix13(f[p].first - mix13(h[u].first));
        f[u].second += mix13(f[p].second - mix13(h[u].second));
    }
    return f;
}
// END tree_hash_reroot

