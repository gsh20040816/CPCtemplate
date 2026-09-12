#include <bits/stdc++.h>
#include <cassert>
using namespace std;

struct Persistent_Range
{
    using ll = long long;

    struct Node
    {
        int left = 0, right = 0;
        ll sum = 0, lazy = 0;
    };

    int n;
    vector<Node> t{Node{}};
    vector<int> root{0};

    explicit Persistent_Range(int size) : n(size)
    {
        assert(n > 0);
    }

    int Clone(int p)
    {
        Node node = t[p];
        t.push_back(node);
        return int(t.size()) - 1;
    }

    void Pushup(int p, int len)
    {
        t[p].sum = t[t[p].left].sum + t[t[p].right].sum + t[p].lazy * len;
    }

    int Change(int p, int l, int r, int ql, int qr, ll value)
    {
        if ( qr <= l || r <= ql )
            return p;
        int u = Clone(p);
        if ( ql <= l && r <= qr )
        {
            t[u].lazy += value;
            t[u].sum += value * (r - l);
            return u;
        }
        int m = l + (r - l) / 2;
        int a = Change(t[p].left, l, m, ql, qr, value);
        int b = Change(t[p].right, m, r, ql, qr, value);
        t[u].left = a;
        t[u].right = b;
        Pushup(u, r - l);
        return u;
    }

    int Replace(int p, int q, int l, int r, int ql, int qr, ll offset)
    {
        if ( qr <= l || r <= ql )
            return p;
        if ( ql <= l && r <= qr )
        {
            if ( offset == 0 )
                return q;
            int u = Clone(q);
            t[u].lazy += offset;
            t[u].sum += offset * (r - l);
            return u;
        }
        int u = Clone(p), m = l + (r - l) / 2;
        offset += t[q].lazy - t[p].lazy;
        int a = Replace(t[p].left, t[q].left, l, m, ql, qr, offset);
        int b = Replace(t[p].right, t[q].right, m, r, ql, qr, offset);
        t[u].left = a;
        t[u].right = b;
        Pushup(u, r - l);
        return u;
    }

    ll Get(int p, int l, int r, int ql, int qr, ll carry) const
    {
        if ( qr <= l || r <= ql )
            return 0;
        if ( ql <= l && r <= qr )
            return t[p].sum + carry * (r - l);
        carry += t[p].lazy;
        int m = l + (r - l) / 2;
        return Get(t[p].left, l, m, ql, qr, carry) +
               Get(t[p].right, m, r, ql, qr, carry);
    }

    void Check(int version, int l, int r) const
    {
        assert(0 <= version && version < int(root.size()));
        assert(0 <= l && l <= r && r <= n);
    }

    int Add(int version, int l, int r, ll value)
    {
        Check(version, l, r);
        int p = l == r || value == 0 ? root[version]
                                     : Change(root[version], 0, n, l, r, value);
        root.push_back(p);
        return int(root.size()) - 1;
    }

    int Splice(int destination, int source, int l, int r)
    {
        Check(destination, l, r);
        Check(source, l, r);
        int p = l == r ? root[destination]
                       : Replace(root[destination], root[source], 0, n, l, r, 0);
        root.push_back(p);
        return int(root.size()) - 1;
    }

    ll Query(int version, int l, int r) const
    {
        Check(version, l, r);
        return l == r ? 0 : Get(root[version], 0, n, l, r, 0);
    }
};


int main()
{
    int n, q;
    scanf("%d%d", &n, &q);
    vector<int> a(n), next(n), last(n + 1, n), version(n + 1);
    for ( auto &x : a )
        scanf("%d", &x);
    for ( int i = n - 1; i >= 0; i-- )
    {
        next[i] = last[a[i]];
        last[a[i]] = i;
    }
    Persistent_Range tree(n);
    function<size_t(int, int, int, int)> nodes =
        [&](int l, int r, int ql, int qr) -> size_t
    {
        if ( qr <= l || r <= ql )
            return 0;
        if ( ql <= l && r <= qr )
            return 1;
        int m = l + (r - l) / 2;
        return 1 + nodes(l, m, ql, qr) + nodes(m, r, ql, qr);
    };
    size_t capacity = 1;
    for ( int i = 0; i < n; i++ )
    {
        capacity += nodes(0, n, i, next[i]);
        capacity += nodes(0, n, next[i], n);
    }
    tree.t.reserve(capacity);
    tree.root.reserve(2 * n + 1);
    for ( int i = n - 1; i >= 0; i-- )
    {
        int p = next[i];
        int v = tree.Add(version[i + 1], i, p, 1);
        version[i] = p == n ? v : tree.Splice(v, version[p + 1], p, n);
    }
    int answer = 0;
    while ( q-- )
    {
        int l, r;
        scanf("%d%d", &l, &r);
        l ^= answer;
        r ^= answer;
        answer = tree.Query(version[l - 1], r - 1, r);
        printf("%d\n", answer);
    }
}
