#include "../src/compact/digit_count.hpp"

array<__int128, 10> positional(long long n)
{
    array<__int128, 10> ans{};
    for (__int128 p = 1; p <= n; p *= 10)
    {
        __int128 high = n / (p * 10);
        int cur = n / p % 10;
        __int128 low = n % p;
        for (int d = 1; d <= 9; d++)
            ans[d] += high * p + (cur > d ? p : cur == d ? low + 1 : 0);
        if (high)
            ans[0] += (high - 1) * p + (cur ? p : low + 1);
    }
    return ans;
}

int main()
{
    array<__int128, 10> brute{};
    if (digit_count(-1) != brute || digit_count(0) != brute) abort();
    for (int n = 1; n <= 10000; n++)
    {
        for (char c : to_string(n)) brute[c - '0']++;
        if (digit_count(n) != brute) abort();
    }
    mt19937_64 rng(2602);
    for (int test = 0; test < 10000; test++)
    {
        long long n = rng() & LLONG_MAX;
        if (digit_count(n) != positional(n)) abort();
    }
    for (long long n : {1LL, 10LL, 100LL, 1000000000000LL, LLONG_MAX})
    {
        if (digit_count(n) != positional(n)) abort();
        auto a = digit_count(n);
        auto b = digit_count(n - 1);
        array<__int128, 10> one{};
        for (char c : to_string(n)) one[c - '0']++;
        for (int d = 0; d < 10; d++)
            if (a[d] - b[d] != one[d]) abort();
    }
    cout << "10000 brute prefixes and 10000 full-range positional oracles PASS\n";
}
