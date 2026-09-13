#pragma once
#include "algebra.hpp"
#include "linear_congruence.hpp"

struct PrimePowerRoots
{
    using ll = long long;
    ll first = 0, step = 1, lifts = 1;
    array<ll, 2> ratio{1, 1}, count{1, 1};

    ll size() const { return count[0] * count[1] * lifts; }

    ll get(ll i, ll j, ll lift) const
    {
        assert(i >= 0 && i < count[0] && j >= 0 && j < count[1]);
        assert(lift >= 0 && lift < lifts);
        ll x = (__int128)first * Mod64::power(ratio[0], i, step) % step;
        x = (__int128)x * Mod64::power(ratio[1], j, step) % step;
        return x + lift * step;
    }

    // p prime, 1 <= e, p^e <= 1e12, k > 0.
    // For odd p, g must be a primitive root modulo p^e. For p=2, g is unused.
    static optional<PrimePowerRoots>
    solve(ll a, unsigned long long k, ll p, int e, ll g = 0)
    {
        assert(p >= 2 && p <= 1000000000000LL && e >= 1 && e <= 39 && k > 0);
        array<ll, 40> power{1};
        for (int i = 1; i <= e; i++)
        {
            assert(power[i - 1] <= 1000000000000LL / p);
            power[i] = power[i - 1] * p;
        }
        ll mod = power[e];
        a %= mod;
        if (a < 0) a += mod;
        PrimePowerRoots answer;
        if (a == 0)
        {
            answer.step = power[(e - 1) / k + 1];
            answer.lifts = mod / answer.step;
            return answer;
        }
        int t = 0;
        while (a % p == 0)
        {
            a /= p;
            ++t;
        }
        if (t % k) return nullopt;
        ll scale = power[t / k], q = power[e - t];
        answer.first = 1;
        answer.step = scale * q;
        answer.lifts = mod / answer.step;
        auto cyclic = [&](ll base, ll target, ll order, int slot)
        {
            ll logarithm = DiscreteLog::solve(base, target, q);
            if (logarithm < 0) return false;
            auto [x, period] = linear_congruence(k % order, -logarithm, order);
            if (x < 0) return false;
            answer.first = (__int128)answer.first * Mod64::power(base, x, q) % q;
            answer.ratio[slot] = Mod64::power(base, period, q);
            answer.count[slot] = order / period;
            return true;
        };
        if (p != 2)
        {
            assert(g >= 1 && g < mod);
            if (!cyclic(g % q, a, q / p * (p - 1), 0)) return nullopt;
        }
        else if (q >= 4)
        {
            int sign = a % 4 == 3;
            auto [x, period] = linear_congruence(k % 2, -sign, 2);
            if (x < 0) return nullopt;
            answer.first = x ? q - 1 : 1;
            answer.ratio[0] = period == 1 ? q - 1 : 1;
            answer.count[0] = 2 / period;
            if (q >= 8 && !cyclic(5, sign ? q - a : a, q / 4, 1)) return nullopt;
        }
        answer.first *= scale;
        return answer;
    }
};
