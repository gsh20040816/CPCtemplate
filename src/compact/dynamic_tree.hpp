#pragma once
#include <algorithm>
#include <vector>
using namespace std;

struct LinkCutTree
{
    using U = unsigned long long;

    struct Node
    {
        int ch[2]{}, fa = 0;
        U val = 0, sum = 0;
        bool rev = false;
    };

    vector<Node> a;
    vector<int> st;

    LinkCutTree(int n) : a(n + 1), st(n + 1) {}

    bool is_root(int x) const
    {
        int f = a[x].fa;
        return a[f].ch[0] != x && a[f].ch[1] != x;
    }

    void pull(int x) { a[x].sum = a[a[x].ch[0]].sum ^ a[x].val ^ a[a[x].ch[1]].sum; }

    void reverse(int x)
    {
        if (!x) return;
        swap(a[x].ch[0], a[x].ch[1]);
        a[x].rev = !a[x].rev;
    }

    void push(int x)
    {
        if (!a[x].rev) return;
        reverse(a[x].ch[0]);
        reverse(a[x].ch[1]);
        a[x].rev = false;
    }

    void rotate(int x)
    {
        int y = a[x].fa, z = a[y].fa;
        int k = a[y].ch[1] == x;
        int w = a[x].ch[k ^ 1];
        if (!is_root(y)) a[z].ch[a[z].ch[1] == y] = x;
        a[x].fa = z;
        a[y].ch[k] = w;
        if (w) a[w].fa = y;
        a[x].ch[k ^ 1] = y;
        a[y].fa = x;
        pull(y);
        pull(x);
    }

    void splay(int x)
    {
        int top = 0, y = x;
        st[top++] = y;
        while (!is_root(y))
        {
            y = a[y].fa;
            st[top++] = y;
        }
        while (top) push(st[--top]);
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
            // The old right child's fa remains y: it becomes a path-parent.
            a[y].ch[1] = last;
            if (last) a[last].fa = y;
            pull(y);
            last = y;
        }
        splay(x);
    }

    void make_root(int x)
    {
        access(x);
        reverse(x);
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

    bool connected(int x, int y) { return x == y || find_root(x) == find_root(y); }

    bool link(int x, int y)
    {
        make_root(x);
        if (find_root(y) == x) return false;
        a[x].fa = y;
        return true;
    }

    bool cut(int x, int y)
    {
        make_root(x);
        access(y);
        if (a[y].ch[0] != x || a[x].ch[1]) return false;
        a[y].ch[0] = 0;
        a[x].fa = 0;
        pull(y);
        return true;
    }

    void set(int x, U value)
    {
        access(x);
        a[x].val = value;
        pull(x);
    }

    // x and y must be connected. This is a path aggregate, not a subtree sum.
    U query(int x, int y)
    {
        make_root(x);
        access(y);
        return a[y].sum;
    }
};
