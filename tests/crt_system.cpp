#include "../src/compact/number_theory.hpp"
#include "../src/classic/number_theory.hpp"
#include <cassert>
#include <iostream>
#include <vector>
using namespace std;

void check(const vector<pair<int, int>> &equations)
{
    long long period = 1;
    for (auto [m, b] : equations)
        period = lcm(period, (long long)m);
    long long expected = -1;
    for (long long x = 0; x < period; x++)
    {
        bool ok = true;
        for (auto [m, b] : equations)
            if ((x - b) % m)
                ok = false;
        if (ok)
        {
            expected = x;
            break;
        }
    }
    for (int style = 0; style < 2; style++)
    {
        long long r = 0, m = 1;
        bool ok = true;
        for (auto [modulus, residue] : equations)
        {
            ok = style ? Number_Theory::Crt(r, m, residue, modulus)
                       : NumberTheory::crt(r, m, residue, modulus);
            if (!ok)
                break;
        }
        assert(ok == (expected >= 0));
        if (ok)
        {
            assert(r == expected && m == period);
            for (int t = -3; t <= 3; t++)
                for (auto [modulus, residue] : equations)
                    assert((r + m * t - residue) % modulus == 0);
        }
    }
}

void generate(vector<pair<int, int>> &equations)
{
    check(equations);
    if (equations.size() == 3)
        return;
    for (int m = 1; m <= 4; m++)
        for (int b = 0; b < m; b++)
        {
            equations.push_back({m, b - 2 * m});
            generate(equations);
            equations.pop_back();
        }
}

int main()
{
    vector<pair<int, int>> equations;
    generate(equations);
    check({{2, 0}, {3, 0}, {6, 1}});
    check({{6, 1}, {3, 0}, {2, 0}});
    cout << "CRT systems dual exhaustive up-to-three equations, empty system, orderings and late inconsistency PASS\n";
}
