#include "../src/compact/persistent_ordered_treap.hpp"
#include <algorithm>
#include <chrono>
#include <climits>
#include <iostream>
#include <string>

using ll = long long;
using Treap = PersistentOrderedTreap;

bool same(const Treap::Node &a, const Treap::Node &b)
{
    return a.val == b.val && a.pri == b.pri && a.l == b.l && a.r == b.r &&
           a.siz == b.siz && a.cnt == b.cnt;
}

int inspect(const Treap &a, int p, optional<ll> lo, optional<ll> hi)
{
    if (!p) return 0;
    const auto &u = a.t[p];
    assert(u.cnt > 0 && (!lo || *lo < u.val) && (!hi || u.val < *hi));
    assert(!u.l || a.t[u.l].pri <= u.pri);
    assert(!u.r || a.t[u.r].pri <= u.pri);
    int count = inspect(a, u.l, lo, u.val) + inspect(a, u.r, u.val, hi) + u.cnt;
    assert(count == u.siz);
    return count;
}

void verify(const Treap &a, int v, const vector<ll> &b)
{
    auto nodes = a.t.size(), capacity = a.t.capacity(), versions = a.root.size();
    assert(a.size(v) == (int)b.size());
    assert(inspect(a, a.root[v], nullopt, nullopt) == (int)b.size());
    for (int k = 1; k <= (int)b.size(); k++) assert(a.kth(v, k) == b[k - 1]);
    vector<ll> probes{LLONG_MIN, LLONG_MAX, -100, -1, 0, 1, 100};
    probes.insert(probes.end(), b.begin(), b.end());
    for (ll x : probes)
    {
        int l = lower_bound(b.begin(), b.end(), x) - b.begin();
        int r = upper_bound(b.begin(), b.end(), x) - b.begin();
        assert(a.less(v, x) == l && a.less(v, x, true) == r);
        assert(a.rank(v, x) == l + 1);
        optional<ll> before = l ? optional<ll>(b[l - 1]) : nullopt;
        optional<ll> after = r < (int)b.size() ? optional<ll>(b[r]) : nullopt;
        assert(a.prev(v, x) == before && a.next(v, x) == after);
    }
    assert(a.t.size() == nodes && a.t.capacity() == capacity && a.root.size() == versions);
}

void branching()
{
    for (int seed = 0; seed < 40; seed++)
    {
        Treap a(seed);
        mt19937_64 rng(seed + 81073);
        vector<vector<ll>> b(1);
        verify(a, 0, b[0]);
        for (int step = 0; step < 600; step++)
        {
            int v = step % 3 ? rng() % b.size() : b.size() - 1;
            ll x = (ll)(rng() % 17) - 8;
            if (step % 13 == 0) x = LLONG_MIN;
            if (step % 17 == 0) x = LLONG_MAX;
            vector<ll> next = b[v];
            auto saved = a.t;
            int id, op = rng() % 4;
            if (op < 2)
            {
                next.insert(lower_bound(next.begin(), next.end(), x), x);
                id = a.insert(v, x);
            }
            else if (op == 2)
            {
                auto it = lower_bound(next.begin(), next.end(), x);
                bool found = it != next.end() && *it == x;
                if (found) next.erase(it);
                id = a.erase(v, x);
                if (!found)
                    assert(a.t.size() == saved.size() && a.root[id] == a.root[v]);
            }
            else
            {
                id = a.copy(v);
                assert(a.t.size() == saved.size() && a.root[id] == a.root[v]);
            }
            assert(id == (int)b.size());
            b.push_back(next);
            for (size_t i = 0; i < saved.size(); i++) assert(same(saved[i], a.t[i]));
            verify(a, id, b[id]);
            for (int j = 0; j < 4; j++)
            {
                int old = rng() % b.size();
                verify(a, old, b[old]);
            }
        }
        for (int v = 0; v < (int)b.size(); v++) verify(a, v, b[v]);
    }
}

