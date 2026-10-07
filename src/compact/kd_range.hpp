#pragma once
#include <algorithm>
#include <array>
#include <vector>
using namespace std;

struct KDRange
{
    using Point = array<long long, 2>;

    struct Item
    {
        Point p;
        int id;
    };

    struct Node
    {
        Item item;
        Point low, high;
        array<int, 2> child{};
        int size = 0, alive = 0;
        bool present = false;
    };

    vector<Node> a{Node{}};
    vector<int> free;
    int root = 0;

    KDRange(vector<Item> points = {})
    {
        a.reserve(points.size() + 1);
        root = build(points, 0, points.size(), 0);
    }

    bool less(const Item &x, const Item &y, int axis) const
    {
        if (x.p[axis] != y.p[axis]) return x.p[axis] < y.p[axis];
        if (x.p[axis ^ 1] != y.p[axis ^ 1]) return x.p[axis ^ 1] < y.p[axis ^ 1];
        return x.id < y.id;
    }

    int node(const Item &item)
    {
        int u;
        if (free.empty())
        {
            u = a.size();
            a.emplace_back();
        }
        else
        {
            u = free.back();
            free.pop_back();
        }
        a[u] = Node{};
        a[u].item = item;
        a[u].low = a[u].high = item.p;
        a[u].size = a[u].alive = 1;
        a[u].present = true;
        return u;
    }

    void pull(int u)
    {
        a[u].low = a[u].high = a[u].item.p;
        a[u].size = 1;
        a[u].alive = a[u].present;
        for (int v : a[u].child)
        {
            if (!v) continue;
            a[u].size += a[v].size;
            a[u].alive += a[v].alive;
            for (int d = 0; d < 2; d++)
            {
                a[u].low[d] = min(a[u].low[d], a[v].low[d]);
                a[u].high[d] = max(a[u].high[d], a[v].high[d]);
            }
        }
    }

    int build(vector<Item> &v, int l, int r, int axis)
    {
        if (l == r) return 0;
        int m = l + (r - l) / 2;
        nth_element(v.begin() + l, v.begin() + m, v.begin() + r,
            [&](const Item &x, const Item &y)
            {
                return less(x, y, axis);
            });
        int u = node(v[m]);
        a[u].child[0] = build(v, l, m, axis ^ 1);
        a[u].child[1] = build(v, m + 1, r, axis ^ 1);
        pull(u);
        return u;
    }

    void collect(int u, vector<Item> &v)
    {
        if (!u) return;
        collect(a[u].child[0], v);
        collect(a[u].child[1], v);
        if (a[u].present) v.push_back(a[u].item);
        free.push_back(u);
    }

    int rebuild(int u, int axis)
    {
        vector<Item> v;
        v.reserve(a[u].alive);
        collect(u, v);
        return build(v, 0, v.size(), axis);
    }

    int add(int u, const Item &item, int axis)
    {
        if (!u) return node(item);
        int side = !less(item, a[u].item, axis);
        a[u].child[side] = add(a[u].child[side], item, axis ^ 1);
        pull(u);
        int heavy = max(a[a[u].child[0]].size, a[a[u].child[1]].size);
        if (4LL * heavy > 3LL * a[u].size) u = rebuild(u, axis);
        return u;
    }

    void add(Item item)
    {
        root = add(root, item, 0);
    }

    void take(int u, Point low, Point high, vector<Item> &out)
    {
        if (!u || !a[u].alive) return;
        bool inside = true;
        for (int d = 0; d < 2; d++)
        {
            if (a[u].high[d] < low[d] || high[d] < a[u].low[d]) return;
            inside &= low[d] <= a[u].item.p[d] && a[u].item.p[d] <= high[d];
        }
        if (a[u].present && inside)
        {
            out.push_back(a[u].item);
            a[u].present = false;
        }
        for (int v : a[u].child) take(v, low, high, out);
        pull(u);
    }

    vector<Item> extract(Point low, Point high)
    {
        vector<Item> out;
        if (low[0] > high[0] || low[1] > high[1]) return out;
        take(root, low, high, out);
        if (2LL * a[root].alive < a[root].size) root = rebuild(root, 0);
        return out;
    }
};
