#include <cstdio>
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

template <int N, int LOG = 20> struct Euler_LCA
{
    static_assert(1 <= LOG && LOG <= 31);
    using ll = long long;
    int n;
    bool ready = false;
    vector<int> g[N + 1], euler;
    vector<ll> cost[N + 1];
    ll root_dist[N + 1];
    int first[N + 1], depth[N + 1], lg[2 * N + 1];
    int st[LOG][2 * N];

    void Init(int vertices)
    {
        assert(0 < vertices && vertices <= N);
        assert((1LL << LOG) > 2LL * vertices - 1);
        n = vertices;
        for ( int u = 1; u <= n; u++ )
        {
            g[u].clear();
            cost[u].clear();
        }
        euler.clear();
        ready = false;
    }

    void Insert(int u, int v, ll w = 1)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        assert(w >= 0);
        g[u].push_back(v);
        g[v].push_back(u);
        cost[u].push_back(w);
        cost[v].push_back(w);
        ready = false;
    }

    int Shallower(int u, int v) const
    {
        return depth[u] <= depth[v] ? u : v;
    }

    void Dfs(int u, int parent)
    {
        first[u] = euler.size();
        euler.push_back(u);
        for ( int i = 0; i < int(g[u].size()); i++ )
        {
            int v = g[u][i];
            if ( v != parent )
            {
                depth[v] = depth[u] + 1;
                root_dist[v] = root_dist[u] + cost[u][i];
                Dfs(v, u);
                euler.push_back(u);
            }
        }
    }

    // Input must be a nonempty tree. Rebuilding may change the root.
    void Build(int root = 1)
    {
        assert(1 <= root && root <= n);
        euler.clear();
        depth[root] = 0;
        root_dist[root] = 0;
        Dfs(root, 0);
        int m = euler.size();
        lg[0] = 0;
        lg[1] = 0;
        for ( int i = 2; i <= m; i++ )
            lg[i] = lg[i / 2] + 1;
        copy(euler.begin(), euler.end(), st[0]);
        for ( int k = 1; k <= lg[m]; k++ )
        {
            for ( int i = 0; i + (1 << k) <= m; i++ )
                st[k][i] = Shallower(st[k - 1][i], st[k - 1][i + (1 << (k - 1))]);
        }
        ready = true;
    }

    int Lca(int u, int v) const
    {
        assert(ready && 1 <= u && u <= n && 1 <= v && v <= n);
        int l = first[u], r = first[v];
        if ( l > r )
            swap(l, r);
        int k = lg[r - l + 1];
        return Shallower(st[k][l], st[k][r - (1 << k) + 1]);
    }

    int Distance(int u, int v) const
    {
        int z = Lca(u, v);
        return depth[u] + depth[v] - 2 * depth[z];
    }

    ll Weighted_Distance(int u, int v) const
    {
        int z = Lca(u, v);
        return (root_dist[u] - root_dist[z]) + (root_dist[v] - root_dist[z]);
    }
};

#include <optional>
#include <utility>
#include <cassert>
using namespace std;

struct Tree_Diameter
{
    using ll = long long;
    int a = -1, b = -1;
    ll length = 0;

    // distance is the metric of one fixed tree with nonnegative edge weights.
    template <class Distance> void Insert(int v, const Distance &distance)
    {
        assert(v >= 0);
        if ( a == -1 )
        {
            a = v;
            b = v;
            return;
        }
        ll x = distance(a, v), y = distance(b, v);
        if ( x >= y && x > length )
        {
            b = v;
            length = x;
        }
        else if ( y > length )
        {
            a = v;
            length = y;
        }
    }

    template <class Distance> void Merge(Tree_Diameter other, const Distance &distance)
    {
        if ( other.a == -1 )
            return;
        Insert(other.a, distance);
        Insert(other.b, distance);
    }

    template <class Distance>
    optional<pair<int, ll>> Farthest(int v, const Distance &distance) const
    {
        if ( a == -1 )
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
    for ( int u = 1; u <= n; u++ )
    {
        int w;
        scanf("%d", &w);
        if ( w <= n )
            position[w] = u;
    }
    static Euler_LCA<500000, 20> lca;
    lca.Init(n);
    for ( int i = 1; i < n; i++ )
    {
        int u, v;
        long long w;
        scanf("%d%d%lld", &u, &v, &w);
        lca.Insert(u, v, w);
    }
    lca.Build();
    auto distance = [&](int u, int v)
    {
        return lca.Weighted_Distance(u, v);
    };
    int mex = 0;
    while ( position[mex] != -1 )
        mex++;
    vector<Tree_Diameter> prefix(mex + 1);
    for ( int i = 0; i < mex; i++ )
    {
        prefix[i + 1] = prefix[i];
        prefix[i + 1].Insert(position[i], distance);
    }
    while ( q-- )
    {
        int x;
        long long k;
        scanf("%d%lld", &x, &k);
        int l = 0, r = mex;
        while ( l < r )
        {
            int m = (l + r + 1) / 2;
            if ( prefix[m].Farthest(x, distance)->second <= k )
                l = m;
            else
                r = m - 1;
        }
        printf("%d\n", l);
    }
    return 0;
}
