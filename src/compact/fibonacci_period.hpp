#pragma once
#include "number_theory.hpp"

struct FibonacciPeriod
{
    using ull = unsigned long long;
    using u128 = __uint128_t;
    PollardRho factorizer;

    static pair<ull, ull> fib(u128 k, ull m)
    {
        assert(m >= 1);
        if (k == 0)
            return {0, 1 % m};
        auto [a, b] = fib(k / 2, m);
        ull c = Mod64::mul(a, (u128(2) * b + m - a) % m, m);
        ull d = (u128(Mod64::mul(a, a, m)) + Mod64::mul(b, b, m)) % m;
        if (k & 1)
            return {d, (u128(c) + d) % m};
        return {c, d};
    }

    static bool is_period(u128 k, ull m)
    {
        return k > 0 && fib(k, m) == make_pair(0ULL, 1 % m);
    }

    u128 prime_period(ull p)
    {
        if (p == 2)
            return 3;
        if (p == 5)
            return 20;
        bool square = p % 5 == 1 || p % 5 == 4;
        ull base = square ? p - 1 : p + 1;
        u128 t = u128(base) * (square ? 1 : 2);
        auto factors = factorizer.factor(base);
        if (!square)
            factors.push_back(2);
        for (ull q : factors)
            while (t % q == 0 && is_period(t / q, p))
                t /= q;
        return t;
    }

    static u128 gcd128(u128 a, u128 b)
    {
        while (b)
        {
            u128 r = a % b;
            a = b;
            b = r;
        }
        return a;
    }

    u128 period(ull m)
    {
        assert(m >= 1);
        auto factors = factorizer.factor(m);
        u128 answer = 1;
        for (int i = 0; i < (int)factors.size();)
        {
            ull p = factors[i];
            ull power = p;
            u128 t = prime_period(p);
            i++;
            while (i < (int)factors.size() && factors[i] == p)
            {
                power *= p;
                if (!is_period(t, power))
                    t *= p;
                i++;
            }
            answer = answer / gcd128(answer, t) * t;
        }
        return answer;
    }
};
