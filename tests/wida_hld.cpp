#include <bits/stdc++.h>
#include <cassert>
using namespace std;
#include "fixtures/wida_hld/main.cpp"

#define check(cond) do { if (!(cond)) { cerr << "fail " << __LINE__ << '\n'; return -1; } } while (0)

struct Tree
{
    int n, root;
    vector<vector<int>> g, child;
    vector<int> parent, dep, siz;
    Tree(int n, int root, const vector<pair<int, int>> &edges) : n(n), root(root), g(n), child(n), parent(n, -1), dep(n), siz(n)
    {
        for (auto [u, v] : edges)
        {
            g[u].push_back(v);
            g[v].push_back(u);
        }
        dfs(root, -1);
    }
    void dfs(int u, int p)
    {
        parent[u] = p;
        dep[u] = p < 0 ? 0 : dep[p] + 1;
        siz[u] = 1;
        for (int v : g[u])
            if (v != p)
            {
                child[u].push_back(v);
                dfs(v, u);
                siz[u] += siz[v];
            }
    }
    int lca(int u, int v) const
    {
        while (dep[u] > dep[v]) u = parent[u];
        while (dep[v] > dep[u]) v = parent[v];
        while (u != v)
        {
            u = parent[u];
            v = parent[v];
        }
        return u;
    }
    int jump(int u, int k) const
    {
        if (dep[u] < k) return -1;
        while (k--) u = parent[u];
        return u;
    }
    bool ancestor(int u, int v) const
    {
        if (dep[v] < dep[u]) return false;
        return jump(v, dep[v] - dep[u]) == u;
    }
    int reroot_parent(int r, int x) const
    {
        if (x == r) return x;
        if (!ancestor(x, r)) return parent[x];
        return jump(r, dep[r] - dep[x] - 1);
    }
    int reroot_size(int r, int x) const
    {
        if (x == r) return n;
        if (!ancestor(x, r)) return siz[x];
        return n - siz[reroot_parent(r, x)];
    }
    int reroot_lca(int a, int b, int c) const
    {
        auto inside = [&](int x, int y, int z)
        {
            int p = lca(x, y), q = lca(x, z), w = lca(y, z);
            if (dep[p] < dep[q]) p = q;
            if (dep[p] < dep[w]) p = w;
            return p;
        };
        // LCA of a and b in the tree rooted at c is the median of a, b, c.
        return inside(a, b, c);
    }
};

static int check_tree(int n, int root, const vector<pair<int, int>> &edges)
{
    HLD h(n);
    for (auto [u, v] : edges)
        h.addEdge(u, v);
    h.work(root);
    Tree t(n, root, edges);
    int checks = 0;
    for (int u = 0; u < n; u++)
        for (int v = 0; v < n; v++)
        {
            check(h.lca(u, v) == t.lca(u, v));
            check(h.dist(u, v) == t.dep[u] + t.dep[v] - 2 * t.dep[t.lca(u, v)]);
            check(h.isAncester(u, v) == t.ancestor(u, v));
            check(h.rootedParent(u, v) == t.reroot_parent(u, v));
            check(h.rootedSize(u, v) == t.reroot_size(u, v));
            checks += 5;
        }
    for (int u = 0; u < n; u++)
        for (int k = 0; k <= t.dep[u] + 1; k++)
        {
            check(h.jump(u, k) == t.jump(u, k));
            checks++;
        }
    if (n <= 8)
        for (int a = 0; a < n; a++)
            for (int b = 0; b < n; b++)
                for (int c = 0; c < n; c++)
                {
                    check(h.rootedLca(a, b, c) == t.reroot_lca(a, b, c));
                    checks++;
                }
    return checks;
}

int main(int argc, char **argv)
{
    int checks = 0;
    checks += check_tree(1, 0, {});
    vector<pair<int, int>> chain;
    for (int i = 0; i < 6; i++)
        chain.push_back({i, i + 1});
    checks += check_tree(7, 0, chain);
    checks += check_tree(7, 3, chain);
    vector<pair<int, int>> star;
    for (int i = 1; i < 7; i++)
        star.push_back({0, i});
    checks += check_tree(7, 0, star);
    checks += check_tree(7, 4, star);
    mt19937 rng(8);
    for (int n = 2; n <= 10; n++)
        for (int rep = 0; rep < 8; rep++)
        {
            vector<pair<int, int>> edges;
            for (int i = 1; i < n; i++)
                edges.push_back({(int)(rng() % i), i});
            checks += check_tree(n, (int)(rng() % n), edges);
        }
    if (argc > 1 && string(argv[1]) == "twice")
    {
        HLD again(4);
        again.addEdge(0, 1);
        again.addEdge(1, 2);
        again.addEdge(1, 3);
        again.work(0);
        again.work(2);
        cout << again.siz[2] << '\n';
        return 0;
    }
    cout << checks << '\n';
}
