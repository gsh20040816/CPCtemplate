#pragma once
#include "flow.hpp"
#include "tarjan.hpp"

// BEGIN unit_flow_edges
vector<array<bool, 2>> unit_flow_edges(const Dinic &g, const vector<int> &ids)
{
    TarjanSCC d(g.n);
    for (auto e : g.e)
        if (e.cap) d.add(e.from, e.to);
    d.run();
    vector<array<bool, 2>> ans;
    for (int id : ids)
    {
        assert(0 <= id && id < (int)g.e.size() && id % 2 == 0);
        auto e = g.e[id];
        assert(e.initial == 1);
        bool used = g.used(id) == 1, same = d.bel[e.from] == d.bel[e.to];
        ans.push_back({used || same, used && !same});
    }
    return ans;
}

// END unit_flow_edges
