#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

template <int N, int LOG = 20> struct Euler_LCA
{
    static_assert(1 <= LOG && LOG <= 31);
    int n;
    bool ready = false;
    vector<int> g[N + 1], euler;
    int first[N + 1], depth[N + 1], lg[2 * N + 1];
    int st[LOG][2 * N];

    void Init(int vertices)
    {
        assert(0 < vertices && vertices <= N);
        assert((1LL << LOG) > 2LL * vertices - 1);
        n = vertices;
        for ( int u = 1; u <= n; u++ )
            g[u].clear();
        euler.clear();
        ready = false;
    }

    void Insert(int u, int v)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        g[u].push_back(v);
        g[v].push_back(u);
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
        for ( int v : g[u] )
            if ( v != parent )
            {
                depth[v] = depth[u] + 1;
                Dfs(v, u);
                euler.push_back(u);
            }
    }

    // Input must be a nonempty tree. Rebuilding may change the root.
    void Build(int root = 1)
    {
        assert(1 <= root && root <= n);
        euler.clear();
        depth[root] = 0;
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
};
