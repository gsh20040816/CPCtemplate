#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <optional>
#include <set>
#include <utility>
#include <vector>
using namespace std;

// BEGIN CentroidNearest
struct CentroidNearest
{
    using ll = long long;
    int n;
    bool built = false;
    vector<vector<pair<int, ll>>> g, path;
    vector<int> siz, removed, active;
    vector<std::set<pair<ll, int>>> bag;

    CentroidNearest(int n)
        : n(n), g(n), path(n), siz(n), removed(n), active(n), bag(n)
    {
        assert(n > 0);
    }

    void add(int u, int v, ll w = 1)
    {
        assert(!built && 0 <= u && u < n && 0 <= v && v < n);
        assert(u != v && w >= 0);
        g[u].push_back({v, w});
        g[v].push_back({u, w});
    }

    void size_dfs(int u, int p)
    {
        siz[u] = 1;
        for (auto [v, w] : g[u])
        {
            if (v == p || removed[v]) continue;
            size_dfs(v, u);
            siz[u] += siz[v];
        }
    }

    int centroid(int u, int p, int total)
    {
        for (auto [v, w] : g[u])
            if (v != p && !removed[v] && siz[v] > total / 2)
                return centroid(v, u, total);
        return u;
    }

    void collect(int u, int p, ll d, int c)
    {
        path[u].push_back({c, d});
        for (auto [v, w] : g[u])
        {
            if (v == p || removed[v]) continue;
            assert(d <= LLONG_MAX - w);
            collect(v, u, d + w, c);
        }
    }

    void decompose(int entry)
    {
        size_dfs(entry, -1);
        int c = centroid(entry, -1, siz[entry]);
        removed[c] = 1;
        collect(c, -1, 0, c);
        for (auto [v, w] : g[c])
            if (!removed[v]) decompose(v);
    }

    // Fixed connected nonnegative-weight tree; rebuild clears all active points.
    void build()
    {
        fill(removed.begin(), removed.end(), 0);
        fill(active.begin(), active.end(), 0);
        for (int u = 0; u < n; u++)
        {
            path[u].clear();
            bag[u].clear();
        }
        decompose(0);
        built = true;
    }

    void set(int u, bool on)
    {
        assert(built && 0 <= u && u < n);
        if (active[u] == on) return;
        active[u] = on;
        for (auto [c, d] : path[u])
        {
            if (on) bag[c].insert({d, u});
            else bag[c].erase({d, u});
        }
    }

    // Minimum (distance, vertex ID); nullopt means no active point.
    optional<pair<ll, int>> query(int u) const
    {
        assert(built && 0 <= u && u < n);
        optional<pair<ll, int>> ans;
        for (auto [c, d] : path[u])
        {
            if (bag[c].empty()) continue;
            auto [x, v] = *bag[c].begin();
            // A detour may overflow even when every simple path fits.
            if (x > LLONG_MAX - d) continue;
            pair<ll, int> now{d + x, v};
            if (!ans || now < *ans) ans = now;
        }
        return ans;
    }
};
// END CentroidNearest
