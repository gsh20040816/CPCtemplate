#pragma once
#include "prime_power_roots.hpp"
#include "root_factors.hpp"

struct CompositeRoots
{
    using ll = long long;
    ll mod = 1, total = 1;
    vector<PrimePowerRoots> parts;
    vector<ll> weight;

    ll get(ll index) const
    {
        assert(index >= 0 && index < total);
        ll answer = 0;
        for (int t = 0; t < (int)parts.size(); t++)
        {
            const auto &p = parts[t];
            ll local = index % p.size();
            index /= p.size();
            ll lift = local % p.lifts;
            local /= p.lifts;
            ll j = local % p.count[1], i = local / p.count[1];
            ll root = p.get(i, j, lift);
            answer = (answer + (__int128)root * weight[t]) % mod;
        }
        return answer;
    }

    // Factors are distinct primes with positive exponents: (p, e, g).
    // Odd-prime g is a primitive root modulo p^e; for p=2 use g=0.
    static optional<CompositeRoots>
    solve(ll a, unsigned long long k, const vector<tuple<ll, int, ll>> &factors)
    {
        assert(k > 0);
        CompositeRoots answer;
        for (auto [p, e, g] : factors)
        {
            auto roots = PrimePowerRoots::solve(a, k, p, e, g);
            if (!roots) return nullopt;
            ll m = roots->step * roots->lifts;
            assert(gcd(answer.mod, m) == 1);
            assert(answer.mod <= 1000000000000LL / m);
            answer.mod *= m;
            answer.total *= roots->size();
            answer.parts.push_back(*roots);
        }
        for (const auto &p : answer.parts)
        {
            ll m = p.step * p.lifts, rest = answer.mod / m;
            ll inverse = mod_inverse(rest % m, m);
            answer.weight.push_back((__int128)rest * inverse % answer.mod);
        }
        return answer;
    }

    static optional<CompositeRoots>
    solve(ll a, unsigned long long k, ll mod, PollardRho &rho)
    {
        return solve(a, k, root_factors(mod, rho));
    }
};
