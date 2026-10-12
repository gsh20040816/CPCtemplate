#pragma once
#include <cassert>
#include <climits>
#include <utility>
#include <vector>
using namespace std;

struct PersistentWeightedIndex
{
    using ll = long long;
    struct Node
    {
        int left = 0, right = 0, count = 0;
        ll sum = 0;
    };
    int n;
    vector<Node> t{Node{}};
    vector<int> roots{0};

    PersistentWeightedIndex(int n) : n(n)
    {
        assert(n > 0);
    }

    int insert(int old, int l, int r, int pos, ll weight)
    {
        assert(t.size() < INT_MAX && t[old].count < INT_MAX);
        int u = t.size();
        Node copy = t[old];
        copy.count++;
        copy.sum += weight;
        t.push_back(copy);
        if (r - l == 1)
            return u;
        int m = l + (r - l) / 2;
        if (pos < m)
            t[u].left = insert(t[u].left, l, m, pos, weight);
        else
            t[u].right = insert(t[u].right, m, r, pos, weight);
        return u;
    }

    int add(int version, int pos, ll weight)
    {
        assert(0 <= version && version < (int)roots.size());
        assert(0 <= pos && pos < n && roots.size() < INT_MAX);
        int root = insert(roots[version], 0, n, pos, weight);
        roots.push_back(root);
        return (int)roots.size() - 1;
    }

    pair<int, ll> query_node(int u, int l, int r, int ql, int qr) const
    {
        if (!u || qr <= l || r <= ql)
            return {0, 0};
        if (ql <= l && r <= qr)
            return {t[u].count, t[u].sum};
        int m = l + (r - l) / 2;
        auto a = query_node(t[u].left, l, m, ql, qr);
        auto b = query_node(t[u].right, m, r, ql, qr);
        return {a.first + b.first, a.second + b.second};
    }

    pair<int, ll> query(int version, int l, int r) const
    {
        assert(0 <= version && version < (int)roots.size());
        assert(0 <= l && l <= r && r <= n);
        return query_node(roots[version], 0, n, l, r);
    }

    int find(int before, int after, int l, int r, int key) const
    {
        if (r <= key || t[after].count == t[before].count)
            return -1;
        if (r - l == 1)
            return l;
        int m = l + (r - l) / 2;
        int answer = find(t[before].left, t[after].left, l, m, key);
        if (answer == -1)
            answer = find(t[before].right, t[after].right, m, r, key);
        return answer;
    }

    // The after-before count at every position must be nonnegative.
    int first(int before, int after, int key) const
    {
        assert(0 <= before && before < (int)roots.size());
        assert(0 <= after && after < (int)roots.size());
        return find(roots[before], roots[after], 0, n, key);
    }
};
