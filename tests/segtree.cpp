#include "../src/compact/segtree.hpp"

string cat(string a, string b)
{
    return a + b;
}

string empty_string()
{
    return "";
}

long long add(long long a, long long b)
{
    return a + b;
}

long long zero()
{
    return 0;
}

int main()
{
    mt19937 rng(42865);
    for (int n = 0; n <= 70; n++)
    {
        vector<string> a(n);
        for (auto &x : a) x = char('a' + rng() % 3);
        segtree<string, cat, empty_string> s(a);
        for (int t = 0; t < 40; t++)
        {
            if (n)
            {
                int p = rng() % n;
                a[p] = char('a' + rng() % 3);
                s.set(p, a[p]);
                assert(s.get(p) == a[p]);
            }
            string all;
            for (auto x : a) all += x;
            assert(s.all() == all);
            // Avoiding "ab" is monotone under extension, but not commutative.
            auto ok = [](const string &x)
            {
                return x.find("ab") == string::npos;
            };
            for (int l = 0; l <= n; l++)
            {
                string x;
                int best = l;
                for (int r = l; r <= n; r++)
                {
                    assert(s.prod(l, r) == x);
                    if (ok(x)) best = r;
                    if (r < n) x += a[r];
                }
                assert(s.max_right(l, ok) == best);
            }
            for (int r = 0; r <= n; r++)
            {
                string x;
                int best = r;
                for (int l = r; l >= 0; l--)
                {
                    if (ok(x)) best = l;
                    if (l) x = a[l - 1] + x;
                }
                assert(s.min_left(r, ok) == best);
            }
        }
    }
    int n = 500000;
    segtree<long long, add, zero> s(vector<long long>(n, 1));
    for (int i = 0; i < n; i += 127)
    {
        int len = min(n - i, 231);
        assert(s.max_right(i, [&](long long x) { return x <= len; }) == i + len);
        len = min(i, 197);
        assert(s.min_left(i, [&](long long x) { return x <= len; }) == i - len);
    }
    assert(s.prod(0, n) == n);
    cout << "Generic segtree: noncommutative substring oracle, both monotone boundary "
            "scans, empty trees and 500000 leaves PASS\n";
}
