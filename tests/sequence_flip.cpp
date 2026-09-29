#include "../src/compact/treap.hpp"
#include <algorithm>
#include <iostream>
#include <numeric>

int audit(SequenceTreap &t, int p)
{
    if (!p) return 0;
    t.push(p);
    int l = t.a[p].l, r = t.a[p].r;
    assert(!l || t.a[p].pri >= t.a[l].pri);
    assert(!r || t.a[p].pri >= t.a[r].pri);
    int size = audit(t, l) + audit(t, r) + 1;
    assert(t.a[p].siz == size);
    assert(t.a[p].sum == t.a[l].sum + t.a[p].val + t.a[r].sum);
    return size;
}

int main()
{
    for (int n = 1; n <= 7; n++)
        for (int mask = 0; mask < (1 << n); mask++)
            for (int l = 1; l <= n; l++)
                for (int r = l; r <= n; r++)
                {
                    SequenceTreap t(mask + n);
                    vector<long long> v(n);
                    for (int i = 0; i < n; i++) t.insert(i, v[i] = mask >> i & 1);
                    t.flip_bits(l, r);
                    for (int i = l - 1; i < r; i++) v[i] ^= 1;
                    assert(t.values() == v);
                    assert(t.query(1, n) == accumulate(v.begin(), v.end(), 0LL));
                    t.flip_bits(l, r);
                    for (int i = 0; i < n; i++)
                        assert(t.query(i + 1, i + 1) == (mask >> i & 1));
                    audit(t, t.root);
                }
    mt19937 rng(109);
    for (int test = 0; test < 500; test++)
    {
        SequenceTreap t(test);
        vector<long long> v;
        for (int step = 0; step < 1000; step++)
        {
            int n = v.size(), op = rng() % 6;
            if (!n || op == 0)
            {
                int k = rng() % (n + 1), bit = rng() % 2;
                t.insert(k, bit);
                v.insert(v.begin() + k, bit);
                continue;
            }
            int l = rng() % n, r = rng() % n;
            if (l > r) swap(l, r);
            if (op == 1)
            {
                t.flip_bits(l + 1, r + 1);
                for (int i = l; i <= r; i++) v[i] ^= 1;
            }
            else if (op == 2)
            {
                t.reverse(l + 1, r + 1);
                reverse(v.begin() + l, v.begin() + r + 1);
            }
            else if (op == 3)
            {
                t.erase(l + 1, r + 1);
                v.erase(v.begin() + l, v.begin() + r + 1);
            }
            else if (op == 4)
            {
                // Add is noncommutative with pending negation; remain binary.
                long long delta = v[l] ? -1 : 1;
                t.add(l + 1, l + 1, delta);
                v[l] += delta;
            }
            else
                assert(t.query(l + 1, r + 1) ==
                       accumulate(v.begin() + l, v.begin() + r + 1, 0LL));
            if (step % 31 == 0)
            {
                assert(t.values() == v);
                audit(t, t.root);
            }
        }
        assert(t.values() == v);
    }
    SequenceTreap t;
    int n = 200000;
    for (int i = 0; i < n; i++) t.insert(i, i % 2);
    for (int i = 0; i < 10000; i++)
    {
        t.flip_bits(1, n);
        t.reverse(1, n);
        assert(t.query(1, n) == n / 2);
    }
    auto v = t.values();
    for (int i = 0; i < n; i++) assert(v[i] == i % 2);
    audit(t, t.root);
    cout << "Sequence bit flip: exhaustive binary intervals through n=7, 500000 mixed "
            "operations, independent vector and heap invariants, 200000 nodes PASS\n";
}
