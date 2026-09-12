#include "../src/compact/primitive_root.hpp"
#include "../src/classic/primitive_root.hpp"
#include <iostream>

int brute_order(long long a, int n)
{
    a = (a % n + n) % n;
    long long x = 1;
    for (int k = 1; k <= n; k++)
    {
        x = x * a % n;
        if (x == 1)
            return k;
    }
    return 0;
}

int main()
{
    PrimitiveRoot a(2);
    Primitive_Root b(2);
    for (int n = 2; n <= 400; n++)
    {
        a.init(n);
        b.Init(n);
        int phi = 0;
        for (int g = 1; g < n; g++)
            phi += gcd(g, n) == 1;
        assert(a.phi == phi && b.phi == phi);
        vector<int> expected;
        for (int g = 0; g < n; g++)
        {
            int order = brute_order(g, n);
            assert(a.order(g) == order && b.Order(g) == order);
            assert(a.is_root(g) == (order == phi));
            assert(b.Is_Root(g) == (order == phi));
            if (order == phi)
                expected.push_back(g);
        }
        assert(a.exists == !expected.empty() && b.exists == !expected.empty());
        assert(a.minimum() == (expected.empty() ? -1 : expected[0]));
        assert(b.Minimum() == a.minimum());
        assert(a.all() == expected && b.All() == expected);
        for (long long x : {LLONG_MIN, LLONG_MAX, -1LL, 0LL})
        {
            int order = brute_order(x, n);
            assert(a.order(x) == order && b.Order(x) == order);
            assert(a.is_root(x) == (order == phi));
            assert(b.Is_Root(x) == (order == phi));
        }
    }
    for (int n : {998244353, 2147483647, 1000000000, 1000000, 999983})
    {
        a.init(n);
        b.Init(n);
        int g = a.minimum();
        assert(g == b.Minimum());
        if (g != -1)
        {
            assert(a.order(g) == a.phi && b.Order(g) == b.phi);
            // Each prime divisor witnesses that no proper divisor is the order.
            for (int q : a.factors)
                assert(NumberTheory::power(g, a.phi / q, n) != 1);
        }
        else
            assert(n == 1000000000 || n == 1000000);
        if (n == 998244353)
            assert(g == 3);
    }
    // Full residue-cycle oracle at the judge's largest prime scale.
    a.init(999983);
    b.Init(999983);
    int g = a.minimum();
    vector<bool> seen(a.mod);
    vector<int> expected;
    long long x = 1;
    for (int k = 1; k <= a.phi; k++)
    {
        x = x * g % a.mod;
        assert(!seen[x]);
        seen[x] = true;
        if (gcd(k, a.phi) == 1)
            expected.push_back(x);
    }
    sort(expected.begin(), expected.end());
    assert(expected == a.all() && expected == b.All());
    cout << "Primitive root dual exhaustive power-cycle oracle, orders, signed inputs, existence, reset, int32 bounds and 999983 full cycle PASS\n";
}
