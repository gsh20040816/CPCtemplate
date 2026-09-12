#include "../src/compact/ordered_set.hpp"

int main()
{
    ost<long long> s;
    vector<long long> a;
    mt19937_64 rng(23657);
    for (int t = 0; t < 30000; t++)
    {
        long long x = (long long)(rng() % 2000) - 1000;
        if (t % 11 == 0) x = LLONG_MIN;
        if (t % 13 == 0) x = LLONG_MAX;
        auto it = lower_bound(a.begin(), a.end(), x);
        bool has = it != a.end() && *it == x;
        if (rng() % 2)
        {
            assert(s.insert(x).second == !has);
            if (!has) a.insert(it, x);
        }
        else
        {
            assert(s.erase(x) == has);
            if (has) a.erase(it);
        }
        assert(s.size() == a.size());
        assert(s.order_of_key(x) ==
               size_t(lower_bound(a.begin(), a.end(), x) - a.begin()));
        auto lo = s.lower_bound(x), hi = s.upper_bound(x);
        auto l = lower_bound(a.begin(), a.end(), x),
             r = upper_bound(a.begin(), a.end(), x);
        assert((lo == s.end()) == (l == a.end()));
        assert((hi == s.end()) == (r == a.end()));
        if (l != a.end()) assert(*lo == *l);
        if (r != a.end()) assert(*hi == *r);
        int k = rng() % (a.size() + 2);
        auto z = s.find_by_order(k);
        assert((z == s.end()) == (k >= int(a.size())));
        if (k < int(a.size())) assert(*z == a[k]);
    }
    ost<pair<long long, int>> m;
    vector<long long> b;
    for (int id = 1; id <= 10000; id++)
    {
        long long x = rng() % 30;
        m.insert({x, id});
        b.insert(upper_bound(b.begin(), b.end(), x), x);
        assert(m.order_of_key({x, 0}) ==
               size_t(lower_bound(b.begin(), b.end(), x) - b.begin()));
        assert(m.order_of_key({x, INT_MAX}) ==
               size_t(upper_bound(b.begin(), b.end(), x) - b.begin()));
    }
    for (int i = 0; i < int(b.size()); i++) assert(m.find_by_order(i)->first == b[i]);
    ost<int, greater<int>> rev;
    for (int i = 0; i < 500000; i++) rev.insert(i);
    for (int i = 0; i < 500000; i++)
    {
        assert(*rev.find_by_order(i) == 499999 - i);
        assert(rev.order_of_key(i) == 499999 - i);
    }
    cout << "PBDS ost sorted-vector oracle, duplicates by pair, bounds, reverse "
            "comparator and 500000 ordered keys PASS\n";
}
