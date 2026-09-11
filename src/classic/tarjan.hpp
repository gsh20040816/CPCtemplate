#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

template <int N> struct Tarjan_SCC
{
    int n, timer = 0, cnt = 0;
    vector<int> g[N + 1], st;
    int dfn[N + 1], low[N + 1], bel[N + 1];

    void Init(int vertices)
    {
        assert(0 <= vertices && vertices <= N);
        n = vertices;
        for ( int u = 1; u <= n; u++ )
            g[u].clear();
    }

    void Insert(int u, int v)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        g[u].push_back(v);
    }

    void Dfs(int u)
    {
        dfn[u] = low[u] = ++timer;
        st.push_back(u);
        for ( int v : g[u] )
        {
            if ( !dfn[v] )
            {
                Dfs(v);
                low[u] = min(low[u], low[v]);
            }
            else if ( !bel[v] )
                low[u] = min(low[u], dfn[v]);
        }
        if ( low[u] == dfn[u] )
        {
            ++cnt;
            while ( true )
            {
                int v = st.back();
                st.pop_back();
                bel[v] = cnt;
                if ( v == u )
                    break;
            }
        }
    }

    // IDs 1..cnt are in reverse topological order. Recursive DFS needs O(n) stack.
    void Run()
    {
        timer = 0;
        cnt = 0;
        fill(dfn, dfn + n + 1, 0);
        fill(low, low + n + 1, 0);
        fill(bel, bel + n + 1, 0);
        st.clear();
        for ( int u = 1; u <= n; u++ )
        {
            if ( !dfn[u] )
                Dfs(u);
        }
    }

    // Retains parallel edges. Use after Run().
    vector<vector<int>> Dag() const
    {
        vector<vector<int>> result(cnt + 1);
        for ( int u = 1; u <= n; u++ )
        {
            for ( int v : g[u] )
            {
                if ( bel[u] != bel[v] )
                    result[bel[u]].push_back(bel[v]);
            }
        }
        return result;
    }
};
