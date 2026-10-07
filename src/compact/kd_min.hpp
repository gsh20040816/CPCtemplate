#pragma once
#include <algorithm>
#include <array>
#include <cassert>
#include <climits>
#include <numeric>
#include <vector>
using namespace std;

struct KDMin
{
    using Point = array<long long, 2>;

    struct Item
    {
        Point p;
        long long key;
    };

    struct Node
    {
        Point low, high;
        int ch[2] = {-1, -1}, fa = -1, best = -1;
        bool alive = true;
    };

    vector<Item> p;
    vector<Node> a;
    int root = -1;

    KDMin(const vector<Item> &points) : p(points), a(points.size())
    {
        assert(points.size() <= INT_MAX);
        vector<int> order(p.size());
        iota(order.begin(), order.end(), 0);
        root = build(order, 0, order.size(), 0);
    }

    int better(int x, int y) const
    {
        if (x == -1) return y;
        if (y == -1) return x;
        if (p[x].key != p[y].key) return p[x].key < p[y].key ? x : y;
        return min(x, y);
    }

    void pull(int u)
    {
        a[u].best = a[u].alive ? u : -1;
        for (int v : a[u].ch)
        {
            if (v != -1) a[u].best = better(a[u].best, a[v].best);
        }
    }

    int build(vector<int> &order, int l, int r, int d)
    {
        if (l == r) return -1;
        int mid = l + (r - l) / 2;
        nth_element(order.begin() + l, order.begin() + mid, order.begin() + r,
                    [&](int x, int y)
        {
            if (p[x].p[d] != p[y].p[d]) return p[x].p[d] < p[y].p[d];
            return x < y;
        });
        int u = order[mid];
        a[u].low = a[u].high = p[u].p;
        a[u].ch[0] = build(order, l, mid, d ^ 1);
        a[u].ch[1] = build(order, mid + 1, r, d ^ 1);
        for (int v : a[u].ch)
        {
            if (v == -1) continue;
            a[v].fa = u;
            for (int j = 0; j < 2; j++)
            {
                a[u].low[j] = min(a[u].low[j], a[v].low[j]);
                a[u].high[j] = max(a[u].high[j], a[v].high[j]);
            }
        }
        pull(u);
        return u;
    }

    void erase(int id)
    {
        assert(0 <= id && id < (int)p.size());
        a[id].alive = false;
        for (int u = id; u != -1; u = a[u].fa) pull(u);
    }

    int query(int u, const Point &low, const Point &high) const
    {
        if (u == -1 || a[u].best == -1) return -1;
        bool covered = true, inside = true;
        for (int d = 0; d < 2; d++)
        {
            if (high[d] < a[u].low[d] || low[d] > a[u].high[d]) return -1;
            if (low[d] > a[u].low[d] || high[d] < a[u].high[d]) covered = false;
            if (p[u].p[d] < low[d] || p[u].p[d] > high[d]) inside = false;
        }
        if (covered) return a[u].best;
        int ans = inside && a[u].alive ? u : -1;
        for (int v : a[u].ch) ans = better(ans, query(v, low, high));
        return ans;
    }

    int query(const Point &low, const Point &high) const
    {
        if (low[0] > high[0] || low[1] > high[1]) return -1;
        return query(root, low, high);
    }
};
