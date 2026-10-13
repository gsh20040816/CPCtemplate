#pragma once
#include <array>
#include <cassert>
#include "exkmp.hpp"
using namespace std;

// BEGIN good_number_sum
// Return adjacent half-open ranges [l,k), [k,r), or {-1,-1,-1}.
array<int, 3> good_number_sum(const string &s, const string &x,
                            unsigned long long mod = (1ULL << 61) - 1)
{
    using U = unsigned long long;
    using W = __uint128_t;
    assert(s.size() <= 500000 && !x.empty() && x.size() <= 200000);
    assert(1 <= mod && mod < (1ULL << 61));
    for (char c : s)
        assert('1' <= c && c <= '9');
    for (char c : x)
        assert('1' <= c && c <= '9');
    int n = s.size(), m = x.size();
    vector<U> h(n + 1), power(n + 1);
    power[0] = 1 % mod;
    for (int i = 0; i < n; i++)
    {
        h[i + 1] = (W(h[i]) * 10 + s[i] - '0') % mod;
        power[i + 1] = W(power[i]) * 10 % mod;
    }
    U target = 0;
    for (char c : x)
        target = (W(target) * 10 + c - '0') % mod;
    auto remainder = [&](int l, int r) -> U
    {
        U removed = W(h[l]) * power[r - l] % mod;
        return (h[r] + mod - removed) % mod;
    };
    auto valid = [&](int l, int k, int r)
    {
        if (l < 0 || l >= k || k >= r || r > n)
            return false;
        if ((remainder(l, k) + remainder(k, r)) % mod != target)
            return false;
        int a = k - 1, b = r - 1, carry = 0;
        for (int i = m - 1; i >= 0; i--)
        {
            int digit = carry;
            if (a >= l)
                digit += s[a--] - '0';
            if (b >= k)
                digit += s[b--] - '0';
            if (digit % 10 != x[i] - '0')
                return false;
            carry = digit / 10;
        }
        return a < l && b < k && carry == 0;
    };
    if (m > 1)
        for (int l = 0; l + 2 * (m - 1) <= n; l++)
        {
            int k = l + m - 1, r = k + m - 1;
            if (valid(l, k, r))
                return {l, k, r};
        }
    auto [z, lcp] = exkmp(s, x);
    for (int i = 0; i + m <= n; i++)
        for (int len : {m - lcp[i], m - lcp[i] - 1})
        {
            if (len <= 0)
                continue;
            if (valid(i - len, i, i + m))
                return {i - len, i, i + m};
            if (valid(i, i + m, i + m + len))
                return {i, i + m, i + m + len};
        }
    return {-1, -1, -1};
}
// END good_number_sum
