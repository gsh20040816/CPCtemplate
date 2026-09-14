#pragma once
#include "string.hpp"
#include <climits>

// BEGIN ac_shortest
vector<int> ac_shortest(const AhoCorasick &ac, const vector<pair<int, int>> &ends)
{
    assert(ac.built);
    vector<int> len(ac.a.size(), INT_MAX);
    for (auto [u, n] : ends)
    {
        assert(0 < u && u < (int)len.size() && 0 < n && n < INT_MAX);
        len[u] = min(len[u], n);
    }
    for (int u : ac.order) len[u] = min(len[u], len[ac.a[u].fail]);
    return len;
}

// END ac_shortest
