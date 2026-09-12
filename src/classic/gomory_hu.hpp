#pragma once
#include "flow.hpp"
#include <tuple>

// BEGIN Gomory_Hu
template <int N, int M>
vector<tuple<int, int, long long>> Gomory_Hu(
    int n, const vector<tuple<int, int, long long>> &edges, Network_Flow<N, M> &flow)
{
    assert(n >= 1);
    vector<int> parent(n);
    vector<long long> value(n);
    for ( int s = 1; s < n; s++ )
    {
        int t = parent[s];
        flow.Init(n);
        for ( auto [u, v, w] : edges )
            if ( u != v )
            {
                flow.Add_Edge(u + 1, v + 1, w);
                flow.Add_Edge(v + 1, u + 1, w);
            }
        long long cut = flow.Max_Flow(s + 1, t + 1);
        vector<bool> side(n);
        for ( int u : flow.Cut(s + 1) )
            side[u - 1] = true;
        for ( int v = 1; v < n; v++ )
            if ( v != s && parent[v] == t && side[v] )
                parent[v] = s;
        if ( side[parent[t]] )
        {
            parent[s] = parent[t];
            parent[t] = s;
            value[s] = value[t];
            value[t] = cut;
        }
        else
            value[s] = cut;
    }
    vector<tuple<int, int, long long>> tree;
    for ( int v = 1; v < n; v++ )
        tree.push_back({v, parent[v], value[v]});
    return tree;
}

// END Gomory_Hu
