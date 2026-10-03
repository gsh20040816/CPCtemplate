#include "../src/compact/number_theory.hpp"
#include "../src/compact/lucas.hpp"
#include "../src/compact/exlucas.hpp"

template <class C> int count_paths(C choose, int mod, int kind, int a, int b, int c)
{
    // Test-sized signed parameters: all sums fit int before API conversion.
    auto Cnk = [&](int n, int k) -> long long
    {
        return n < 0 || k < 0 || k > n ? 0 : choose(n, k);
    };
    long long x = 0;
    if (kind == 0)
    {
        int l = a, h = b, e = c;
        if (h < 0 || e < 0 || abs(e - h) > l || (l + e - h) % 2) return 0;
        int k = (l + e - h) / 2;
        x = Cnk(l, k) - Cnk(l, k + h + 1);
    }
    else if (kind == 1)
    {
        int p = a, q = b;
        if (p < q) return 0;
        x = Cnk(p + q, q) - Cnk(p + q, q - 1);
    }
    else
    {
        int p = a, q = b;
        if (p + q == 0) return 1 % mod;
        if (p <= q) return 0;
        x = Cnk(p + q - 1, q) - Cnk(p + q - 1, q - 1);
    }
    return (x % mod + mod) % mod;
}

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    Binomial<1000003> binom(1000);
    map<int, Lucas> lucas;
    map<int, ExLucas> exlucas;
    char op;
    int mod, kind, a, b, c;
    while (cin >> op >> mod >> kind >> a >> b >> c)
    {
        int result;
        if (op == 'F')
        {
            assert(mod == 1000003);
            result = count_paths([&](int n, int k) { return binom.choose(n, k).v; },
                                 mod, kind, a, b, c);
        }
        else if (op == 'L')
        {
            auto &z = lucas.try_emplace(mod, mod).first->second;
            result = count_paths([&](int n, int k) { return z.choose(n, k); },
                                 mod, kind, a, b, c);
        }
        else
        {
            assert(op == 'E');
            auto &z = exlucas.try_emplace(mod, mod).first->second;
            result = count_paths([&](int n, int k) { return z.choose(n, k); },
                                 mod, kind, a, b, c);
        }
        cout << result << '\n';
    }
}
