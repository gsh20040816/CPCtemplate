#include "../src/compact/gcd_sequence.hpp"
#include "../src/classic/gcd_sequence.hpp"
#include <iostream>
#include <limits>

int main()
{
    using U = unsigned long long;
    std::mt19937_64 rng(923741);
    static Gcd_Sequence_Treap<64> b;
    for (int trial = 0; trial < 200; trial++)
    {
        GcdSequenceTreap a(trial);
        b.Init(trial);
        std::vector<std::pair<U, int>> v;
        for (int step = 0; step < 2000; step++)
        {
            int n = v.size();
            int op = rng() % 7;
            U value = rng();
            if (step % 3 == 0)
                value = 0;
            if (step % 5 == 0)
                value = std::numeric_limits<U>::max();
            int tag = rng() % 2;
            if (op == 6)
            {
                v.assign(rng() % 65, {value, tag});
                a.build(v);
                b.Build(v);
            }
            else if (n == 0 || (op == 0 && n < 64))
            {
                int k = rng() % (n + 1);
                a.insert(k, value, tag);
                b.Insert(k, value, tag);
                v.insert(v.begin() + k, {value, tag});
            }
            else
            {
                int l = rng() % n + 1;
                int r = rng() % n + 1;
                if (l > r)
                    std::swap(l, r);
                if (op == 1)
                {
                    a.erase(l, r);
                    b.Erase(l, r);
                    v.erase(v.begin() + l - 1, v.begin() + r);
                }
                else if (op == 2)
                {
                    a.set(l, value);
                    b.Set(l, value);
                    v[l - 1].first = value;
                }
                else if (op == 3)
                {
                    a.toggle(l);
                    b.Toggle(l);
                    v[l - 1].second ^= 1;
                }
                else
                {
                    std::optional<U> expected;
                    for (int i = l - 1; i < r; i++)
                    {
                        if (v[i].second == tag)
                            expected = std::gcd(expected.value_or(0), v[i].first);
                    }
                    assert(a.query(l, r, tag) == expected);
                    assert(b.Query(l, r, tag) == expected);
                }
            }
            assert(a.size() == (int)v.size());
            assert(b.Size() == (int)v.size());
            if (step % 31 == 0)
            {
                for (int i = 0; i < (int)v.size(); i++)
                {
                    for (int t = 0; t < 2; t++)
                    {
                        std::optional<U> expected;
                        if (v[i].second == t)
                            expected = v[i].first;
                        assert(a.query(i + 1, i + 1, t) == expected);
                        assert(b.Query(i + 1, i + 1, t) == expected);
                    }
                }
            }
        }
    }
    GcdSequenceTreap a;
    b.Init();
    for (int step = 0; step < 10000; step++)
    {
        for (int i = 0; i < 64; i++)
        {
            a.insert(i, 0, 1);
            b.Insert(i, 0, 1);
        }
        assert(a.query(1, 64, 1) == 0);
        assert(b.Query(1, 64, 1) == 0);
        assert(!a.query(1, 64, 0));
        assert(!b.Query(1, 64, 0));
        a.erase(1, 64);
        b.Erase(1, 64);
        assert(a.a.size() == 65);
        assert(b.tot == 64);
    }
    std::cout << "Tagged GCD treap / vector oracle and recycled capacity PASS\n";
}
