#include "../src/compact/fps_sqrt.hpp"
#include "../src/compact/polynomial_division.hpp"
#include <iostream>
using V = FpsInverse::Poly;
using ll = long long;
const ll p = 998244353;

ll power(ll x, ll k)
{
    ll result = 1;
    for (; k; k >>= 1, x = x * x % p)
        if (k & 1) result = result * x % p;
    return result;
}

void trim(vector<ll> &a)
{
    while (!a.empty() && !a.back()) a.pop_back();
}

void same(const V &a, const vector<ll> &b)
{
    assert(a.size() == b.size());
    for (int i = 0; i < (int)a.size(); i++) assert(a[i].v == b[i]);
}

vector<ll> square(const vector<ll> &a, int n)
{
    vector<ll> result(n);
    for (int i = 0; i < (int)a.size(); i++)
        for (int j = 0; j < (int)a.size() && i + j < n; j++)
            result[i + j] = (result[i + j] + a[i] * a[j]) % p;
    return result;
}

int main()
{
    mt19937 rng(52054512);
    for (int trial = 0; trial < 3000; trial++)
    {
        int n = rng() % 90, m = 1 + rng() % 90;
        vector<ll> a(n), b(m);
        for (auto &x : a) x = rng() % p;
        for (auto &x : b) x = rng() % p;
        if (trial % 3 == 0) fill(a.begin(), a.end(), 0);
        if (trial % 4 == 0) fill(b.begin() + 1, b.end(), 0);
        b[0] = 1 + rng() % (p - 1);
        V av(a.begin(), a.end()), bv(b.begin(), b.end());
        if (trial % 2 == 0) av.resize(n + 4);
        if (trial % 5 == 0) bv.resize(m + 4);
        trim(a);
        trim(b);
        vector<ll> q(a.size() < b.size() ? 0 : a.size() - b.size() + 1);
        ll iv = power(b.back(), p - 2);
        for (int i = (int)q.size() - 1; i >= 0; i--)
        {
            q[i] = a[i + b.size() - 1] * iv % p;
            for (int j = 0; j < (int)b.size(); j++)
                a[i + j] = (a[i + j] - q[i] * b[j] % p + p) % p;
        }
        trim(a);
        auto [quotient, remainder] = PolynomialDivision::divide(av, bv);
        same(quotient, q);
        same(remainder, a);
    }
    for (int trial = 0; trial < 2400; trial++)
    {
        int n = rng() % 100, shift = rng() % (n + 1);
        vector<ll> root(n);
        for (int i = shift; i < n; i++) root[i] = rng() % p;
        if (shift < n) root[shift] = 1 + rng() % (p - 1);
        auto a = square(root, n);
        V input(a.begin(), a.end());
        if (trial % 3 == 0) input.resize(n + 20, 123);
        auto answer = FpsSqrt::sqrt(input, n);
        assert(answer);
        vector<ll> got;
        for (auto x : *answer) got.push_back(x.v);
        assert(square(got, n) == a);
        if (2 * shift < n)
        {
            bool negate = root[shift] > p - root[shift];
            for (int i = shift; i < n - shift; i++)
                assert(got[i] == (negate && root[i] ? p - root[i] : root[i]));
            for (int i = n - shift; i < n; i++) assert(got[i] == 0);
        }
        else
            same(*answer, vector<ll>(n));
    }
    for (int n = 1; n <= 80; n++)
        for (int k = 0; k < n; k++)
        {
            V a(n);
            a[k] = 3;
            assert(!FpsSqrt::sqrt(a, n));
            a[k] = 4;
            auto b = FpsSqrt::sqrt(a, n);
            assert(bool(b) == !(k & 1));
            if (b)
            {
                vector<ll> want(n);
                want[k / 2] = 2;
                same(*b, want);
            }
        }
    // Implicit zero input coefficients; sqrt(1+2x+x^2)=1+x.
    same(*FpsSqrt::sqrt({1, 2, 1}, 200000),
         []
         {
             vector<ll> a(200000);
             a[0] = a[1] = 1;
             return a;
         }());
    same(*FpsSqrt::sqrt({}, 17), vector<ll>(17));
    int n = 500000;
    V a(n), b(n / 2 + 1);
    b[0] = b.back() = 1;
    vector<ll> q(n / 2), r(n / 2);
    for (int i = 0; i < n / 2; i++)
    {
        q[i] = (ll(i) * i + 17) % p;
        r[i] = (7LL * i + 9) % p;
        a[i] = (q[i] + r[i]) % p;
        a[i + n / 2] = q[i];
    }
    auto result = PolynomialDivision::divide(a, b);
    same(result.first, q);
    same(result.second, r);
    // sqrt((1-x)^-2)=(1-x)^-1: full dense non-power-of-two target.
    V dense(n);
    for (int i = 0; i < n; i++) dense[i] = i + 1;
    same(*FpsSqrt::sqrt(dense, n), vector<ll>(n, 1));
    cout << "Polynomial division/sqrt: 3000 long-division oracles, 2400 truncated "
            "squares, 6480 valuation/residue cases, empty/long/short inputs, "
            "200000 and 500000 closed forms PASS\n";
}
