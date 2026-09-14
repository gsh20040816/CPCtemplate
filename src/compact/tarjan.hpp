#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

struct TarjanSCC
{
    int n, timer = 0, cnt = 0;
    vector<vector<int>> g;
    vector<int> dfn, low, bel, st;

    TarjanSCC(int n) : n(n), g(n + 1) {}

    void add(int u, int v)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        g[u].push_back(v);
    }

    void dfs(int u)
    {
        dfn[u] = low[u] = ++timer;
        st.push_back(u);
        for (int v : g[u])
        {
            if (!dfn[v])
            {
                dfs(v);
                low[u] = min(low[u], low[v]);
            }
            else if (!bel[v])
                low[u] = min(low[u], dfn[v]);
        }
        if (low[u] == dfn[u])
        {
            ++cnt;
            while (true)
            {
                int v = st.back();
                st.pop_back();
                bel[v] = cnt;
                if (v == u) break;
            }
        }
    }

    // IDs 1..cnt are in reverse topological order. Recursive DFS needs O(n) stack.
    void run()
    {
        timer = cnt = 0;
        dfn.assign(n + 1, 0);
        low = dfn;
        bel = dfn;
        st.clear();
        for (int u = 1; u <= n; u++)
        {
            if (!dfn[u]) dfs(u);
        }
    }

    // Retains parallel edges. Use after run().
    vector<vector<int>> dag() const
    {
        vector<vector<int>> result(cnt + 1);
        for (int u = 1; u <= n; u++)
        {
            for (int v : g[u])
            {
                if (bel[u] != bel[v]) result[bel[u]].push_back(bel[v]);
            }
        }
        return result;
    }
};
