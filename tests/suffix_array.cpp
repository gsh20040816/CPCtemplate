#include "../src/compact/string.hpp"
#include "../src/classic/string.hpp"
#include <random>
#include <iostream>

template<class Sequence>
void check(const Sequence &s, int alphabet = 256)
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
        if (a == n || b == n)
            return a == n && b != n;
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
    Suffix_Array b(symbols, alphabet);
    if constexpr (is_same_v<Sequence, string>)
    {
        SuffixArray c(s);
        Suffix_Array d(s);
        assert(c.sa == want && d.sa == want);
        assert(c.lcp == height && d.lcp == height);
    }
    a = SuffixArray({}, 1);
    b.Init({}, 1);
    assert(a.sa.empty() && a.rk.empty() && a.lcp.empty());
    assert(b.sa.empty() && b.rk.empty() && b.lcp.empty());
    a = SuffixArray(symbols, alphabet);
    b.Init(symbols, alphabet);
    assert(a.sa == want && b.sa == want);
    assert(a.lcp == height && b.lcp == height);
    for (int i = 0; i < n; i++)
        assert(a.rk[want[i]] == i && b.rk[want[i]] == i);
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
    for (int i = 0; i < n; i++)
        s[i] = pattern[i % period];
    SuffixArray a(s);
    Suffix_Array b(s);
    vector<int> phases(period);
    iota(phases.begin(), phases.end(), 0);
    sort(phases.begin(), phases.end(), [&](int x, int y)
    {
        return (unsigned char)pattern[x] < (unsigned char)pattern[y];
    });
    int rank = 0;
    for (int phase : phases)
    {
        int last = n - 1 - (n - 1 - phase) % period;
        for (int i = last; i >= 0; i -= period)
        {
            assert(a.sa[rank] == i && b.sa[rank] == i);
            assert(a.rk[i] == rank && b.rk[i] == rank);
            int height = i == last ? 0 : n - i - period;
            assert(a.lcp[rank] == height && b.lcp[rank] == height);
            rank++;
        }
    }
    assert(rank == n);
}

int main()
{
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
        for (char &c : s)
            c = rng() % 256;
        check(s);
    }
    for (int test = 0; test < 50; test++)
    {
        vector<int> s(rng() % 80);
        for (int &x : s)
            x = vector<int>{0, 1000, 50000, 100000}[rng() % 4];
        check(s, 100001);
    }
    check(vector<int>{}, 1);
    check(vector<int>{0,0,0}, 1);
    string bytes;
    for (int i = 0; i < 256; i++)
        bytes.push_back((char)i);
    check(bytes);
    reverse(bytes.begin(), bytes.end());
    check(bytes);
    for (int n : {1023,1024,1025,1000000})
    {
        scale(n, "a");
        scale(n, string("\xff\0\x7f\x01",4));
    }
    cout << "Suffix array dual exhaustive bytes, integer alphabets, reset, LCP minima and million-character periodic oracle PASS\n";
}
