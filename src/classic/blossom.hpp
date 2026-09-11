#pragma once
#include <algorithm>
#include <cassert>
#include <numeric>
#include <vector>
using namespace std;

template <int N> struct General_Matching
{
    int n;
    vector<int> g[N];
    int mate[N], pre[N], base[N], q[N];
    bool outer[N], flower[N], seen[N];

    void Init(int vertices)
    {
        assert(0 <= vertices && vertices <= N);
        n = vertices;
        for ( int u = 0; u < n; u++ )
            g[u].clear();
        fill(mate, mate + n, -1);
    }

    void Insert(int u, int v)
    {
        assert(0 <= u && u < n && 0 <= v && v < n);
        if ( u == v )
            return;
        g[u].push_back(v);
        g[v].push_back(u);
    }

    int Lca(int u, int v)
    {
        fill(seen, seen + n, false);
        while ( true )
        {
            u = base[u];
            seen[u] = true;
            if ( mate[u] == -1 )
                break;
            u = pre[mate[u]];
        }
        while ( !seen[base[v]] )
            v = pre[mate[base[v]]];
        return base[v];
    }

    void Mark(int u, int b, int v)
    {
        while ( base[u] != b )
        {
            flower[base[u]] = true;
            flower[base[mate[u]]] = true;
            pre[u] = v;
            v = mate[u];
            u = pre[v];
        }
    }

    bool Augment(int root)
    {
        fill(outer, outer + n, false);
        fill(pre, pre + n, -1);
        iota(base, base + n, 0);
        int tail = 0;
        q[tail++] = root;
        outer[root] = true;
        for ( int head = 0; head < tail; head++ )
        {
            int u = q[head];
            for ( int v : g[u] )
            {
                if ( base[u] == base[v] || mate[u] == v )
                    continue;
                if ( v == root || (mate[v] != -1 && pre[mate[v]] != -1) )
                {
                    int b = Lca(u, v);
                    fill(flower, flower + n, false);
                    Mark(u, b, v);
                    Mark(v, b, u);
                    for ( int x = 0; x < n; x++ )
                    {
                        if ( !flower[base[x]] )
                            continue;
                        base[x] = b;
                        if ( !outer[x] )
                        {
                            outer[x] = true;
                            q[tail++] = x;
                        }
                    }
                }
                else if ( pre[v] == -1 )
                {
                    pre[v] = u;
                    if ( mate[v] == -1 )
                    {
                        while ( v != -1 )
                        {
                            int p = pre[v];
                            int next = mate[p];
                            mate[v] = p;
                            mate[p] = v;
                            v = next;
                        }
                        return true;
                    }
                    int x = mate[v];
                    outer[x] = true;
                    q[tail++] = x;
                }
            }
        }
        return false;
    }

    // Rebuild the maximum matching; mate[u] is -1 for an unmatched vertex.
    int Solve()
    {
        fill(mate, mate + n, -1);
        int answer = 0;
        for ( int u = 0; u < n; u++ )
        {
            if ( mate[u] == -1 && Augment(u) )
                answer++;
        }
        return answer;
    }
};
