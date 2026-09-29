#include "../src/compact/convolution_fft.hpp"
#include "../src/compact/convolution_mod_fft.hpp"
#include "../src/compact/convolution_i64.hpp"
#include <boost/multiprecision/cpp_dec_float.hpp>
#include <boost/math/constants/constants.hpp>
#include <climits>
#include <iostream>
#include <random>

vector<long long> brute(const vector<int> &a, const vector<int> &b)
{
    if (a.empty() || b.empty()) return {};
    vector<long long> c(a.size() + b.size() - 1);
    for (int i = 0; i < (int)a.size(); i++)
        for (int j = 0; j < (int)b.size(); j++) c[i + j] += 1LL * a[i] * b[j];
    return c;
}

vector<int> brute_mod(const vector<int> &a, const vector<int> &b, int p)
{
    if (a.empty() || b.empty()) return {};
    vector<int> c(a.size() + b.size() - 1);
    for (int i = 0; i < (int)a.size(); i++)
        for (int j = 0; j < (int)b.size(); j++)
        {
            __int128 v = c[i + j] + (__int128)a[i] * b[j];
            c[i + j] = (v % p + p) % p;
        }
    return c;
}

vector<int> exact_mod(vector<int> a, vector<int> b, int mod)
{
    for (int &x : a) x = (x % mod + (long long)mod) % mod;
    for (int &x : b) x = (x % mod + (long long)mod) % mod;
    vector<long long> aa(a.begin(), a.end()), bb(b.begin(), b.end());
    const long long p = 167772161, q = 469762049, r = 1224736769;
    auto x = convolution_residue<p>(aa, bb);
    auto y = convolution_residue<q>(aa, bb);
    auto z = convolution_residue<r>(aa, bb);
    long long ip = ModInt<q>(p).inv().v, ipq = ModInt<r>(p * q).inv().v;
    vector<int> result(x.size());
    for (int i = 0; i < (int)x.size(); i++)
    {
        long long t = (y[i] - (long long)x[i] + q) % q * ip % q;
        long long v = x[i] + p * t;
        long long u = (z[i] - v % r + r) % r * ipq % r;
        result[i] = (v + (__int128)p * q * u) % mod;
    }
    return result;
}

void transform_test()
{
    using W = boost::multiprecision::cpp_dec_float_100;
    W pi = boost::math::constants::pi<W>();
    mt19937 rng(83124);
    for (int n = 1; n <= 32; n *= 2)
    {
        ComplexFFT fft(n);
        vector<ComplexFFT::C> a(n);
        for (auto &z : a)
            z = {(int)(rng() % 201) - 100.0L, (int)(rng() % 201) - 100.0L};
        for (bool inverse : {false, true})
        {
            auto b = a;
            fft.transform(b, inverse);
            for (int k = 0; k < n; k++)
            {
                W re = 0, im = 0;
                for (int j = 0; j < n; j++)
                {
                    W angle = (inverse ? -2 : 2) * pi * j * k / n;
                    re += W(a[j].real()) * cos(angle) - W(a[j].imag()) * sin(angle);
                    im += W(a[j].real()) * sin(angle) + W(a[j].imag()) * cos(angle);
                }
                if (inverse)
                {
                    re /= n;
                    im /= n;
                }
                assert(abs(W(b[k].real()) - re) < W("2e-10"));
                assert(abs(W(b[k].imag()) - im) < W("2e-10"));
            }
        }
        auto b = a;
        fft.transform(b);
        fft.transform(b, true);
        for (int i = 0; i < n; i++) assert(abs(a[i] - b[i]) < 2e-10L);
    }
}

int main()
{
    transform_test();
    vector<vector<int>> arrays{{}};
    int count = 1;
    for (int n = 1; n <= 4; n++)
    {
        count *= 3;
        for (int mask = 0; mask < count; mask++)
        {
            vector<int> a(n);
            int code = mask;
            for (int &v : a)
            {
                v = vector<int>{-2, 0, 3}[code % 3];
                code /= 3;
            }
            arrays.push_back(a);
        }
    }
    for (const auto &a : arrays)
        for (const auto &b : arrays) assert(convolution_fft(a, b) == brute(a, b));
    mt19937 rng(2400929);
    for (int t = 0; t < 1200; t++)
    {
        vector<int> a(rng() % 65), b(rng() % 65);
        for (int &x : a) x = (int)(rng() % 20001) - 10000;
        for (int &x : b) x = (int)(rng() % 20001) - 10000;
        assert(convolution_fft(a, b) == brute(a, b));
    }
    for (int p : {1, 2, 9, 998244353, 1000000009, INT_MAX})
    {
        for (int t = 0; t < 100; t++)
        {
            vector<int> a(rng() % 40), b(rng() % 40);
            for (int &x : a) x = (long long)rng() - (1LL << 31);
            for (int &x : b) x = (long long)rng() - (1LL << 31);
            auto want = brute_mod(a, b, p);
            assert(convolution_mod_fft(a, b, p) == want);
            if (!a.empty() && !b.empty()) assert(exact_mod(a, b, p) == want);
        }
        vector<int> a{INT_MIN, INT_MAX, -1, 0, 1};
        assert(convolution_mod_fft(a, a, p) == brute_mod(a, a, p));
    }
    assert(convolution_fft({INT_MIN}, {-511}) == brute({INT_MIN}, {-511}));
    assert(convolution_fft({-7}, {3}) == vector<long long>{-21});
    {
        const int n = 1000001;
        vector<int> a(n, 9);
        auto c = convolution_fft(a, a);
        for (int i = 0; i < (int)c.size(); i++)
            assert(c[i] == 81LL * min(i + 1, 2 * n - 1 - i));
    }
    {
        const int n = 100001;
        vector<int> a(n), b(n);
        for (int i = 0; i < n; i++)
        {
            a[i] = llroundl(2047 * cosl(0.017L * i));
            b[i] = llroundl(2047 * sinl(0.017L * i));
        }
        vector<long long> aa(a.begin(), a.end()), bb(b.begin(), b.end());
        assert(convolution_fft(a, b) == convolution_i64(aa, bb));
        for (int p : {1000000009, INT_MAX})
        {
            for (int &v : a) v = (long long)rng() - (1LL << 31);
            for (int &v : b) v = (long long)rng() - (1LL << 31);
            assert(convolution_mod_fft(a, b, p) == exact_mod(a, b, p));
        }
    }
    {
        const int n = 262144, p = INT_MAX;
        vector<int> a(n, p - 1), b(n + 1, p - 1);
        auto c = convolution_mod_fft(a, b, p);
        assert(c.size() == (1 << 19));
        for (int i = 0; i < (int)c.size(); i++)
            assert(c[i] == min({i + 1, n, 2 * n - i}));
    }
    cout << "FFT: 100-digit DFT, 14641 signed exhaustive pairs, 1200 integer and 600 "
            "modular random pairs, signed int boundaries, million-degree triangles, "
            "spectral inputs, exact CRT and full 2^19 modular length PASS\n";
}
