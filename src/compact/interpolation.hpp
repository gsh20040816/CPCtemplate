#pragma once
#include <cassert>
#include <vector>
using namespace std;

struct Lagrange
{
    using ll = long long;
    int n, mod;
    vector<ll> x, w;

    ll norm(ll a) const
    {
        a %= mod;
        if (a < 0) a += mod;
        return a;
    }

    ll power(ll a, int b) const
    {
        ll result = 1;
        while (b)
        {
            if (b & 1) result = result * a % mod;
            a = a * a % mod;
            b >>= 1;
        }
        return result;
    }

    Lagrange(const vector<ll> &xs, const vector<ll> &ys, int p)
    {
        n = ys.size();
        mod = p;
        assert(p >= 2 && n <= p && xs.size() == ys.size());
        x.resize(n);
        w.resize(n);
        for (int i = 0; i < n; i++) x[i] = norm(xs[i]);
        for (int i = 0; i < n; i++)
        {
            ll denominator = 1;
            for (int j = 0; j < n; j++)
                if (i != j) denominator = denominator * norm(x[i] - x[j]) % mod;
            assert(denominator != 0);
            w[i] = norm(ys[i]) * power(denominator, mod - 2) % mod;
        }
    }

    Lagrange(const vector<ll> &ys, int p)
    {
        n = ys.size();
        mod = p;
        assert(p >= 2 && n <= p);
        x.resize(n);
        w.resize(n);
        if (!n) return;
        vector<ll> invfac(n, 1);
        ll factorial = 1;
        for (int i = 1; i < n; i++) factorial = factorial * i % mod;
        invfac[n - 1] = power(factorial, mod - 2);
        for (int i = n - 1; i > 0; i--) invfac[i - 1] = invfac[i] * i % mod;
        for (int i = 0; i < n; i++)
        {
            x[i] = i;
            w[i] = norm(ys[i]) * invfac[i] % mod * invfac[n - 1 - i] % mod;
            if ((n - 1 - i) & 1) w[i] = norm(-w[i]);
        }
    }

    ll query(ll k) const
    {
        k = norm(k);
        vector<ll> pre(n + 1, 1);
        for (int i = 0; i < n; i++) pre[i + 1] = pre[i] * norm(k - x[i]) % mod;
        ll answer = 0, suffix = 1;
        for (int i = n - 1; i >= 0; i--)
        {
            answer = (answer + w[i] * pre[i] % mod * suffix) % mod;
            suffix = suffix * norm(k - x[i]) % mod;
        }
        return answer;
    }
};

// BEGIN lagrange_consecutive
// ys[i] = f(i) for i = 0..n-1 (deg f < n); returns f(k) mod prime p, n <= p. O(n + log p).
long long lagrange_consecutive(const vector<long long> &ys, long long k, int p)
{
    int n = ys.size();
    assert(p >= 2 && n <= p);
    if (!n) return 0;
    auto norm = [&](long long a) { return (a % p + p) % p; };
    auto power = [&](long long a, long long e)
    {
        long long r = 1;
        for (a = norm(a); e; e >>= 1, a = a * a % p)
            if (e & 1) r = r * a % p;
        return r;
    };
    k = norm(k);
    vector<long long> pre(n + 1, 1), suf(n + 1, 1), ifac(n, 1);
    for (int i = 0; i < n; i++) pre[i + 1] = pre[i] * norm(k - i) % p;
    for (int i = n - 1; i >= 0; i--) suf[i] = suf[i + 1] * norm(k - i) % p;
    long long fact = 1;
    for (int i = 1; i < n; i++) fact = fact * i % p;
    ifac[n - 1] = power(fact, p - 2);
    for (int i = n - 1; i > 0; i--) ifac[i - 1] = ifac[i] * i % p;
    long long answer = 0;
    for (int i = 0; i < n; i++)
    {
        // prod_{j != i} (k - j) / prod_{j != i} (i - j)
        long long term = norm(ys[i]) * pre[i] % p * suf[i + 1] % p * ifac[i] % p * ifac[n - 1 - i] % p;
        answer = ((n - 1 - i) & 1 ? answer - term + p : answer + term) % p;
    }
    return answer;
}
// END lagrange_consecutive
