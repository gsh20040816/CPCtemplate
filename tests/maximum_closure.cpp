#include "../src/compact/maximum_closure.hpp"
#include "../src/classic/maximum_closure.hpp"
#include <iostream>
#include <random>
#include <pthread.h>
using ll = long long;
using I = __int128_t;

void certificate(const vector<ll> &w, const vector<pair<int, int>> &edges,
                 const pair<ll, vector<int>> &answer, I want)
{
    assert(answer.first == want);
    vector<bool> selected(w.size() + 1);
    I total = 0;
    for (int u : answer.second)
    {
        assert(1 <= u && u <= int(w.size()) && !selected[u]);
        selected[u] = true;
        total += w[u - 1];
    }
    for (auto [u, v] : edges)
        assert(!selected[u] || selected[v]);
    assert(total == want);
}

void check(const vector<ll> &w, const vector<pair<int, int>> &edges)
{
    I best = 0;
    for (int mask = 0; mask < (1 << w.size()); mask++)
    {
        bool ok = true;
        for (auto [u, v] : edges)
            if ((mask >> (u - 1) & 1) && !(mask >> (v - 1) & 1))
                ok = false;
        if (!ok)
            continue;
        I total = 0;
        for (int i = 0; i < int(w.size()); i++)
            if (mask >> i & 1)
                total += w[i];
        best = max(best, total);
    }
    static Network_Flow<12, 220> graph;
    certificate(w, edges, maximum_closure(w, edges), best);
    certificate(w, edges, Maximum_Closure(w, edges, graph), best);
}

void run_tests()
{
    for (int n = 0; n <= 3; n++)
    {
        int weight_states = 1;
        for (int i = 0; i < n; i++)
            weight_states *= 3;
        for (int code = 0; code < weight_states; code++)
        {
            vector<ll> w(n);
            int x = code;
            for (ll &a : w)
            {
                a = vector<ll>{-2, 0, 3}[x % 3];
                x /= 3;
            }
            for (int mask = 0; mask < (1 << (n * n)); mask++)
            {
                vector<pair<int, int>> edges;
                for (int i = 0; i < n; i++)
                    for (int j = 0; j < n; j++)
                        if (mask >> (i * n + j) & 1)
                            edges.push_back({i + 1, j + 1});
                check(w, edges);
            }
        }
    }
    mt19937_64 rng(4174);
    for (int it = 0; it < 1000; it++)
    {
        int n = 1 + rng() % 9;
        vector<ll> w(n);
        for (ll &a : w)
            a = ll(rng() % 41) - 20;
        vector<pair<int, int>> edges;
        for (int j = 0; j < 25; j++)
            edges.push_back({1 + rng() % n, 1 + rng() % n});
        check(w, edges);
    }
    check({LLONG_MAX - 1, LLONG_MIN}, {});
    check({LLONG_MAX - 1, LLONG_MIN}, {{1, 2}});
    check({LLONG_MAX - 1, -1}, {{1, 2}, {2, 1}});
    check({LLONG_MAX / 2, LLONG_MAX / 2, LLONG_MIN}, {{1, 3}, {2, 3}});
    check({0, LLONG_MIN, -1}, {{1, 2}, {2, 3}, {3, 1}});
    constexpr int n = 100000;
    vector<ll> w(n);
    w[0] = 7;
    w[n - 1] = -3;
    vector<pair<int, int>> edges;
    for (int i = 1; i < n; i++)
        edges.push_back({i, i + 1});
    auto result = maximum_closure(w, edges);
    certificate(w, edges, result, 4);
    assert(result.second.size() == n);
    static Network_Flow<n + 2, n + 2> graph;
    result = Maximum_Closure(w, edges, graph);
    certificate(w, edges, result, 4);
    assert(result.second.size() == n);
    cout << "Maximum closure dual exhaustive subsets, solution certificates, int64 negatives and recursive chain PASS\n";
}

void *entry(void *)
{
    run_tests();
    return nullptr;
}

int main()
{
    pthread_attr_t attr;
    assert(pthread_attr_init(&attr) == 0);
    assert(pthread_attr_setstacksize(&attr, 256ULL << 20) == 0);
    pthread_t worker;
    assert(pthread_create(&worker, &attr, entry, nullptr) == 0);
    assert(pthread_attr_destroy(&attr) == 0);
    assert(pthread_join(worker, nullptr) == 0);
}
