#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <vector>
using namespace std;

struct SequenceSplay
{
    struct Node
    {
        int ch[2]{}, fa = 0, siz = 0;
        bool rev = false;
    };
    int n, root;
    vector<Node> a;

    // Initial order: original IDs 0, 1, ..., n-1.
    SequenceSplay(int n) : n(n)
    {
        assert(0 <= n && n <= INT_MAX - 3);
        a.resize(n + 3);
        root = build(1, n + 3, 0);
    }

    void pull(int x)
    {
        a[x].siz = a[a[x].ch[0]].siz + a[a[x].ch[1]].siz + 1;
    }

    int build(int l, int r, int p)
    {
        if (l == r) return 0;
        int x = l + (r - l) / 2;
        a[x].fa = p;
        a[x].ch[0] = build(l, x, x);
        a[x].ch[1] = build(x + 1, r, x);
        pull(x);
        return x;
    }

    void flip(int x)
    {
        if (!x) return;
        swap(a[x].ch[0], a[x].ch[1]);
        a[x].rev = !a[x].rev;
    }

    void push(int x)
    {
        if (!a[x].rev) return;
        flip(a[x].ch[0]);
        flip(a[x].ch[1]);
        a[x].rev = false;
    }

    void push_path(int x)
    {
        if (a[x].fa) push_path(a[x].fa);
        push(x);
    }

    void rotate(int x)
    {
        int y = a[x].fa, z = a[y].fa;
        int k = a[y].ch[1] == x, w = a[x].ch[k ^ 1];
        if (z) a[z].ch[a[z].ch[1] == y] = x;
        else root = x;
        a[x].fa = z;
        a[y].ch[k] = w;
        if (w) a[w].fa = y;
        a[x].ch[k ^ 1] = y;
        a[y].fa = x;
        pull(y);
        pull(x);
    }

    void splay(int x, int goal = 0)
    {
        push_path(x);
        while (a[x].fa != goal)
        {
            int y = a[x].fa, z = a[y].fa;
            if (z != goal)
            {
                bool same = (a[y].ch[1] == x) == (a[z].ch[1] == y);
                rotate(same ? y : x);
            }
            rotate(x);
        }
    }

    // Internal rank includes the two sentinels; does not splay.
    int select(int k)
    {
        int x = root;
        while (true)
        {
            push(x);
            int l = a[a[x].ch[0]].siz;
            if (k == l) return x;
            if (k < l) x = a[x].ch[0];
            else
            {
                k -= l + 1;
                x = a[x].ch[1];
            }
        }
    }

    // Current 0-based position of an original ID.
    int pos(int id)
    {
        assert(0 <= id && id < n);
        int x = id + 2;
        splay(x);
        return a[a[x].ch[0]].siz - 1;
    }

    // Original ID at the current 0-based position.
    int at(int k)
    {
        assert(0 <= k && k < n);
        int x = select(k + 1);
        splay(x);
        return x - 2;
    }

    void reverse(int l, int r)
    {
        assert(0 <= l && l <= r && r <= n);
        if (l == r) return;
        int x = select(l);
        splay(x);
        int y = select(r + 1);
        splay(y, x);
        flip(a[y].ch[0]);
    }

    void collect(int x, vector<int> &v)
    {
        if (!x) return;
        push(x);
        collect(a[x].ch[0], v);
        if (2 <= x && x <= n + 1) v.push_back(x - 2);
        collect(a[x].ch[1], v);
    }

    vector<int> order()
    {
        vector<int> v;
        v.reserve(n);
        collect(root, v);
        return v;
    }
};
