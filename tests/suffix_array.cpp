#include "../src/compact/string.hpp"
#include <random>
#include <iostream>

template <class Sequence> void check(const Sequence &s, int alphabet = 256)
{
    vector<int> symbols;
    for (auto c : s)
    {
        if constexpr (is_same_v<Sequence, string>)
            symbols.push_back((unsigned char)c);
        else
            symbols.push_back(c);
    }
    int n = s.size();
    vector<int> want(n), height(n);
    iota(want.begin(), want.end(), 0);
    auto less_suffix = [&](int a, int b)
    {
        while (a < n && b < n && s[a] == s[b])
        {
            a++;
            b++;
        }
        if (a == n || b == n) return a == n && b != n;
        return symbols[a] < symbols[b];
    };
    sort(want.begin(), want.end(), less_suffix);
    for (int i = 1; i < n; i++)
    {
        int a = want[i - 1], b = want[i];
        while (a + height[i] < n && b + height[i] < n &&
               s[a + height[i]] == s[b + height[i]])
            height[i]++;
    }
    SuffixArray a(symbols, alphabet);
    if constexpr (is_same_v<Sequence, string>)
    {
        SuffixArray c(s);
        assert(c.sa == want);
        assert(c.lcp == height);
    }
    a = SuffixArray({}, 1);
    assert(a.sa.empty() && a.rk.empty() && a.lcp.empty());
    a = SuffixArray(symbols, alphabet);
    assert(a.sa == want);
    assert(a.lcp == height);
    for (int i = 0; i < n; i++) assert(a.rk[want[i]] == i);
    // Every-pair LCP via the minimum on (rank_i,rank_j].
    for (int i = 0; i < n; i++)
    {
        int common = n;
        for (int j = i + 1; j < n; j++)
        {
            common = min(common, a.lcp[j]);
            int x = a.sa[i], y = a.sa[j], expected = 0;
            while (x + expected < n && y + expected < n &&
                   s[x + expected] == s[y + expected])
                expected++;
            assert(common == expected);
        }
    }
}

void scale(int n, const string &pattern)
{
    int period = pattern.size();
    string s(n, 0);
    for (int i = 0; i < n; i++) s[i] = pattern[i % period];
    SuffixArray a(s);
    vector<int> phases(period);
    iota(phases.begin(), phases.end(), 0);
    sort(phases.begin(),
         phases.end(),
         [&](int x, int y)
         { return (unsigned char)pattern[x] < (unsigned char)pattern[y]; });
    int rank = 0;
    for (int phase : phases)
    {
        int last = n - 1 - (n - 1 - phase) % period;
        for (int i = last; i >= 0; i -= period)
        {
            assert(a.sa[rank] == i);
            assert(a.rk[i] == rank);
            int height = i == last ? 0 : n - i - period;
            assert(a.lcp[rank] == height);
            rank++;
        }
    }
    assert(rank == n);
}

void segmented()
{
    mt19937 rng(91512);
    for (int trial = 0; trial < 1500; trial++)
    {
        int n = rng() % 65;
        vector<int> s(n), remaining(n + 1);
        for (int &x : s) x = rng() % 5;
        // Ordinary alphabet 0..2, separators 3 and 4 may repeat or be consecutive.
        for (int i = n - 1; i >= 0; i--)
            if (s[i] < 3) remaining[i] = remaining[i + 1] + 1;
        SuffixArray suffix(s, 5);
        auto clipped = suffix.lcp;
        for (int k = 1; k < n; k++)
        {
            int x = suffix.sa[k - 1], y = suffix.sa[k];
            clipped[k] = min({clipped[k], remaining[x], remaining[y]});
            int expected = 0;
            while (x + expected < n && y + expected < n && s[x + expected] < 3 &&
                   s[y + expected] < 3 && s[x + expected] == s[y + expected])
                expected++;
            assert(clipped[k] == expected);
        }
    }
}

int main()
{
    segmented();
    for (int n = 0, total = 1; n <= 9; n++, total *= 3)
        for (int mask = 0; mask < total; mask++)
        {
            int x = mask;
            string s(n, 0);
            for (char &c : s)
            {
                c = string("\0\x7f\xff", 3)[x % 3];
                x /= 3;
            }
            check(s);
        }
    mt19937 rng(3809);
    for (int test = 0; test < 1000; test++)
    {
        string s(rng() % 160, 0);
        for (char &c : s) c = rng() % 256;
        check(s);
    }
    for (int test = 0; test < 50; test++)
    {
        vector<int> s(rng() % 80);
        for (int &x : s) x = vector<int>{0, 1000, 50000, 100000}[rng() % 4];
        check(s, 100001);
    }
    check(vector<int>{}, 1);
    check(vector<int>{0, 0, 0}, 1);
    string bytes;
    for (int i = 0; i < 256; i++) bytes.push_back((char)i);
    check(bytes);
    reverse(bytes.begin(), bytes.end());
    check(bytes);
    for (int n : {1023, 1024, 1025, 1000000})
    {
        scale(n, "a");
        scale(n, string("\xff\0\x7f\x01", 4));
    }
    cout << "Suffix array vector exhaustive bytes, integer alphabets, reset, LCP "
            "minima and million-character periodic oracle and 1500 repeated-separator "
            "LCP cases PASS\n";
}
