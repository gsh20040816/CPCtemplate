#pragma once
#include "ntt_convolution.hpp"

template <int mod = 998244353, int primitive = 3> struct Ntt2D
{
    using N = NttConvolution<mod, primitive>;
    using Z = typename N::Z;
    using Matrix = vector<vector<Z>>;
    static constexpr int max_size = N::max_size;

    static void transform(Matrix &a, bool invert = false)
    {
        assert(!a.empty() && !a[0].empty());
        int n = a.size(), m = a[0].size();
        assert(n <= max_size && (n & (n - 1)) == 0);
        assert(m <= max_size && (m & (m - 1)) == 0);
        for (auto &row : a)
        {
            assert((int)row.size() == m);
            N::ntt(row, invert);
        }
        vector<Z> column(n);
        for (int j = 0; j < m; j++)
        {
            for (int i = 0; i < n; i++)
                column[i] = a[i][j];
            N::ntt(column, invert);
            for (int i = 0; i < n; i++)
                a[i][j] = column[i];
        }
    }

    static Matrix multiply(Matrix a, Matrix b)
    {
        if (a.empty() || b.empty() || a[0].empty() || b[0].empty())
            return {};
        int h = a[0].size(), w = b[0].size();
        for (const auto &row : a)
            assert((int)row.size() == h);
        for (const auto &row : b)
            assert((int)row.size() == w);
        assert(a.size() + b.size() - 1 <= max_size);
        assert((long long)h + w - 1 <= max_size);
        int n = a.size() + b.size() - 1, m = h + w - 1;
        int x = 1, y = 1;
        while (x < n)
            x *= 2;
        while (y < m)
            y *= 2;
        a.resize(x);
        b.resize(x);
        for (auto &row : a)
            row.resize(y);
        for (auto &row : b)
            row.resize(y);
        transform(a);
        transform(b);
        for (int i = 0; i < x; i++)
            for (int j = 0; j < y; j++)
                a[i][j] *= b[i][j];
        transform(a, true);
        a.resize(n);
        for (auto &row : a)
            row.resize(m);
        return a;
    }
};
