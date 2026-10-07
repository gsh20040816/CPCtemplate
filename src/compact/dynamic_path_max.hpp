#pragma once
#include <algorithm>
#include <optional>
#include <vector>
using namespace std;

struct DynamicPathMax
{
    using ll = long long;

    struct Node
    {
        int ch[2]{}, fa = 0;
        ll val = 0, mx = 0, add = 0;
        bool rev = false;
    };

    vector<Node> a;

    DynamicPathMax(const vector<ll> &v) : a(v.size() + 1)
    {
        for (int i = 0; i < (int)v.size(); i++)
            a[i + 1].val = a[i + 1].mx = v[i];
    }

    bool is_root(int x) const
    {
        int f = a[x].fa;
        return a[f].ch[0] != x && a[f].ch[1] != x;
    }

    void pull(int x)
    {
        a[x].mx = a[x].val;
        for (int y : a[x].ch)
            if (y)
                a[x].mx = max(a[x].mx, a[y].mx);
    }

    void flip(int x)
    {
        if (!x)
            return;
        swap(a[x].ch[0], a[x].ch[1]);
        a[x].rev = !a[x].rev;
    }

    void apply(int x, ll w)
    {
        if (!x)
            return;
        a[x].val += w;
        a[x].mx += w;
        a[x].add += w;
    }

    void push(int x)
    {
        if (a[x].rev)
        {
            flip(a[x].ch[0]);
            flip(a[x].ch[1]);
            a[x].rev = false;
        }
        if (a[x].add)
        {
            apply(a[x].ch[0], a[x].add);
            apply(a[x].ch[1], a[x].add);
            a[x].add = 0;
        }
    }

    void push_path(int x)
    {
        if (!is_root(x))
            push_path(a[x].fa);
        push(x);
    }

    void rotate(int x)
    {
        int y = a[x].fa, z = a[y].fa;
        int k = a[y].ch[1] == x;
        int w = a[x].ch[k ^ 1];
        if (!is_root(y))
            a[z].ch[a[z].ch[1] == y] = x;
        a[x].fa = z;
        a[y].ch[k] = w;
        if (w)
            a[w].fa = y;
        a[x].ch[k ^ 1] = y;
        a[y].fa = x;
        pull(y);
        pull(x);
    }

    void splay(int x)
    {
        push_path(x);
        while (!is_root(x))
        {
            int y = a[x].fa, z = a[y].fa;
            if (!is_root(y))
            {
                bool same = (a[y].ch[1] == x) == (a[z].ch[1] == y);
                rotate(same ? y : x);
            }
            rotate(x);
        }
    }

    void access(int x)
    {
        int last = 0;
        for (int y = x; y; y = a[y].fa)
        {
            splay(y);
            a[y].ch[1] = last;
            if (last)
                a[last].fa = y;
            pull(y);
            last = y;
        }
        splay(x);
    }

    void make_root(int x)
    {
        access(x);
        flip(x);
    }

    int find_root(int x)
    {
        access(x);
        push(x);
        while (a[x].ch[0])
        {
            x = a[x].ch[0];
            push(x);
        }
        splay(x);
        return x;
    }

    bool expose(int x, int y)
    {
        make_root(x);
        if (find_root(y) != x)
            return false;
        access(y);
        return true;
    }

    bool link(int x, int y)
    {
        make_root(x);
        if (find_root(y) == x)
            return false;
        a[x].fa = y;
        return true;
    }

    bool cut(int x, int y)
    {
        if (!expose(x, y) || a[y].ch[0] != x || a[x].ch[1])
            return false;
        a[y].ch[0] = 0;
        a[x].fa = 0;
        pull(y);
        return true;
    }

    bool cut_parent(int root, int x)
    {
        if (root == x || !expose(root, x))
            return false;
        int left = a[x].ch[0];
        a[left].fa = 0;
        a[x].ch[0] = 0;
        pull(x);
        return true;
    }

    bool add(int x, int y, ll w)
    {
        if (!expose(x, y))
            return false;
        apply(y, w);
        return true;
    }

    optional<ll> query(int x, int y)
    {
        if (!expose(x, y))
            return nullopt;
        return a[y].mx;
    }
};
