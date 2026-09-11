#pragma once
#include <algorithm>
#include <cassert>
#include <random>
#include <utility>
#include <vector>
using namespace std;

// BEGIN Mod_Sqrt
inline vector<long long> Mod_Sqrt(long long n, int p)
{
    using ll = long long;
    assert(p >= 2);
    n = (n % p + p) % p;
    if ( n == 0 || p == 2 )
        return {n};
    auto Power = [p](ll a, ll b)
    {
        ll result = 1;
        while ( b )
        {
            if ( b & 1 )
                result = result * a % p;
            a = a * a % p;
            b >>= 1;
        }
        return result;
    };
    if ( Power(n, (p - 1) / 2) != 1 )
        return {};
    ll answer;
    if ( p % 4 == 3 )
        answer = Power(n, (ll(p) + 1) / 4);
    else
    {
        static mt19937_64 rng(712367);
        ll a, w;
        do
        {
            a = rng() % p;
            w = (a * a % p - n + p) % p;
        } while ( Power(w, (p - 1) / 2) != p - 1 );
        using P = pair<ll, ll>;
        auto Mul = [p, w](P x, P y)
        {
            ll real = (x.first * y.first + x.second * y.second % p * w) % p;
            ll imag = (x.first * y.second + x.second * y.first) % p;
            return P{real, imag};
        };
        P result{1, 0}, base{a, 1};
        ll exponent = (ll(p) + 1) / 2;
        while ( exponent )
        {
            if ( exponent & 1 )
                result = Mul(result, base);
            base = Mul(base, base);
            exponent >>= 1;
        }
        answer = result.first;
    }
    ll other = p - answer;
    if ( answer > other )
        swap(answer, other);
    return {answer, other};
}

// END Mod_Sqrt
