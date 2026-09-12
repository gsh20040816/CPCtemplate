#include <cstdio>
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

struct EulerLCA
{
    using ll = long long;
    int n;
    bool ready = false;
    vector<vector<int>> g, st;
    vector<vector<ll>> cost;
    vector<ll> root_dist;
    vector<int> first, depth, euler, lg;

    EulerLCA(int n)
        : n(n), g(n + 1), cost(n + 1), root_dist(n + 1), first(n + 1), depth(n + 1)
    {
    }

    void add(int u, int v, ll w = 1)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        assert(w >= 0);
        g[u].push_back(v);
        g[v].push_back(u);
        cost[u].push_back(w);
        cost[v].push_back(w);
        ready = false;
    }

    int shallower(int u, int v) const
    {
        return depth[u] <= depth[v] ? u : v;
    }

    void dfs(int u, int parent)
    {
        first[u] = euler.size();
        euler.push_back(u);
        for (int i = 0; i < int(g[u].size()); i++)
        {
            int v = g[u][i];
            if (v != parent)
            {
                depth[v] = depth[u] + 1;
                root_dist[v] = root_dist[u] + cost[u][i];
                dfs(v, u);
                euler.push_back(u);
            }
        }
    }

    // Input must be a nonempty tree. Rebuilding may change the root.
    void build(int root = 1)
    {
        assert(1 <= root && root <= n);
        euler.clear();
        depth[root] = 0;
        root_dist[root] = 0;
        dfs(root, 0);
        int m = euler.size();
        lg.assign(m + 1, 0);
        for (int i = 2; i <= m; i++)
            lg[i] = lg[i / 2] + 1;
        st.assign(lg[m] + 1, {});
        st[0] = euler;
        for (int k = 1; k <= lg[m]; k++)
        {
            st[k].resize(m - (1 << k) + 1);
            for (int i = 0; i + (1 << k) <= m; i++)
                st[k][i] = shallower(st[k - 1][i], st[k - 1][i + (1 << (k - 1))]);
        }
        ready = true;
    }

    int lca(int u, int v) const
    {
        assert(ready && 1 <= u && u <= n && 1 <= v && v <= n);
        int l = first[u], r = first[v];
        if (l > r)
            swap(l, r);
        int k = lg[r - l + 1];
        return shallower(st[k][l], st[k][r - (1 << k) + 1]);
    }

    int distance(int u, int v) const
    {
        int z = lca(u, v);
        return depth[u] + depth[v] - 2 * depth[z];
    }

    ll weighted_distance(int u, int v) const
    {
        int z = lca(u, v);
        return (root_dist[u] - root_dist[z]) + (root_dist[v] - root_dist[z]);
    }
};

#include <optional>
#include <utility>
#include <cassert>
using namespace std;

struct TreeDiameter
{
    using ll = long long;
    int a = -1, b = -1;
    ll length = 0;

    // distance is the metric of one fixed tree with nonnegative edge weights.
    template <class Distance> void insert(int v, const Distance &distance)
    {
        assert(v >= 0);
        if (a == -1)
        {
            a = v;
            b = v;
            return;
        }
        ll x = distance(a, v), y = distance(b, v);
        if (x >= y && x > length)
        {
            b = v;
            length = x;
        }
        else if (y > length)
        {
            a = v;
            length = y;
        }
    }

    template <class Distance> void merge(TreeDiameter other, const Distance &distance)
    {
        if (other.a == -1)
            return;
        insert(other.a, distance);
        insert(other.b, distance);
    }

    template <class Distance>
    optional<pair<int, ll>> farthest(int v, const Distance &distance) const
    {
        if (a == -1)
            return nullopt;
        ll x = distance(a, v), y = distance(b, v);
        return x >= y ? make_pair(a, x) : make_pair(b, y);
    }
};


int main()
{
    int n, q;
    scanf("%d%d", &n, &q);
    vector<int> position(n + 1, -1);
    for (int u = 1; u <= n; u++)
    {
        int w;
        scanf("%d", &w);
        if (w <= n)
            position[w] = u;
    }
    EulerLCA lca(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        long long w;
        scanf("%d%d%lld", &u, &v, &w);
        lca.add(u, v, w);
    }
    lca.build();
    auto distance = [&](int u, int v)
    {
        return lca.weighted_distance(u, v);
    };
    int mex = 0;
    while (position[mex] != -1)
        mex++;
    vector<TreeDiameter> prefix(mex + 1);
    for (int i = 0; i < mex; i++)
    {
        prefix[i + 1] = prefix[i];
        prefix[i + 1].insert(position[i], distance);
    }
    while (q--)
    {
        int x;
        long long k;
        scanf("%d%lld", &x, &k);
        int l = 0, r = mex;
        while (l < r)
        {
            int m = (l + r + 1) / 2;
            if (prefix[m].farthest(x, distance)->second <= k)
                l = m;
            else
                r = m - 1;
        }
        printf("%d\n", l);
    }
    return 0;
}
