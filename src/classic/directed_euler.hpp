#pragma once
#include <algorithm>
#include <cassert>
#include <utility>
#include <vector>
using namespace std;

template <int N> struct Directed_Euler
{
    int n;
    vector<pair<int, int>> g[N + 1], edges;
    vector<int> vertices, edge_ids;
    int in[N + 1], out[N + 1], next[N + 1];

    void Init(int count)
    {
        assert(0 < count && count <= N);
        n = count;
        for ( int u = 1; u <= n; u++ )
        {
            g[u].clear();
            in[u] = 0;
            out[u] = 0;
        }
        edges.clear();
        vertices.clear();
        edge_ids.clear();
    }

    int Insert(int u, int v)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        int id = edges.size();
        edges.push_back({u, v});
        g[u].push_back({v, id});
        out[u]++;
        in[v]++;
        vertices.clear();
        edge_ids.clear();
        return id;
    }

    void Dfs(int u, int incoming)
    {
        while ( next[u] < (int)g[u].size() )
        {
            auto [v, id] = g[u][next[u]++];
            Dfs(v, id);
        }
        vertices.push_back(u);
        if ( incoming != -1 )
            edge_ids.push_back(incoming);
    }

    // start=0 chooses the smallest feasible start. Isolated vertices are ignored.
    bool Run(int start = 0, bool lexicographic = true)
    {
        assert(0 <= start && start <= n);
        vertices.clear();
        edge_ids.clear();
        int source = 0, sink = 0;
        for ( int u = 1; u <= n; u++ )
        {
            int delta = out[u] - in[u];
            if ( delta == 1 && !source )
                source = u;
            else if ( delta == -1 && !sink )
                sink = u;
            else if ( delta != 0 )
                return false;
        }
        if ( bool(source) != bool(sink) )
            return false;
        if ( source )
        {
            if ( start && start != source )
                return false;
            start = source;
        }
        if ( !start )
        {
            start = 1;
            for ( int u = 1; u <= n; u++ )
                if ( out[u] )
                {
                    start = u;
                    break;
                }
        }
        if ( lexicographic )
            for ( int u = 1; u <= n; u++ )
                sort(g[u].begin(), g[u].end());
        fill(next, next + n + 1, 0);
        Dfs(start, -1);
        if ( edge_ids.size() != edges.size() )
        {
            vertices.clear();
            edge_ids.clear();
            return false;
        }
        reverse(vertices.begin(), vertices.end());
        reverse(edge_ids.begin(), edge_ids.end());
        return true;
    }
};
