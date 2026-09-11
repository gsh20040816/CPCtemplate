#pragma once
#include "flow.hpp"

// BEGIN Maximum_Closure
template <int N, int M>
pair<long long, vector<int>> Maximum_Closure(const vector<long long> &weight,
                                             const vector<pair<int, int>> &dependencies,
                                             Network_Flow<N, M> &graph)
{
    using I = __int128_t;
    int n = weight.size(), s = n + 1, t = n + 2;
    I positive = 0;
    for ( long long w : weight )
        if ( w > 0 )
            positive += w;
    assert(positive < LLONG_MAX);
    long long inf = (long long)positive + 1;
    graph.Init(n + 2);
    for ( int u = 1; u <= n; u++ )
    {
        long long w = weight[u - 1];
        if ( w > 0 )
            graph.Add_Edge(s, u, w);
        else if ( w < 0 )
            graph.Add_Edge(u, t, (long long)min(-I(w), I(inf)));
    }
    for ( auto [u, v] : dependencies )
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        graph.Add_Edge(u, v, inf);
    }
    long long answer = (long long)positive - graph.Max_Flow(s, t);
    vector<int> selected;
    for ( int u : graph.Cut(s) )
        if ( u <= n )
            selected.push_back(u);
    return {answer, selected};
}

// END Maximum_Closure
