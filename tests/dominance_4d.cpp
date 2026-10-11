#include "../src/compact/dominance_4d.hpp"
#include <random>

void check(const vector<array<long long, 4>> &p)
{
    for (bool strict : {false, true})
    {
        vector<int> want(p.size());
        for (int i = 0; i < int(p.size()); i++)
        {
            for (int j = 0; j < int(p.size()); j++)
            {
                if (i == j) continue;
                bool ok = true;
                for (int d = 0; d < 4; d++)
                    ok &= strict ? p[j][d] < p[i][d] : p[j][d] <= p[i][d];
                want[i] += ok;
            }
        }
        if (Dominance4D::count(p, strict) != want) abort();
    }
}

int main()
{
    check({});
    for (int mask = 0; mask < (1 << 16); mask++)
    {
        vector<array<long long, 4>> p;
        for (int point = 0; point < 16; point++)
        {
            if (!(mask >> point & 1)) continue;
            array<long long, 4> a;
            for (int d = 0; d < 4; d++) a[d] = point >> d & 1;
            p.push_back(a);
        }
        check(p);
    }
    mt19937_64 rng(21566);
    for (int trial = 0; trial < 5000; trial++)
    {
        int n = rng() % 65;
        vector<array<long long, 4>> p(n);
        for (auto &point : p)
            for (auto &x : point)
                x = trial % 2 ? static_cast<long long>(rng()) : rng() % 5;
        check(p);
        shuffle(p.begin(), p.end(), rng);
        check(p);
    }
    check({{LLONG_MIN, LLONG_MIN, LLONG_MIN, LLONG_MIN},
           {LLONG_MAX, LLONG_MAX, LLONG_MAX, LLONG_MAX},
           {LLONG_MIN, LLONG_MIN, LLONG_MIN, LLONG_MIN}});
    cout << "PASS: 65536 Boolean-grid subsets, 5000 random multisets and permutations, signed64 extremes, both comparison modes\n";
}
