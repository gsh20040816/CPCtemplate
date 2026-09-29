#include "../src/compact/scapegoat_tree.hpp"
#include <climits>
#include <iostream>
#include <random>
#include <tuple>

using ll = long long;

tuple<int, int, int>
audit(const ScapegoatTree &t, int p, optional<ll> low = {}, optional<ll> high = {})
{
    if (!p) return {0, 0, 0};
    const auto &a = t.a[p];
    assert(!low || *low < a.value);
    assert(!high || a.value < *high);
    auto [ls, ln, lv] = audit(t, a.l, low, a.value);
    auto [rs, rn, rv] = audit(t, a.r, a.value, high);
    assert(a.count >= 0);
    assert(a.size == ls + rs + a.count);
    assert(a.nodes == ln + rn + 1);
    assert(a.live == lv + rv + (a.count > 0));
    assert(4LL * max(ln, rn) <= 3LL * a.nodes);
    assert(2LL * a.live >= a.nodes);
    return {a.size, a.nodes, a.live};
}

void check(const ScapegoatTree &t, const vector<ll> &v, ll x)
{
    int lower = lower_bound(v.begin(), v.end(), x) - v.begin();
    int upper = upper_bound(v.begin(), v.end(), x) - v.begin();
    assert(t.size() == int(v.size()));
    assert(t.rank(x) == lower + 1);
    assert(t.less(x, true) == upper);
    optional<ll> before, after;
    if (lower) before = v[lower - 1];
    if (upper < int(v.size())) after = v[upper];
    assert(t.prev(x) == before && t.next(x) == after);
}

int main()
{
    mt19937_64 rng(110);
    for (int test = 0; test < 300; test++)
    {
        ScapegoatTree t;
        vector<ll> v;
        for (int step = 0; step < 2000; step++)
        {
            ll x = ll(rng() % 201) - 100;
            if (step % 29 == 0) x = LLONG_MIN;
            if (step % 31 == 0) x = LLONG_MAX;
            auto it = lower_bound(v.begin(), v.end(), x);
            if (rng() % 2)
            {
                t.insert(x);
                v.insert(it, x);
            }
            else
            {
                bool found = it != v.end() && *it == x;
                assert(t.erase(x) == found);
                if (found) v.erase(it);
            }
            check(t, v, x);
            check(t, v, LLONG_MIN);
            check(t, v, LLONG_MAX);
            if (!v.empty())
            {
                int k = rng() % v.size();
                assert(t.kth(k + 1) == v[k]);
            }
            if (step % 37 == 0) audit(t, t.root);
        }
        for (int k = 0; k < int(v.size()); k++) assert(t.kth(k + 1) == v[k]);
        for (ll x : v) assert(t.erase(x));
        assert(t.root == 0 && t.size() == 0);
        assert(!t.erase(0) && t.rank(0) == 1);
    }
    ScapegoatTree t;
    int n = 200000;
    for (int i = 0; i < n; i++) t.insert(i);
    assert(t.a.size() == size_t(n + 1));
    audit(t, t.root);
    for (int i = 0; i < n; i += 2) assert(t.erase(i));
    audit(t, t.root);
    for (int k = 1; k <= n / 2; k++) assert(t.kth(k) == 2 * k - 1);
    for (int i = n - 1; i >= 1; i -= 2) assert(t.erase(i));
    assert(t.root == 0);
    for (int i = n; i; i--) t.insert(i);
    audit(t, t.root);
    for (int i = 0; i < n; i++) t.insert(LLONG_MIN);
    for (int i = 0; i < n; i++) assert(t.erase(LLONG_MIN));
    audit(t, t.root);
    assert(t.rank(1) == 1 && t.size() == n);
    cout << "ScapegoatTree: 600000 sorted-vector operations, signed64 bounds, "
            "recursive BST/balance/density/count audit, 200000 monotone "
            "insert/delete/reinsert and duplicates PASS\n";
}
