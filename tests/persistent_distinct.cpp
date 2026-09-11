#include "../src/compact/persistent_distinct.hpp"
#include "../src/classic/persistent_distinct.hpp"
#include <climits>
#include <iostream>
#include <random>
#include <set>
using ll = long long;

void check(const vector<ll> &a)
{
    PersistentDistinct dynamic(a);
    static Persistent_Distinct<64, 448> classic;
    classic.Init(a);
    int n = a.size();
    for (int l = 1; l <= n; l++)
    {
        set<ll> values;
        for (int r = l; r <= n; r++)
        {
            values.insert(a[r - 1]);
            int want = values.size();
            assert(dynamic.query(l, r) == want);
            assert(classic.Query(l, r) == want);
        }
    }
    for (int i = 0; i <= n; i++)
    {
        assert(dynamic.t[dynamic.root[i]].sum == i);
        assert(classic.t[classic.root[i]].sum == i);
    }
}

int main()
{
    vector<ll> alphabet{LLONG_MIN, 0, LLONG_MAX};
    for (int n = 1; n <= 8; n++)
    {
        int states = 1;
        for (int i = 0; i < n; i++)
            states *= 3;
        for (int code = 0; code < states; code++)
        {
            vector<ll> a(n);
            int x = code;
            for (ll &value : a)
            {
                value = alphabet[x % 3];
                x /= 3;
            }
            check(a);
        }
    }
    mt19937_64 rng(1972);
    for (int it = 0; it < 150; it++)
    {
        int n = 1 + rng() % 64;
        vector<ll> a(n);
        for (ll &value : a)
            value = ll(rng() % 30) - 15;
        check(a);
    }
    constexpr int n = 200000;
    static Persistent_Distinct<n, n * 19> large;
    for (int period : {1, 997, n})
    {
        vector<ll> a(n);
        for (int i = 0; i < n; i++)
            a[i] = i % period;
        PersistentDistinct dynamic(a);
        large.Init(a);
        assert(dynamic.t.size() <= size_t(n) * 19 + 1);
        assert(large.tot <= n * 19);
        for (int it = 0; it < 1000; it++)
        {
            int l = 1 + rng() % n;
            int r = l + rng() % (n - l + 1);
            int want = min(period, r - l + 1);
            assert(dynamic.query(l, r) == want);
            assert(large.Query(l, r) == want);
        }
    }
    large.Init({LLONG_MIN});
    assert(large.Query(1, 1) == 1 && large.tot == 1);
    cout << "Persistent distinct dual exhaustive set oracle, signed endpoints, reset and large arrays PASS\n";
}
