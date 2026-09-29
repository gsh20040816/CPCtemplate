#include <bits/stdc++.h>
#include "../src/compact/division_tree.hpp"
using namespace std;
mt19937_64 rng(2026093003);
long long calls = 0;

void check(const vector<long long> &a, bool full)
{
    auto saved = a;
    DivisionTree tree(a);
    assert(a == saved);
    int n = a.size();
    auto query = [&](int l, int r)
    {
        vector<long long> v(a.begin() + l, a.begin() + r);
        sort(v.begin(), v.end());
        for (int k = 0; k < r - l; k++)
        {
            assert(tree.kth(l, r, k) == v[k]);
            calls++;
        }
    };
    if (full)
    {
        for (int l = 0; l < n; l++)
            for (int r = l + 1; r <= n; r++) query(l, r);
    }
    else if (n)
    {
        query(0, n);
        for (int t = 0; t < 70; t++)
        {
            int l = rng() % n, r = l + 1 + rng() % (n - l);
            query(l, r);
        }
    }
}

int main()
{
    int exhaustive = 0;
    for (int n = 0, pow3 = 1; n <= 7; n++, pow3 *= 3)
        for (int mask = 0; mask < pow3; mask++)
        {
            vector<long long> a(n);
            int x = mask;
            for (auto &v : a)
            {
                v = x % 3 - 1;
                x /= 3;
            }
            check(a, true);
            exhaustive++;
        }
    for (int t = 0; t < 700; t++)
    {
        vector<long long> a(rng() % 150);
        for (auto &v : a)
        {
            if (t % 3 == 0)
                v = (long long)(rng() % 9) - 4;
            else if (t % 3 == 1)
                v = rng() & 1 ? LLONG_MIN : LLONG_MAX;
            else
                v = bit_cast<long long>(rng());
        }
        check(a, false);
    }
    for (int n : {31, 32, 33, 63, 64, 65, 127, 128, 129, 255, 256, 257})
    {
        vector<long long> a(n);
        iota(a.begin(), a.end(), -100);
        check(a, false);
        reverse(a.begin(), a.end());
        check(a, false);
        // Many occurrences of the splitting value require an exact left quota.
        fill(a.begin(), a.end(), 0);
        a[0] = LLONG_MIN;
        a.back() = LLONG_MAX;
        check(a, false);
    }
    int n = 500000;
    vector<long long> a(n);
    for (int mode = 0; mode < 3; mode++)
    {
        if (mode == 0) iota(a.begin(), a.end(), -250000);
        if (mode == 1) reverse(a.begin(), a.end());
        if (mode == 2) fill(a.begin(), a.end(), LLONG_MIN);
        DivisionTree tree(a);
        for (int t = 0; t < 200000; t++)
        {
            int l = rng() % n, r = l + 1 + rng() % (n - l), k = rng() % (r - l);
            auto want = mode == 0 ? a[l + k] : mode == 1 ? a[r - 1 - k] : LLONG_MIN;
            assert(tree.kth(l, r, k) == want);
            calls++;
        }
    }
    cout << "DivisionTree PASS: " << exhaustive
         << " exhaustive arrays, 700 random, 36 power-of-two/quota boundaries, three "
            "500000-element arrays; "
         << calls << " sorting/closed-form checks\n";
}
