#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// BEGIN TreeBlockDistinct
struct TreeBlockDistinct
{
    using ull = unsigned long long;
    int n, block, lg, words, k;
    vector<vector<int>> g, up;
    vector<int> c, dep, id, near, keys, count;
    vector<vector<ull>> paths;
    vector<ull> bits;

    TreeBlockDistinct(int n) : n(n), g(n + 1)
    {
        assert(n >= 1 && n < INT_MAX);
    }

    void add(int u, int v)
    {
        g[u].push_back(v);
        g[v].push_back(u);
    }

    int partition(int u, int p)
    {
        up[0][u] = p;
        for (int j = 1; j < lg; j++)
            up[j][u] = up[j - 1][up[j - 1][u]];
        int size = 1;
        for (int v : g[u])
        {
            if (v == p) continue;
            dep[v] = dep[u] + 1;
            size += partition(v, u);
        }
        if (size < block) return size;
        id[u] = keys.size();
        keys.push_back(u);
        return 0;
    }

    void mark(int u, int p, int last)
    {
        if (id[u] >= 0) last = u;
        near[u] = last;
        for (int v : g[u])
            if (v != p) mark(v, u, last);
    }

    void collect(int u, int p, int source)
    {
        int x = c[u];
        if (count[x]++ == 0) bits[x >> 6] |= 1ULL << (x & 63);
        if (id[u] >= 0) paths[size_t(source) * k + id[u]] = bits;
        for (int v : g[u])
            if (v != p) collect(v, u, source);
        if (--count[x] == 0) bits[x >> 6] &= ~(1ULL << (x & 63));
    }

    void build(const vector<long long> &values, int b = 512, int root = 1)
    {
        assert(values.size() == size_t(n + 1) && b >= 1);
        assert(1 <= root && root <= n);
        block = b;
        vector<long long> all(values.begin() + 1, values.end());
        sort(all.begin(), all.end());
        all.erase(unique(all.begin(), all.end()), all.end());
        c.resize(n + 1);
        for (int u = 1; u <= n; u++)
            c[u] = lower_bound(all.begin(), all.end(), values[u]) - all.begin();
        words = (all.size() + 63) / 64;
        count.assign(all.size(), 0);
        bits.assign(words, 0);
        dep.assign(n + 1, 0);
        near.assign(n + 1, 0);
        id.assign(n + 1, -1);
        keys.clear();
        lg = 1;
        while ((1LL << lg) <= n) lg++;
        up.assign(lg, vector<int>(n + 1));
        partition(root, 0);
        if (id[root] < 0)
        {
            id[root] = keys.size();
            keys.push_back(root);
        }
        mark(root, 0, root);
        k = keys.size();
        paths = vector<vector<ull>>(size_t(k) * k);
        for (int i = 0; i < k; i++) collect(keys[i], 0, i);
    }

    int jump(int u, int steps) const
    {
        for (int j = 0; j < lg; j++)
            if (steps >> j & 1) u = up[j][u];
        return u;
    }

    int lca(int u, int v) const
    {
        if (dep[u] < dep[v]) swap(u, v);
        u = jump(u, dep[u] - dep[v]);
        if (u == v) return u;
        for (int j = lg - 1; j >= 0; j--)
        {
            if (up[j][u] != up[j][v])
            {
                u = up[j][u];
                v = up[j][v];
            }
        }
        return up[0][u];
    }

    void leg(int u, int ancestor, vector<ull> &ans) const
    {
        if (dep[u] - dep[ancestor] >= block)
        {
            int a = near[u];
            int x = jump(u, dep[u] - dep[ancestor] - block + 1);
            int b = near[x];
            const auto &path = paths[size_t(id[a]) * k + id[b]];
            for (int i = 0; i < words; i++) ans[i] |= path[i];
            while (u != a)
            {
                ans[c[u] >> 6] |= 1ULL << (c[u] & 63);
                u = up[0][u];
            }
            u = b;
        }
        while (u != ancestor)
        {
            ans[c[u] >> 6] |= 1ULL << (c[u] & 63);
            u = up[0][u];
        }
    }

    int query(int u, int v) const
    {
        int p = lca(u, v);
        vector<ull> ans(words);
        leg(u, p, ans);
        leg(v, p, ans);
        ans[c[p] >> 6] |= 1ULL << (c[p] & 63);
        int result = 0;
        for (ull x : ans) result += __builtin_popcountll(x);
        return result;
    }
};
// END TreeBlockDistinct


int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<long long> a(n + 1);
    for (int u = 1; u <= n; u++) cin >> a[u];
    TreeBlockDistinct g(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        cin >> u >> v;
        g.add(u, v);
    }
    g.build(a);
    int last = 0;
    while (q--)
    {
        int u, v;
        cin >> u >> v;
        u ^= last;
        last = g.query(u, v);
        cout << last << '\n';
    }
}
