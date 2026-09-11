#pragma once
#include <algorithm>
#include <array>
#include <cassert>
#include <climits>
#include <cmath>
#include <functional>
#include <map>
#include <numeric>
#include <optional>
#include <queue>
#include <random>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;

struct Shortest_Path
{
    using ll = long long;
    static constexpr ll inf = LLONG_MAX;
    int n;
    vector<vector<pair<int, ll>>> g;
    vector<ll> dis;
    vector<int> pre;

    Shortest_Path(int n) : n(n), g(n + 1)
    {
    }

    void Insert(int u, int v, ll w)
    {
        assert(w >= 0);
        g[u].push_back({v, w});
    }

    void Run(int s)
    {
        dis.assign(n + 1, inf);
        pre.assign(n + 1, -1);
        dis[s] = 0;
        priority_queue<pair<ll, int>, vector<pair<ll, int>>, greater<pair<ll, int>>> q;
        q.push({0, s});
        while ( !q.empty() )
        {
            auto [d, u] = q.top();
            q.pop();
            if ( d != dis[u] )
                continue;
            for ( auto [v, w] : g[u] )
                if ( w < inf - d && d + w < dis[v] )
                {
                    dis[v] = d + w;
                    pre[v] = u;
                    q.push({dis[v], v});
                }
        }
    }

    vector<int> Path(int t) const
    {
        if ( dis[t] == inf )
            return {};
        vector<int> ans;
        for ( ; t != -1; t = pre[t] )
            ans.push_back(t);
        reverse(ans.begin(), ans.end());
        return ans;
    }
};

struct Strong_Component
{
    int n, cnt = 0;
    vector<vector<int>> g, rg;
    vector<int> bel;

    Strong_Component(int n) : n(n), g(n + 1), rg(n + 1)
    {
    }

    void Insert(int u, int v)
    {
        g[u].push_back(v);
        rg[v].push_back(u);
    }

    void Dfs1(int u, vector<int> &vis, vector<int> &order)
    {
        vis[u] = 1;
        for ( int v : g[u] )
        {
            if ( !vis[v] )
                Dfs1(v, vis, order);
        }
        order.push_back(u);
    }

    void Dfs2(int u)
    {
        bel[u] = cnt;
        for ( int v : rg[u] )
        {
            if ( !bel[v] )
                Dfs2(v);
        }
    }

    // Recursive Kosaraju; component IDs are in topological order, 1..cnt.
    void Run()
    {
        vector<int> vis(n + 1), order;
        cnt = 0;
        bel.assign(n + 1, 0);
        for ( int s = 1; s <= n; s++ )
        {
            if ( !vis[s] )
                Dfs1(s, vis, order);
        }
        reverse(order.begin(), order.end());
        for ( int s : order )
        {
            if ( !bel[s] )
            {
                ++cnt;
                Dfs2(s);
            }
        }
    }
};

struct Two_SAT
{
    int n;
    Strong_Component g;
    vector<int> ans;

    Two_SAT(int n) : n(n), g(2 * n)
    {
    }

    int id(int x, bool value) const
    {
        return 2 * x - 1 + value;
    }

    void Insert(int x, bool a, int y, bool b)
    {
        g.Insert(id(x, !a), id(y, b));
        g.Insert(id(y, !b), id(x, a));
    }

    bool Solve()
    {
        g.Run();
        ans.assign(n + 1, 0);
        for ( int x = 1; x <= n; x++ )
        {
            if ( g.bel[id(x, 0)] == g.bel[id(x, 1)] )
                return false;
            ans[x] = g.bel[id(x, 1)] > g.bel[id(x, 0)];
        }
        return true;
    }
};

template <int N, int M> struct Bipartite_Matching
{
    int n, m;
    vector<int> g[N + 1];
    int l[N + 1], r[M + 1], dep[N + 1], cur[N + 1], que[N + 1];

    void Init(int left_size, int right_size)
    {
        assert(0 <= left_size && left_size <= N && 0 <= right_size && right_size <= M);
        n = left_size;
        m = right_size;
        fill(l, l + n + 1, 0);
        fill(r, r + m + 1, 0);
        for ( int u = 1; u <= n; u++ )
            g[u].clear();
    }

    void Insert(int u, int v)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= m);
        g[u].push_back(v);
    }

    bool Bfs()
    {
        int head = 0, tail = 0;
        fill(dep, dep + n + 1, n + 1);
        fill(cur, cur + n + 1, 0);
        for ( int u = 1; u <= n; u++ )
        {
            if ( !l[u] )
            {
                dep[u] = 0;
                que[tail++] = u;
            }
        }
        while ( head < tail )
        {
            int u = que[head++];
            if ( dep[u] >= dep[0] )
                continue;
            for ( int v : g[u] )
            {
                int next = r[v];
                if ( dep[next] != n + 1 )
                    continue;
                dep[next] = dep[u] + 1;
                if ( next )
                    que[tail++] = next;
            }
        }
        return dep[0] != n + 1;
    }

    bool Dfs(int u)
    {
        if ( !u )
            return true;
        for ( int &i = cur[u]; i < (int)g[u].size(); i++ )
        {
            int v = g[u][i];
            if ( dep[r[v]] == dep[u] + 1 && Dfs(r[v]) )
            {
                l[u] = v;
                r[v] = u;
                return true;
            }
        }
        dep[u] = n + 1;
        return false;
    }

    // Retains an existing matching; edges may be added between calls.
    int Solve()
    {
        int answer = 0;
        for ( int u = 1; u <= n; u++ )
            answer += (l[u] != 0);
        while ( Bfs() )
        {
            for ( int u = 1; u <= n; u++ )
            {
                if ( !l[u] && Dfs(u) )
                    answer++;
            }
        }
        return answer;
    }

    // Call after Solve(), before adding more edges. Returns left/right vertex IDs.
    pair<vector<int>, vector<int>> Cover() const
    {
        vector<int> left, right;
        for ( int u = 1; u <= n; u++ )
        {
            if ( dep[u] == n + 1 )
                left.push_back(u);
        }
        for ( int v = 1; v <= m; v++ )
        {
            if ( r[v] && dep[r[v]] != n + 1 )
                right.push_back(v);
        }
        return {left, right};
    }
};

struct Low_Link
{
    int n, timer = 0;
    vector<vector<pair<int, int>>> g;
    vector<int> dfn, low, cut, bridge;
    int edges = 0;

    Low_Link(int n) : n(n), g(n + 1)
    {
    }

    int Insert(int u, int v)
    {
        g[u].push_back({v, edges});
        g[v].push_back({u, edges});
        return edges++;
    }

    void Dfs(int u, int pe)
    {
        dfn[u] = low[u] = ++timer;
        int children = 0;
        for ( auto [v, id] : g[u] )
        {
            if ( id == pe )
                continue;
            if ( !dfn[v] )
            {
                ++children;
                Dfs(v, id);
                low[u] = min(low[u], low[v]);
                if ( low[v] > dfn[u] )
                    bridge[id] = 1;
                if ( pe != -1 && low[v] >= dfn[u] )
                    cut[u] = 1;
            }
            else
                low[u] = min(low[u], dfn[v]);
        }
        if ( pe == -1 && children > 1 )
            cut[u] = 1;
    }

    void Run()
    {
        timer = 0;
        dfn.assign(n + 1, 0);
        low = dfn;
        cut = dfn;
        bridge.assign(edges, 0);
        for ( int u = 1; u <= n; u++ )
            if ( !dfn[u] )
                Dfs(u, -1);
    }
};
