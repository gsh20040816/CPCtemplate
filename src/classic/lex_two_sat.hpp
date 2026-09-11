#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

template <int N> struct Lex_Two_SAT
{
    int n;
    vector<int> g[2 * N], history, answer;
    int marked[2 * N];

    void Init(int variables)
    {
        assert(0 <= variables && variables <= N);
        n = variables;
        for ( int u = 0; u < 2 * n; u++ )
            g[u].clear();
        history.clear();
        answer.clear();
    }

    int Id(int x, bool value) const
    {
        assert(1 <= x && x <= n);
        return 2 * (x - 1) + value;
    }

    // (x == a) OR (y == b). Internal literal IDs are 0-based.
    void Add(int x, bool a, int y, bool b)
    {
        int u = Id(x, a), v = Id(y, b);
        g[u ^ 1].push_back(v);
        g[v ^ 1].push_back(u);
        answer.clear();
    }

    void Force(int x, bool value)
    {
        Add(x, value, x, value);
    }

    bool Paint(int u)
    {
        if ( marked[u ^ 1] )
            return false;
        if ( marked[u] )
            return true;
        marked[u] = 1;
        history.push_back(u);
        for ( int v : g[u] )
            if ( !Paint(v) )
                return false;
        return true;
    }

    bool Solve()
    {
        fill(marked, marked + 2 * n, 0);
        history.clear();
        answer.clear();
        for ( int x = 1; x <= n; x++ )
        {
            int u = Id(x, false);
            if ( marked[u] || marked[u ^ 1] )
                continue;
            int checkpoint = history.size();
            if ( !Paint(u) )
            {
                while ( (int)history.size() > checkpoint )
                {
                    marked[history.back()] = 0;
                    history.pop_back();
                }
                if ( !Paint(u ^ 1) )
                    return false;
            }
        }
        answer.assign(n + 1, 0);
        for ( int x = 1; x <= n; x++ )
            answer[x] = marked[Id(x, true)];
        return true;
    }
};
