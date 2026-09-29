#pragma once
#include <algorithm>
#include <array>
#include <vector>
using namespace std;

template <class Coord = int> struct KDTreeSum
{
    using ll = long long;
    using Point = array<Coord, 2>;

    struct Node
    {
        Point point{}, low{}, high{};
        array<int, 2> child{};
        int size = 1;
        ll value = 0, sum = 0;
    };

    vector<Node> a;
    int root = 0;

    KDTreeSum(int reserve_points = 0)
    {
        a.reserve(reserve_points + 1);
        a.push_back(Node{});
        a[0].size = 0;
    }

    bool less(Point x, Point y, int axis) const
    {
        if (x[axis] != y[axis]) return x[axis] < y[axis];
        return x[axis ^ 1] < y[axis ^ 1];
    }

    void pull(int p)
    {
        a[p].low = a[p].high = a[p].point;
        a[p].size = 1;
        a[p].sum = a[p].value;
        for (int q : a[p].child)
        {
            if (!q) continue;
            a[p].size += a[q].size;
            a[p].sum += a[q].sum;
            for (int d = 0; d < 2; d++)
            {
                a[p].low[d] = min(a[p].low[d], a[q].low[d]);
                a[p].high[d] = max(a[p].high[d], a[q].high[d]);
            }
        }
    }

    void collect(int p, vector<int> &v)
    {
        if (!p) return;
        collect(a[p].child[0], v);
        v.push_back(p);
        collect(a[p].child[1], v);
    }

    int build(vector<int> &v, int l, int r, int axis)
    {
        if (l == r) return 0;
        int m = l + (r - l) / 2;
        nth_element(v.begin() + l,
                    v.begin() + m,
                    v.begin() + r,
                    [&](int x, int y) { return less(a[x].point, a[y].point, axis); });
        int p = v[m];
        a[p].child[0] = build(v, l, m, axis ^ 1);
        a[p].child[1] = build(v, m + 1, r, axis ^ 1);
        pull(p);
        return p;
    }

    int add(int p, Point point, ll delta, int axis)
    {
        if (!p)
        {
            p = a.size();
            a.push_back(Node{});
            a[p].point = a[p].low = a[p].high = point;
            a[p].value = a[p].sum = delta;
            return p;
        }
        if (a[p].point == point)
            a[p].value += delta;
        else
        {
            int side = !less(point, a[p].point, axis);
            a[p].child[side] = add(a[p].child[side], point, delta, axis ^ 1);
        }
        pull(p);
        int heavy = max(a[a[p].child[0]].size, a[a[p].child[1]].size);
        if (4LL * heavy <= 3LL * a[p].size) return p;
        vector<int> v;
        v.reserve(a[p].size);
        collect(p, v);
        return build(v, 0, v.size(), axis);
    }

    void add(Coord x, Coord y, ll delta) { root = add(root, {x, y}, delta, 0); }

    ll query(int p, Point low, Point high) const
    {
        if (!p) return 0;
        bool covered = true, inside = true;
        for (int d = 0; d < 2; d++)
        {
            if (a[p].high[d] < low[d] || high[d] < a[p].low[d]) return 0;
            covered &= low[d] <= a[p].low[d] && a[p].high[d] <= high[d];
            inside &= low[d] <= a[p].point[d] && a[p].point[d] <= high[d];
        }
        if (covered) return a[p].sum;
        ll answer = inside ? a[p].value : 0;
        for (int q : a[p].child) answer += query(q, low, high);
        return answer;
    }

    ll query(Coord x1, Coord y1, Coord x2, Coord y2) const
    {
        if (x1 > x2 || y1 > y2) return 0;
        return query(root, {x1, y1}, {x2, y2});
    }
};
