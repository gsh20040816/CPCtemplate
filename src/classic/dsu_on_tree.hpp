#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

template <int N> struct Subtree_Colors
{
    int n, best = 0;
    long long sum = 0;
    vector<int> g[N + 1], order, value, freq;
    int siz[N + 1], heavy[N + 1], tin[N + 1], tout[N + 1];
    int color[N + 1], max_freq[N + 1];
    long long answer[N + 1];

    void Init(int vertices)
    {
        assert(0 <= vertices && vertices <= N);
        n = vertices;
        for ( int u = 1; u <= n; u++ )
            g[u].clear();
    }

    void Insert(int u, int v)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n && u != v);
        g[u].push_back(v);
        g[v].push_back(u);
    }

    void Prepare(int u, int p)
    {
        siz[u] = 1;
        tin[u] = order.size();
        order.push_back(u);
        for ( int v : g[u] )
        {
            if ( v == p )
                continue;
            Prepare(v, u);
            siz[u] += siz[v];
            if ( siz[v] > siz[heavy[u]] )
                heavy[u] = v;
        }
        tout[u] = (int)order.size() - 1;
    }

    void Add_Color(int u)
    {
        int c = color[u];
        freq[c]++;
        if ( freq[c] > best )
        {
            best = freq[c];
            sum = value[c];
        }
        else if ( freq[c] == best )
            sum += value[c];
    }

    void Dfs(int u, int p, bool keep)
    {
        for ( int v : g[u] )
        {
            if ( v != p && v != heavy[u] )
                Dfs(v, u, false);
        }
        if ( heavy[u] )
            Dfs(heavy[u], u, true);
        for ( int v : g[u] )
        {
            if ( v == p || v == heavy[u] )
                continue;
            for ( int i = tin[v]; i <= tout[v]; i++ )
                Add_Color(order[i]);
        }
        Add_Color(u);
        max_freq[u] = best;
        answer[u] = sum;
        if ( !keep )
        {
            for ( int i = tin[u]; i <= tout[u]; i++ )
                freq[color[order[i]]]--;
            best = 0;
            sum = 0;
        }
    }

    // A connected tree, colors[1..n]. Sum all colors tied for maximum frequency.
    void Run(const vector<int> &colors, int root = 1)
    {
        assert((int)colors.size() == n + 1);
        fill(siz, siz + n + 1, 0);
        fill(heavy, heavy + n + 1, 0);
        fill(tin, tin + n + 1, 0);
        fill(tout, tout + n + 1, 0);
        fill(color, color + n + 1, 0);
        fill(max_freq, max_freq + n + 1, 0);
        fill(answer, answer + n + 1, 0);
        order.clear();
        value.assign(colors.begin() + 1, colors.end());
        sort(value.begin(), value.end());
        value.erase(unique(value.begin(), value.end()), value.end());
        freq.assign(value.size(), 0);
        best = 0;
        sum = 0;
        if ( !n )
            return;
        assert(1 <= root && root <= n);
        for ( int u = 1; u <= n; u++ )
            color[u] =
                lower_bound(value.begin(), value.end(), colors[u]) - value.begin();
        Prepare(root, 0);
        Dfs(root, 0, false);
    }
};
