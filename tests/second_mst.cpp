#include <bits/stdc++.h>
#include <pthread.h>
#include "../src/compact/second_mst.hpp"
using namespace std;
using I = __int128_t;
using E = SecondMST::Edge;
mt19937_64 rng(2026093001);
int checked = 0;

bool connected(int n, const vector<E> &e, unsigned mask)
{
    vector<vector<int>> g(n);
    for (int i = 0; i < (int)e.size(); i++)
        if (mask >> i & 1)
        {
            g[e[i].u].push_back(e[i].v);
            g[e[i].v].push_back(e[i].u);
        }
    vector<int> queue{0}, seen(n);
    seen[0] = 1;
    for (int k = 0; k < (int)queue.size(); k++)
        for (int v : g[queue[k]])
            if (!seen[v])
            {
                seen[v] = 1;
                queue.push_back(v);
            }
    return (int)queue.size() == n;
}

void check(int n, const vector<E> &e)
{
    vector<pair<I, unsigned>> trees;
    for (unsigned mask = 0; mask < (1U << e.size()); mask++)
        if (popcount(mask) == n - 1 && connected(n, e, mask))
        {
            I sum = 0;
            for (int i = 0; i < (int)e.size(); i++)
                if (mask >> i & 1) sum += (I)e[i].w;
            trees.push_back({sum, mask});
        }
    sort(trees.begin(), trees.end());
    SecondMST mst(n);
    for (int i = 0; i < (int)e.size(); i++)
        assert(mst.add(e[i].u, e[i].v, e[i].w) == i);
    for (bool strict : {true, false, true})
    {
        auto ans = mst.solve(strict);
        assert(ans.connected == !trees.empty());
        if (trees.empty())
        {
            assert(ans.weight == 0 && ans.tree.empty() && !ans.next);
            assert(ans.in == -1 && ans.out == -1);
            continue;
        }
        unsigned mask = 0;
        I sum = 0;
        for (int id : ans.tree)
        {
            assert(0 <= id && id < (int)e.size() && !(mask >> id & 1));
            mask |= 1U << id;
            sum += (I)e[id].w;
        }
        assert(popcount(mask) == n - 1 && connected(n, e, mask));
        assert(ans.weight == sum && sum == trees[0].first);
        optional<I> best;
        for (auto [w, set] : trees)
            if ((strict ? w > sum : set != mask) && (!best || w < *best)) best = w;
        assert(ans.next == best);
        if (!best)
            assert(ans.in == -1 && ans.out == -1);
        else
        {
            assert(0 <= ans.in && ans.in < (int)e.size());
            assert(0 <= ans.out && ans.out < (int)e.size());
            assert(!(mask >> ans.in & 1) && (mask >> ans.out & 1));
            unsigned next = mask ^ (1U << ans.in) ^ (1U << ans.out);
            assert(connected(n, e, next) && popcount(next) == n - 1);
            assert(sum + (I)e[ans.in].w - (I)e[ans.out].w == *best);
        }
    }
    checked++;
}

void all()
{
    for (int n = 1; n <= 4; n++)
    {
        vector<pair<int, int>> pairs;
        for (int u = 0; u < n; u++)
            for (int v = u + 1; v < n; v++) pairs.push_back({u, v});
        for (int code = 0; code < (1 << (2 * pairs.size())); code++)
        {
            int x = code;
            vector<E> e;
            for (auto [u, v] : pairs)
            {
                if (x % 4) e.push_back({u, v, x % 4 - 2});
                x /= 4;
            }
            check(n, e);
        }
    }
    for (int t = 0; t < 2200; t++)
    {
        int n = 1 + rng() % 7, m = rng() % 13;
        vector<E> e;
        for (int i = 0; i < m; i++)
        {
            long long w = (long long)(rng() % 11) - 5;
            if (t % 4 == 0) w = rng() & 1 ? LLONG_MIN : LLONG_MAX;
            e.push_back({(int)(rng() % n), (int)(rng() % n), w});
        }
        check(n, e);
    }
    check(3, {{0, 1, 1}, {1, 2, 1}, {0, 2, 1}});
    check(3, {{0, 1, 0}, {1, 2, 1}, {0, 2, 1}});
    check(3, {{0, 1, LLONG_MIN}, {1, 2, LLONG_MAX}, {0, 2, LLONG_MAX}});
    SecondMST a(100000);
    I sum = 0;
    for (int v = 1; v < a.n; v++)
    {
        a.add(v - 1, v, v % 2);
        sum += v % 2;
    }
    for (int i = a.e.size(); i < 300000; i++) a.add(0, a.n - 1, 1);
    auto s = a.solve();
    assert(s.connected && s.weight == sum && s.next == sum + 1);
    assert(a.e[s.in].w == 1 && a.e[s.out].w == 0);
    assert(a.solve(false).next == sum);
    // Repeated solve after adding a cheaper edge must rebuild all tables.
    a.add(0, a.n - 1, -1);
    s = a.solve();
    assert(s.weight == sum - 2 && s.next == sum - 1);
    SecondMST star(100000);
    for (int v = 1; v < star.n; v++)
    {
        star.add(0, v, LLONG_MIN);
        star.add(0, v, LLONG_MIN);
    }
    s = star.solve();
    assert(s.weight == I(star.n - 1) * LLONG_MIN && !s.next);
    assert(star.solve(false).next == s.weight);
    star.add(1, 2, LLONG_MAX);
    s = star.solve();
    assert(s.next == s.weight + I(LLONG_MAX) - I(LLONG_MIN));
    cout << "SecondMST PASS: " << checked
         << " graphs vs all spanning trees, both meanings and exchange witnesses; "
            "100000-node chain/star, 300000 edges, signed extremes and rebuild\n";
}

void *entry(void *)
{
    all();
    return nullptr;
}

int main()
{
    pthread_attr_t attr;
    assert(pthread_attr_init(&attr) == 0);
    assert(pthread_attr_setstacksize(&attr, 256ULL << 20) == 0);
    pthread_t thread;
    assert(pthread_create(&thread, &attr, entry, nullptr) == 0);
    assert(pthread_attr_destroy(&attr) == 0);
    assert(pthread_join(thread, nullptr) == 0);
}
