#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <tuple>
#include <vector>
using namespace std;

// BEGIN cut_tree_values
vector<vector<long long>>
cut_tree_values(int n, const vector<tuple<int, int, long long>> &tree)
{
    assert(n >= 1 && tree.size() == (size_t)n - 1);
    vector<vector<pair<int, long long>>> g(n);
    for (auto [u, v, w] : tree)
    {
        assert(0 <= u && u < n && 0 <= v && v < n && w >= 0);
        g[u].push_back({v, w});
        g[v].push_back({u, w});
    }
    vector<vector<long long>> answer(n, vector<long long>(n, LLONG_MAX));
    for (int s = 0; s < n; s++)
    {
        auto dfs = [&](auto &&self, int u, int parent, long long value) -> void
        {
            answer[s][u] = value;
            for (auto [v, w] : g[u])
                if (v != parent) self(self, v, u, min(value, w));
        };
        dfs(dfs, s, -1, LLONG_MAX);
    }
    return answer;
}

// END cut_tree_values
