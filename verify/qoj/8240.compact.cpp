#include "../../src/compact/persistent_range.hpp"

int main()
{
    int n, q;
    scanf("%d%d", &n, &q);
    vector<int> a(n), next(n), last(n + 1, n), version(n + 1);
    for (auto &x : a) scanf("%d", &x);
    for (int i = n - 1; i >= 0; i--)
    {
        next[i] = last[a[i]];
        last[a[i]] = i;
    }
    PersistentRange tree(n);
    function<size_t(int, int, int, int)> nodes =
        [&](int l, int r, int ql, int qr) -> size_t
    {
        if (qr <= l || r <= ql) return 0;
        if (ql <= l && r <= qr) return 1;
        int m = l + (r - l) / 2;
        return 1 + nodes(l, m, ql, qr) + nodes(m, r, ql, qr);
    };
    size_t capacity = 1;
    for (int i = 0; i < n; i++)
    {
        capacity += nodes(0, n, i, next[i]);
        capacity += nodes(0, n, next[i], n);
    }
    tree.t.reserve(capacity);
    tree.root.reserve(2 * n + 1);
    for (int i = n - 1; i >= 0; i--)
    {
        int p = next[i];
        int v = tree.add(version[i + 1], i, p, 1);
        version[i] = p == n ? v : tree.splice(v, version[p + 1], p, n);
    }
    int answer = 0;
    while (q--)
    {
        int l, r;
        scanf("%d%d", &l, &r);
        l ^= answer;
        r ^= answer;
        answer = tree.query(version[l - 1], r - 1, r);
        printf("%d\n", answer);
    }
}
