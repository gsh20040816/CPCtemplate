#pragma once
#include <array>
#include <cassert>
#include <climits>
#include <vector>
using namespace std;

struct PersistentParityIndex
{
    using ll = long long;
    struct Node
    {
        int left = 0, right = 0;
        ll count = 0, odd = 0;
    };
    int n;
    vector<Node> t{Node{}};
    vector<int> roots{0};

    PersistentParityIndex(int n) : n(n)
    {
        assert(n > 0);
    }

    int update(int p, int l, int r, int x, ll delta)
    {
        assert(t.size() < INT_MAX);
        int u = t.size();
        Node node = t[p];
        t.push_back(node);
        if (r - l == 1)
        {
            assert(delta >= -node.count);
            t[u].count += delta;
            t[u].odd = (x % 2) * t[u].count;
            return u;
        }
        int m = l + (r - l) / 2;
        if (x < m)
            t[u].left = update(node.left, l, m, x, delta);
        else
            t[u].right = update(node.right, m, r, x, delta);
        t[u].count = t[t[u].left].count + t[t[u].right].count;
        t[u].odd = t[t[u].left].odd + t[t[u].right].odd;
        return u;
    }

    int add(int version, int x, ll delta)
    {
        assert(0 <= version && version < (int)roots.size());
        assert(0 <= x && x < n && roots.size() < INT_MAX);
        int p = roots[version];
        assert(delta <= 0 || t[p].count <= LLONG_MAX - delta);
        int root = delta == 0 ? p : update(p, 0, n, x, delta);
        roots.push_back(root);
        return (int)roots.size() - 1;
    }

    array<ll, 2> difference(int before, int after) const
    {
        assert(0 <= before && before < (int)roots.size());
        assert(0 <= after && after < (int)roots.size());
        auto a = t[roots[before]], b = t[roots[after]];
        return {b.count - a.count, b.odd - a.odd};
    }

    int stop_node(int a, int b, int l, int r, ll k) const
    {
        if (r - l == 1)
            return l;
        int m = l + (r - l) / 2;
        int x = t[a].right, y = t[b].right;
        ll count = t[y].count - t[x].count;
        ll odd = t[y].odd - t[x].odd;
        if (odd > 0 || count > k)
            return stop_node(x, y, m, r, k);
        return stop_node(t[a].left, t[b].left, l, m, k - count);
    }

    // Queries require nonnegative after-before counts at every position.
    // Remove up to k largest even elements, stopping at the first odd element.
    int stop(int before, int after, ll k) const
    {
        assert(k >= 0);
        auto [count, odd] = difference(before, after);
        if (odd == 0 && count <= k)
            return -1;
        return stop_node(roots[before], roots[after], 0, n, k);
    }

    array<ll, 3> odd_node(int a, int b, int l, int r, ll k) const
    {
        if (r - l == 1)
            return {l, t[b].odd - t[a].odd, k};
        int m = l + (r - l) / 2;
        int x = t[a].right, y = t[b].right;
        ll count = t[y].odd - t[x].odd;
        if (count > k)
            return odd_node(x, y, m, r, k);
        return odd_node(t[a].left, t[b].left, l, m, k - count);
    }

    // Descending zero-based rank; result is {position, multiplicity, offset}.
    array<ll, 3> odd_kth(int before, int after, ll k) const
    {
        assert(k >= 0);
        auto [count, odd] = difference(before, after);
        if (k >= odd)
            return {-1, 0, k - odd};
        return odd_node(roots[before], roots[after], 0, n, k);
    }
};
