#pragma once
#include <cassert>
#include <utility>
#include <vector>
using namespace std;

struct LeftistHeap
{
    struct Node
    {
        long long key;
        int l, r, dist;
    };

    vector<Node> t{{0, 0, 0, 0}};

    int singleton(long long key)
    {
        t.push_back({key, 0, 0, 1});
        return int(t.size()) - 1;
    }

    int meld(int x, int y)
    {
        if (!x || !y) return x ? x : y;
        assert(x != y);
        if (pair(t[x].key, x) > pair(t[y].key, y)) swap(x, y);
        t[x].r = meld(t[x].r, y);
        if (t[t[x].l].dist < t[t[x].r].dist) swap(t[x].l, t[x].r);
        t[x].dist = t[t[x].r].dist + 1;
        return x;
    }

    int pop(int x)
    {
        assert(x > 0);
        int root = meld(t[x].l, t[x].r);
        t[x].l = t[x].r = 0;
        t[x].dist = 1;
        return root;
    }
};
