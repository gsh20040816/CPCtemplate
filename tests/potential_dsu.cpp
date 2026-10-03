#include "../src/compact/potential_dsu.hpp"
#include "../src/compact/dynamic_modint.hpp"

long long states = 0, queries = 0, accepted = 0, rejected = 0, swaps = 0;

struct Oracle
{
    long long mod;
    vector<vector<pair<int, long long>>> g;

    Oracle(int n, long long m) : mod(m), g(n) {}

    long long norm(long long x) const
    {
        if (!mod) return x;
        x %= mod;
        return x < 0 ? x + mod : x;
    }

    vector<optional<long long>> from(int u) const
    {
        vector<optional<long long>> d(g.size());
        queue<int> q;
        d[u] = 0;
        q.push(u);
        while (!q.empty())
        {
            int x = q.front();
            q.pop();
            for (auto [y, w] : g[x])
                if (!d[y])
                {
                    d[y] = norm(*d[x] + w);
                    q.push(y);
                }
        }
        return d;
    }

    bool add(int u, int v, long long w)
    {
        auto d = from(v);
        if (d[u] && *d[u] != norm(w)) return false;
        g[v].push_back({u, norm(w)});
        g[u].push_back({v, norm(-w)});
        return true;
    }
};

long long value(long long x) { return x; }

template <int tag> long long value(mint<tag> x) { return x.v; }

template <class T> void check(PotentialDSU<T> &d, const Oracle &g)
{
    states++;
    int n = g.g.size();
    for (int u = 0; u < n; u++)
    {
        auto expected = g.from(u);
        int count = 0;
        for (int v = 0; v < n; v++)
        {
            auto actual = d.diff(u, v);
            assert(bool(actual) == bool(expected[v]));
            if (actual) assert(value(*actual) == g.norm(-*expected[v]));
            count += bool(expected[v]);
            queries++;
        }
        assert(d.size(u) == count);
        int root = d.find(u);
        assert(d.fa[root] == root && value(d.d[root]) == 0);
    }
}

template <class T>
void explore(PotentialDSU<T> d, Oracle g, const vector<long long> &weights, int left)
{
    check(d, g);
    if (!left) return;
    int n = g.g.size();
    for (int u = 0; u < n; u++)
        for (int v = 0; v < n; v++)
            for (long long w : weights)
            {
                auto a = d;
                auto b = g;
                bool expect = b.add(u, v, w);
                if (a.find(u) != a.find(v) && a.size(u) < a.size(v)) swaps++;
                bool ok = a.merge(u, v, T(w));
                assert(ok == expect);
                (ok ? accepted : rejected)++;
                explore(a, b, weights, left - 1);
            }
}

template <class T> void random_test(long long mod)
{
    mt19937 rng(232);
    for (int trial = 0; trial < 100; trial++)
    {
        int n = 2 + rng() % 15;
        PotentialDSU<T> d(n);
        Oracle g(n, mod);
        for (int i = 0; i < 150; i++)
        {
            int u = rng() % n, v = rng() % n;
            long long w = int(rng() % 41) - 20;
            bool expect = g.add(u, v, w);
            assert(d.merge(u, v, T(w)) == expect);
            check(d, g);
        }
    }
}

template <class T> void large_test(long long mod)
{
    int n = 200000;
    auto norm = [&](long long x)
    {
        if (!mod) return x;
        x %= mod;
        return x < 0 ? x + mod : x;
    };
    PotentialDSU<T> d(n);
    // Balanced union rounds produce logarithmic parent depth before querying leaves.
    for (int step = 1; step < n; step *= 2)
        for (int u = 0; u + step < n; u += 2 * step)
            assert(d.merge(u, u + step, T(-7LL * step)));
    for (int u = 0; u < n; u++)
    {
        auto x = d.diff(u, n - 1);
        assert(x && value(*x) == norm(7LL * (u - n + 1)));
        assert(d.size(u) == n);
    }
    assert(d.merge(1, n - 1, T(7LL * (2 - n))));
    assert(!d.merge(1, n - 1, T(7LL * (2 - n) + 1)));
    assert(value(*d.diff(1, n - 1)) == norm(7LL * (2 - n)));
    PotentialDSU<T> chain(n);
    for (int u = 1; u < n; u++) assert(chain.merge(u - 1, u, T(1)));
    for (int u = n - 1; u >= 0; u--)
        assert(value(*chain.diff(0, u)) == norm(u));
}

int main()
{
    PotentialDSU<> empty(0);
    assert(empty.fa.empty() && empty.sz.empty() && empty.d.empty());
    {
        PotentialDSU<> d(6);
        Oracle g(6, 0);
        for (auto [u, v, w] : vector<tuple<int, int, long long>>{
                 {0,1,5}, {2,3,-7}, {4,2,11}, {1,3,4}, {0,4,5},
                 {4,0,-5}, {0,4,6}, {5,5,0}, {5,5,1}})
        {
            bool expected = g.add(u, v, w);
            assert(d.merge(u, v, w) == expected);
            check(d, g);
        }
        assert(*d.diff(0,3) == 9 && *d.diff(1,4) == 0);
        assert(*d.diff(0,4) == 5 && d.size(0) == 5);
        assert(!d.diff(5,0) && *d.diff(5,5) == 0);
    }
    explore(PotentialDSU<>(3), Oracle(3, 0), {-2,-1,0,1,2}, 3);
    using Z = mint<232>;
    for (int m : {1,2,3,4,6})
    {
        Z::set_mod(m);
        vector<long long> weights(m);
        iota(weights.begin(), weights.end(), 0);
        explore(PotentialDSU<Z>(3), Oracle(3, m), weights, m == 6 ? 2 : 3);
    }
    random_test<long long>(0);
    for (int m : {2,6,97})
    {
        Z::set_mod(m);
        random_test<Z>(m);
    }
    // Large signed values stay within the documented sufficient intermediate bound.
    for (int n : {2,5,31})
    for (int pattern : {0,1,2})
    {
        long long w = LLONG_MAX / (2LL * n + 1);
        PotentialDSU<> d(n);
        Oracle g(n, 0);
        for (int u = 1; u < n; u++)
        {
            long long x = pattern == 0 ? (u % 2 ? w : -w)
                        : pattern == 1 ? w : -w;
            assert(d.merge(u, u - 1, x) && g.add(u, u - 1, x));
            check(d, g);
        }
        assert(!d.merge(0, 0, 1));
        check(d, g);
    }
    using A = mint<233>;
    using B = mint<234>;
    A::set_mod(6);
    PotentialDSU<A> a(2);
    assert(a.merge(0,1,A(5)));
    B::set_mod(7);
    {
        PotentialDSU<B> b(2);
        assert(b.merge(0,1,B(6)));
    }
    B::set_mod(11); // The B-tag instance is gone; the A-tag instance stays valid.
    assert(a.diff(0,1)->v == 5 && !a.merge(0,1,A(4)));
    large_test<long long>(0);
    Z::set_mod(998244353);
    large_test<Z>(998244353);
    assert(accepted && rejected && swaps);
    cout << "Potential DSU: " << states << " graph states, " << queries
         << " full-pair differences; accepted=" << accepted << ", rejected=" << rejected
         << ", smaller-left-root=" << swaps
         << "; integer/modular groups, tag isolation and 200000-node cases PASS\n";
}
