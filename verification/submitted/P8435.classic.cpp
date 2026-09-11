#include <algorithm>
#include <cassert>
#include <utility>
#include <vector>
using namespace std;

template <int N> struct Biconnected_Graph
{
    int n, timer = 0, cnt = 0;
    vector<pair<int, int>> g[N + 1], edges;
    vector<vector<int>> blocks;
    vector<int> bridge, st;
    int dfn[N + 1], low[N + 1], cut[N + 1], bel[N + 1];

    void Init(int vertices)
    {
        assert(0 <= vertices && vertices <= N);
        n = vertices;
        for ( int u = 1; u <= n; u++ )
            g[u].clear();
        edges.clear();
    }

    int Insert(int u, int v)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        int id = edges.size();
        edges.push_back({u, v});
        if ( u != v )
        {
            g[u].push_back({v, id});
            g[v].push_back({u, id});
        }
        return id;
    }

    void Dfs(int u, int parent_edge)
    {
        dfn[u] = low[u] = ++timer;
        st.push_back(u);
        int children = 0;
        for ( auto [v, id] : g[u] )
        {
            if ( id == parent_edge )
                continue;
            if ( !dfn[v] )
            {
                children++;
                Dfs(v, id);
                low[u] = min(low[u], low[v]);
                if ( low[v] > dfn[u] )
                    bridge[id] = 1;
                if ( low[v] >= dfn[u] )
                {
                    if ( parent_edge != -1 || children > 1 )
                        cut[u] = 1;
                    blocks.push_back({u});
                    while ( true )
                    {
                        int x = st.back();
                        st.pop_back();
                        blocks.back().push_back(x);
                        if ( x == v )
                            break;
                    }
                }
            }
            else
                low[u] = min(low[u], dfn[v]);
        }
        if ( parent_edge == -1 && children == 0 )
            blocks.push_back({u});
    }

    void Paint(int u)
    {
        bel[u] = cnt;
        for ( auto [v, id] : g[u] )
        {
            if ( !bridge[id] && !bel[v] )
                Paint(v);
        }
    }

    void Run()
    {
        timer = 0;
        cnt = 0;
        fill(dfn, dfn + n + 1, 0);
        fill(low, low + n + 1, 0);
        fill(cut, cut + n + 1, 0);
        fill(bel, bel + n + 1, 0);
        bridge.assign(edges.size(), 0);
        blocks.clear();
        st.clear();
        for ( int u = 1; u <= n; u++ )
        {
            if ( !dfn[u] )
            {
                Dfs(u, -1);
                st.pop_back();
            }
        }
        for ( int u = 1; u <= n; u++ )
        {
            if ( bel[u] )
                continue;
            ++cnt;
            Paint(u);
        }
    }

    // Original vertices 1..n; block i has node n+i+1. Includes isolated vertices.
    vector<vector<int>> Block_Forest() const
    {
        vector<vector<int>> tree(n + blocks.size() + 1);
        for ( int i = 0; i < (int)blocks.size(); i++ )
        {
            int b = n + i + 1;
            for ( int u : blocks[i] )
            {
                tree[u].push_back(b);
                tree[b].push_back(u);
            }
        }
        return tree;
    }

    // Edge-connected component IDs 1..cnt; forest edges carry original edge IDs.
    vector<vector<pair<int, int>>> Bridge_Forest() const
    {
        vector<vector<pair<int, int>>> tree(cnt + 1);
        for ( int id = 0; id < (int)edges.size(); id++ )
        {
            if ( !bridge[id] )
                continue;
            auto [u, v] = edges[id];
            u = bel[u];
            v = bel[v];
            tree[u].push_back({v, id});
            tree[v].push_back({u, id});
        }
        return tree;
    }
};

#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    static Biconnected_Graph<500000> graph;
    graph.Init(n);
    for ( int i = 0; i < m; i++ )
    {
        int u, v;
        std::cin >> u >> v;
        graph.Insert(u, v);
    }
    graph.Run();
    const auto &blocks = graph.blocks;
    std::cout << blocks.size() << '\n';
    for ( const auto &block : blocks )
    {
        std::cout << block.size();
        for ( int u : block )
            std::cout << ' ' << u;
        std::cout << '\n';
    }
}
