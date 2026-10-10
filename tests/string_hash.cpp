#include <bits/stdc++.h>
#include "../src/compact/string_hash.hpp"
using namespace std;

void check(bool ok)
{
    if (!ok) abort();
}

StringHash::H truth(const string &s, StringHash::H base)
{
    StringHash::H ans{};
    for (int j = 0; j < 2; j++)
    {
        long long power = 1;
        for (int i = int(s.size()) - 1; i >= 0; i--)
        {
            ans[j] = (ans[j] + power * ((unsigned char)s[i] + 1)) % StringHash::mod[j];
            power = power * base[j] % StringHash::mod[j];
        }
    }
    return ans;
}

void verify(const string &s, StringHash::H base)
{
    StringHash h(s, base);
    int n = s.size();
    for (int l = 0; l <= n; l++)
    {
        for (int r = l; r <= n; r++)
        {
            string t = s.substr(l, r - l);
            check(h.get(l, r) == truth(t, base));
            StringHash other(t, base);
            check(h.get(l, r) == other.get(0, t.size()));
            reverse(t.begin(), t.end());
            check(h.get(l, r, true) == truth(t, base));
            for (int k = l; k <= r; k++)
            {
                check(h.join(h.get(l, k), h.get(k, r), r - k) == h.get(l, r));
            }
        }
    }
    auto whole = h.get(0, n);
    auto twice = h.join(whole, whole, n);
    check(twice == truth(s + s, base));
    check(h.join(twice, whole, n) == truth(s + s + s, base));
}

int main()
{
    mt19937 rng(3370);
    for (int n = 0; n <= 6; n++)
    {
        int total = 1;
        for (int i = 0; i < n; i++) total *= 3;
        for (int mask = 0; mask < total; mask++)
        {
            int x = mask;
            string s(n, 0);
            for (char &c : s)
            {
                c = array<int, 3>{0, 128, 255}[x % 3];
                x /= 3;
            }
            verify(s, {257, 263});
            verify(s, {1000000005, 1000000007});
        }
    }
    for (int c = 0; c < 256; c++) verify(string(1, c), {257, 1000000007});
    for (int it = 0; it < 200; it++)
    {
        string s(rng() % 31, 0);
        for (char &c : s) c = rng() % 256;
        StringHash::H b;
        for (int j = 0; j < 2; j++)
        {
            b[j] = uniform_int_distribution<int>(257, StringHash::mod[j] - 2)(rng);
        }
        verify(s, b);
    }
    string a{char(0), char(2)}, b{char(1), char(4)};
    StringHash x(a, {1000000005, 1000000007});
    StringHash y(b, x.base);
    check(a != b && x.get(0, 2) == y.get(0, 2));
    check(x.get(0, 2) == StringHash::H{1, 1});
    string big(1000000, 'a');
    for (char &c : big) c = rng() % 256;
    StringHash h(big, {911382323, 972663749});
    check(h.get(0, big.size()) == truth(big, h.base));
    for (int it = 0; it < 10000; it++)
    {
        int l = rng() % big.size();
        int r = min(int(big.size()), l + int(rng() % 50));
        string t = big.substr(l, r - l);
        check(h.get(l, r) == truth(t, h.base));
        reverse(t.begin(), t.end());
        check(h.get(l, r, true) == truth(t, h.base));
    }
    cout << "PASS exhaustive bytes, intervals, reverse, joins, real collision, million-byte stress\n";
}
