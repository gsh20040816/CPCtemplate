#pragma once
#include "fps_functions.hpp"
#include "set_convolution.hpp"
#include "recurrence.hpp"

// Compatibility entry; the handbook prints the independently classified modules.
struct Polynomial : FpsFunctions
{
    static void fwt(Poly &a, char op, bool invert = false)
    {
        SetConvolution<mod>::transform(a, op, invert);
    }

    static Poly berlekamp_massey(const Poly &s)
    {
        vector<int> a;
        for (auto x : s) a.push_back(x.v);
        auto c = ::berlekamp_massey(a, mod);
        return Poly(c.begin(), c.end());
    }

    static Z recurrence(Poly init, const Poly &c, unsigned long long n)
    {
        if (n < init.size()) return init[n];
        if (c.empty()) return 0;
        assert(init.size() >= c.size());
        vector<int> a, b;
        for (int i = 0; i < (int)c.size(); i++)
        {
            a.push_back(init[i].v);
            b.push_back(c[i].v);
        }
        return ::recurrence_nth(a, b, n, mod);
    }
};
