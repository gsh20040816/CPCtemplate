#include "../src/compact/flow.hpp"

using I = __int128_t;

struct Edge
{
    int u, v, cap, cost;
};

vector<long long> brute(int n, const vector<Edge> &e)
{
    vector<long long> ans(30, LLONG_MAX);
    vector<int> bal(n + 1);
    function<void(int, long long)> dfs = [&](int i, long long cost)
    {
        if (i == int(e.size()))
        {
            for (int u = 2; u < n; u++)
                if (bal[u]) return;
            int f = -bal[1];
            if (f >= 0 && bal[n] == f) ans[f] = min(ans[f], cost);
            return;
        }
        auto [u, v, cap, c] = e[i];
        for (int f = 0; f <= cap; f++)
        {
            bal[u] -= f;
            bal[v] += f;
            dfs(i + 1, cost + f * c);
            bal[u] += f;
            bal[v] -= f;
        }
    };
    dfs(0, 0);
    while (ans.back() == LLONG_MAX) ans.pop_back();
    return ans;
}

void verify(const vector<pair<long long, I>> &s,
            const vector<long long> &cost,
            int offset,
            int limit)
{
    assert(s.front() == make_pair(0LL, I(0)));
    assert(s.back().first == min(limit, int(cost.size()) - 1 - offset));
    optional<I> old;
    for (int i = 1; i < int(s.size()); i++)
    {
        auto [a, x] = s[i - 1];
        auto [b, y] = s[i];
        assert(a < b);
        assert((y - x) % (b - a) == 0);
        I unit = (y - x) / (b - a);
        if (old) assert(*old < unit);
        old = unit;
        for (int f = a; f <= b; f++)
            assert(x + (f - a) * unit == I(cost[offset + f]) - cost[offset]);
    }
}

int main()
{
    mt19937 rng(19371);
    for (int t = 0; t < 5000; t++)
    {
        int n = 2 + rng() % 4;
        vector<int> pot(n + 1);
        for (int &x : pot) x = int(rng() % 9) - 4;
        vector<Edge> e;
        MinCostFlow g(n), h(n);
        for (int i = 0; i < 7; i++)
        {
            int u = rng() % n + 1, v = rng() % n + 1;
            int cap = rng() % 3, c = rng() % 4 + pot[v] - pot[u];
            e.push_back({u, v, cap, c});
            g.add(u, v, cap, c);
            h.add(u, v, cap, c);
        }
        auto cost = brute(n, e);
        int limit = rng() % 10;
        auto s = g.slope(1, n, limit);
        verify(s, cost, 0, limit);
        auto one = h.flow(1, n, limit);
        assert(one == s.back());
        int offset = s.back().first;
        auto rest = g.slope(1, n);
        verify(rest, cost, offset, 100);
    }
    MinCostFlow g(2);
    g.add(1, 2, 1000000000LL, 1000000000000000000LL);
    g.add(1, 2, 1000000000LL, 1000000000000000000LL);
    auto s = g.slope(1, 2);
    assert(s.size() == 2);
    assert(s.back() ==
           make_pair(2000000000LL, I(2000000000LL) * 1000000000000000000LL));
    assert(g.slope(1, 2).size() == 1);
    MinCostFlow bad(2);
    bad.add(1, 1, 1, -1);
    bool rejected = false;
    try
    {
        bad.slope(1, 2);
    }
    catch (const invalid_argument &)
    {
        rejected = true;
    }
    assert(rejected);
    cout << "Min-cost slope: exhaustive feasible-flow costs, negative edges without "
            "negative cycles, ties, limits, continuation and int128 totals PASS\n";
}
