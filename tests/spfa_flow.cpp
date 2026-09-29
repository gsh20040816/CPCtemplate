#include "../src/compact/spfa_flow.hpp"
#include "../src/compact/flow.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using B = boost::multiprecision::cpp_int;
using I = __int128_t;

struct Arc
{
    int u, v, cap;
    long long cost;
};

vector<optional<B>> enumerate(int n, const vector<Arc> &e)
{
    int upper = 0;
    for (auto a : e) upper += a.cap;
    vector<optional<B>> ans(upper + 1);
    vector<int> bal(n + 1);
    function<void(int, B)> visit = [&](int i, B cost)
    {
        if (i == (int)e.size())
        {
            for (int u = 2; u < n; u++)
                if (bal[u]) return;
            int f = -bal[1];
            if (f < 0 || bal[n] != f) return;
            if (!ans[f] || cost < *ans[f]) ans[f] = cost;
            return;
        }
        auto a = e[i];
        for (int f = 0; f <= a.cap; f++)
        {
            bal[a.u] -= f;
            bal[a.v] += f;
            visit(i + 1, cost + B(f) * a.cost);
            bal[a.u] += f;
            bal[a.v] -= f;
        }
    };
    visit(0, 0);
    while (!ans.back()) ans.pop_back();
    for (auto a : ans) assert(a);
    return ans;
}

template <class Flow> void certificate(Flow &g, long long f, I cost)
{
    vector<B> bal(g.n + 1);
    B total = 0;
    for (int i = 0; i < (int)g.e.size(); i += 2)
    {
        auto a = g.e[i];
        long long used = g.used(i);
        assert(0 <= used && used <= a.initial);
        assert(g.e[i ^ 1].cap == used);
        bal[a.from] -= used;
        bal[a.to] += used;
        total += B(used) * a.cost;
    }
    assert(bal[1] == -B(f) && bal[g.n] == B(f) && total == B(cost));
    for (int u = 2; u < g.n; u++) assert(bal[u] == 0);
}

template <class Flow> void check(int n, const vector<Arc> &e, int limit)
{
    auto want = enumerate(n, e);
    Flow g(n);
    for (auto a : e) g.add(a.u, a.v, a.cap, a.cost);
    assert(g.flow(1, n, 0) == make_pair(0LL, I(0)));
    auto [f, c] = g.flow(1, n, limit);
    assert(f == min(limit, (int)want.size() - 1));
    assert(B(c) == *want[f]);
    certificate(g, f, c);
    auto [more, extra] = g.flow(1, n);
    assert(f + more == (int)want.size() - 1);
    assert(B(c) + extra == *want.back());
    certificate(g, f + more, c + extra);
    assert(g.flow(1, n) == make_pair(0LL, I(0)));
}

template <class Flow> void extra_checks()
{
    // The second augmentation must cancel edge 2->3.
    Flow cancel(4);
    cancel.add(1, 2, 1, 0);
    int id = cancel.add(2, 3, 1, -5);
    cancel.add(3, 4, 1, 0);
    cancel.add(1, 3, 1, 0);
    cancel.add(2, 4, 1, 0);
    assert(cancel.flow(1, 4, 1) == make_pair(1LL, I(-5)));
    assert(cancel.used(id) == 1);
    assert(cancel.flow(1, 4) == make_pair(1LL, I(5)));
    assert(cancel.used(id) == 0);
    certificate(cancel, 2, 0);
    for (bool disconnected : {false, true})
        for (int length : {1, 2, 5})
        {
            Flow g(8);
            int start = disconnected ? 2 : 1;
            for (int i = 0; i < length; i++)
                g.add(start + i, start + (i + 1) % length, 1, i ? 0 : -1);
            bool rejected = false;
            try
            {
                g.flow(1, 8);
            }
            catch (const invalid_argument &)
            {
                rejected = true;
            }
            assert(rejected);
            for (int i = 0; i < (int)g.e.size(); i += 2) assert(g.used(i) == 0);
        }
    Flow big(3);
    big.add(1, 2, 1000000000LL, LLONG_MAX);
    big.add(2, 3, 1000000000LL, LLONG_MAX);
    auto result = big.flow(1, 3);
    assert(result == make_pair(1000000000LL, I(2000000000LL) * LLONG_MAX));
    certificate(big, result.first, result.second);
    Flow capacity(2);
    capacity.add(1, 2, LLONG_MAX, -1);
    assert(capacity.flow(1, 2, LLONG_MAX - 1) ==
           make_pair(LLONG_MAX - 1, -I(LLONG_MAX - 1)));
    assert(capacity.flow(1, 2) == make_pair(1LL, I(-1)));
    certificate(capacity, LLONG_MAX, -I(LLONG_MAX));
    Flow chain(5000);
    for (int u = 4999; u >= 1; u--) chain.add(u, u + 1, 1, -1);
    assert(chain.flow(1, 5000) == make_pair(1LL, I(-4999)));
    certificate(chain, 1, -4999);
}

int main()
{
    mt19937 rng(20260929);
    for (int test = 0; test < 4000; test++)
    {
        int n = 2 + rng() % 4;
        vector<long long> h(n + 1);
        for (auto &x : h) x = (int(rng() % 21) - 10) * 10000000000000000LL;
        vector<Arc> e;
        for (int i = 0; i < 7; i++)
        {
            int u = rng() % n + 1, v = rng() % n + 1;
            long long c = rng() % 4 + h[v] - h[u];
            e.push_back({u, v, int(rng() % 3), c});
        }
        int limit = rng() % 8;
        check<SpfaFlow>(n, e, limit);
        check<MinCostFlow>(n, e, limit);
    }
    extra_checks<SpfaFlow>();
    extra_checks<MinCostFlow>();
    cout << "SPFA and potential min-cost flow: 4000 cpp_int exhaustive feasible-flow "
            "oracles, residual certificates, limits/continuation, forced cancellation, "
            "global negative-cycle rejection, int64 capacity and long-path int128 "
            "costs PASS\n";
}
