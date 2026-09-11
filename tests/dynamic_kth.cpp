#include "../src/compact/dynamic_kth.hpp"
#include "../src/classic/dynamic_kth.hpp"
#include <climits>
#include <functional>
#include <iostream>
#include <numeric>
#include <random>
using ll = long long;

template <class G>
void validate(const G &g, int allocated)
{
    vector<bool> seen(allocated + 1);
    function<int(int, int, int)> walk = [&](int p, int l, int r)
    {
        if (!p)
            return 0;
        assert(1 <= p && p <= allocated && !seen[p]);
        seen[p] = true;
        assert(g.t[p].sum > 0);
        if (l < r)
        {
            int m = (l + r) / 2;
            assert(g.t[p].sum == walk(g.t[p].l, l, m) + walk(g.t[p].r, m + 1, r));
        }
        return g.t[p].sum;
    };
    for (int i = 1; i <= g.n; i++)
        assert(walk(g.bit[i], 0, int(g.vals.size()) - 1) == (i & -i));
    for (int p = g.free_head; p; p = g.t[p].l)
    {
        assert(1 <= p && p <= allocated && !seen[p] && g.t[p].sum == 0);
        seen[p] = true;
    }
    for (int p = 1; p <= allocated; p++)
        assert(seen[p]);
}

int main()
{
    mt19937_64 rng(2617);
    vector<ll> domain{LLONG_MIN, LLONG_MAX, -7, -1, 0, 1, 7, 99};
    static Dynamic_Kth<40, 2000> classic;
    for (int trial = 0; trial < 100; trial++)
    {
        int n = 1 + rng() % 40;
        vector<ll> a(n);
        for (ll &x : a)
            x = domain[rng() % domain.size()];
        DynamicKth dynamic(a, domain);
        classic.Init(a, domain);
        for (int step = 0; step < 500; step++)
        {
            if (step % 2 == 0)
            {
                int pos = rng() % n;
                ll value = domain[rng() % domain.size()];
                dynamic.set(pos + 1, value);
                classic.Set(pos + 1, value);
                a[pos] = value;
            }
            int l = rng() % n;
            int r = l + rng() % (n - l);
            vector<ll> sorted(a.begin() + l, a.begin() + r + 1);
            sort(sorted.begin(), sorted.end());
            for (int k = 1; k <= int(sorted.size()); k++)
            {
                assert(dynamic.kth(l + 1, r + 1, k) == sorted[k - 1]);
                assert(classic.Kth(l + 1, r + 1, k) == sorted[k - 1]);
            }
            if (step % 20 == 0)
            {
                validate(dynamic, dynamic.t.size() - 1);
                validate(classic, classic.tot);
            }
        }
    }
    vector<ll> future(1000);
    iota(future.begin(), future.end(), 0);
    DynamicKth one({0}, future);
    Dynamic_Kth<1, 11> tiny;
    tiny.Init({0}, future);
    for (int it = 0; it < 5000; it++)
    {
        ll value = it % 1000;
        one.set(1, value);
        tiny.Set(1, value);
        assert(one.kth(1, 1, 1) == value && tiny.Kth(1, 1, 1) == value);
        assert(one.t.size() <= 12 && tiny.tot <= 11);
        validate(one, one.t.size() - 1);
        validate(tiny, tiny.tot);
    }
    constexpr int n = 30000;
    vector<ll> a(n), next(n);
    iota(a.begin(), a.end(), 0);
    iota(next.begin(), next.end(), n);
    DynamicKth dynamic(a, next);
    static Dynamic_Kth<n, 5000000> large;
    large.Init(a, next);
    for (int i = 1; i <= n; i++)
    {
        dynamic.set(i, 2 * n - i);
        large.Set(i, 2 * n - i);
    }
    for (int k : {1, 2, n / 2, n - 1, n})
    {
        assert(dynamic.kth(1, n, k) == n + k - 1);
        assert(large.Kth(1, n, k) == n + k - 1);
    }
    validate(dynamic, dynamic.t.size() - 1);
    validate(large, large.tot);
    size_t copies = 0;
    for (int i = 1; i <= n; i++)
        copies += i & -i;
    assert(dynamic.t.size() <= copies * 17 + 1);
    assert(size_t(large.tot) <= copies * 17);
    large.Init({7, 7, 7});
    assert(large.Kth(1, 3, 2) == 7);
    assert(large.tot == 3);
    cout << "Dynamic kth dual sorted-slice oracle, recycling ownership, reset and large updates PASS\n";
}
