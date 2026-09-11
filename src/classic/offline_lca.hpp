#pragma once
#include <algorithm>
#include <cassert>
#include <numeric>
#include <utility>
#include <vector>
using namespace std;

template <int N> struct Offline_LCA
{
    int n;
    vector<int> g[N + 1], answer;
    vector<pair<int, int>> queries[N + 1];
    int parent[N + 1], size[N + 1], ancestor[N + 1], done[N + 1];

    void Init(int vertices)
    {
        assert(0 <= vertices && vertices <= N);
        n = vertices;
        for ( int u = 1; u <= n; u++ )
        {
            g[u].clear();
            queries[u].clear();
        }
        answer.clear();
    }

    void Insert(int u, int v)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        g[u].push_back(v);
        g[v].push_back(u);
    }

    int Add_Query(int u, int v)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        int id = answer.size();
        answer.push_back(0);
        queries[u].push_back({v, id});
        queries[v].push_back({u, id});
        return id;
    }

    int Find(int u)
    {
        if ( parent[u] != u )
            parent[u] = Find(parent[u]);
        return parent[u];
    }

    void Merge(int u, int v)
    {
        u = Find(u);
        v = Find(v);
        if ( size[u] < size[v] )
            swap(u, v);
        parent[v] = u;
        size[u] += size[v];
    }

    void Dfs(int u, int p)
    {
        for ( int v : g[u] )
            if ( v != p )
            {
                Dfs(v, u);
                Merge(u, v);
                ancestor[Find(u)] = u;
            }
        done[u] = 1;
        for ( auto [v, id] : queries[u] )
            if ( done[v] )
                answer[id] = ancestor[Find(v)];
    }

    // Input must be a nonempty tree. Query IDs are 0-based.
    void Run(int root = 1)
    {
        assert(1 <= root && root <= n);
        iota(parent, parent + n + 1, 0);
        iota(ancestor, ancestor + n + 1, 0);
        fill(size, size + n + 1, 1);
        fill(done, done + n + 1, 0);
        fill(answer.begin(), answer.end(), 0);
        Dfs(root, 0);
    }
};
