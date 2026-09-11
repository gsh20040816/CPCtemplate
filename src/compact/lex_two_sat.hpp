#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

struct LexTwoSAT
{
    int n;
    vector<vector<int>> g;
    vector<int> marked, history, answer;

    LexTwoSAT(int n) : n(n), g(2 * n), marked(2 * n)
    {
        assert(n >= 0);
    }

    int id(int x, bool value) const
    {
        assert(1 <= x && x <= n);
        return 2 * (x - 1) + value;
    }

    // (x == a) OR (y == b). Internal literal IDs are 0-based.
    void add(int x, bool a, int y, bool b)
    {
        int u = id(x, a), v = id(y, b);
        g[u ^ 1].push_back(v);
        g[v ^ 1].push_back(u);
        answer.clear();
    }

    void force(int x, bool value)
    {
        add(x, value, x, value);
    }

    bool paint(int u)
    {
        if (marked[u ^ 1])
            return false;
        if (marked[u])
            return true;
        marked[u] = 1;
        history.push_back(u);
        for (int v : g[u])
            if (!paint(v))
                return false;
        return true;
    }

    bool solve()
    {
        fill(marked.begin(), marked.end(), 0);
        history.clear();
        answer.clear();
        for (int x = 1; x <= n; x++)
        {
            int u = id(x, false);
            if (marked[u] || marked[u ^ 1])
                continue;
            int checkpoint = history.size();
            if (!paint(u))
            {
                while ((int)history.size() > checkpoint)
                {
                    marked[history.back()] = 0;
                    history.pop_back();
                }
                if (!paint(u ^ 1))
                    return false;
            }
        }
        answer.assign(n + 1, 0);
        for (int x = 1; x <= n; x++)
            answer[x] = marked[id(x, true)];
        return true;
    }
};
