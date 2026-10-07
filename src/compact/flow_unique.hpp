#pragma once
#include "flow.hpp"
#include "tarjan.hpp"

// BEGIN flow_unique
bool flow_unique(const Dinic &g)
{
    TarjanSCC d(g.n);
    for (auto e : g.e)
        if (e.cap) d.add(e.from, e.to);
    d.run();
    vector<int> left(d.cnt + 1);
    for (int u = 1; u <= g.n; u++)
        left[d.bel[u]]++;
    for (int id = 0; id < (int)g.e.size(); id += 2)
    {
        auto e = g.e[id];
        if (!e.cap && !g.e[id ^ 1].cap) continue;
        if (d.bel[e.from] != d.bel[e.to]) continue;
        if (--left[d.bel[e.from]] == 0) return false;
    }
    return true;
}
// END flow_unique
