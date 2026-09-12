#include "../src/compact/modified_mo.hpp"
#include <array>
#include <iostream>
#include <random>
#include <set>

int main()
{
    mt19937 rng(1903);
    long long forward_steps = 0, backward_steps = 0;
    for (int trial = 0; trial < 1000; trial++)
    {
        int n = 1 + rng() % 15, updates = rng() % 20;
        vector<int> initial(n);
        for (int &v : initial)
            v = rng() % 7;
        vector<vector<int>> snapshots{initial};
        vector<array<int, 3>> edits;
        for (int i = 0; i < updates; i++)
        {
            auto a = snapshots.back();
            int p = rng() % n, v = rng() % 7;
            edits.push_back({p, a[p], v});
            a[p] = v;
            snapshots.push_back(a);
        }
        ModifiedMo mo(n, updates);
        for (int t = updates; t >= 0; t--)
            for (int l = 0; l <= n; l++)
                for (int r = l; r <= n; r++)
                    mo.add(l, r, t);
        // Custom blocks, defaults, replay with freshly reset callback state.
        for (int block : {0, 1, 3, n + 1})
        {
            vector<int> a = initial, active(n), count(7), result(mo.q.size());
            int distinct = 0, time = 0;
            long long sum = 0;
            auto add = [&](int p)
            {
                assert(!active[p]);
                active[p] = 1;
                sum += a[p];
                distinct += count[a[p]]++ == 0;
            };
            auto erase = [&](int p)
            {
                assert(active[p]);
                active[p] = 0;
                sum -= a[p];
                distinct -= --count[a[p]] == 0;
            };
            auto change = [&](int t, bool forward, int l, int r)
            {
                assert(t == (forward ? time : time - 1));
                for (int p = 0; p < n; p++)
                    assert(active[p] == (l <= p && p < r));
                auto [p, before, after] = edits[t];
                assert(a[p] == (forward ? before : after));
                bool inside = l <= p && p < r;
                if (inside)
                    erase(p);
                a[p] = forward ? after : before;
                if (inside)
                    add(p);
                if (forward)
                {
                    time++;
                    forward_steps++;
                }
                else
                {
                    time--;
                    backward_steps++;
                }
                assert(a == snapshots[time]);
            };
            auto answer = [&](int id)
            {
                auto q = mo.q[id];
                assert(time == q.t && !result[id]++);
                set<int> values;
                long long expected = 0;
                for (int p = 0; p < n; p++)
                {
                    assert(active[p] == (q.l <= p && p < q.r));
                    if (active[p])
                    {
                        values.insert(snapshots[q.t][p]);
                        expected += snapshots[q.t][p];
                    }
                }
                assert(distinct == int(values.size()) && sum == expected);
            };
            mo.run(add, erase, change, answer, block);
            for (int v : result)
                assert(v == 1);
        }
    }
    ModifiedMo empty(1, 10);
    auto unused = [](auto...) { assert(false); };
    empty.run(unused, unused, unused, unused);
    assert(forward_steps && backward_steps);
    cout << "Modified Mo snapshot/set oracle, all ranges/times, empty queries, custom blocks and bidirectional state invariants PASS\n";
}
