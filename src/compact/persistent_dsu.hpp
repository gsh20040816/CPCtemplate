#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

// BEGIN PersistentDSU
struct PersistentDSU
{
    struct Node
    {
        int l = 0, r = 0, v = -1;
    };

    int n;
    vector<Node> t{Node{}};
    vector<int> root{0};

    PersistentDSU(int n) : n(n)
    {
        assert(n > 0);
    }

    int get(int p, int l, int r, int x) const
    {
        if (!p) return -1;
        if (r - l == 1) return t[p].v;
        int m = l + (r - l) / 2;
        if (x < m) return get(t[p].l, l, m, x);
        return get(t[p].r, m, r, x);
    }

    int set(int old, int l, int r, int x, int v)
    {
        Node node = t[old];
        int p = t.size();
        t.push_back(node);
        if (r - l == 1)
            t[p].v = v;
        else
        {
            int m = l + (r - l) / 2;
            if (x < m)
            {
                int q = set(node.l, l, m, x, v);
                t[p].l = q;
            }
            else
            {
                int q = set(node.r, m, r, x, v);
                t[p].r = q;
            }
        }
        return p;
    }

    // Queries never compress paths or allocate nodes. Vertices are 0-based.
    int find(int ver, int x) const
    {
        assert(0 <= ver && ver < (int)root.size());
        assert(0 <= x && x < n);
        int p = get(root[ver], 0, n, x);
        while (p >= 0)
        {
            x = p;
            p = get(root[ver], 0, n, x);
        }
        return x;
    }

    int size(int ver, int x) const
    {
        return -get(root[ver], 0, n, find(ver, x));
    }

    bool same(int ver, int x, int y) const
    {
        return find(ver, x) == find(ver, y);
    }

    int copy(int ver)
    {
        assert(0 <= ver && ver < (int)root.size());
        root.push_back(root[ver]);
        return (int)root.size() - 1;
    }

    // Always create one version; ties attach the first root to the second.
    int merge(int ver, int x, int y)
    {
        x = find(ver, x);
        y = find(ver, y);
        if (x == y) return copy(ver);
        int a = get(root[ver], 0, n, x);
        int b = get(root[ver], 0, n, y);
        if (a < b)
        {
            swap(x, y);
            swap(a, b);
        }
        int p = set(root[ver], 0, n, x, y);
        p = set(p, 0, n, y, a + b);
        root.push_back(p);
        return (int)root.size() - 1;
    }
};
// END PersistentDSU
