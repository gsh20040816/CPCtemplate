#include <bits/stdc++.h>
#include <cassert>
using namespace std;
using i64 = long long;
namespace source
{
#include "fixtures/wida_poly_variants/12D-mint.cpp"
}
#include "../src/compact/recurrence.hpp"
#include "../src/compact/bostan_mori.hpp"
long long checks = 0;
void check(bool ok)
{
    if (!ok)
        throw runtime_error("mismatch at " + to_string(checks));
    checks++;
}
int power(int a, unsigned long long n, int mod)
{
    int r = 1;
    while (n)
    {
        if (n & 1)
            r = 1LL * r * a % mod;
        a = 1LL * a * a % mod;
        n >>= 1;
    }
    return r;
}
bool possible(const vector<int> &s, int k, int p)
{
    vector<vector<int>> a;
    for (int i = k; i < (int)s.size(); i++)
    {
        vector<int> row(k + 1);
        for (int j = 0; j < k; j++)
            row[j] = s[i - 1 - j];
        row[k] = s[i];
        a.push_back(row);
    }
    int rank = 0;
    for (int j = 0; j < k; j++)
    {
        int pivot = rank;
        while (pivot < (int)a.size() && a[pivot][j] == 0)
            pivot++;
        if (pivot == (int)a.size())
            continue;
        swap(a[pivot], a[rank]);
        int inv = power(a[rank][j], p - 2, p);
        for (int col = j; col <= k; col++)
            a[rank][col] = 1LL * a[rank][col] * inv % p;
        for (int i = rank + 1; i < (int)a.size(); i++)
        {
            int factor = a[i][j];
            for (int col = j; col <= k; col++)
                a[i][col] = (a[i][col] - 1LL * factor * a[rank][col] % p + p) % p;
        }
        rank++;
    }
    for (int i = rank; i < (int)a.size(); i++)
        if (a[i][k])
            return false;
    return true;
}
template<int p> void sequence(const vector<int> &s)
{
    source::Poly<p> input;
    for (int x : s)
        input.push_back(x);
    auto q = source::berlekampMassey(input);
    auto c = berlekamp_massey(s, p);
    int minimum = 0;
    while (!possible(s, minimum, p))
        minimum++;
    check((int)q.size() == minimum + 1);
    check((int)c.size() == minimum);
    check(q[0].x == 1);
    for (int i = minimum; i < (int)s.size(); i++)
    {
        long long lhs = s[i], rhs = 0;
        for (int j = 1; j <= minimum; j++)
        {
            lhs = (lhs + 1LL * q[j].x * s[i - j]) % p;
            rhs = (rhs + 1LL * c[j - 1] * s[i - j]) % p;
        }
        check(lhs == 0);
        check(rhs == s[i]);
    }
}
template<int p> void exhaustive(int limit)
{
    int total = 1;
    for (int n = 0; n <= limit; n++)
    {
        for (int code = 0; code < total; code++)
        {
            int v = code;
            vector<int> s(n);
            for (int &x : s)
            {
                x = v % p;
                v /= p;
            }
            sequence<p>(s);
        }
        total *= p;
    }
}
pair<int, int> fibonacci(unsigned long long n)
{
    constexpr int p = 998244353;
    if (!n)
        return {0, 1};
    auto [a, b] = fibonacci(n / 2);
    int c = 1LL * a * ((2LL * b - a + p) % p) % p;
    int d = (1LL * a * a + 1LL * b * b) % p;
    if (n & 1)
        return {d, (c + d) % p};
    return {c, d};
}
int main(int argc, char **argv)
{
    using B = BostanMori<>;
    using Z = B::Z;
    string task = argc > 1 ? argv[1] : "normal";
    if (task == "short-numerator")
    {
        auto x = source::linearRecurrence(source::Poly<>{1}, source::Poly<>{1, 1, 1}, 1);
        cout << x << '\n';
        return 0;
    }
    if (task == "constant-denominator")
    {
        check(source::linearRecurrence(source::Poly<>{2}, source::Poly<>{1}, 1).x == 2);
        check(B::coefficient({2}, {1}, 1).v == 0);
        check(B::coefficient({}, {1}, ULLONG_MAX).v == 0);
        check(B::coefficient({1}, {1, 1, 1}, 1).v == 998244352);
        cout << checks << " constant-denominator counterexample checks PASS\n";
        return 0;
    }
    source::Comb comb;
    Binomial<998244353> current_comb;
    vector<int> pascal{1};
    for (int n = 0; n <= 512; n++)
    {
        current_comb.init(n);
        for (int k = 0; k <= n; k++)
        {
            check(comb.binom(n, k).x == pascal[k]);
            check(current_comb.choose(n, k).v == pascal[k]);
        }
        check(comb.binom(n, -1).x == 0);
        check(comb.binom(n, n + 1).x == 0);
        pascal.push_back(0);
        for (int k = n + 1; k > 0; k--)
            pascal[k] = (pascal[k] + pascal[k - 1]) % 998244353;
    }
    long long factorial = 1;
    check(comb.inv(0).x == 0);
    for (int n = 1; n <= 4096; n++)
    {
        factorial = factorial * n % 998244353;
        check(comb.fac(n).x == factorial);
        check(1LL * comb.invfac(n).x * factorial % 998244353 == 1);
        check(1LL * comb.inv(n).x * n % 998244353 == 1);
    }
    int allocated = comb.n;
    comb.init(3);
    check(comb.n == allocated);
    exhaustive<2>(10);
    exhaustive<3>(7);
    mt19937 rng(45737810);
    for (int t = 0; t < 250; t++)
    {
        vector<int> s(rng() % 25);
        for (int &x : s)
            x = rng() % 998244353;
        sequence<998244353>(s);
    }
    for (int trial = 0; trial < 84; trial++)
    {
        constexpr int p = 998244353;
        int k = trial < 80 ? 1 + rng() % 15 : vector<int>{127, 128, 129, 257}[trial - 80];
        vector<int> q(k + 1), numer(k), coefficients(1026);
        q[0] = 1 + rng() % (p - 1);
        for (int i = 1; i <= k; i++)
            q[i] = rng() % p;
        for (int &x : numer)
            x = rng() % p;
        int inv = power(q[0], p - 2, p);
        for (int i = 0; i < (int)coefficients.size(); i++)
        {
            long long value = i < k ? numer[i] : 0;
            for (int j = 1; j <= min(i, k); j++)
                value = (value - 1LL * q[j] * coefficients[i - j] % p + p) % p;
            coefficients[i] = value * inv % p;
        }
        source::Poly<> old_p, old_q;
        for (int x : numer)
            old_p.push_back(x);
        for (int x : q)
            old_q.push_back(x);
        B::Poly new_p(numer.begin(), numer.end()), new_q(q.begin(), q.end());
        for (int n : {0, 1, 2, 7, 31, 64, 129, 511, 1025})
        {
            check(source::linearRecurrence(old_p, old_q, n).x == coefficients[n]);
            check(B::coefficient(new_p, new_q, n).v == coefficients[n]);
        }
    }
    for (unsigned long long n : {0ULL, 1ULL, 2ULL, 1000000000000000000ULL, (unsigned long long)LLONG_MAX, ULLONG_MAX})
    {
        int truth = fibonacci(n).first;
        check(B::recurrence({0, 1}, {1, 1}, n).v == truth);
        check(recurrence_nth({0, 1}, {1, 1}, n) == truth);
        if (n <= LLONG_MAX)
            check(source::linearRecurrence(source::Poly<>{0, 1}, source::Poly<>{1, -1, -1}, n).x == truth);
    }
    for (int k : {1, 2, 127, 128, 129, 1024})
    {
        source::Poly<> s(2 * k);
        vector<int> values(2 * k);
        s[k - 1] = 1;
        s[2 * k - 1] = 1;
        values[k - 1] = values[2 * k - 1] = 1;
        auto q = source::berlekampMassey(s);
        auto c = berlekamp_massey(values);
        check((int)q.size() == k + 1 && (int)c.size() == k);
        check(q[0].x == 1);
        for (int i = 1; i <= k; i++)
        {
            check(q[i].x == (i == k ? 998244352 : 0));
            check(c[i - 1] == (i == k ? 1 : 0));
        }
    }
    for (int t = 0; t < 30; t++)
    {
        constexpr int p = 998244353;
        unsigned long long n = ((unsigned long long)rng() << 32) | rng();
        int ratio = 1 + rng() % (p - 1), first = rng() % p;
        int truth = 1LL * first * power(ratio, n, p) % p;
        check(B::coefficient({first}, {1, Z(0) - Z(ratio)}, n).v == truth);
        unsigned long long signed_n = n & LLONG_MAX;
        truth = 1LL * first * power(ratio, signed_n, p) % p;
        check(source::linearRecurrence(source::Poly<>{first}, source::Poly<>{1, -ratio}, signed_n).x == truth);
    }
    cout << checks << " independent finite-prefix minimality/rational-coefficient checks PASS\n";
}
