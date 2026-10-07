#pragma once
#include <bits/stdc++.h>
using namespace std;

// Nonnegative weighted tree, vertices 0..n-1; ties use the smaller vertex ID.
struct TreeMarket
{
    using I = __int128_t;
    using Key = pair<I, int>;
    int n;
    vector<vector<pair<int, long long>>> g;
    vector<int> size, removed, market, answer;
    vector<Key> best;

    TreeMarket(int n) : n(n), g(n), size(n), removed(n), answer(n)
    {
    }

    void add(int u, int v, long long w)
    {
        g[u].push_back({v, w});
        g[v].push_back({u, w});
    }

    void size_dfs(int u, int p)
    {
        size[u] = 1;
        for (auto [v, w] : g[u])
            if (v != p && !removed[v])
            {
                size_dfs(v, u);
                size[u] += size[v];
            }
    }

    int centroid(int u, int p, int total)
    {
        for (auto [v, w] : g[u])
            if (v != p && !removed[v] && size[v] > total / 2)
                return centroid(v, u, total);
        return u;
    }

    void collect(int u, int p, I d, vector<pair<int, I>> &nodes)
    {
        nodes.push_back({u, d});
        for (auto [v, w] : g[u])
            if (v != p && !removed[v]) collect(v, u, d + w, nodes);
    }

    void count(const vector<pair<int, I>> &nodes, int sign)
    {
        vector<Key> keys;
        for (auto [u, d] : nodes) keys.push_back({best[u].first - d, best[u].second});
        sort(keys.begin(), keys.end());
        for (auto [u, d] : nodes)
            if (!market[u])
            {
                int pos = upper_bound(keys.begin(), keys.end(), Key{d, u}) - keys.begin();
                answer[u] += sign * ((int)keys.size() - pos);
            }
    }

    void decompose(int entry)
    {
        size_dfs(entry, -1);
        int c = centroid(entry, -1, size[entry]);
        vector<pair<int, I>> nodes;
        collect(c, -1, 0, nodes);
        count(nodes, 1);
        removed[c] = 1;
        for (auto [v, w] : g[c])
            if (!removed[v])
            {
                nodes.clear();
                collect(v, c, w, nodes);
                count(nodes, -1);
                decompose(v);
            }
    }

    // Existing markets get answer 0. No existing market: every site wins n.
    vector<int> solve(const vector<int> &existing)
    {
        market = existing;
        fill(answer.begin(), answer.end(), 0);
        fill(removed.begin(), removed.end(), 0);
        best.assign(n, {I(1) << 120, n});
        using State = tuple<I, int, int>;
        priority_queue<State, vector<State>, greater<State>> q;
        for (int u = 0; u < n; u++)
            if (market[u])
            {
                best[u] = {0, u};
                q.push({0, u, u});
            }
        if (q.empty())
        {
            fill(answer.begin(), answer.end(), n);
            return answer;
        }
        while (!q.empty())
        {
            auto [d, id, u] = q.top();
            q.pop();
            if (best[u] != Key{d, id}) continue;
            for (auto [v, w] : g[u])
                if (Key{d + w, id} < best[v])
                {
                    best[v] = {d + w, id};
                    q.push({d + w, id, v});
                }
        }
        decompose(0);
        return answer;
    }
};
