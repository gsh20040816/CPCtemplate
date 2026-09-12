#pragma once
#include "number_theory.hpp"

struct Primitive_Root
{
    int mod, phi;
    bool exists;
    vector<int> Factors;

    static vector<int> Factor(int n)
    {
        vector<int> result;
        for ( int p = 2; p <= n / p; p++ )
            if ( n % p == 0 )
            {
                result.push_back(p);
                while ( n % p == 0 )
                    n /= p;
            }
        if ( n > 1 )
            result.push_back(n);
        return result;
    }

    Primitive_Root(int n)
    {
        Init(n);
    }

    void Init(int n)
    {
        assert(n >= 2);
        mod = n;
        phi = n;
        for ( int p : Factor(n) )
            phi -= phi / p;
        int odd = n;
        if ( odd % 2 == 0 )
            odd /= 2;
        exists = n == 2 || n == 4 || (odd % 2 && Factor(odd).size() == 1);
        Factors = Factor(phi);
    }

    int Order(long long a) const
    {
        a %= mod;
        if ( a < 0 )
            a += mod;
        if ( gcd(a, (long long)mod) != 1 )
            return 0;
        int result = phi;
        for ( int p : Factors )
            while ( result % p == 0 && Number_Theory::Power(a, result / p, mod) == 1 )
                result /= p;
        return result;
    }

    bool Is_Root(long long a) const
    {
        if ( !exists )
            return false;
        a %= mod;
        if ( a < 0 )
            a += mod;
        if ( gcd(a, (long long)mod) != 1 )
            return false;
        for ( int p : Factors )
            if ( Number_Theory::Power(a, phi / p, mod) == 1 )
                return false;
        return true;
    }

    int Minimum() const
    {
        if ( !exists )
            return -1;
        for ( int g = 1; g < mod; g++ )
            if ( Is_Root(g) )
                return g;
        return -1;
    }

    vector<int> All() const
    {
        int g = Minimum();
        vector<int> roots;
        if ( g == -1 )
            return roots;
        long long value = 1;
        for ( int k = 1; k <= phi; k++ )
        {
            value = value * g % mod;
            if ( gcd(k, phi) == 1 )
                roots.push_back(value);
        }
        sort(roots.begin(), roots.end());
        return roots;
    }
};
