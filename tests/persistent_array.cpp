#include "../src/compact/persistent_array.hpp"
#include "../src/classic/persistent_array.hpp"
#include <iostream>
#include <limits>
#include <random>

int main()
{
    using ll = long long;
    std::mt19937_64 rng(873131);
    static Persistent_Array<8000> b;
    for (int trial = 0; trial < 100; trial++)
    {
        int n = 1 + rng() % 64;
        std::vector<ll> initial(n);
        for (auto &x : initial)
            x = (ll)(rng() >> 1);
        PersistentArray a(initial);
        b.Init(initial);
        std::vector<std::vector<ll>> versions{initial};
        int levels = 1;
        for (int x = n - 1; x; x >>= 1)
            levels++;
        for (int step = 0; step < 1000; step++)
        {
            int version = rng() % versions.size();
            int pos = 1 + rng() % n;
            ll value = step % 2 ? std::numeric_limits<ll>::min() : std::numeric_limits<ll>::max();
            auto next = versions[version];
            int before_a = a.t.size(), before_b = b.tot;
            int x, y;
            if (rng() % 3 == 0)
            {
                x = a.copy(version);
                y = b.Copy(version);
                assert((int)a.t.size() == before_a && b.tot == before_b);
            }
            else
            {
                x = a.set(version, pos, value);
                y = b.Set(version, pos, value);
                next[pos - 1] = value;
                assert((int)a.t.size() - before_a <= levels);
                assert(b.tot - before_b <= levels);
            }
            assert(x == (int)versions.size() && y == x);
            versions.push_back(next);
            for (int check = 0; check < 10; check++)
            {
                int old = rng() % versions.size();
                int at = 1 + rng() % n;
                assert(a.query(old, at) == versions[old][at - 1]);
                assert(b.Query(old, at) == versions[old][at - 1]);
            }
        }
        for (int v = 0; v < (int)versions.size(); v++)
            for (int pos = 1; pos <= n; pos++)
            {
                assert(a.query(v, pos) == versions[v][pos - 1]);
                assert(b.Query(v, pos) == versions[v][pos - 1]);
            }
    }
    Persistent_Array<2> one;
    one.Init({7});
    assert(one.Set(0, 1, -9) == 1);
    for (int i = 0; i < 10000; i++)
        one.Copy(i % 2);
    assert(one.tot == 2 && one.Query(0, 1) == 7 && one.Query(1, 1) == -9);
    const int n = 100000, updates = 20000;
    PersistentArray a(std::vector<ll>(n), updates);
    static Persistent_Array<600000> large;
    large.Init(std::vector<ll>(n));
    auto capacity = a.t.capacity();
    for (int i = 1; i <= updates; i++)
    {
        int pos = 1 + i % n;
        assert(a.set(0, pos, i) == i);
        assert(large.Set(0, pos, i) == i);
        assert(a.query(i, pos) == i && large.Query(i, pos) == i);
        assert(a.query(0, pos) == 0 && large.Query(0, pos) == 0);
    }
    assert(a.t.capacity() == capacity);
    std::cout << "Persistent array branching versions, snapshots, allocation bounds and reserve PASS\n";
}