void exhaustive(Treap &a, int v, const vector<ll> &b, int depth)
{
    verify(a, v, b);
    if (!depth) return;
    for (ll x : {LLONG_MIN, 0LL, LLONG_MAX})
    {
        auto next = b;
        next.insert(lower_bound(next.begin(), next.end(), x), x);
        exhaustive(a, a.insert(v, x), next, depth - 1);
        next = b;
        auto it = lower_bound(next.begin(), next.end(), x);
        if (it != next.end() && *it == x) next.erase(it);
        exhaustive(a, a.erase(v, x), next, depth - 1);
    }
    exhaustive(a, a.copy(v), b, depth - 1);
    verify(a, v, b);
}

void deletion_paths()
{
    Treap a(92731);
    mt19937_64 rng(237419);
    vector<ll> keys(1500);
    for (int i = 0; i < (int)keys.size(); i++) keys[i] = i;
    shuffle(keys.begin(), keys.end(), rng);
    vector<vector<ll>> b(1);
    int v = 0;
    for (ll x : keys)
    {
        auto next = b.back();
        next.insert(lower_bound(next.begin(), next.end(), x), x);
        v = a.insert(v, x);
        b.push_back(next);
    }
    shuffle(keys.begin(), keys.end(), rng);
    for (ll x : keys)
    {
        auto next = b.back();
        next.erase(lower_bound(next.begin(), next.end(), x));
        auto saved = a.t;
        v = a.erase(v, x);
        b.push_back(next);
        for (size_t i = 0; i < saved.size(); i++) assert(same(saved[i], a.t[i]));
        if (v % 31 == 0) verify(a, v, b[v]);
    }
    for (int old = 0; old <= v; old += 37) verify(a, old, b[old]);
    verify(a, v, {});
}

void stress(const string &mode, int n, bool reserve)
{
    Treap a;
    if (reserve)
    {
        a.t.reserve(26ULL * n + 1);
        a.root.reserve(n + 1);
    }
    vector<ll> keys(n);
    for (int i = 0; i < n; i++) keys[i] = i;
    if (mode == "random")
    {
        mt19937_64 rng(9213);
        shuffle(keys.begin(), keys.end(), rng);
    }
    auto start = chrono::steady_clock::now();
    for (int i = 0; i < n; i++)
    {
        ll x = mode == "duplicates" ? 42 : keys[i];
        int v = a.insert(i, x);
        assert(v == i + 1 && a.size(v) == v && a.size(i) == i);
    }
    for (int v = 0; v <= n; v += 997)
    {
        assert(a.size(v) == v);
        if (v && mode != "random")
        {
            assert(a.kth(v, 1) == (mode == "duplicates" ? 42 : 0));
            assert(a.kth(v, v) == (mode == "duplicates" ? 42 : v - 1));
        }
    }
    auto nodes = a.t.size();
    for (int k = 1; k <= n; k++)
        assert(a.kth(n, k) == (mode == "duplicates" ? 42 : k - 1));
    assert(a.t.size() == nodes);
    double seconds = chrono::duration<double>(chrono::steady_clock::now() - start).count();
    cout << mode << ": operations=" << n << " nodes=" << nodes
         << " node_bytes=" << sizeof(Treap::Node) << " capacity_bytes="
         << a.t.capacity() * sizeof(Treap::Node) << " seconds=" << seconds << '\n';
}

int main(int argc, char **argv)
{
    if (argc > 1)
    {
        stress(argv[1], argc > 2 ? stoi(argv[2]) : 500000, argc > 3);
        return 0;
    }
    branching();
    deletion_paths();
    Treap a(713);
    exhaustive(a, 0, {}, 5);
    // Force pool growth on deep sequential versions, then delete all duplicates.
    Treap duplicates;
    for (int i = 0; i < 2000; i++) assert(duplicates.insert(i, LLONG_MIN) == i + 1);
    int v = 2000;
    for (int i = 2000; i > 0; i--)
    {
        v = duplicates.erase(v, LLONG_MIN);
        assert(duplicates.size(v) == i - 1 && duplicates.size(i) == i);
    }
    assert(!duplicates.prev(v, LLONG_MAX) && !duplicates.next(v, LLONG_MIN));
    cout << "Persistent ordered treap branching, exhaustive, immutable snapshots, extremes and allocation checks PASS\n";
}
