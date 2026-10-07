#include "../src/compact/sequence_kth.hpp"
#include <stdexcept>

void require(bool ok)
{
    if (!ok)
        throw runtime_error("SequenceKth mismatch");
}

using ll = long long;
vector<pair<ll, int>> walk(const SequenceKth &t, int u, set<int> &seen)
{
    if (!u)
        return {};
    require(seen.insert(u).second);
    auto v = walk(t, t.a[u].l, seen);
    v.push_back({t.a[u].val, u});
    auto w = walk(t, t.a[u].r, seen);
    v.insert(v.end(), w.begin(), w.end());
    auto sorted = v;
    sort(sorted.begin(), sorted.end());
    vector<pair<ll, int>> keys(t.a[u].keys.begin(), t.a[u].keys.end());
    require(keys == sorted);
    require(t.a[u].sz == (int)v.size());
    require(4LL * max(t.a[t.a[u].l].sz, t.a[t.a[u].r].sz) <= 3LL * t.a[u].sz);
    return v;
}

void check(const SequenceKth &t, const vector<ll> &v, bool full)
{
    require(t.size() == (int)v.size());
    set<int> seen;
    auto got = walk(t, t.root, seen);
    require(seen.size() + 1 == t.a.size());
    for (int i = 0; i < (int)v.size(); i++)
        require(got[i].first == v[i]);
    if (!full)
        return;
    for (int l = 0; l < (int)v.size(); l++)
        for (int r = l; r < (int)v.size(); r++)
        {
            vector<ll> part(v.begin() + l, v.begin() + r + 1);
            sort(part.begin(), part.end());
            for (int k = 0; k < (int)part.size(); k++)
                require(t.kth(l + 1, r + 1, k + 1) == part[k]);
            for (ll x : {LLONG_MIN, -1LL, 0LL, 1LL, LLONG_MAX})
            {
                require(t.less(l + 1, r + 1, x) == lower_bound(part.begin(), part.end(), x) - part.begin());
                require(t.less(l + 1, r + 1, x, true) == upper_bound(part.begin(), part.end(), x) - part.begin());
            }
        }
}

int main()
{
    int scenarios = 0;
    for (int n = 0; n <= 5; n++)
        for (int mask = 0; mask < (1 << n); mask++)
        {
            vector<ll> v(n);
            for (int i = 0; i < n; i++)
                v[i] = mask >> i & 1;
            SequenceKth base(v);
            check(base, v, true);
            for (int k = 0; k <= n; k++)
                for (ll x : {LLONG_MIN, -1LL, 0LL, LLONG_MAX})
                {
                    auto t = base;
                    auto a = v;
                    t.insert(k, x);
                    a.insert(a.begin() + k, x);
                    check(t, a, true);
                    t.set(k + 1, x);
                    check(t, a, true);
                    t.set(k + 1, 1);
                    a[k] = 1;
                    check(t, a, true);
                    scenarios++;
                }
        }
    mt19937 rng(30652026);
    for (int trial = 0; trial < 30; trial++)
    {
        SequenceKth t;
        vector<ll> v;
        for (int step = 0; step < 300; step++)
        {
            ll x = (int)(rng() % 201) - 100;
            if (step % 17 == 0)
                x = LLONG_MIN;
            if (step % 19 == 0)
                x = LLONG_MAX;
            if (v.empty() || step % 3 == 0)
            {
                int k = rng() % (v.size() + 1);
                t.insert(k, x);
                v.insert(v.begin() + k, x);
            }
            else
            {
                int k = rng() % v.size();
                t.set(k + 1, x);
                v[k] = x;
            }
            check(t, v, false);
            int l = rng() % v.size();
            int r = rng() % v.size();
            if (l > r)
                swap(l, r);
            auto part = vector<ll>(v.begin() + l, v.begin() + r + 1);
            sort(part.begin(), part.end());
            int k = rng() % part.size();
            require(t.kth(l + 1, r + 1, k + 1) == part[k]);
        }
    }
    cout << scenarios << " exhaustive inserts and updates; 9000 random operations PASS\n";
}
