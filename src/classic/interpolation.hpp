#pragma once
#include <cassert>
#include <vector>
using namespace std;

template <int N> struct Lagrange_Interpolation
{
    using ll = long long;
    int n, mod;
    ll x[N], w[N], invfac[N], pre[N + 1];

    ll Norm(ll a) const
    {
        a %= mod;
        if ( a < 0 )
            a += mod;
        return a;
    }

    ll Power(ll a, int b) const
    {
        ll result = 1;
        while ( b )
        {
            if ( b & 1 )
                result = result * a % mod;
            a = a * a % mod;
            b >>= 1;
        }
        return result;
    }

    void Init(const vector<ll> &xs, const vector<ll> &ys, int p)
    {
        n = ys.size();
        mod = p;
        assert(p >= 2 && n <= p && xs.size() == ys.size());
        assert(n <= N);
        for ( int i = 0; i < n; i++ )
            x[i] = Norm(xs[i]);
        for ( int i = 0; i < n; i++ )
        {
            ll denominator = 1;
            for ( int j = 0; j < n; j++ )
                if ( i != j )
                    denominator = denominator * Norm(x[i] - x[j]) % mod;
            assert(denominator != 0);
            w[i] = Norm(ys[i]) * Power(denominator, mod - 2) % mod;
        }
    }

    void Consecutive(const vector<ll> &ys, int p)
    {
        n = ys.size();
        mod = p;
        assert(p >= 2 && n <= p);
        assert(n <= N);
        if ( !n )
            return;

        ll factorial = 1;
        for ( int i = 1; i < n; i++ )
            factorial = factorial * i % mod;
        invfac[n - 1] = Power(factorial, mod - 2);
        for ( int i = n - 1; i > 0; i-- )
            invfac[i - 1] = invfac[i] * i % mod;
        for ( int i = 0; i < n; i++ )
        {
            x[i] = i;
            w[i] = Norm(ys[i]) * invfac[i] % mod * invfac[n - 1 - i] % mod;
            if ( (n - 1 - i) & 1 )
                w[i] = Norm(-w[i]);
        }
    }

    ll Query(ll k)
    {
        k = Norm(k);
        pre[0] = 1;
        for ( int i = 0; i < n; i++ )
            pre[i + 1] = pre[i] * Norm(k - x[i]) % mod;
        ll answer = 0, suffix = 1;
        for ( int i = n - 1; i >= 0; i-- )
        {
            answer = (answer + w[i] * pre[i] % mod * suffix) % mod;
            suffix = suffix * Norm(k - x[i]) % mod;
        }
        return answer;
    }
};
