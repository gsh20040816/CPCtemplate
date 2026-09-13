#include "../src/compact/convolution_i64.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using boost::multiprecision::cpp_int;

void check(const vector<long long> &a, const vector<long long> &b)
{
    auto got = convolution_i64(a, b);
    if (a.empty() || b.empty())
    {
        assert(got.empty());
        return;
    }
    vector<cpp_int> want(a.size() + b.size() - 1);
    for (int i = 0; i < (int)a.size(); i++)
        for (int j = 0; j < (int)b.size(); j++) want[i + j] += cpp_int(a[i]) * b[j];
    assert(got.size() == want.size());
    for (int i = 0; i < (int)got.size(); i++) assert(cpp_int(got[i]) == want[i]);
}

long long power(long long x, long long n, long long p)
{
    long long y = 1;
    for (; n; n >>= 1, x = (__int128)x * x % p)
        if (n & 1) y = (__int128)y * x % p;
    return y;
}

int main()
{
    for (int p : {167772161, 469762049, 1224736769})
    {
        for (int d = 2; 1LL * d * d <= p; d++) assert(p % d);
        int n = p - 1;
        for (int d = 2; 1LL * d * d <= n; d++)
            if (n % d == 0)
            {
                assert(power(3, (p - 1) / d, p) != 1);
                while (n % d == 0) n /= d;
            }
        if (n > 1) assert(power(3, (p - 1) / n, p) != 1);
    }
    check({}, {});
    check({}, {1});
    check({LLONG_MIN, LLONG_MAX}, {1});
    check({LLONG_MIN, LLONG_MAX}, {1, 1});
    check({-LLONG_MAX, LLONG_MAX}, {1, 1});
    check({167772161LL * 469762049}, {-1});
    check({1224736769}, {469762049});
    mt19937 rng(13867);
    for (int t = 0; t < 1000; t++)
    {
        vector<long long> a(rng() % 40), b(rng() % 40);
        for (auto &x : a) x = int(rng() % 2000001) - 1000000;
        for (auto &x : b) x = int(rng() % 2000001) - 1000000;
        check(a, b);
    }
    int n = 200000;
    vector<long long> a(n), b(n);
    for (int i = 0; i < n; i++) a[i] = b[i] = i % 2 ? -1 : 1;
    auto c = convolution_i64(a, b);
    for (int i = 0; i < 2 * n - 1; i++)
    {
        long long count = min(i + 1, 2 * n - 1 - i);
        assert(c[i] == (i % 2 ? -count : count));
    }
    cout << "Signed integer convolution: cpp_int oracle, certified primes/roots, int64 "
            "cancellation and large alternating triangles PASS\n";
}
