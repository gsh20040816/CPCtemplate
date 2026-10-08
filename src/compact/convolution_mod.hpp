#pragma once
#include "ntt_convolution.hpp"

// BEGIN convolution_mod
template <int p>
vector<int> convolution_prime(const vector<int> &a, const vector<int> &b)
{
    using N = NttConvolution<p>;
    typename N::Poly x(a.begin(), a.end()), y(b.begin(), b.end());
    auto c = N::multiply(move(x), move(y));
    vector<int> result(c.size());
    for (int i = 0; i < (int)c.size(); i++)
        result[i] = c[i].v;
    return result;
}

vector<int> convolution_mod(vector<int> a, vector<int> b, int mod)
{
    assert(mod >= 1);
    if (a.empty() || b.empty())
        return {};
    assert(a.size() <= (1 << 24) && b.size() <= (1 << 24));
    assert(a.size() + b.size() - 1 <= (1 << 24));
    int n = a.size() + b.size() - 1;
    if (mod == 1)
        return vector<int>(n);
    for (int &v : a)
    {
        v %= mod;
        if (v < 0)
            v += mod;
    }
    for (int &v : b)
    {
        v %= mod;
        if (v < 0)
            v += mod;
    }
    const long long p = 167772161, q = 469762049, r = 1224736769;
    const long long pq = p * q;
    static const long long ip = ModInt<q>(p).inv().v;
    static const long long ipq = ModInt<r>(pq).inv().v;
    auto x = convolution_prime<p>(a, b);
    auto y = convolution_prime<q>(a, b);
    auto z = convolution_prime<r>(a, b);
    for (int i = 0; i < n; i++)
    {
        long long t = (y[i] - (long long)x[i] + q) % q * ip % q;
        long long v = x[i] + p * t;
        long long u = (z[i] - v % r + r) % r * ipq % r;
        __int128 value = v + (__int128)pq * u;
        x[i] = value % mod;
    }
    return x;
}

// END convolution_mod
