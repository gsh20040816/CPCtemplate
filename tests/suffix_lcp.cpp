#include "../src/compact/suffix_lcp.hpp"
#include "../src/classic/suffix_lcp.hpp"
#include <iostream>
#include <random>

void check(const vector<int> &s, int alphabet)
{
    int n = s.size();
    SuffixArray forward(s, alphabet);
    Suffix_Array forward_classic(s, alphabet);
    SuffixLCP a(forward);
    Suffix_LCP b(forward_classic);
    vector<int> reverse_s(s.rbegin(), s.rend());
    SuffixLCP reverse_a{SuffixArray(reverse_s, alphabet)};
    Suffix_LCP reverse_b{Suffix_Array(reverse_s, alphabet)};
    // Queries own their rank and RMQ data; source lifetime is irrelevant.
    forward.init({}, 1);
    forward_classic.Init({}, 1);
    for (int x = 0; x <= n; x++)
        for (int y = 0; y <= n; y++)
        {
            int prefix = 0, suffix = 0;
            while (x + prefix < n && y + prefix < n && s[x + prefix] == s[y + prefix])
                prefix++;
            while (suffix < x && suffix < y && s[x - suffix - 1] == s[y - suffix - 1])
                suffix++;
            assert(a.query(x, y) == prefix && b.Query(x, y) == prefix);
            assert(prefix_lcs(reverse_a, x, y) == suffix);
            assert(Prefix_Lcs(reverse_b, x, y) == suffix);
        }
    for (int l1 = 0; l1 <= n; l1++)
        for (int r1 = l1; r1 <= n; r1++)
            for (int l2 = 0; l2 <= n; l2++)
                for (int r2 = l2; r2 <= n; r2++)
                {
                    int x = l1, y = l2;
                    while (x < r1 && y < r2 && s[x] == s[y])
                    {
                        x++;
                        y++;
                    }
                    int expected;
                    if (x == r1 || y == r2)
                        expected = (x != r1) - (y != r2);
                    else
                        expected = (s[x] > s[y]) - (s[x] < s[y]);
                    assert(a.compare(l1, r1, l2, r2) == expected);
                    assert(b.Compare(l1, r1, l2, r2) == expected);
                }
    vector<long long> start(n), finish(n);
    for (int l = 0; l < n; l++)
        for (int len = 1; len <= (n-l)/2; len++)
        {
            bool equal = true;
            for (int j = 0; j < len; j++)
                equal &= s[l+j] == s[l+len+j];
            if (equal)
            {
                start[l]++;
                finish[l+2*len-1]++;
            }
        }
    auto expected_counts = make_pair(start,finish);
    assert(square_counts(a,reverse_a) == expected_counts);
    assert(Square_Counts(b,reverse_b) == expected_counts);
    a.init(forward);
    b.Init(forward_classic);
    assert(a.query(0, 0) == 0 && b.Query(0, 0) == 0);
    assert(a.compare(0, 0, 0, 0) == 0 && b.Compare(0, 0, 0, 0) == 0);
    forward.init(s, alphabet);
    forward_classic.Init(s, alphabet);
    a.init(forward);
    b.Init(forward_classic);
    assert(a.query(0, 0) == n && b.Query(0, 0) == n);
}

int main()
{
    for (int n = 0, total = 1; n <= 7; n++, total *= 3)
        for (int code = 0; code < total; code++)
        {
            int x = code;
            vector<int> s(n);
            for (int &c : s)
            {
                c = vector<int>{0,127,255}[x % 3];
                x /= 3;
            }
            check(s, 256);
        }
    mt19937 rng(20260912);
    for (int trial = 0; trial < 150; trial++)
    {
        vector<int> s(rng() % 21);
        for (int &c : s)
            c = rng() % 5;
        check(s, 5);
    }
    check({100000,0,50000,100000,0,100000},100001);
    string bytes("\xff\0\x7f\xff\0",5);
    SuffixLCP byte_a{SuffixArray(bytes)};
    Suffix_LCP byte_b{Suffix_Array(bytes)};
    assert(byte_a.query(0,3) == 2 && byte_b.Query(0,3) == 2);
    assert(byte_a.compare(0,1,2,3) == 1 && byte_b.Compare(0,1,2,3) == 1);
    const int n = 200000;
    string s(n, 0);
    for (int i = 0; i < n; i++)
        s[i] = "dcba"[i % 4];
    SuffixLCP a{SuffixArray(s)};
    Suffix_LCP b{Suffix_Array(s)};
    reverse(s.begin(), s.end());
    SuffixLCP reverse_a{SuffixArray(s)};
    Suffix_LCP reverse_b{Suffix_Array(s)};
    for (int trial = 0; trial < 100000; trial++)
    {
        int x = rng() % (n+1), y = rng() % (n+1);
        int prefix = x % 4 == y % 4 ? n - max(x,y) : 0;
        int suffix = x % 4 == y % 4 ? min(x,y) : 0;
        assert(a.query(x,y) == prefix && b.Query(x,y) == prefix);
        assert(prefix_lcs(reverse_a,x,y) == suffix);
        assert(Prefix_Lcs(reverse_b,x,y) == suffix);
        int r1 = x + rng() % (n-x+1), r2 = y + rng() % (n-y+1);
        int len1 = r1-x, len2 = r2-y;
        int expected = prefix >= min(len1,len2) ? (len1>len2)-(len1<len2)
                      : (x%4<y%4 ? 1 : -1);
        assert(a.compare(x,r1,y,r2) == expected);
        assert(b.Compare(x,r1,y,r2) == expected);
    }
    auto counts = square_counts(a,reverse_a);
    auto classic_counts = Square_Counts(b,reverse_b);
    assert(counts == classic_counts);
    for (int i = 0; i < n; i++)
    {
        assert(counts.first[i] == (n-i)/8);
        assert(counts.second[i] == (i+1)/8);
    }
    cout << "Suffix LCP dual exhaustive substring comparison, reversed prefix LCS, square counts, reset and large RMQ PASS\n";
}
