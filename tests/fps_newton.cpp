#include "../src/compact/fps_sqrt.hpp"
#include <cstdlib>

using F = FpsSqrt;
using V = F::Poly;
constexpr long long P = F::mod;
long long checks = 0;

void check(bool ok)
{
    if (!ok)
        abort();
    checks++;
}

long long power(long long a, long long e)
{
    long long b = 1;
    while (e)
    {
        if (e & 1)
            b = b * a % P;
        a = a * a % P;
        e >>= 1;
    }
    return b;
}

int main(int argc, char **argv)
{
    if (argc > 1)
    {
        int n = F::max_size;
        auto inv = F::inverse({1, P - 1}, n);
        for (auto x : inv)
            check(x.v == 1);
        inv.clear();
        inv.shrink_to_fit();
        n /= 2;
        V a(n);
        for (int i = 0; i < n; i++)
            a[i] = i + 1;
        auto r = F::inverse_sqrt(a, n);
        check(r.has_value());
        for (int i = 0; i < n; i++)
            check((*r)[i].v == (i == 0 ? 1 : (i == 1 ? P - 1 : 0)));
        r.reset();
        auto s = F::sqrt(a, n);
        check(s.has_value());
        for (auto x : *s)
            check(x.v == 1);
        cout << checks << " full-capacity analytic inverse/root checks PASS\n";
        return 0;
    }
    check(F::inverse_sqrt({}, 0)->empty());
    check(F::inverse_sqrt({0}, 0)->empty());
    check(F::inverse_sqrt({3}, 0)->empty());
    check(!F::inverse_sqrt({}, 1));
    check(!F::inverse_sqrt({0}, 1));
    check(!F::inverse_sqrt({0, 0, 1}, 3));
    check(power(3, (P - 1) / 2) == P - 1);
    check(!F::inverse_sqrt({3, 1}, 2));
    mt19937 rng(20261013);
    vector<int> sizes{1, 2, 3, 7, 8, 9, 31, 32, 33, 63, 64, 65, 127, 128, 129, 255, 256, 257};
    for (int repeat = 0; repeat < 8; repeat++)
    {
        shuffle(sizes.begin(), sizes.end(), rng);
        for (int n : sizes)
        {
            vector<long long> root(n), a(n), inverse(n);
            for (auto &x : root)
                x = rng() % P;
            root[0] = 1 + rng() % (P - 1);
            if (root[0] > P / 2)
                for (auto &x : root)
                    x = (P - x) % P;
            for (int i = 0; i < n; i++)
                for (int j = 0; i + j < n; j++)
                    a[i + j] = (a[i + j] + root[i] * root[j]) % P;
            inverse[0] = power(root[0], P - 2);
            for (int i = 1; i < n; i++)
            {
                long long sum = 0;
                for (int j = 1; j <= i; j++)
                    sum = (sum + root[j] * inverse[i - j]) % P;
                inverse[i] = (P - sum) * inverse[0] % P;
            }
            V input(a.begin(), a.end());
            // Extra tail coefficients must not affect the requested prefix.
            input.insert(input.end(), repeat, F::Z(123));
            auto got = F::inverse_sqrt(input, n);
            check(got.has_value() && (int)got->size() == n);
            auto sq = F::sqrt(input, n);
            check(sq.has_value() && (int)sq->size() == n);
            for (int i = 0; i < n; i++)
            {
                check((*got)[i].v == inverse[i]);
                check((*sq)[i].v == root[i]);
            }
            V coefficient(1, input[0]);
            got = F::inverse_sqrt(coefficient, n);
            check(got.has_value());
            for (int i = 0; i < n; i++)
                check((*got)[i].v == (i ? 0 : inverse[0]));
        }
    }
    cout << checks << " independent inverse-root recurrence/branch/reuse checks PASS\n";
}
