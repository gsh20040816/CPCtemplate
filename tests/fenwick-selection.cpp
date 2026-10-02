#include "../src/compact/data_structure.hpp"

long long states = 0, selections = 0;

void check(const Fenwick<long long> &f, const vector<long long> &a)
{
    int n = int(a.size()) - 1;
    vector<long long> prefix(n + 1);
    for (int i = 1; i <= n; i++)
    {
        assert(a[i] >= 0);
        prefix[i] = prefix[i - 1] + a[i];
        assert(f.sum(i) == prefix[i]);
        assert(f.query(i, i) == a[i]);
    }
    assert(f.sum(0) == 0);
    vector<long long> ks = {1, prefix[n] + 1, LLONG_MAX};
    for (int i = 1; i <= n; i++)
    {
        if (a[i])
        {
            ks.push_back(prefix[i - 1] + 1);
            ks.push_back(prefix[i]);
        }
    }
    for (long long k : ks)
    {
        int want = lower_bound(prefix.begin() + 1, prefix.end(), k) - prefix.begin();
        assert(f.kth(k) == want);
        selections++;
    }
    if (n) assert(f.query(1, n) == prefix[n]);
    states++;
}

int main()
{
    // Complete ternary frequency enumeration, including empty trees and zero gaps.
    for (int n = 0; n <= 9; n++)
    {
        int count = 1;
        for (int i = 0; i < n; i++) count *= 3;
        for (int mask = 0; mask < count; mask++)
        {
            Fenwick<long long> f(n);
            vector<long long> a(n + 1);
            int code = mask;
            for (int i = 1; i <= n; i++)
            {
                a[i] = code % 3;
                code /= 3;
                f.add(i, a[i]);
            }
            check(f, a);
            for (int i = n; i >= 1; i--)
            {
                if (a[i])
                {
                    f.add(i, -1);
                    a[i]--;
                }
            }
            check(f, a);
        }
    }
    mt19937_64 rng(3369210);
    for (int trial = 0; trial < 100; trial++)
    {
        int n = 1 + rng() % 257;
        Fenwick<long long> f(n);
        vector<long long> a(n + 1);
        for (int step = 0; step < 500; step++)
        {
            int p = 1 + rng() % n;
            long long next = step % 3 == 0 ? 0 : rng() % 1000000000001LL;
            f.add(p, next - a[p]);
            a[p] = next;
            if (step % 10 == 0 || step == 499) check(f, a);
        }
    }
    // Powers of two, both adjacent sizes, and maximum P3369 operation-domain size.
    for (int n : {1, 2, 3, 31, 32, 33, 65535, 65536, 65537, 100000})
    {
        Fenwick<long long> f(n);
        vector<long long> a(n + 1);
        for (int i = 1; i <= n; i++)
        {
            a[i] = i % 7;
            f.add(i, a[i]);
        }
        check(f, a);
        for (int i = 1; i <= n; i += 3)
        {
            f.add(i, -a[i]);
            a[i] = 0;
        }
        check(f, a);
        for (int i = 1; i <= n; i++)
        {
            f.add(i, -a[i]);
            a[i] = 0;
        }
        check(f, a);
    }
    cout << "Fenwick selection independent prefix-array oracle: " << states
         << " states, " << selections << " kth checks PASS\n";
}
