#pragma once
#include <cassert>
#include <climits>
#include <utility>
#include <vector>
using namespace std;

// Roots belong to one pool. Merge requires every left value <= every right value.
struct ShiftSplay
{
    using ll = long long;
    struct Node
    {
        int ch[2]{}, fa = 0;
        ll val = 0, lazy = 0;
    };
    vector<Node> a{Node{}};

    void add(int root, ll delta)
    {
        if (!root)
            return;
        a[root].val += delta;
        a[root].lazy += delta;
    }

    void push(int x)
    {
        add(a[x].ch[0], a[x].lazy);
        add(a[x].ch[1], a[x].lazy);
        a[x].lazy = 0;
    }

    void down(int x)
    {
        if (a[x].fa)
            down(a[x].fa);
        push(x);
    }

    void rotate(int x)
    {
        int y = a[x].fa, z = a[y].fa;
        int k = a[y].ch[1] == x;
        int w = a[x].ch[k ^ 1];
        if (z)
            a[z].ch[a[z].ch[1] == y] = x;
        a[x].fa = z;
        a[y].ch[k] = w;
        if (w)
            a[w].fa = y;
        a[x].ch[k ^ 1] = y;
        a[y].fa = x;
    }

    void splay(int x)
    {
        down(x);
        while (a[x].fa)
        {
            int y = a[x].fa, z = a[y].fa;
            if (z)
            {
                bool same = (a[y].ch[1] == x) == (a[z].ch[1] == y);
                rotate(same ? y : x);
            }
            rotate(x);
        }
    }

    int insert(int &root, ll value)
    {
        assert(a.size() < INT_MAX);
        int x = a.size();
        a.push_back(Node{});
        a[x].val = value;
        int p = root, parent = 0, side = 0;
        while (p)
        {
            push(p);
            parent = p;
            side = value >= a[p].val;
            p = a[p].ch[side];
        }
        a[x].fa = parent;
        if (parent)
            a[parent].ch[side] = x;
        splay(x);
        root = x;
        return x;
    }

    pair<int, int> split(int root, ll key)
    {
        if (!root)
            return {0, 0};
        int p = root, last = root, next = 0;
        while (p)
        {
            push(p);
            last = p;
            if (a[p].val >= key)
            {
                next = p;
                p = a[p].ch[0];
            }
            else
                p = a[p].ch[1];
        }
        splay(last);
        if (!next)
            return {last, 0};
        splay(next);
        int left = a[next].ch[0];
        a[next].ch[0] = 0;
        if (left)
            a[left].fa = 0;
        return {left, next};
    }

    int merge(int left, int right)
    {
        if (!left || !right)
            return left ? left : right;
        int x = left;
        while (a[x].ch[1])
            x = a[x].ch[1];
        splay(x);
        a[x].ch[1] = right;
        a[right].fa = x;
        return x;
    }

    ll value(int &root, int id)
    {
        assert(0 < id && id < (int)a.size());
        splay(id);
        root = id;
        return a[id].val;
    }
};
