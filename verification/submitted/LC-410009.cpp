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

    int find_last(int before, int after, int l, int r, int key) const
    {
        if (l >= key || t[after].count == t[before].count)
            return -1;
        if (r - l == 1)
            return l;
        int m = l + (r - l) / 2;
        int answer = find_last(t[before].right, t[after].right, m, r, key);
        if (answer == -1)
            answer = find_last(t[before].left, t[after].left, l, m, key);
        return answer;
    }

    // Strict predecessor; the same nonnegative count-difference contract applies.
    int last(int before, int after, int key) const
    {
        assert(0 <= before && before < (int)roots.size());
        assert(0 <= after && after < (int)roots.size());
        return find_last(roots[before], roots[after], 0, n, key);
    }
};

// https://judge.yosupo.jp/problem/rectangle_sum
#include <algorithm>
#include <array>
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<array<int, 3>> a(n);
    vector<int> xs, ys;
    for (auto &[x, y, w] : a)
    {
        cin >> x >> y >> w;
        ys.push_back(y);
    }
    sort(a.begin(), a.end());
    sort(ys.begin(), ys.end());
    ys.erase(unique(ys.begin(), ys.end()), ys.end());
    auto rank = [&](int y)
    {
        return lower_bound(ys.begin(), ys.end(), y) - ys.begin();
    };
    PersistentWeightedIndex tree(ys.size());
    for (int i = 0; i < n; i++)
    {
        auto [x, y, w] = a[i];
        xs.push_back(x);
        tree.add(i, rank(y), w);
    }
    while (q--)
    {
        int l, d, r, u;
        cin >> l >> d >> r >> u;
        int before = lower_bound(xs.begin(), xs.end(), l) - xs.begin();
        int after = lower_bound(xs.begin(), xs.end(), r) - xs.begin();
        long long answer = tree.query(after, rank(d), rank(u)).second;
        answer -= tree.query(before, rank(d), rank(u)).second;
        cout << answer << '\n';
    }
}
