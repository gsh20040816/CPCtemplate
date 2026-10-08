#include "../src/compact/dc3.hpp"
namespace original
{
#include "fixtures/dc3_sources/kuangbin.cpp"
}
long long cases = 0, source_cases = 0;

void require(bool value)
{
    if (!value)
        throw runtime_error("DC3 verification failed");
}

vector<int> doubling(const vector<int> &s)
{
    int n = s.size();
    vector<int> sa(n), rank = s, next(n);
    iota(sa.begin(), sa.end(), 0);
    for (int k = 1; k < max(n, 2); k *= 2)
    {
        auto key = [&](int i)
        {
            return pair{rank[i], i + k < n ? rank[i + k] : -1};
        };
        sort(sa.begin(), sa.end(), [&](int a, int b)
        {
            return key(a) < key(b);
        });
        if (n)
            next[sa[0]] = 0;
        for (int i = 1; i < n; i++)
            next[sa[i]] = next[sa[i - 1]] + (key(sa[i - 1]) != key(sa[i]));
        rank = next;
        if (!n || rank[sa.back()] == n - 1)
            break;
    }
    return sa;
}

void check(const vector<int> &s, int alphabet)
{
    cases++;
    int n = s.size();
    auto input = s;
    DC3 d(s, alphabet);
    require(s == input);
    vector<int> expected(n);
    iota(expected.begin(), expected.end(), 0);
    sort(expected.begin(), expected.end(), [&](int a, int b)
    {
        return lexicographical_compare(s.begin() + a, s.end(), s.begin() + b, s.end());
    });
    require(d.sa == expected);
    require(d.rk.size() == s.size() && d.lcp.size() == s.size());
    for (int i = 0; i < n; i++)
    {
        require(d.rk[d.sa[i]] == i);
        int k = 0;
        if (i)
        {
            int a = d.sa[i - 1], b = d.sa[i];
            while (a + k < n && b + k < n && s[a + k] == s[b + k])
                k++;
        }
        require(d.lcp[i] == k);
    }
    if (alphabet <= 256)
    {
        string text;
        for (int c : s)
            text.push_back((char)c);
        DC3 bytes(text);
        require(bytes.sa == d.sa && bytes.rk == d.rk && bytes.lcp == d.lcp);
    }
    if (n && n <= 2000 && alphabet <= 256)
    {
        source_cases++;
        vector<int> a(3 * original::MAXN), sa(a.size()), rank(a.size()), height(a.size());
        for (int i = 0; i < n; i++)
            a[i] = s[i] + 1;
        original::da(a.data(), sa.data(), rank.data(), height.data(), n, alphabet + 1);
        require(sa[0] == n);
        for (int i = 0; i < n; i++)
        {
            require(sa[i + 1] == d.sa[i]);
            require(rank[i] - 1 == d.rk[i]);
            require(height[i + 1] == d.lcp[i]);
        }
    }
}

int main()
{
    for (int alphabet : {2, 3})
    {
        int limit = alphabet == 2 ? 14 : 9;
        int count = 1;
        for (int n = 0; n <= limit; n++)
        {
            for (int mask = 0; mask < count; mask++)
            {
                vector<int> s(n);
                int value = mask;
                for (int &c : s)
                {
                    c = value % alphabet;
                    value /= alphabet;
                }
                check(s, alphabet);
            }
            count *= alphabet;
        }
    }
    mt19937 rng(20261011);
    for (int trial = 0; trial < 1000; trial++)
    {
        int n = rng() % 250;
        int alphabet = trial % 2 ? 256 : 10000;
        vector<int> s(n);
        for (int &c : s)
            c = rng() % alphabet;
        check(s, alphabet);
    }
    for (int n : {1, 2, 3, 4, 5, 1998, 1999, 2000})
        for (int period : {1, 2, 3, 7})
        {
            vector<int> s(n);
            for (int i = 0; i < n; i++)
                s[i] = i % period ? 255 : 0;
            check(s, 256);
        }
    for (int n : {10000, 10001, 10002})
    {
        vector<int> s(n);
        for (int &c : s)
            c = rng() % 7;
        DC3 d(s, 7);
        require(d.sa == doubling(s));
    }
    for (int n : {500000, 500001, 500002})
    {
        vector<int> same(n, 255);
        DC3 d(same, 256);
        for (int i = 0; i < n; i++)
        {
            require(d.sa[i] == n - 1 - i);
            require(d.rk[i] == n - 1 - i);
            require(d.lcp[i] == i);
        }
        vector<int> increasing(n);
        iota(increasing.begin(), increasing.end(), 0);
        DC3 e(increasing, n);
        for (int i = 0; i < n; i++)
            require(e.sa[i] == i && e.rk[i] == i && e.lcp[i] == 0);
    }
    cout << cases << ' ' << source_cases << '\n';
}
