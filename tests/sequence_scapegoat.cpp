#include "../src/compact/sequence_scapegoat.hpp"
#include <climits>
#include <iostream>
#include <random>
#include <set>
#include <stdexcept>

void require(bool ok)
{
    if (!ok)
        throw runtime_error("sequence scapegoat mismatch");
}

using ll = long long;
vector<ll> walk(const SequenceScapegoat &t, int u, set<int> &seen)
{
    if (!u)
        return {};
    require(seen.insert(u).second);
    auto v = walk(t, t.a[u].l, seen);
    if (t.a[u].live)
        v.push_back(t.a[u].val);
    auto w = walk(t, t.a[u].r, seen);
    v.insert(v.end(), w.begin(), w.end());
    map<ll, int> freq;
    for (ll x : v)
        freq[x]++;
    require(freq == t.a[u].freq);
    require((int)v.size() == t.a[u].sz);
    int nodes = t.a[t.a[u].l].cnt + t.a[t.a[u].r].cnt + 1;
    require(nodes == t.a[u].cnt);
    require(4LL * max(t.a[t.a[u].l].cnt, t.a[t.a[u].r].cnt) <= 3LL * nodes);
    require(2LL * t.a[u].sz >= nodes);
    return v;
}

void check(const SequenceScapegoat &t, const vector<ll> &v, bool all)
{
    require(t.size() == (int)v.size());
    set<int> seen;
    require(walk(t, t.root, seen) == v);
    for (int u : t.spare)
    {
        require(u != 0 && seen.insert(u).second);
        require(t.a[u].freq.empty() && t.a[u].cnt == 0);
    }
    require(seen.size() + 1 == t.a.size());
    if (!all)
        return;
    for (int l = 0; l < (int)v.size(); l++)
        for (int r = l; r < (int)v.size(); r++)
            for (ll x : {LLONG_MIN, -1LL, 0LL, 1LL, 2LL, LLONG_MAX})
                require(t.count(l + 1, r + 1, x) == std::count(v.begin() + l, v.begin() + r + 1, x));
}

int main()
{
    int scenarios = 0;
    for (int n = 0; n <= 7; n++)
        for (int mask = 0; mask < (1 << n); mask++)
        {
            vector<ll> v(n);
            for (int i = 0; i < n; i++)
                v[i] = mask >> i & 1;
            SequenceScapegoat original(v);
            check(original, v, true);
            for (int k = 0; k <= n; k++)
                for (ll x : {LLONG_MIN, -1LL, 0LL, 1LL, LLONG_MAX})
                {
                    auto t = original;
                    auto a = v;
                    t.insert(k, x);
                    a.insert(a.begin() + k, x);
                    check(t, a, true);
                    require(t.erase(k + 1) == x);
                    check(t, v, true);
                    scenarios++;
                }
            for (int l = 0; l < n; l++)
                for (int r = l; r < n; r++)
                {
                    auto t = original;
                    auto a = v;
                    t.rotate(l + 1, r + 1);
                    std::rotate(a.begin() + l, a.begin() + r, a.begin() + r + 1);
                    check(t, a, true);
                    scenarios++;
                }
        }
    mt19937 rng(4552026);
    SequenceScapegoat t;
    vector<ll> v;
    for (int step = 0; step < 30000; step++)
    {
        int op = rng() % 4;
        if (v.empty() || (op == 0 && v.size() < 150))
        {
            int k = rng() % (v.size() + 1);
            ll x = (int)(rng() % 17) - 8;
            t.insert(k, x);
            v.insert(v.begin() + k, x);
        }
        else if (op == 1)
        {
            int k = rng() % v.size();
            require(t.erase(k + 1) == v[k]);
            v.erase(v.begin() + k);
        }
        else
        {
            int l = rng() % v.size();
            int r = rng() % v.size();
            if (l > r)
                swap(l, r);
            if (op == 2)
            {
                t.rotate(l + 1, r + 1);
                std::rotate(v.begin() + l, v.begin() + r, v.begin() + r + 1);
            }
            else
            {
                ll x = (int)(rng() % 19) - 9;
                require(t.count(l + 1, r + 1, x) == std::count(v.begin() + l, v.begin() + r + 1, x));
            }
        }
        check(t, v, step % 2000 == 0);
    }
    while (!v.empty())
    {
        require(t.erase(1) == v.front());
        v.erase(v.begin());
        check(t, v, false);
    }
    auto capacity = t.a.size();
    for (int i = 0; i < 10000; i++)
    {
        t.insert(0, i);
        require(t.erase(1) == i);
    }
    require(t.a.size() == capacity);
    check(t, {}, true);
    cout << scenarios << " exhaustive modifications; 30000 random operations; recycling PASS\n";
}
