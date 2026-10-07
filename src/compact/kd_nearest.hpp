#pragma once
#include <algorithm>
#include <array>
#include <cassert>
#include <numeric>
#include <queue>
#include <utility>
#include <vector>
using namespace std;

template <int D = 2> struct KDNearest
{
    static_assert(D > 0);
    using Point = array<int, D>;
    using Wide = __int128_t;
    using Key = pair<Wide, int>;

    struct Node
    {
        Point low, high;
        array<int, 2> child{-1, -1};
        int first;
    };

    vector<Point> p;
    vector<Node> a;
    int root;

    KDNearest(const vector<Point> &points = {}) : p(points), a(p.size())
    {
        vector<int> order(p.size());
        iota(order.begin(), order.end(), 0);
        root = build(order, 0, order.size(), 0);
    }

    int build(vector<int> &order, int l, int r, int axis)
    {
        if (l == r) return -1;
        int m = (l + r) / 2;
        nth_element(order.begin() + l, order.begin() + m, order.begin() + r,
            [&](int x, int y)
            {
                return pair(p[x][axis], x) < pair(p[y][axis], y);
            });
        int u = order[m];
        a[u].low = a[u].high = p[u];
        a[u].first = u;
        a[u].child[0] = build(order, l, m, (axis + 1) % D);
        a[u].child[1] = build(order, m + 1, r, (axis + 1) % D);
        for (int v : a[u].child)
        {
            if (v == -1) continue;
            a[u].first = min(a[u].first, a[v].first);
            for (int d = 0; d < D; d++)
            {
                a[u].low[d] = min(a[u].low[d], a[v].low[d]);
                a[u].high[d] = max(a[u].high[d], a[v].high[d]);
            }
        }
        return u;
    }

    Wide distance(const Point &x, const Point &y) const
    {
        Wide ans = 0;
        for (int d = 0; d < D; d++)
        {
            Wide t = Wide(x[d]) - y[d];
            ans += t * t;
        }
        return ans;
    }

    Key bound(int u, const Point &q, bool far) const
    {
        Wide ans = 0;
        for (int d = 0; d < D; d++)
        {
            Wide l = Wide(a[u].low[d]) - q[d];
            Wide r = Wide(a[u].high[d]) - q[d];
            if (far) ans -= max(l * l, r * r);
            else if (l > 0) ans += l * l;
            else if (r < 0) ans += r * r;
        }
        return {ans, a[u].first};
    }

    void search(int u, const Point &q, int k, bool far,
                priority_queue<Key> &heap) const
    {
        if (u == -1) return;
        if ((int)heap.size() == k && bound(u, q, far) >= heap.top()) return;
        Wide dist = distance(p[u], q);
        Key cur{far ? -dist : dist, u};
        if ((int)heap.size() < k || cur < heap.top())
        {
            heap.push(cur);
            if ((int)heap.size() > k) heap.pop();
        }
        int x = a[u].child[0];
        int y = a[u].child[1];
        if (x == -1 || (y != -1 && bound(y, q, far) < bound(x, q, far)))
        {
            swap(x, y);
        }
        search(x, q, k, far, heap);
        search(y, q, k, far, heap);
    }

    vector<int> query(const Point &q, int k, bool far = false) const
    {
        assert(0 <= k && k <= (int)p.size());
        if (k == 0) return {};
        priority_queue<Key> heap;
        search(root, q, k, far, heap);
        vector<int> ans;
        while (!heap.empty())
        {
            ans.push_back(heap.top().second);
            heap.pop();
        }
        reverse(ans.begin(), ans.end());
        return ans;
    }
};
