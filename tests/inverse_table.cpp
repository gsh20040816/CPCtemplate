#include "../src/compact/inverse_table.hpp"
#include "../src/classic/inverse_table.hpp"
#include "../src/compact/number_theory.hpp"
#include "../src/classic/number_theory.hpp"
#include <iostream>

void check(int n, int p)
{
    auto a = inverse_table(n, p);
    auto b = Inverse_Table(n, p);
    assert(a == b && (int)a.size() == n + 1 && a[0] == 0);
    for (int i = 1; i <= n; i++)
    {
        assert(0 < a[i] && a[i] < p);
        assert(1LL * i * a[i] % p == 1);
    }
}

int main()
{
    for (int p = 2; p <= 300; p++)
    {
        bool prime = true;
        for (int d = 2; d * d <= p; d++)
            if (p % d == 0)
                prime = false;
        if (!prime)
            continue;
        for (int a = 1; a < p; a++)
        {
            auto x = NumberTheory::power(a, p - 2, p);
            auto y = Number_Theory::Power(a, p - 2, p);
            assert(x == y && x * a % p == 1);
        }
        for (int n = 0; n < p; n++)
            check(n, p);
    }
    check(3000000, 998244353);
    check(1000000, INT_MAX);
    // Audit the older general inverse independently, including composite moduli.
    for (int m = 1; m <= 100; m++)
        for (int a = -2*m; a <= 2*m; a++)
        {
            int want = -1;
            for (int x = 0; x < m; x++)
                if ((1LL * a * x % m + m) % m == 1 % m)
                {
                    want = x;
                    break;
                }
            assert(NumberTheory::inverse(a,m) == want);
            assert(Number_Theory::Inverse(a,m) == want);
        }
    cout << "Inverse table dual prime-prefix certificates, n=0, int32 modulus, three million entries and general inverse brute oracle PASS\n";
}
